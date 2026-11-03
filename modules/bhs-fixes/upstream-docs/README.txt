BHS Fixes by flx 1.0

Required: Body Health System (GAMMA Medications Balance supported).
Optional: LNCT Campfire Healing / Chiki-Briki Campfire Rest.
Enable this mod in Mod Organizer. It contains one uniquely named script and
does not replace BHS, campfire, camera, or dialog files supplied by other mods.

Fixes:
1. Campfire limb healing is persisted, including fractional temporary HP.
2. Doctors recognize injuries hidden by temporary HP and fully heal all limbs.
   Existing treatment prices and radiation-only treatment remain unchanged.
3. Saved limb values are restored BEFORE BHS can run its first save/decay tick.
   Long loading times cannot overwrite saved injuries with full default HP.

Existing saves are read from the original BHS actor variables. Future saves
also contain a separate copy of current limb HP and the temporary-HP timer.
Loading restores that saved state without applying any healing.
Disabling the mod leaves compatible values in the original BHS variables.
This mod cannot reconstruct injuries already overwritten in an older save;
use an earlier save if the unwanted full heal has already been saved.

The original files edited during development were restored from backups.
The independent Chiki-Briki camera-smoothing fix stays in that mod.
