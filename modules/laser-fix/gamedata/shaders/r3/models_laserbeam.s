function normal(shader, t_base, t_second, t_detail)
	local vs = "models_laserbeam"
	local ps = "models_laserbeam"
	if string.find(t_base, "laserdot") or string.find(t_base, "laser_dot") or string.find(t_base, "dot_reticle") then
		vs = "models_laserbeam_dot"
		ps = "models_laserbeam_dot"
	end
	shader:begin(vs, ps)
		: fog(false)
		: zb(true, false)
		: blend(true, blend.srcalpha, blend.one)
		: aref(true, 0)
		: sorting(2, true)
	shader:dx10texture("s_base", t_base)
	shader:dx10texture("s_position", "$user$position")
	shader:dx10sampler("smp_base")
	shader:dx10sampler("smp_nofilter")
end
