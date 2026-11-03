FLX visual/weather patch - 2026-10-29
Active profile: G.A.M.M.A. / current DX11 renderer.

Softer sun shafts: gain 2.5 -> 1.15, scattering density .012 -> .008,
5-tap shadow visibility filter, earlier distance fade, reduced side/back scatter.
Local volumetric light intensity .10 -> .075. Bloom 3/1.1 -> 2.2/1.0.
Texture LOD 0, AF16, mip bias -.15, POM refinement enabled.

Enabled existing texture packs: Rotten Life 3.0 4K, Terrain Redone 4K,
World Textures 4K Cap. No tree/mesh or experimental DX12 core changes.

Airborne Pulse update disabled independently of Momopate's Improved Pulses.
Other anomalies, emissions and psi-storms retain their behavior.
Normal rain/storm weather occurrence = None (1). Distant thunder disabled.
Existing rain/storm save cycles switch to partly cloudy on first actor update,
unless a weather effect is active. Ordinary weather rain density reduced to
8% of its original value, maximum .08, and lightning collections cleared.

To undo: disable this patch and the three texture packs in Mod Organizer,
then restore the profile, original MCM options and user.ltx from the backup
recorded in D:\GAMMA\_work\FLXVisual20261029\install.json.
Restart the game after changing shaders or texture packs.


FPS optimization - 2026-10-29
GPU observation: Anomaly process ~97% 3D utilization at 1920x1080.
High-quality sun rays: 64 -> 48 march steps, same 5-tap soft shadow kernel.
Indirect lighting: 48 -> 32 samples, same intensity, radius and accumulation.
GTAO: quality 8 -> 6 (4x8 -> 3x6 depth samples), same intensity and blur.
SSR quality 4: 48 -> 40 march steps, same depth tolerance and binary refinement.
HD texture packs, AF16, resolution, grass, view distance, 2048 shadows and
POM remain as before. No edits to the live game's user.ltx or MCM settings.
Restart the game for this preset to apply. FPS gain has not been measured.
Some sampling noise or small reflection detail can differ from the old preset.
