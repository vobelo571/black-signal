FLX Stash Network 1.2

Hold the normal secondary interaction key on a placed player-owned box to
open the Hideout Furniture style radial menu. It offers Open container,
Pick up container and contents, and Manage connections. The last option
opens an independent settings dialog without opening the inventory. Short press
still opens/searches the box normally. Pickup uses the existing Dot Marks
pickup implementation. World/quest boxes keep their original interaction.
The existing furniture radial menu also enables Manage connections when
the target is a supported player-owned storage box. Non-storage furniture
cannot receive items and keeps that option disabled.

Choose Manage connections from the radial menu. Click the role to cycle Disabled / Intake /
Receiver. Click Network to cycle networks 1-8. Receivers accept any number
of selected categories. Use the same network on intake and receiver boxes.

Deposit items into an intake normally: sorting runs on the next engine tick,
including bulk/selected transfers. It never scans the actor's inventory.
Only online, explicitly configured receivers within 50 m of the intake are
eligible. The nearest receiver wins; ties use object ID. Unsupported items
remain in the intake if no receiver accepts Other. Quest items stay put.
An intake's old contents are not automatically moved when enabling it.

Settings are stored with the save game. Picked-up/removed furniture loses
its assignment. Existing world/quest stashes and weapon showcases cannot
join a network. The current build uses Unlimited Stashes Weight, so no
additional capacity restriction is imposed by this addon.

Installed additively in D:\Anomaly\gamedata as well so no Mod Organizer
profile change is required. This folder is a distributable source copy.
Do not enable both copies if you later modify one of them: keep them in sync
or remove the base-game copy before using this folder through MO2.

New script discovery requires the game's startup script scan. Reloading a
save may not be sufficient in an already running process; restart the game
yourself if Storage network does not appear. No running game was closed or
controlled during installation. In-game layout and engine behavior still
require user verification. Lua logic and UI callbacks were tested in mocks.

To uninstall, remove these five additive files from D:\Anomaly\gamedata:
 scripts\ui_flx_stash_network.script
 scripts\zzzzzz_flx_stash_network.script
 configs\ui\flx_stash_network.xml
 configs\text\rus\st_flx_stash_network.xml
 configs\text\eng\st_flx_stash_network.xml
