# Gauntlet for Colour Maximite 2

Original CMM2 port by **Mauro Xavier**; original arcade game designed by **Ed Logg for Atari Games**. Original artwork, music, sound and trademarks retain their existing ownership notices. The original author's description and changelog are preserved below.

## Maintenance updates — 11 November 2026

This fork provides two **CMM2-only** maintenance branches. The default `master` branch retains the original upstream nine-room game source. Choose a maintenance release for the updated game:

| Edition | Scope | Download and source |
| --- | --- | --- |
| Gameplay fixes | Original nine room maps, with gameplay corrections | [Release and complete game ZIP](https://github.com/GremlinMo/gauntlet_cmm2/releases/tag/v0.4a-cmm2-fixes.1) · [Source branch](https://github.com/GremlinMo/gauntlet_cmm2/tree/cmm2-gameplay-fixes) |
| Campaign expansion | The same fixes, 30 additional rooms and a defined 39-room ending with scores and credits | [Release and complete game ZIP](https://github.com/GremlinMo/gauntlet_cmm2/releases/tag/v0.4a-cmm2-campaign.1) · [Source branch](https://github.com/GremlinMo/gauntlet_cmm2/tree/cmm2-campaign-expansion) |

Both maintenance branches address the original v0.4a reports and related defects:

- Center players on the exit tile they enter, including during scrolling; wait for every living player to finish exiting before advancing the room once.
- Restore demon fire in all eight directions, with independent projectile ownership, one movement step per frame, and wall/player collision.
- Bound collision-map access and improve wall sliding, diagonal approaches, doors and pickups; guard map-clearing operations.
- Correct enemy targeting, generator state/health and full enemy-pool allocation.
- Invoke `StopWAV` explicitly at stage start and clear interrupted sound priority, addressing [upstream issue #2](https://github.com/mauroxavierneto/gauntlet_cmm2/issues/2).
- Correct the bitmap-font row boundary and require a fresh title-screen Space press after release.

The fixes edition preserves the original post-room-nine behavior: it supplies no ROOM10 map or campaign completion screen. The expansion provides rooms 1–39 and a completion sequence; the original nine map bytes are unchanged in both editions.

## Install the complete game

The original author specifies **CMM2 firmware 5.05.05 or later** for v0.4a. Extract the complete game ZIP to the SD card, change into its `Gauntlet` folder at the MMBasic prompt, and run `RUN "GAUNTLET.BAS"`. Keep the matching `.INC` files and `FONTS`, `IMAGES`, `MAPS`, `MOD` and `SOUND` directories together.

Each release also offers a directly downloadable **GAUNTLET.BAS**, source ZIP, upstream patch, release notes, test results, build information and SHA-256 checksums. **The BASIC file alone is not the complete game:** it requires the matching includes and assets from the same release. The complete game ZIP is recommended.

These releases retain CMM2 hardware/controller paths and contain no Windows executable or emulator.

## Validation and update history

On 11 November 2026, **49 source-driven Python checks passed for the fixes branch** and **74 passed for the campaign branch**. These tests execute selected routines from the actual BASIC source through a focused Python language subset and check map data. They do not validate complete native MMBasic execution, the physical framebuffer, Wii devices, audible sound, frame rate or 39-room combat balance. **Physical CMM2 testing remains pending.** Exact test output and a hardware checklist accompany each release.

Dated changes are recorded in the [fixes commit history](https://github.com/GremlinMo/gauntlet_cmm2/commits/cmm2-gameplay-fixes/) and [campaign commit history](https://github.com/GremlinMo/gauntlet_cmm2/commits/cmm2-campaign-expansion/). Each branch includes `CHANGELOG-CMM2.md` and `TESTING-CMM2.md`.

---

## Original project description and historical changelog

The following text is retained from the original author. Its beta-firmware recommendation and bug lists describe the historical releases.

### gauntlet_cmm2
Gauntlet port for the Colour Maximite 2
(I RECOMMEND YOU USE THE LAST BETA FIRMWARE FOR CMM2)

This is a version of Gauntlet to Colour Maximite 2.
I don´t own any rights about Gauntlet trademark, this is only a homebrew project made by me in my free time, and for sure in the current state, it has lots of bugs.
Keep in mind I´m only a Gauntlet fan with some basic developing skills and my target is only to challenge myself to port it to CMM2, it´s not a project with profit intentions.

Changelog:

v0.4a - 2020-08-06
- Need at least the 5.05.05 firmware or it doesn´t run!
- Two players support.
- 320x240 resolution.
- Smoother scroll.
- Removed 8-bit sound style for speed sake (sorry!).
- The player's characteristics were rebalanced.
- Some speed optimizations.
- Source code separated in INC files.
- Four-channel sound effects support thanks to the last update on the firmware.
- Sound test with music and voices in the options screen.
- Some arts was redone to 320x240 resolution.
- Wii Classic Controller support (not Wii Nunchuk yet).
- The copyright screen was disabled until the next release.

Historical known bugs from v0.4a (2020):

These reports describe the original game retained on `master`. The maintenance branches above address these behaviors; physical CMM2 verification of the fixes remains pending.

- Players sometimes don´t centralize in the exit.
- Demon´s fire stopped working.
- When someone goes to the exit, the game will change level even if another player is still playing.
- Many collision bugs.


v0.3a - 2020-05-06
- Made for the first CMM2 Gauntlet video on my Youtube channel.
- Some little optimizations

v0.1a - 2020-04-20
- Initial port from CMM1 to CMM2 - very unoptimized
- One player only.
- Only keyboard.
- Credits not working on the options menu.
- Many credits for the music are absent yet.
- Severe slow down when the screen is full of enemies.
- When demons have a shoot the player´s weapon can disappear for a moment (this is because they share the same code).
