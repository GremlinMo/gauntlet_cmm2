# Expansion rooms

Rooms 10–39 add 23 combat rooms and seven treasure rooms. Original rooms 1–9 are preserved.

The seven treasure rooms use different layouts and contain no enemies. Combat rooms introduce denser groups and tougher enemy mixes in stages; optional side vaults reward exploration without locking the route to the exit.

| Room | Name | Type | Layout | Enemies / generators | Treasure | Food |
| --- | --- | --- | --- | --- | --- | --- |
| 10 | The Broken Barracks | Combat | Switchbacks | 17 / 2 | 19 | 7 |
| 11 | Courts of Ash | Combat | Courtyards | 17 / 2 | 29 | 7 |
| 12 | The Amber Treasury | Treasure | Courtyards | 0 / 0 | 94 | 3 |
| 13 | Pillars of the Fallen | Combat | Colonnades | 18 / 2 | 19 | 7 |
| 14 | The Divided Crypt | Combat | Chambers | 19 / 2 | 29 | 7 |
| 15 | Bastion Run | Combat | Bastions | 19 / 2 | 30 | 7 |
| 16 | The Emerald Galleries | Treasure | Colonnades | 0 / 0 | 98 | 3 |
| 17 | The Forked Passage | Combat | Forked Halls | 20 / 2 | 30 | 7 |
| 18 | Demon's Keep | Combat | Citadels | 21 / 3 | 30 | 8 |
| 19 | The Wheel of Blades | Combat | Crossroads | 21 / 3 | 20 | 8 |
| 20 | The Sapphire Vault | Treasure | Chambers | 0 / 0 | 102 | 3 |
| 21 | The Iron Switchback | Combat | Switchbacks | 22 / 3 | 32 | 8 |
| 22 | The Sunken Courts | Combat | Courtyards | 23 / 3 | 21 | 8 |
| 23 | The Black Colonnade | Combat | Colonnades | 24 / 3 | 32 | 8 |
| 24 | The Ruby Hoard | Treasure | Bastions | 0 / 0 | 106 | 3 |
| 25 | Chambers of Dread | Combat | Chambers | 25 / 3 | 22 | 8 |
| 26 | The Dragon's Teeth | Combat | Bastions | 26 / 4 | 33 | 9 |
| 27 | The Long Divide | Combat | Forked Halls | 26 / 4 | 33 | 9 |
| 28 | The Golden Labyrinth | Treasure | Forked Halls | 0 / 0 | 110 | 3 |
| 29 | Citadel of Cinders | Combat | Citadels | 28 / 4 | 33 | 9 |
| 30 | The Spider's Cross | Combat | Crossroads | 28 / 4 | 35 | 9 |
| 31 | The Final Barricade | Combat | Switchbacks | 28 / 4 | 23 | 9 |
| 32 | The Silver Reserve | Treasure | Citadels | 0 / 0 | 114 | 3 |
| 33 | The Demon Courts | Combat | Courtyards | 30 / 4 | 35 | 9 |
| 34 | The Last Colonnade | Combat | Colonnades | 31 / 5 | 23 | 10 |
| 35 | The Shattered Cells | Combat | Chambers | 32 / 5 | 36 | 10 |
| 36 | The Crown Treasury | Treasure | Crossroads | 0 / 0 | 118 | 3 |
| 37 | The Gauntlet's Teeth | Combat | Bastions | 32 / 5 | 24 | 10 |
| 38 | The Deathward Halls | Combat | Forked Halls | 34 / 5 | 36 | 10 |
| 39 | The Siege of Gauntlet | Combat | Citadels | 33 / 5 | 36 | 10 |

## Rebuilding and editing

Run `python tools/generate_maps.py` from the project folder to rebuild these 30 maps deterministically. It never writes rooms 1–9. Every room has a fixed seed and validates its accessible exit, pickups, spawn sanctuary and supported tile codes before writing.

Coordinates in the generator are zero-based source-map coordinates. The map has a 34×34 loaded area; objectives stay in columns 2–31 and rows 2–28, within the existing camera range. The player marker is at (6, 6); the loader places player one at (5, 6) and player two at (5, 7). The surrounding sanctuary contains no enemies or generators.

The original binary layout is retained: a 32-byte header and CRLF, followed by 36 rows of 36 tile bytes and CRLF (1,402 bytes total). A stored tile is its source-map code plus 32. Only the first 34 columns and rows are loaded. The extra two columns and rows are space padding; do not edit these files as UTF-8 text.

Only existing assets and implemented tiles are used. Regular exits are explicit. Doors guard optional treasure alcoves, with a key outside; the main exit is accessible before opening any door. Teleporters, hidden exits and random exit markers are deliberately absent from the expansion.

Run `python -m unittest discover -s tests -v` for independent map and gameplay checks. Device testing is still required to tune combat balance, rendering, music and frame rate on a CMM2.
