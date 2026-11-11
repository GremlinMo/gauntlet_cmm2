"""Build the deterministic 30-room expansion in the original CMM map format.

The game reads a 34 x 34 tile area from files containing 36 x 36 bytes of tiles.
Each row has CRLF and each stored tile is its source code plus 32. Do not save
these maps through a Unicode text editor. Original rooms 1 through 9 are never
written by this script.
"""

from collections import deque
from dataclasses import dataclass
from pathlib import Path
import random


ROOT = Path(__file__).resolve().parents[1]
HEADER = b"' MAP MADE WITH CDN MEDIA STUDIO"
SIZE = 34
SPAWN = (6, 6)
# Coordinates in this module are zero-based source-map columns and rows.
# Keep all objectives within the existing camera's vertical travel.
LEFT, TOP, RIGHT, BOTTOM = 2, 2, 31, 28
WALL = 99
WALL_CODES = frozenset(range(88, 105))
PICKUPS = frozenset((17, 21, 24, 25, 26))


@dataclass
class Room:
    number: int
    name: str
    kind: str
    family: str
    tiles: list[list[int]]
    seed: int
    door_groups: int = 0


NAMES = {
    10: "The Broken Barracks", 11: "Courts of Ash", 12: "The Amber Treasury",
    13: "Pillars of the Fallen", 14: "The Divided Crypt", 15: "Bastion Run",
    16: "The Emerald Galleries", 17: "The Forked Passage", 18: "Demon's Keep",
    19: "The Wheel of Blades", 20: "The Sapphire Vault", 21: "The Iron Switchback",
    22: "The Sunken Courts", 23: "The Black Colonnade", 24: "The Ruby Hoard",
    25: "Chambers of Dread", 26: "The Dragon's Teeth", 27: "The Long Divide",
    28: "The Golden Labyrinth", 29: "Citadel of Cinders", 30: "The Spider's Cross",
    31: "The Final Barricade", 32: "The Silver Reserve", 33: "The Demon Courts",
    34: "The Last Colonnade", 35: "The Shattered Cells", 36: "The Crown Treasury",
    37: "The Gauntlet's Teeth", 38: "The Deathward Halls", 39: "The Siege of Gauntlet",
}


def rectangle(grid, x1, y1, x2, y2, value=WALL):
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            grid[y][x] = value


def outline(grid, x1, y1, x2, y2):
    rectangle(grid, x1, y1, x2, y1)
    rectangle(grid, x1, y2, x2, y2)
    rectangle(grid, x1, y1, x1, y2)
    rectangle(grid, x2, y1, x2, y2)


def clear_spawn(grid):
    rectangle(grid, 2, 2, 10, 10, 0)


def distances(grid, start, doors_open=True):
    """Return shortest paths through scenery, treating combat/pickups as clear."""
    queue = deque([start])
    result = {start: 0}
    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if not (LEFT <= nx <= RIGHT and TOP <= ny <= BOTTOM):
                continue
            tile = grid[ny][nx]
            if tile in WALL_CODES or (tile in (22, 23) and not doors_open):
                continue
            if (nx, ny) not in result:
                result[(nx, ny)] = result[(x, y)] + 1
                queue.append((nx, ny))
    return result


def connect_floor(grid):
    """Connect otherwise isolated floor pockets with two-tile-wide passages."""
    while True:
        connected = distances(grid, (SPAWN[0] - 1, SPAWN[1]))
        missing = [(x, y) for y in range(TOP, BOTTOM + 1)
                   for x in range(LEFT, RIGHT + 1)
                   if grid[y][x] == 0 and (x, y) not in connected]
        if not missing:
            return
        x1, y1 = missing[0]
        x2, y2 = min(connected, key=lambda p: abs(x1 - p[0]) + abs(y1 - p[1]))
        rectangle(grid, min(x1, x2), y1, max(x1, x2), min(BOTTOM, y1 + 1), 0)
        rectangle(grid, x2, min(y1, y2), min(RIGHT, x2 + 1), max(y1, y2), 0)


def architecture(family, rng):
    grid = [[WALL] * SIZE for _ in range(SIZE)]
    rectangle(grid, LEFT, TOP, RIGHT, BOTTOM, 0)
    if family == "switchbacks":
        for index, x in enumerate((11, 19, 27)):
            rectangle(grid, x, TOP, x, BOTTOM)
            y = rng.randint(3, 6) if index % 2 else rng.randint(22, 25)
            rectangle(grid, x, y, x, y + 3, 0)
    elif family == "courtyards":
        for x1, y1, x2, y2 in ((8, 8, 28, 25), (13, 12, 23, 21)):
            outline(grid, x1, y1, x2, y2)
            gap_x = rng.randint(x1 + 2, x2 - 3)
            rectangle(grid, gap_x, y1, gap_x + 2, y1, 0)
            gap_y = rng.randint(y1 + 2, y2 - 3)
            rectangle(grid, x2, gap_y, x2, gap_y + 2, 0)
            rectangle(grid, x1 + 2, y2, x1 + 4, y2, 0)
    elif family == "colonnades":
        for y in range(5, 28, 5):
            for x in range(6, 31, 6):
                width = rng.choice((1, 2, 3))
                height = rng.choice((1, 2, 3))
                rectangle(grid, x, y, x + width - 1, min(BOTTOM, y + height - 1))
    elif family == "chambers":
        for x in (11, 21):
            rectangle(grid, x, TOP, x, BOTTOM)
            for y in (rng.randint(3, 6), rng.randint(14, 17), rng.randint(24, 26)):
                rectangle(grid, x, y, x, y + 2, 0)
        for y in (12, 22):
            rectangle(grid, LEFT, y, RIGHT, y)
            for x in (rng.randint(4, 7), rng.randint(14, 17), rng.randint(25, 28)):
                rectangle(grid, x, y, x + 2, y, 0)
    elif family == "bastions":
        for y in (5, 14, 23):
            for x in (6, 16, 26):
                width = rng.choice((3, 4))
                rectangle(grid, x, y, min(RIGHT, x + width), min(BOTTOM, y + 2))
                rectangle(grid, x, min(BOTTOM, y + 3), x, min(BOTTOM, y + 4))
    elif family == "forked halls":
        for index, y in enumerate((11, 17, 23)):
            rectangle(grid, LEFT, y, RIGHT, y)
            x = rng.randint(23, 27) if index % 2 == 0 else rng.randint(4, 8)
            rectangle(grid, x, y, x + 3, y, 0)
            branch = rng.randint(12, 18)
            rectangle(grid, branch, y - 3, branch, y - 1)
    elif family == "citadels":
        outline(grid, 12, 10, 27, 24)
        for x, y in ((17, 10), (22, 24)):
            rectangle(grid, x, y, x + 2, y, 0)
        rectangle(grid, 12, 16, 12, 18, 0)
        rectangle(grid, 27, 13, 27, 15, 0)
        outline(grid, 16, 14, 23, 20)
        rectangle(grid, 18, 14, 20, 14, 0)
        rectangle(grid, 21, 20, 22, 20, 0)
        for y in (4, 26):
            rectangle(grid, 15, y, 21 + rng.randint(0, 4), y)
    elif family == "crossroads":
        rectangle(grid, 17, TOP, 17, BOTTOM)
        rectangle(grid, LEFT, 15, RIGHT, 15)
        for y in (5, 11, 21, 26):
            rectangle(grid, 17, y, 17, min(BOTTOM, y + 2), 0)
        for x in (5, 12, 23, 28):
            rectangle(grid, x, 15, x + 2, 15, 0)
        for x, y in ((11, 7), (24, 9), (8, 22), (23, 23)):
            rectangle(grid, x, y, x + rng.randint(1, 3), y + 2)
    else:
        raise ValueError(family)
    clear_spawn(grid)
    connect_floor(grid)
    return grid


def side_vault(grid, number):
    """Optional locked bonus alcove; no exit or required resource goes inside."""
    x1, y1, x2, y2 = ((25, 3, 31, 9), (25, 21, 31, 27),
                       (3, 21, 9, 27))[number % 3]
    outline(grid, x1, y1, x2, y2)
    rectangle(grid, x1 + 1, y1 + 1, x2 - 1, y2 - 1, 0)
    gate_y = y2 if y1 == 3 else y1
    outside_y = gate_y + 1 if y1 == 3 else gate_y - 1
    rectangle(grid, x1 + 1, outside_y, x2 - 1, outside_y, 0)
    for x in (x1 + 2, x1 + 3):
        grid[gate_y][x] = 23
    vault = {(x, y) for y in range(y1 + 1, y2)
             for x in range(x1 + 1, x2)}
    return vault


def finish_walls(grid):
    """Reuse horizontal, vertical and solid sprites from the existing sheet."""
    walls = {(x, y) for y, row in enumerate(grid) for x, value in enumerate(row)
             if value == WALL}
    for x, y in walls:
        north, south = (x, y - 1) in walls, (x, y + 1) in walls
        west, east = (x - 1, y) in walls, (x + 1, y) in walls
        if west and east and not north and not south:
            grid[y][x] = 88
        elif north and south and not west and not east:
            grid[y][x] = 89
        else:
            grid[y][x] = 99


def place(grid, rng, candidates, count, choices):
    available = sorted(p for p in candidates if grid[p[1]][p[0]] == 0)
    rng.shuffle(available)
    positions = available[:count]
    for x, y in positions:
        grid[y][x] = rng.choice(choices)
    if len(positions) != count:
        raise ValueError("Not enough empty cells for room content")
    return positions


def generate_room(number):
    if not 10 <= number <= 39:
        raise ValueError("Expansion rooms are 10 through 39")
    seed = 0xC0DE + number * 7919
    rng = random.Random(seed)
    treasure = number % 4 == 0
    families = ("switchbacks", "courtyards", "colonnades", "chambers",
                "bastions", "forked halls", "citadels", "crossroads")
    if treasure:
        family = ("courtyards", "colonnades", "chambers", "bastions",
                  "forked halls", "citadels", "crossroads")[(number - 12) // 4]
    else:
        # Advance combat architecture independently of treasure interruptions.
        combat_index = len([r for r in range(10, number) if r % 4])
        family = families[combat_index % len(families)]
    grid = architecture(family, rng)
    vault = set()
    if not treasure and number % 3 != 1:
        vault = side_vault(grid, number)
        # A vault can intersect a partition: reconnect the outside around it,
        # while preserving the intentionally locked alcove itself.
        for x, y in vault:
            grid[y][x] = WALL
        connect_floor(grid)
        for x, y in vault:
            grid[y][x] = 0
    start = (SPAWN[0] - 1, SPAWN[1])
    reachable = distances(grid, start, doors_open=False)
    exit_cell = max(reachable, key=lambda p: (reachable[p], p[1], p[0]))
    grid[exit_cell[1]][exit_cell[0]] = 20
    grid[SPAWN[1]][SPAWN[0]] = 1
    reserved = {(x, y) for y in range(3, 10) for x in range(3, 10)}
    candidates = set(reachable) - reserved - {exit_cell}
    # Guaranteed accessible key comes before every optional locked vault.
    if vault:
        grid[8][8] = 24
        place(grid, rng, vault, 9 + number // 10, (17,))
        place(grid, rng, vault, 1, (26,))
    if treasure:
        place(grid, rng, candidates, 82 + number, (17,))
        place(grid, rng, candidates, 3, (21, 25))
        place(grid, rng, candidates, 2, (24,))
        place(grid, rng, candidates, 1, (26,))
    else:
        tier = (number - 10) // 8
        place(grid, rng, candidates, 17 + number // 5, (17,))
        place(grid, rng, candidates, 6 + tier, (21, 25))
        place(grid, rng, candidates, 3 + tier, (26,))
        place(grid, rng, candidates, 2, (24,))
        far_cells = {p for p in candidates if abs(p[0] - start[0]) + abs(p[1] - start[1]) >= 12}
        # Generators are deliberately limited to supported source-map codes.
        place(grid, rng, far_cells, 2 + tier, (31, 32, 50, 51))
        choices = (34, 38, 42, 53, 55, 59, 61, 65, 69, 84)
        if number >= 18:
            choices += (63, 67, 71, 73, 85, 86, 87)
        place(grid, rng, far_cells, 17 + (number - 10) // 2, choices)
        if number >= 23:
            place(grid, rng, far_cells, 1 if number < 33 else 2, (77, 79))
        if number >= 29 and number % 3 == 2:
            place(grid, rng, far_cells, 1, (81,))
        # A small food cache is always available in the starting sanctuary.
        grid[9][9] = 21
    finish_walls(grid)
    room = Room(number, NAMES[number], "treasure" if treasure else "combat",
                family, grid, seed, int(bool(vault)))
    validate_room(room)
    return room


def validate_room(room):
    grid = room.tiles
    assert len(grid) == SIZE and all(len(row) == SIZE for row in grid)
    assert sum(row.count(1) for row in grid) == 1
    assert sum(row.count(20) for row in grid) >= 1
    start = (SPAWN[0] - 1, SPAWN[1])
    reached = distances(grid, start)
    for y, row in enumerate(grid):
        for x, code in enumerate(row):
            if code in PICKUPS or code == 20 or 31 <= code <= 87:
                assert (x, y) in reached, (room.number, code, x, y)
            assert 0 <= code <= 106
    for x in range(3, 10):
        for y in range(3, 10):
            assert not 31 <= grid[y][x] <= 87
    closed = distances(grid, start, doors_open=False)
    assert any(grid[y][x] == 20 for x, y in closed)
    assert sum(grid[y][x] == 24 for x, y in closed) >= room.door_groups
    if room.kind == "treasure":
        assert not any(31 <= code <= 87 for row in grid for code in row)
        assert sum(row.count(17) for row in grid) >= 90


def encode_map(grid):
    rows = [bytes(code + 32 for code in row) + b"  " for row in grid]
    rows += [b" " * 36] * 2
    return HEADER + b"\r\n" + b"\r\n".join(rows) + b"\r\n"


def build_rooms():
    return [generate_room(number) for number in range(10, 40)]


def catalog(rooms):
    lines = ["# Expansion rooms", "",
             "Rooms 10–39 add 23 combat rooms and seven treasure rooms. Original rooms 1–9 are preserved.", "",
             "The seven treasure rooms use different layouts and contain no enemies. Combat rooms introduce denser groups and tougher enemy mixes in stages; optional side vaults reward exploration without locking the route to the exit.", "",
             "| Room | Name | Type | Layout | Enemies / generators | Treasure | Food |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for room in rooms:
        codes = [code for row in room.tiles for code in row]
        enemies = sum(31 <= code <= 87 for code in codes)
        generators = sum(code in (31, 32, 33, 50, 51, 52) for code in codes)
        lines.append(f"| {room.number} | {room.name} | {room.kind.title()} | {room.family.title()} | {enemies - generators} / {generators} | {codes.count(17)} | {codes.count(21) + codes.count(25)} |")
    lines += ["", "## Rebuilding and editing", "",
              "Run `python tools/generate_maps.py` from the project folder to rebuild these 30 maps deterministically. It never writes rooms 1–9. Every room has a fixed seed and validates its accessible exit, pickups, spawn sanctuary and supported tile codes before writing.", "",
              "Coordinates in the generator are zero-based source-map coordinates. The map has a 34×34 loaded area; objectives stay in columns 2–31 and rows 2–28, within the existing camera range. The player marker is at (6, 6); the loader places player one at (5, 6) and player two at (5, 7). The surrounding sanctuary contains no enemies or generators.", "",
              "The original binary layout is retained: a 32-byte header and CRLF, followed by 36 rows of 36 tile bytes and CRLF (1,402 bytes total). A stored tile is its source-map code plus 32. Only the first 34 columns and rows are loaded. The extra two columns and rows are space padding; do not edit these files as UTF-8 text.", "",
              "Only existing assets and implemented tiles are used. Regular exits are explicit. Doors guard optional treasure alcoves, with a key outside; the main exit is accessible before opening any door. Teleporters, hidden exits and random exit markers are deliberately absent from the expansion.", "",
              "Run `python -m unittest discover -s tests -v` for independent map and gameplay checks. Device testing is still required to tune combat balance, rendering, music and frame rate on a CMM2.", ""]
    return "\n".join(lines)


def main():
    rooms = build_rooms()
    for room in rooms:
        (ROOT / "MAPS" / f"ROOM{room.number:02}.MAP").write_bytes(encode_map(room.tiles))
    (ROOT / "MAPS" / "ROOMS.md").write_text(catalog(rooms), encoding="utf-8")
    print(f"Wrote {len(rooms)} validated expansion maps (rooms 10–39).")


if __name__ == "__main__":
    main()
