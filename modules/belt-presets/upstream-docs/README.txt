FLX Belt Presets

Enable "1009- FLX Belt Presets" in Mod Organizer and launch the game through MO.
If the mod is absent from the list, refresh MO or restart it.

Three small buttons appear between F1-F4 and the artifact belt in inventory mode.
Click 1/2/3: load that preset.
Shift + click 1/2/3: overwrite that preset with the current belt.
An asterisk marks a saved preset. An empty belt can also be saved.

Presets store the entire belt, including belt attachments, in belt order.
They refer to specific item IDs and sections, not interchangeable copies.
All required items must be carried by the actor. Insufficient slots or missing
items leave the belt unchanged. Rejected equipment triggers a rollback.
Presets persist in game saves; save the game after configuring them.
Each playthrough/save branch has its own three presets.

Requires GAMMA's scripted ui_inventory UI. Hooks existing methods without
replacing ui_inventory.script or its XML. Includes English and Russian text.
Controls are hidden during trade, looting and repair.
Hover a preset button for a compact help/status tooltip (350 ms delay).
No messages are sent to the PDA/news log.
Belt changes are staged across engine frames; repeated clicks are ignored
while switching. The previous belt is restored if equipment is rejected.

Verified: Lua parsing, XML parsing, mocked save/load, all three presets,
missing-item/capacity validation, rollback and empty-belt presets.
Also verified deferred movement between frames, switching both ways,
rollback with delayed movement, and tooltip timing/visibility.
Actual rendering and engine behavior still require an in-game check.
