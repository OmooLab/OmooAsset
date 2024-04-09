// This is a fork of ASM with following changes:
// Use scatting color channel as Subsurface Raidus.
// Use scatting channel as Subsurface Weight.
// Use translucency channel as Transmission Weight.
// Add scale controller to "height to normal".
// Orangized params group to fit AutoDesk Standard Surface.
// Kill absorption color channel.
// Kill alpha cut.

// But some how "sssEnabled" cannot be delete, if I do so, SSS would gone.
// So, I keep import lib-sss.glsl.

//- OmooLab Standard Surface Definition
//- ===============================================
//-
//- Import from libraries.
import lib-pbr.glsl
import lib-pbr-aniso.glsl

//: param custom {
//:   "group": "Specular",
//:   "label": "Enable anisotropy",
//:   "default": false,
//:   "asm": "anisotropy",
//:   "description": "<html><head/><body><p>Allows reflections to stretch in one direction along the surface.<br/><b>Please note</b>: The following channels need to be present for this parameter to have an effect: <b>Anisotropy angle</b> and <b>Anisotropy level</b>.</p></body></html>"
//: }
uniform_specialization bool anisotropyEnabled;
//: param custom {
//:   "group": "Specular",
//:   "label": "Index of refraction",
//:   "min": 0.0,
//:   "max": 40.0,
//:   "default": 1.5,
//:   "asm": "specular_ior",
//:   "description": "<html><head/><body><p>The amount light bends as it passes through the object. Also affects the specular reflection intensity.</p></body></html>"
//: }
uniform float specularIoR;
//: param custom {
//:   "group": "Specular",
//:   "label": "Enable edge color",
//:   "default": false,
//:   "asm": "specular_edge_color",
//:   "description": "<html><head/><body><p>Allows specifying the color of light reflections. Affects glancing angles for metallic materials.<br/><b>Please note</b>: The following channel needs to be present for this parameter to have an effect: <b>Specular edge color</b></p></body></html>"
//: }
uniform_specialization bool specularEdgeColorEnabled;


import lib-coat.glsl

// If there is a "Coat Color" channel, the default Coat Weight should be 1.0, not 0.0
float getCoatWeight(SamplerSparse coatColor, SamplerSparse coatWeight, SparseCoord coord)
{
	vec4 weight = textureSparse(coatWeight, coord);
	vec4 color = textureSparse(coatColor, coord);
	float default_weight = color.a;
  return weight.r + default_weight * (1.0 - weight.g);
}

//: param custom {
//:   "group": "Transmission",
//:   "label": "Enable",
//:   "default": false,
//:   "asm": "transmission",
//:   "description": "<html><head/><body><p>Allows for refractive transmission of light through the surface.<br/><b>Please note</b>: The following channel needs to be present for this parameter to have an effect: <b>Translucency</b></p></body></html>",
//:   "enable": "!input.subsurfaceEnabled",
//:   "description_disabled": "<html><head/><body><p>Disable the <b>Subsurface Scattering</b> to use <b>Transmission</b>.</p></body></html>"
//: }
uniform_specialization bool transmissionEnabled;

//- Rewrite lib-sheen.glsl
//- ---------------------------------------

//: param custom {
//:   "group": "Sheen",
//:   "label": "Enable",
//:   "default": false,
//:   "asm": "sheen",
//:   "description": "<html><head/><body><p>Simulates the effect of microscopic fibers or fuzz on the surface.<br/><b>Please note</b>: The following channel needs to be present for this parameter to have an effect: <b>Sheen opacity</b>. Optionally, the following channels provide additional control: <b>Sheen color</b> and <b>Sheen roughness</b>.</p></body></html>"
//: }
uniform_specialization bool _sheenEnabled;
//: param auto channel_sheenopacity
uniform SamplerSparse _sheenOpacity_tex;
//: param auto channel_sheencolor
uniform SamplerSparse _sheenColor_tex;
//: param auto channel_sheenroughness
uniform SamplerSparse _sheenRoughness_tex;

vec3 _sheen_contrib(float ndh, float ndl, float ndv, vec3 Ks, float roughness)
{
	float ndh2 = ndh*ndh;
	float ndl2 = ndl*ndl;
	float ndv2 = ndv*ndv;
	float r2 = roughness*roughness;

	// TODO: move the D component out, to the importance sampling.
	float t = 1.0 - ndh2 + ndh2/r2;
	float Pi_D = 1.0 / (roughness * t * t);

	float Li = sqrt(1.0 - ndl2 + r2*ndl2) / ndl;
	float Lo = sqrt(1.0 - ndv2 + r2*ndv2) / ndv;
	float G = (1.0 - exp(-(Li + Lo))) / (Li + Lo);

	// This is the contribution when using importance sampling with uniform
	// sample distribution. This means _sheen_contrib = sheen_brdf / (1/(2*Pi))
	// ndl is omitted since it cancels out with the ndl outside the BRDF.
	return Ks * ((2.0 * Pi_D * G / ndv) * 0.5);
}

vec3 _pbrComputeSheen(LocalVectors vectors, vec3 specColor, float roughness)
{
	vec3 radiance = vec3(0.0);
	float ndv = dot(vectors.eye, vectors.normal);
	roughness = max(1e-3, roughness);
	vec3 envT = worldToEnvSpace(vectors.tangent);
	vec3 envB = worldToEnvSpace(vectors.bitangent);
	vec3 envN = worldToEnvSpace(vectors.normal);
	vec3 envE = worldToEnvSpace(vectors.eye);
	vec3 envVertexNormal = worldToEnvSpace(vectors.vertexNormal);

	for(int i=0; i<nbSamples; ++i)
	{
		vec2 Xi = fibonacci2D(i, nbSamples);
		vec3 Ln = uniformSample(Xi, envT, envB, envN);
		vec3 Hn = normalize(Ln + envE);
		float fade = horizonFading(dot(envVertexNormal, Ln), horizonFade);

		float ndl = dot(envN, Ln);
		if (ndl > 0.0 && ndv > 0.0) {
			ndl = max( 1e-8, ndl );
			float vdh = max(1e-8, dot(envE, Hn));
			float ndh = max(1e-8, dot(envN, Hn));
			float lodS = computeLOD(Ln, 0.5 * M_INV_PI);
			radiance += fade * envSample(Ln, lodS) * _sheen_contrib(ndh, ndl, ndv, specColor, roughness);
		}
	}
	radiance /= float(nbSamples);

	return radiance;
}

// If there is a "Sheen Color" channel, the default Sheen Weight should be 1.0, not 0.0
float getSheenWeight(SamplerSparse sheenColor, SamplerSparse sheenWeight, SparseCoord coord)
{
	vec4 weight = textureSparse(sheenWeight, coord);
	vec4 color = textureSparse(sheenColor, coord);
	float default_weight = color.a;
  return weight.r + default_weight * (1.0 - weight.g);
}

//- Rewrite lib-sss.glsl
//- ---------------------------------------

//: param auto channel_translucency
uniform SamplerSparse transmissionweight_tex;

//: param auto channel_scattering
uniform SamplerSparse subsurfaceweight_tex;

//: param auto channel_scatteringcolor
uniform SamplerSparse subsurfaceradius_tex;


//: param auto scene_original_radius
uniform float SceneScale;

//: param custom {
//:   "label": "Enable",
//:   "default": false,
//:   "group": "Subsurface",
//:   "description": "<html><head/><body><p>Scatters light below the surface, rather than passing straight through.<br/><b>Please note</b>: <b>Activate Subsurface Scattering</b> needs to be enabled in <b>Display Settings</b> and the following channel needs to be present for the subsurface scattering parameters to have an effect: <b>Scattering</b></p></body></html>",
//:   "asm": "scatter"
//: }
uniform_specialization bool subsurfaceEnabled;


//: param custom {
//:   "default": 0.1,
//:   "label": "Scale",
//:   "min": 0.01,
//:   "max": 1.0,
//:   "group": "Subsurface",
//:   "description": "<html><head/><body><p>Controls the radius/depth of the light absorption in the material.<br/><b>Please note</b>: <b>Activate Subsurface Scattering</b> needs to be enabled in <b>Display Settings</b> and the following channel needs to be present for the subsurface scattering parameters to have an effect: <b>Scattering</b></p></body></html>",
//:   "visible": "input.subsurfaceEnabled",
//:   "asm": "scatter_distance"
//: }
uniform float subsurfaceScale;

vec4 getSubsurfaceRadius(vec3 subsurfaceRadius) {
	vec4 coeffs = vec4(0.0);
	if (subsurfaceEnabled) {
		coeffs.xyz = subsurfaceScale / SceneScale * subsurfaceRadius;
		coeffs.w = coeffs.xyz==vec3(0.0) ? 0.0 : 1.0;
	}
	return coeffs;
}

vec4 getSubsurfaceRadius(SamplerSparse subsurfaceRadius, SparseCoord coord) {
	if (subsurfaceEnabled) {
		return getSubsurfaceRadius(getScatteringPerComponent(subsurfaceRadius, coord));
	}
	return vec4(0.0);
}

vec4 getSubsurfaceColor(vec3 color, float weight) {
	return vec4(color,weight);
}

// If there is a "Subsurface Radius" channel, the default Subsurface Weight should be 1.0, not 0.0
float getSubsurfaceWeight(SamplerSparse subsurfaceRadius, SamplerSparse subsurfaceWeight, SparseCoord coord)
{
	vec4 weight = textureSparse(subsurfaceWeight, coord);
	vec4 radius = getSubsurfaceRadius(subsurfaceRadius, coord);
	float default_weight = radius.a;
  return weight.r + default_weight * (1.0 - weight.g);
}

vec4 getSubsurfaceColor(SamplerSparse subsurfaceRadius, SamplerSparse subsurfaceWeight, SparseCoord coord) {
	if (subsurfaceEnabled) {
		return getSubsurfaceColor(vec3(1.0),getSubsurfaceWeight(subsurfaceRadius, subsurfaceWeight, coord));
	}
	return vec4(0.0);
}

//: param custom {
//:   "group": "Geometry",
//:   "label": "Enable Double sided",
//:   "default": false,
//:   "description": "<html><head/><body><p>When enabled, the surface is visible on both sides, i.e. back-face culling is disabled.</p></body></html>"
//: }
uniform_specialization bool doubleSided;


//: param auto channel_opacity
uniform SamplerSparse opacity_tex;

//: param custom {
//:   "group": "Geometry",
//:   "label": "Enable Opacity",
//:   "default": false,
//:   "asm": "opacity",
//:   "description": "<html><head/><body><p>Uses the opacity texture to progressively blend the transparent surface over the background.<br/><b>Please note</b>: The following channel needs to be present for this parameter to have an effect: <b>Opacity</b></p></body></html>",
//:   "enable": "!input.subsurfaceEnabled",
//:   "description_disabled": "<html><head/><body><p>Disable the <b>Subsurface Scattering</b> to use <b>Alpha blending</b>.</p></body></html>"
//: }
uniform_specialization bool OpacityEnabled;

import lib-bent-normal.glsl

//- Rewrite lib-normal.glsl
//- ---------------------------------------

//: param custom {
//:   "group": "Detail",
//:   "label": "Detail Display Normal Scale",
//:   "default": 0.5,
//:   "min": 0.0,
//:   "max": 1.0,
//:   "description": "<html><head/><body><p>This would not effect output.</p></body></html>"
//: }
uniform float heightDisplayScale;

vec3 _normalFromHeight(SparseCoord coord, float height_force)
{
  // Normal computation using height map

  // Determine gradient offset in function of derivatives
  vec2 dfd = max(coord.dfdx,coord.dfdy);
  dfd = max(dfd,height_texture.size.zw);

  vec2 dfdx,dfdy;
  textureSparseQueryGrad(dfdx, dfdy, height_texture, coord);
  float h_l  = textureGrad(height_texture.tex, coord.tex_coord+vec2(-dfd.x,  0    ), dfdx, dfdy).r;
  float h_t  = textureGrad(height_texture.tex, coord.tex_coord+vec2(     0,  dfd.y), dfdx, dfdy).r;

  vec2 dh_dudv;
  if (height_2_normal_method==1) {
    float h_c  = textureGrad(height_texture.tex, coord.tex_coord, dfdx, dfdy).r;
		dh_dudv = 4.0 * height_force / dfd * vec2(h_l-h_c,h_c-h_t);
  }
  else {
    float h_r  = textureGrad(height_texture.tex, coord.tex_coord+vec2( dfd.x,  0    ), dfdx, dfdy).r;
    float h_b  = textureGrad(height_texture.tex, coord.tex_coord+vec2(     0, -dfd.y), dfdx, dfdy).r;
    float h_rt = textureGrad(height_texture.tex, coord.tex_coord+vec2( dfd.x,  dfd.y), dfdx, dfdy).r;
    float h_lt = textureGrad(height_texture.tex, coord.tex_coord+vec2(-dfd.x,  dfd.y), dfdx, dfdy).r;
    float h_rb = textureGrad(height_texture.tex, coord.tex_coord+vec2( dfd.x, -dfd.y), dfdx, dfdy).r;
    float h_lb = textureGrad(height_texture.tex, coord.tex_coord+vec2(-dfd.x, -dfd.y), dfdx, dfdy).r;

    dh_dudv = (0.5 * height_force) / dfd * vec2(
      2.0*(h_l-h_r)+h_lt-h_rt+h_lb-h_rb,
      2.0*(h_b-h_t)+h_rb-h_rt+h_lb-h_lt);
  }

  return normalize(vec3(dh_dudv, HEIGHT_FACTOR));
}

vec3 _getTSNormal(SparseCoord coord, SamplerSparse texture)
{
  float height_force = heightDisplayScale / SceneScale * 10;
  vec3 normalH = _normalFromHeight(coord, height_force);
  return getTSNormal(coord, texture, normalH);
}

vec3 _getTSNormal(SparseCoord coord)
{
  return _getTSNormal(coord, base_normal_texture);
}

vec3 _computeWSNormal(SparseCoord coord, vec3 tangent, vec3 bitangent, vec3 normal)
{
  vec3 normal_vec = _getTSNormal(coord);
  return normalize(
    normal_vec.x * tangent +
    normal_vec.y * bitangent +
    normal_vec.z * normal
  );
}

vec3 _computeWSBentNormal(SparseCoord coord, vec3 tangent, vec3 bitangent, vec3 normal)
{
  vec3 bent_normal_vec = _getTSNormal(coord, bent_normal_texture);
  return normalize(
    bent_normal_vec.x * tangent +
    bent_normal_vec.y * bitangent +
    bent_normal_vec.z * normal
  );
}

void _computeBentNormal(inout LocalVectors vectors, V2F inputs) {
  if (use_bent_normal) {
    vectors.bent = _computeWSBentNormal(inputs.sparse_coord, inputs.tangent, inputs.bitangent, inputs.normal);
  }
}

vec3 _getDiffuseBentNormal(LocalVectors vectors) {
  return use_bent_normal ?
    normalize(mix(vectors.normal, vectors.bent, bent_normal_diffuse_amount)) :
    vectors.normal;
}

float _getBentNormalSpecularAmount() {
  return use_bent_normal ? bent_normal_specular_amount : 0.0;
}


import lib-utils.glsl

// must import this lib to enable sss.
import lib-sss.glsl

//- Declare the iray mdl material to use with this shader.
//: metadata {
//:   "mdl":"mdl::alg::materials::painter::standard"
//: }

//- Disable culling if double sided option is enabled
//: state cull_face off {"enable":"input.doubleSided"}
//- Enable 'over' alpha blending if opacity alpha blend
//: state blend over {"enable":"input.OpacityEnabled && !input.subsurfaceEnabled && !input.transmissionEnabled"}
//- Enable 'premultiplied over' alpha blending if translucency
//: state blend over_premult {"enable":"input.transmissionEnabled && !input.subsurfaceEnabled"}
//- Enable 'add multiply' alpha blending if absorption is required
//: state blend add_multiply {"enable":"input.transmissionEnabled && !input.subsurfaceEnabled"}

//- Channels needed for metal/rough workflow are bound here.
//: param auto channel_basecolor
uniform SamplerSparse basecolor_tex;
//: param auto channel_roughness
uniform SamplerSparse roughness_tex;
//: param auto channel_metallic
uniform SamplerSparse metallic_tex;
//: param auto channel_anisotropylevel
uniform SamplerSparse anisotropylevel_tex;
//: param auto channel_anisotropyangle
uniform SamplerSparse anisotropyangle_tex;
//: param auto channel_specularlevel
uniform SamplerSparse specularlevel_tex;
//: param auto channel_specularedgecolor
uniform SamplerSparse specularedgecolor_tex;
//: param auto channel_absorptioncolor
uniform SamplerSparse absorptioncolor_tex;


//- Shader entry point.
void shade(V2F inputs)
{

	// Fetch material parameters, and conversion to the specular/roughness model
	float baseRoughness = getRoughness(roughness_tex, inputs.sparse_coord);

	float anisotropyLevel = 0.0;
	float anisotropyAngle = 0.0;
	if (anisotropyEnabled) {
		anisotropyLevel = getAnisotropyLevel(anisotropylevel_tex, inputs.sparse_coord);
		if (anisotropyLevel > 0.0) {
			anisotropyAngle = getAnisotropyAngle(anisotropyangle_tex, inputs.sparse_coord);
		}
	}

	vec3 baseColor = getBaseColor(basecolor_tex, inputs.sparse_coord);
	float metallic = getMetallic(metallic_tex, inputs.sparse_coord);
	vec3 diffColor = generateDiffuseColor(baseColor, metallic);
	float specularLevel = getSpecularLevel(specularlevel_tex, inputs.sparse_coord);
	vec3 specColor_metal = baseColor;
	float dielectricF0 = iorToSpecularLevel(1.0, specularIoR);
	float coatWeight = 0.0;
	if (coatEnabled) {
		coatWeight = getCoatWeight(coatColor_tex, coatOpacity_tex, inputs.sparse_coord);
		if (coatWeight > 0.0) {
			float underCoatF0 = iorToSpecularLevel(coatIoR, specularIoR);
			dielectricF0 = mix(dielectricF0, underCoatF0, coatWeight);
		}
	}
	vec3 specColor_dielectric = vec3(dielectricF0 * 2.0 * specularLevel);

	// Get detail (ambient occlusion) and global (shadow) occlusion factors
	// separately in order to blend the bent normals properly
	float shadowFactor = getShadowFactor();
	float occlusion = getAO(inputs.sparse_coord, true, use_bent_normal);

	float specOcclusion = specularOcclusionCorrection(
		use_bent_normal ? shadowFactor : occlusion * shadowFactor,
		metallic,
		baseRoughness);

	vec3 normal = _computeWSNormal(inputs.sparse_coord,
		inputs.tangent, inputs.bitangent, inputs.normal);
	LocalVectors vectors = computeLocalFrame(inputs, normal, anisotropyAngle);
	_computeBentNormal(vectors,inputs);

	// Diffuse lobe:
	vec3 diffuseShading = occlusion * shadowFactor * envIrradiance(_getDiffuseBentNormal(vectors));

	// Specular lobes:
	// The specs can be interpreted as interpolating between two lobes.
	// However, due to the prohibitive cost for real-time, we interpolate
	// between two specular colors and use it for a single specular lobe.
	vec3 specColor = mix(specColor_dielectric, specColor_metal, metallic);
	vec3 specSecondaryColor = vec3(1.0);
	if (specularEdgeColorEnabled) {
		specSecondaryColor = getSpecularEdgeColor(specularedgecolor_tex, inputs.sparse_coord);
	}
	vec3 specEdgeColor = mix(vec3(1.0), specSecondaryColor, metallic);
	vec3 specColoring = mix(vec3(1.0), specSecondaryColor, 1.0 - metallic);
	vec3 specReflection = vec3(0.0);
	if (anisotropyEnabled) {
		vec2 roughnessAniso = generateAnisotropicRoughnessASM(baseRoughness, anisotropyLevel);
		specReflection = pbrComputeSpecularAnisotropic(
			vectors,
			specColor,
			specEdgeColor,
			roughnessAniso,
			occlusion,
			_getBentNormalSpecularAmount());
	}
	else {
		specReflection = pbrComputeSpecular(
			vectors,
			specColor,
			specEdgeColor,
			baseRoughness,
			occlusion,
			_getBentNormalSpecularAmount());
	}
	vec3 specularShading = specOcclusion * specColoring * specReflection;

	// Sheen:
	if (_sheenEnabled) {
		float sheenWeight = getSheenWeight(_sheenColor_tex, _sheenOpacity_tex, inputs.sparse_coord);
		if (sheenWeight > 0.0) {
			float sheenRoughness = getSheenRoughness(_sheenRoughness_tex, inputs.sparse_coord);
			vec3 sheenColor = sheenWeight * getSheenColor(_sheenColor_tex, inputs.sparse_coord);
			vec3 sheenSpecularShading = _pbrComputeSheen(vectors, sheenColor, sheenRoughness);
			specularShading += specOcclusion * sheenSpecularShading;
		}
	}

	// Coating:
	// Keep track of coat absorption quantity to know how much to reduce contribution for lower layers
	vec3 coatAbsorption = vec3(1.0);
	if (coatWeight > 0.0) {
		vec3 coatNormal = getWSCoatNormal(inputs.sparse_coord,
			inputs.tangent, inputs.bitangent, inputs.normal);
		LocalVectors coatVectors = computeLocalFrame(inputs, coatNormal, 0.0);

		vec3 coatColor = getCoatColor(coatColor_tex, inputs.sparse_coord);
		float coatSpecularLevel = getCoatSpecularLevel(coatSpecularLevel_tex, inputs.sparse_coord);
		vec3 coatSpecColor = vec3(iorToSpecularLevel(1.0, coatIoR) * 2.0 * coatSpecularLevel);

		float coatRoughness = getCoatRoughness(coatRoughness_tex, inputs.sparse_coord);
		float coatSpecOcclusion = specularOcclusionCorrection(occlusion * shadowFactor, 0.0, coatRoughness);
		vec3 coatSpecularShading = pbrComputeSpecular(coatVectors, coatSpecColor, coatRoughness);

		float ndv = clamp(dot(coatVectors.normal, vectors.eye), 1e-4, 1.0);
		coatAbsorption = coatPassageColorMultiplier(coatColor, coatWeight, ndv);
		coatAbsorption *= coatAbsorption;

		diffuseShading *= coatAbsorption;
		specularShading *= coatAbsorption;
		specularShading += (coatSpecOcclusion * coatWeight) * coatSpecularShading;
	}

	albedoOutput(diffColor);

	vec3 emissiveShading = pbrComputeEmissive(emissive_tex, inputs.sparse_coord);

	// Blending related effects
	if ((transmissionEnabled || OpacityEnabled) && !subsurfaceEnabled) {
		float alpha = 1.0;
		// Opacity cut-through
		if (OpacityEnabled) {
			alpha = getOpacity(opacity_tex, inputs.sparse_coord);
		}

		// Refractive transmission
		if (transmissionEnabled) {
			// Blending premultiplied over: must premultiply contributions manually
			emissiveShading *= alpha;
			specularShading *= alpha;
			diffuseShading *= alpha;

			float transmission = getTranslucency(transmissionweight_tex, inputs.sparse_coord) * (1.0-metallic);
			diffuseShading *= 1.0-transmission;

			vec3 absorption = vec3(1.0);
			
			// Absorption use dual output blending mode
			absorption = coatAbsorption * getAbsorptionColor(absorptioncolor_tex, inputs.sparse_coord);
			color1Output(vec4(vec3(1.0)-alpha*(vec3(1.0)-absorption*transmission*(1.0-baseRoughness)), 1.0));
			

			// Approximation: roughness cutoff the transparency
			diffuseShading += absorption * alpha * baseRoughness * transmission * envIrradiance(-vectors.normal);
			
			alpha *= 1.0-(transmission*(1.0-baseRoughness));
		}

		alphaOutput(alpha);
	}

	emissiveColorOutput(emissiveShading);
	diffuseShadingOutput(diffuseShading);
	specularShadingOutput(specularShading);

	sssCoefficientsOutput(getSubsurfaceRadius(subsurfaceradius_tex,inputs.sparse_coord));
	sssColorOutput(getSubsurfaceColor(subsurfaceradius_tex, subsurfaceweight_tex,inputs.sparse_coord));

}
