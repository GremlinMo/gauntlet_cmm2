"""Independent format, navigation, and campaign checks for the extra 30 rooms."""

from collections import deque
import hashlib
from pathlib import Path
import unittest

from basic_runner import Basic


ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "MAPS"
ORIGINAL_HASHES = {
    1: "ec3a25b3a67c570d8784e940f7824c935ff622763e8dbdc409f1a5e4c134a007",
    2: "c7dac9ac47c7bc1f5e449e224c45fdd00cbc50f4dfbda771dc00c53128e8cd78",
    3: "a833143ac0903c7fba7c966e87f5001995abb97d9746340dad4cb0c9da8aabdb",
    4: "35e0bd0bccb89c204b84b317ace59c9055d15b2f9b3c8bbc26b71bb0654b1055",
    5: "45afa1912273eaad07561109dd62ab9206db253df2303b6e1fef295d0234646c",
    6: "66d521f8d8c8dc1935be67222bf992b2dd1d8851f727cbcdd90801ebe4b440fe",
    7: "7e1705aff6d6fe83af2158971763fc1f89d4fd275aebc0cdf76149eb56a69e6d",
    8: "35e0bd0bccb89c204b84b317ace59c9055d15b2f9b3c8bbc26b71bb0654b1055",
    9: "9b300ea0a28f13a3c24ac7f4f185b7077da418996ae265d705f99f734e70b5ee",
}
WALLS = set(range(88, 104))
DOORS = {22, 23}
ENEMIES = set(range(31, 88))
REWARDS = {17, 21, 24, 25, 26}


def read_map(room):
    """Read exactly the bytes consumed by LoadMap, independently of the authoring tool."""
    raw = (MAPS / f"ROOM{room:02d}.MAP").read_bytes()
    header, payload = raw.split(b"\r\n", 1)
    assert header.startswith(b"' "), (room, "missing map comment header")
    assert len(payload) == 36 * 38, (room, "wrong row count or stride")
    rows = []
    for row in range(36):
        data = payload[row * 38:(row + 1) * 38]
        assert data[36:] == b"\r\n", (room, row, "row alignment")
        assert data[34:36] == b"  ", (room, row, "column padding")
        if row < 34:
            rows.append(tuple(value - 32 for value in data[:34]))
        else:
            assert data[:34] == b" " * 34, (room, row, "row padding")
    return rows


def positions(grid, values):
    return {(x, y) for y, row in enumerate(grid)
            for x, value in enumerate(row) if value in values}


def neighbors(cell):
    x, y = cell
    return ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))


def door_groups(grid):
    pending = positions(grid, DOORS)
    groups = []
    while pending:
        group = {pending.pop()}
        frontier = list(group)
        while frontier:
            for cell in neighbors(frontier.pop()):
                if cell in pending:
                    pending.remove(cell)
                    group.add(cell)
                    frontier.append(cell)
        groups.append(group)
    return groups


def reachable(grid, start, opened=frozenset()):
    """Combat can clear enemies; normal traversal cannot cross walls or unopened doors."""
    found = {start}
    frontier = deque([start])
    while frontier:
        for cell in neighbors(frontier.popleft()):
            x, y = cell
            if not (0 <= x < 34 and 0 <= y < 30) or cell in found:
                continue
            value = grid[y][x]
            if value in WALLS or value in {106, 223}:
                continue
            if value in DOORS and cell not in opened:
                continue
            found.add(cell)
            frontier.append(cell)
    return found


def inventory_routes(grid, start):
    """Explore door choices from zero carried keys, including keys earned along the way."""
    groups = door_groups(grid)
    keys = positions(grid, {24})
    states = deque([frozenset()])
    visited = {frozenset()}
    routes = []
    while states:
        state = states.popleft()
        opened = set().union(*(groups[index] for index in state)) if state else set()
        area = reachable(grid, start, opened)
        routes.append(area)
        remaining = len(keys & area) - len(state)
        if remaining <= 0:
            continue
        for index, group in enumerate(groups):
            if index in state or not any(set(neighbors(cell)) & area for cell in group):
                continue
            next_state = state | {index}
            if next_state not in visited:
                visited.add(next_state)
                states.append(next_state)
    return routes


class MapTests(unittest.TestCase):
    def test_all_39_room_files_are_present(self):
        self.assertEqual({path.name for path in MAPS.glob("ROOM*.MAP")},
                         {f"ROOM{room:02d}.MAP" for room in range(1, 40)})

    def test_original_nine_maps_are_unchanged(self):
        for room, digest in ORIGINAL_HASHES.items():
            with self.subTest(room=room):
                actual = hashlib.sha256((MAPS / f"ROOM{room:02d}.MAP").read_bytes()).hexdigest()
                self.assertEqual(actual, digest)

    def test_new_maps_have_loader_compatible_binary_format(self):
        for room in range(10, 40):
            with self.subTest(room=room):
                grid = read_map(room)
                self.assertEqual((len(grid), len(grid[0])), (34, 34))

    def test_new_layouts_are_distinct(self):
        layouts = {tuple(read_map(room)) for room in range(10, 40)}
        self.assertEqual(len(layouts), 30)

    def test_new_maps_use_supported_tiles(self):
        # No teleports or editor-only specials: these have no gameplay handler.
        allowed = {0, 1, 17, 20, 21, 22, 23, 24, 25, 26, 105, 106} | WALLS | ENEMIES
        for room in range(10, 40):
            with self.subTest(room=room):
                actual = {value for row in read_map(room) for value in row}
                self.assertLessEqual(actual, allowed)

    def test_outer_boundaries_are_closed(self):
        for room in range(10, 40):
            with self.subTest(room=room):
                grid = read_map(room)
                edge = list(grid[0]) + list(grid[-1]) + [row[0] for row in grid] + [row[-1] for row in grid]
                self.assertTrue(all(value in WALLS for value in edge))

    def test_both_players_have_clear_spawn_space(self):
        for room in range(10, 40):
            with self.subTest(room=room):
                grid = read_map(room)
                markers = positions(grid, {1})
                self.assertEqual(len(markers), 1)
                marker_x, marker_y = next(iter(markers))
                # LoadMap positions players one column LEFT of the editor marker.
                for spawn_x, spawn_y in ((marker_x - 1, marker_y), (marker_x - 1, marker_y + 1)):
                    self.assertTrue(2 <= spawn_x <= 30 and 2 <= spawn_y <= 27)
                    for y in range(spawn_y - 2, spawn_y + 3):
                        for x in range(spawn_x - 2, spawn_x + 3):
                            self.assertIn(grid[y][x], (0, 1))

    def test_exits_and_rewards_are_reachable_from_zero_keys(self):
        for room in range(10, 40):
            with self.subTest(room=room):
                grid = read_map(room)
                marker_x, marker_y = next(iter(positions(grid, {1})))
                start = marker_x - 1, marker_y
                exits = positions(grid, {20})
                self.assertGreaterEqual(len(exits), 1)
                routes = inventory_routes(grid, start)
                self.assertTrue(any(exits & area for area in routes), "no completable exit")
                for point in positions(grid, REWARDS):
                    self.assertTrue(any(point in area for area in routes), ("unreachable reward", point))
                # Door side vaults must never force a key hunt on the main exit route.
                self.assertTrue(exits & reachable(grid, start), "exit requires unlocking a door")

    def test_new_content_fits_the_camera_reach(self):
        for room in range(10, 40):
            with self.subTest(room=room):
                grid = read_map(room)
                for x, y in positions(grid, REWARDS | ENEMIES | DOORS | {1, 20, 105}):
                    self.assertTrue(1 <= x <= 32 and 1 <= y <= 29, (x, y))

    def test_treasure_rooms_have_rewards_and_no_enemies(self):
        for room in range(12, 40, 4):
            with self.subTest(room=room):
                grid = read_map(room)
                self.assertFalse(positions(grid, ENEMIES))
                self.assertGreaterEqual(len(positions(grid, {17})), 40)

    def test_combat_rooms_include_food_and_controlled_enemy_density(self):
        for room in range(10, 40):
            if room % 4 == 0:
                continue
            with self.subTest(room=room):
                grid = read_map(room)
                self.assertGreaterEqual(len(positions(grid, {21, 25})), 2)
                self.assertGreaterEqual(len(positions(grid, ENEMIES)), 8)
                self.assertLessEqual(len(positions(grid, ENEMIES)), 100)


class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.basic = Basic(ROOT, {"roomwalloffset", "roomistreasure", "nextcampaignroom"})
        self.basic.globals.update(totalrooms=39, wallthemes=11)

    def test_wall_palette_stays_inside_the_existing_sprite_sheet(self):
        for room in range(1, 40):
            offset = self.basic.call("RoomWallOffset", room)
            self.assertEqual(offset, ((room - 1) % 11) * 18)
            self.assertTrue(0 <= offset <= 180)

    def test_treasure_schedule_includes_all_nine_treasure_rooms(self):
        treasure = [room for room in range(1, 40) if self.basic.call("RoomIsTreasure", room)]
        self.assertEqual(treasure, list(range(4, 40, 4)))

    def test_progression_stops_after_room_39(self):
        for room in range(1, 39):
            self.assertEqual(self.basic.call("NextCampaignRoom", room), room + 1)
        self.assertEqual(self.basic.call("NextCampaignRoom", 39), 0)
        self.assertEqual(self.basic.call("NextCampaignRoom", 40), 0)


if __name__ == "__main__":
    unittest.main()
