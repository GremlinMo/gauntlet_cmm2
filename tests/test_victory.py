"""Exercise the actual ending routines with graphics recorded and keyboard scripted."""

import math
from pathlib import Path
import unittest

from basic_runner import Basic, split


ROOT = Path(__file__).resolve().parents[1]


class QuitGame(Exception):
    pass


class VictoryBasic(Basic):
    def __init__(self):
        self.tick = 0
        self.frames = []
        self.fast_frames = False
        self.keyboard = lambda tick: 0
        self.classic_buttons = lambda tick: 0
        super().__init__(ROOT, {"drawcampaignvictory", "showcampaignvictory",
                                "campaigncontinuepressed"})
        self.builtins.update({"sin": math.sin, "cos": math.cos, "len": len,
                              "str$": lambda value: str(value),
                              "rgb": lambda *values: tuple(round(v) for v in values),
                              "keydown": lambda index: self.keyboard(self.tick) if index == 1 else 0,
                              "classic": lambda *_: self.classic_buttons(self.tick),
                              "bin$": lambda value: bin(int(value))[2:],
                              "right$": lambda value, count: value[-count:],
                              "mid$": lambda value, start, count: value[start - 1:start - 1 + count]})
        self.noops.update({"printg", "playmod", "stopwav"})
        self.globals.update(pln=1, plq=2, totalrooms=39, music=1)
        self.arrays["plname$"].set((1,), "ELF")
        self.arrays["plname$"].set((2,), "WIZARD")
        self.arrays["score"].set((1,), 12345)
        self.arrays["score"].set((2,), 67890)

    def parse(self, lines, i, stops=()):
        # Bare DO is exactly the same loop node as DO WHILE 1 in this subset.
        lines = ["Do While 1" if line.lower() == "do" else line for line in lines]
        return super().parse(lines, i, stops)

    def statement(self, statement, local):
        lower = statement.lower()
        for command in ("line", "text", "box"):
            if lower.startswith(command + " "):
                args = [self.expression(arg, local) if arg else None
                        for arg in split(statement[len(command) + 1:])]
                self.calls.append((command, args))
                return
        if lower == "end":
            raise QuitGame()
        if lower == "cls" or lower.startswith(("load png ", "mode ", "pause ")):
            self.calls.append(statement)
            return
        return super().statement(statement, local)

    def call(self, name, *args):
        if name.lower() == "drawcampaignvictory":
            self.frames.append(args[0])
            self.tick = args[0] + 1
            if self.fast_frames:
                return
        return super().call(name, *args)


class VictoryTests(unittest.TestCase):
    def setUp(self):
        self.basic = VictoryBasic()

    def text(self):
        return [call[1][2] for call in self.basic.calls
                if isinstance(call, tuple) and call[0] in ("printg", "text")]

    def test_ending_announces_all_rooms_and_credits_the_developer(self):
        self.basic.call("DrawCampaignVictory", 90)
        text = self.text()
        self.assertIn("QUEST COMPLETE", text)
        self.assertIn("ALL 39 ROOMS CONQUERED", text)
        self.assertIn("CMM2 PORT: MAURO XAVIER", text)
        self.assertIn("ORIGINAL GAME: ED LOGG / ATARI", text)
        self.assertIn("THANK YOU FOR PLAYING!", text)

    def test_both_player_scores_are_shown(self):
        self.basic.call("DrawCampaignVictory", 90)
        self.assertIn("ELF  SCORE 12345", self.text())
        self.assertIn("WIZARD  SCORE 67890", self.text())

    def test_font_row_boundary_keeps_t_u_v_and_developer_name_readable(self):
        class GlyphBasic(Basic):
            def statement(self, statement, local):
                if statement.lower().startswith("blit "):
                    self.calls.append(tuple(self.expression(arg, local)
                                            for arg in split(statement[5:])))
                    return
                return super().statement(statement, local)

        basic = GlyphBasic(ROOT, {"printg"})
        basic.builtins.update({"len": len, "asc": ord,
                               "mid$": lambda text, start, size: text[start - 1:start - 1 + size]})
        basic.call("PrintG", 0, 0, "TUV")
        self.assertEqual([call[:2] for call in basic.calls],
                         [(312, 170), (0, 178), (6, 178)])

    def test_fireworks_animate_and_remain_onscreen(self):
        patterns = []
        for frame in (0, 12, 24, 36):
            self.basic.calls.clear()
            self.basic.call("DrawCampaignVictory", frame)
            lines = [call[1] for call in self.basic.calls
                     if isinstance(call, tuple) and call[0] == "line"]
            self.assertTrue(lines)
            for x1, y1, x2, y2, width, color in lines:
                self.assertTrue(0 <= x1 < 320 and 0 <= x2 < 320)
                self.assertTrue(0 <= y1 < 240 and 0 <= y2 < 240)
                self.assertEqual(width, 1)
                self.assertTrue(all(0 <= channel <= 255 for channel in color))
            patterns.append(lines)
        self.assertNotEqual(patterns[0], patterns[1])

    def test_continue_prompt_waits_until_announcement_has_been_shown(self):
        self.basic.call("DrawCampaignVictory", 40)
        self.assertFalse(any("SPACE / FIRE" in text for text in self.text()))
        self.basic.call("DrawCampaignVictory", 80)
        self.assertTrue(any("SPACE / FIRE" in text for text in self.text()))

    def test_fresh_press_after_minimum_display_time_returns(self):
        self.basic.fast_frames = True
        self.basic.keyboard = lambda tick: 32 if tick >= 80 else 0
        self.basic.call("ShowCampaignVictory")
        self.assertEqual(self.basic.frames, list(range(80)))

    def test_held_fire_does_not_skip_until_released_and_pressed_again(self):
        self.basic.fast_frames = True
        self.basic.keyboard = lambda tick: 0 if tick == 90 else 32
        self.basic.call("ShowCampaignVictory")
        self.assertEqual(self.basic.frames, list(range(91)))

    def test_wii_classic_fire_or_start_can_leave_the_ending(self):
        for button in (8192, 2):
            with self.subTest(button=button):
                basic = VictoryBasic()
                basic.fast_frames = True
                basic.arrays["ctrltype"].set((2,), 1)
                basic.classic_buttons = lambda tick: button if tick >= 80 else 0
                basic.call("ShowCampaignVictory")
                self.assertEqual(basic.frames, list(range(80)))

    def test_escape_can_quit_during_the_announcement(self):
        self.basic.fast_frames = True
        self.basic.keyboard = lambda tick: 27 if tick >= 20 else 0
        with self.assertRaises(QuitGame):
            self.basic.call("ShowCampaignVictory")
        self.assertEqual(self.basic.frames, list(range(20)))

    def test_returning_from_victory_keeps_title_visible_until_fresh_space(self):
        self.basic.fast_frames = True
        self.basic.globals["kb"] = 32  # Selection used this shared global earlier.
        self.basic.keyboard = lambda tick: 32 if tick >= 80 else 0
        self.basic.call("ShowCampaignVictory")
        title = TitleBasic(initial_kb=self.basic.globals["kb"])
        title.run_title([32, 32, 0, 32])
        self.assertEqual(title.drawn_frames, 4)


class TitleBasic(Basic):
    def __init__(self, initial_kb=0):
        super().__init__(ROOT, set())
        self.drawn_frames = 0
        self.keys = []
        self.globals.update(kb=initial_kb, retro=0)
        self.builtins["keydown"] = lambda _: self.keys[self.drawn_frames]

    def statement(self, statement, local):
        lower = statement.lower().strip()
        if lower == "page copy 7 to 0,i":
            self.drawn_frames += 1
        if lower == "end":
            raise QuitGame()
        if lower in ("mode 1", "cls"):
            self.calls.append(lower)
            return
        return super().statement(statement, local)

    def run_title(self, keys):
        self.keys = keys
        intro = (ROOT / "INTRO.INC").read_text()
        loop = intro.split("co=1:temp=0:Timer=0\n", 1)[1].split("\nif retro=1 then UnloadVGM", 1)[0]
        self.snippet("co=1:temp=0:Timer=0\n" + loop)


class TitleTests(unittest.TestCase):
    def test_stale_key_and_held_space_wait_for_release_and_new_press(self):
        basic = TitleBasic(initial_kb=32)
        basic.run_title([32, 32, 0, 32])
        self.assertEqual(basic.drawn_frames, 4)

    def test_unheld_title_accepts_the_next_space_press(self):
        basic = TitleBasic(initial_kb=32)
        basic.run_title([0, 32])
        self.assertEqual(basic.drawn_frames, 2)

    def test_escape_still_quits_while_space_is_held(self):
        basic = TitleBasic(initial_kb=32)
        with self.assertRaises(QuitGame):
            basic.run_title([32, 27])
        self.assertEqual(basic.drawn_frames, 1)
        self.assertIn("mode 1", basic.calls)


if __name__ == "__main__":
    unittest.main()
