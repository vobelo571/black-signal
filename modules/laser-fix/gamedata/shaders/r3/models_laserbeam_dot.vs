#include "common.h"
#include "skin.h"

float4 shader_param_6;

struct vf
{
	float2 tc0	: TEXCOORD0;
	float3 wn	: TEXCOORD1;
	float3 wpos	: TEXCOORD2;
	float4 c0	: COLOR0;
	float4 hpos	: SV_Position;
};

vf _main (v_model v)
{
	vf o;

	float raw_w = shader_param_6.w;
	float dot_index = floor(raw_w / 10.0);
	float dot_size = dot_index * 0.5 + 0.5;

	float2 uv_off = v.tc - 0.5;
	float uv_r = length(uv_off);
	float3 tang_disp = v.T * uv_off.x + v.B * uv_off.y;
	v.P.xyz += tang_disp / sqrt(max(uv_r, 0.01)) * 0.06 * (dot_size - 1.0);

	o.hpos	= mul(m_WVP, v.P);
	o.tc0	= v.tc.xy;
	o.wpos	= mul(m_W, v.P).xyz;
	float3 dir_v	= normalize(mul(m_WV, v.P));
	float3 norm_v	= normalize(mul(m_WV, v.N));
	float fresnel	= abs(dot(dir_v, norm_v));
	o.c0	= float4(1, 0, 0, fresnel);
	o.wn	= norm_v;
	return o;
}

#ifdef SKIN_NONE
vf main(v_model v)			{ return _main(v);		}
#endif
#ifdef SKIN_0
vf main(v_model_skinned_0 v)		{ return _main(skinning_0(v));	}
#endif
#ifdef SKIN_1
vf main(v_model_skinned_1 v)		{ return _main(skinning_1(v));	}
#endif
#ifdef SKIN_2
vf main(v_model_skinned_2 v)		{ return _main(skinning_2(v));	}
#endif
#ifdef SKIN_3
vf main(v_model_skinned_3 v)		{ return _main(skinning_3(v));	}
#endif
#ifdef SKIN_4
vf main(v_model_skinned_4 v)		{ return _main(skinning_4(v));	}
#endif
