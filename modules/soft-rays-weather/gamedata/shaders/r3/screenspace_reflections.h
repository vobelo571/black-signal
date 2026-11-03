/**
 * @ Version: SCREEN SPACE SHADERS - UPDATE 21
 * @ Description: SSR Ray-march
 * @ Modified time: 2025-02-08 17:02
 * @ Author: https://www.moddb.com/members/ascii1457
 * @ Mod: https://www.moddb.com/mods/stalker-anomaly/addons/screen-space-shaders
 */

#ifndef SSFX_SSR_QUALITY
	#define SSFX_SSR_QUALITY 0
#endif

#include "screenspace_common.h"
#include "settings_screenspace_SSR.h"

uniform float4 ssr_setup; // x: SSR Resolution | y: Blur Intensity | z: Temporal Intensity
uniform float4 ssfx_ssr_2; // x: Intensity | y: Sky Intensity | z: Weapon Intensity | w: Max Weapon Intensity
uniform float4 ssfx_is_underground;

Texture2D blue_noise;

static const int2 q_ssr_steps[6] =
{
	int2(8,72),
	int2(16,36),
	int2(24,18),
	int2(32,5),
	int2(40,1), // Balanced preset: retain strict depth tolerance and binary refinement.
	int2(64,1),
};


float4 SSFX_ssr_fast_ray(float3 ray_start_vs, float3 ray_dir_vs, float2 tc, float HudMask, inout float2 noise, uint iSample : SV_SAMPLEINDEX)
{
	float2 sky_tc = 0;
	float2 behind_hit = 0;

	// Noise to "improve" consistency between steps
	float2 uv_noise = tc + timers.x * (ssr_setup.w > 0);
	uv_noise.x *= screen_res.x / screen_res.y;
	noise = blue_noise.Sample(smp_linear, uv_noise).x * ssr_setup.w * 0.5f * HudMask;

	noise = noise * 2 - 1;

	// Initialize Ray
	RayTrace ssr_ray = SSFX_ray_init(ray_start_vs, ray_dir_vs, 150, q_ssr_steps[SSFX_SSR_QUALITY].x, 1.0f - noise);

	// Save the original step.x
	float ori_x = ssr_ray.r_step.x;

	// Depth from the start of the ray
	float ray_depthstart = SSFX_get_depth(ssr_ray.r_start, iSample);
	
	float2 ray_check = 0;

	// Ray-march
	[unroll (q_ssr_steps[SSFX_SSR_QUALITY].x)]
	for (int i = 0; i < q_ssr_steps[SSFX_SSR_QUALITY].x; i++)
	{
		// Ray out of screen...
		if (ssr_ray.r_pos.y < 0.0f || ssr_ray.r_pos.y > 1.0f)
			return 0;

		// Trick for the horizontal out of bounds. Mirror border of the screen.
		if (ssr_ray.r_pos.x < 0.0f || ssr_ray.r_pos.x > 1.0f)
		{
			ssr_ray.r_pos -= ssr_ray.r_step; // Step back
			ssr_ray.r_step.x = -ssr_ray.r_step.x; // Invert Horizontal
			ssr_ray.r_pos += ssr_ray.r_step; // Step
		}

		// Ray intersect check
		ray_check = SSFX_ray_intersect(ssr_ray, iSample);

		// Sampled depth is not weapon or sky ( SKY_EPS float(0.001) )
		bool NoWpnSky = ray_check.y > 1.3f;

		// Disable weapon and sky
		ray_check.x *= NoWpnSky;

		// Return if ray is not reflecting backward
		if (ray_check.x > 0)
		{
			if (ray_check.x <= q_ssr_steps[SSFX_SSR_QUALITY].y)
				return float4(ssr_ray.r_pos, ray_check.y, 0);

#if SSFX_SSR_QUALITY > 2 // 1 Binary Search step in higher quality settigns ( Quality 4 & 5 )
			
			// Current ray pos & step to restore later...
			float4 prev_step = 0;
			prev_step.xy = ssr_ray.r_pos;
			prev_step.zw = ssr_ray.r_step;

			// Half and flip
			ssr_ray.r_step *= -0.5f;

			// Step ray
			ssr_ray.r_pos += ssr_ray.r_step;

			// Ray intersect check
			ray_check = SSFX_ray_intersect(ssr_ray, iSample);

			// Depth test... Conditions to use as reflections...
			if (abs(ray_check.x) <= 1.25f)
				return float4(ssr_ray.r_pos, ray_check.y, 0);

			// Restore previous ray position & step
			ssr_ray.r_pos = prev_step.xy;
			ssr_ray.r_step = prev_step.zw;

#endif

		}
		else
		{
			// TexCoor for sky ( Used to fade "SSFX_calc_SSR_fade" )
			if (ray_check.y <= SKY_EPS)
				sky_tc = ssr_ray.r_pos;
			
			behind_hit = ssr_ray.r_pos;

			// Reset or keep depending on... ( > 1.3f = no interaction with weapons and sky )
			behind_hit *= (ray_depthstart - 2.0f < ray_check.y) && NoWpnSky;
		}

		
		// Step the ray
		ssr_ray.r_pos += ssr_ray.r_step;
	}

	return float4(behind_hit, ray_check.y, sky_tc.y);
}


void SSFX_ScreenSpaceReflections(float2 tc, float4 P, float3 N, float4 gloss, inout float4 color, float HudMask, inout float2 noise, inout float hitdepth, uint iSample : SV_SAMPLEINDEX)
{
	// Note: Distance falloff on "rain_patch_normal.ps"

	// Material condition — sentinel only (slot 31, material_ID=1.333333)
	bool m_terrain = abs(P.w - MAT_TERRAIN_SENTINEL) <= MAT_TERRAIN_SENTINEL_E;

	// Calc reflection bounce
	float3 inVec = normalize(P.xyz); // Incident
	float3 reVec = reflect(inVec , N); // Reflected

	// World-space reflection vector for cubemap fallback
	float3 v2point   = mul(m_inv_V, inVec);
	float3 nw        = mul(m_inv_V, N);
	float3 v2reflect = reflect(v2point, nw);

	float4 hit_uv = 0;

	// Calc SSR ray. Discard low reflective pixels
	if (gloss.w > 0.02f)
		hit_uv = SSFX_ssr_fast_ray(P.xyz, reVec, tc, HudMask, noise, iSample);

	float3 reflection = gloss.rgb;

	bool self_intersect = m_terrain
	                   && (hit_uv.y >= tc.y)
	                   && (abs(hit_uv.z - P.z) < 2.0f);

	#define SSR_STEEP_LO -0.25f
	#define SSR_STEEP_HI -0.70f
	float view_dot      = dot(inVec, N);
	float steep_blend   = m_terrain ? smoothstep(SSR_STEEP_LO, SSR_STEEP_HI, view_dot) : 0.0f;
	bool  self_or_steep = self_intersect || (steep_blend >= 1.0f);

#ifdef G_SSR_CHEAP_SKYBOX
	float3 env_fallback = SSFX_calc_env(v2reflect) * ssfx_ssr_2.y * !ssfx_is_underground.x;
#else
	float3 env_fallback = SSFX_calc_sky(v2reflect) * ssfx_ssr_2.y * !ssfx_is_underground.x;
#endif

	if (all(hit_uv.xy) && !self_or_steep)
	{
		// Get scene reflection
		float3 scene = SSFX_get_image(hit_uv.xy, iSample);

		// Vertical screen fade
		float HitFade = saturate(hit_uv.y * G_SSR_VERTICAL_SCREENFADE);

		float3 ssr_result = lerp(reflection * m_terrain, scene, HitFade);
		reflection.rgb = lerp(ssr_result, env_fallback, steep_blend);
	}
	else
	{
		float ray_fade = saturate(saturate(hit_uv.w * G_SSR_VERTICAL_SCREENFADE) + m_terrain);
		reflection = lerp(reflection * ray_fade, env_fallback, (float)m_terrain);
	}

	color.rgb = reflection;

	hitdepth = hit_uv.z;
}