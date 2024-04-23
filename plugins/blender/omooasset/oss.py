NODE_DICT = {
    "BaseColor": {
        "type": "color_tex",
        "source": "BaseColor:file",
        "to": ["SurfaceShader:Base Color"]
    },
    "Metalness": {
        "type": "float_tex",
        "source": "Metalness:file",
        "to": ["SurfaceShader:Metallic"]
    },
    "SpecularRoughness": {
        "type": "float_tex",
        "source": "SpecularRoughness:file",
        "to": ["SurfaceShader:Roughness"]
    },
    "SpecularColor": {
        "type": "color_tex",
        "source": "SpecularColor:file",
        "to": ["SurfaceShader:Specular Tint"]
    },
    "SpecularAnisotropy": {
        "type": "float_tex",
        "source": "SpecularAnisotropy:file",
        "to": ["SurfaceShader:Anisotropic"]
    },
    "SpecularRotation": {
        "type": "float_tex",
        "source": "SpecularRotation:file",
        "to": ["SurfaceShader:Anisotropic Rotation"]
    },
    "CoatWeight": {
        "type": "float_tex",
        "source": "CoatWeight:file",
        "to": ["SurfaceShader:Coat Weight"]
    },
    "CoatNormal": {
        "type": "normal_tex",
        "source": "CoatNormal:file",
        "to": ["CoatNormalMap:Color"]
    },
    "CoatNormalMap": {
        "type": "normal",
        "to": ["SurfaceShader:Coat Normal"]
    },
    "CoatColor": {
        "type": "color_tex",
        "source": "CoatColor:file",
        "to": ["SurfaceShader:Coat Tint"]
    },
    "CoatRoughness": {
        "type": "float_tex",
        "source": "CoatRoughness:file",
        "to": ["SurfaceShader:Coat Roughness"]
    },
    "SheenWeight": {
        "type": "float_tex",
        "source": "SheenWeight:file",
        "to": ["SurfaceShader:Sheen Weight"]
    },
    "SheenColor": {
        "type": "color_tex",
        "source": "SheenColor:file",
        "to": ["SurfaceShader:Sheen Tint"]
    },
    "SheenRoughness": {
        "type": "float_tex",
        "source": "SheenRoughness:file",
        "to": ["SurfaceShader:Sheen Roughness"]
    },
    "SubsurfaceWeight": {
        "type": "float_tex",
        "source": "SubsurfaceWeight:file",
        "to": ["SurfaceShader:Subsurface Weight"]
    },
    "SubsurfaceRadius": {
        "type": "color_tex",
        "source": "SubsurfaceRadius:file",
        "to": ["SurfaceShader:Subsurface Radius"]
    },
    "SubsurfaceScale": {
        "type": "float",
        "default": 1.0,
        "source": "SubsurfaceScale:value",
        "to": ["SubsurfaceSceneScale:0"]
    },
    "SubsurfaceSceneScale": {
        "type": "multiply",
        "to": ["SurfaceShader:Subsurface Scale"]
    },
    "SubsurfaceAnisotropy": {
        "type": "float_tex",
        "source": "SubsurfaceAnisotropy:file",
        "to": ["SubsurfaceAnisotropyRemap:Value"]
    },
    "SubsurfaceAnisotropyRemap": {
        "type": "remap",
        "to": ["SubsurfaceAnisotropyOffset:0"]
    },
    "SubsurfaceAnisotropyOffset": {
        "type": "add",
        "default": 0.0,
        "source": "SubsurfaceAnisotropyOffset:in2",
        "to": ["SurfaceShader:Subsurface Anisotropy"]
    },
    "EmissionScale": {
        "type": "float",
        "default": 1.0,
        "source": "EmissionScale:value",
        "to": ["SurfaceShader:Emission Strength"]
    },
    "EmissionColor": {
        "type": "color_tex",
        "source": "EmissionColor:file",
        "to": ["SurfaceShader:Emission Color"]
    },
    "Opacity": {
        "type": "float_tex",
        "source": "Opacity:file",
        "to": ["SurfaceShader:Alpha"]
    },
    "TransmissionWeight": {
        "type": "float_tex",
        "source": "TransmissionWeight:file",
        "to": ["SurfaceShader:Transmission Weight"]
    },
    "Normal": {
        "type": "normal_tex",
        "source": "Normal:file",
        "to": ["NormalMap:Color"]
    },
    "NormalMap": {
        "type": "normal",
        "to": ["CombinedNormal:Normal"]
    },
    "Detail": {
        "type": "float_tex",
        "source": "Detail:file",
        "to": ["DetailScale:0"]
    },
    "DetailScale": {
        "type": "multiply",
        "default": 1.0,
        "source": "DetailScale:in2",
        "to": ["CombinedNormal:Height", "CombinedDisplacement:1"]
    },
    "CombinedNormal": {
        "type": "normal_add",
        "to": ["SurfaceShader:Normal"]
    },
    "Displacement": {
        "type": "float_tex",
        "source": "Displacement:file",
        "to": ["CombinedDisplacement:0"]
    },
    "CombinedDisplacement": {
        "type": "add",
        "to": ["DisplacementShader:Height"]
    },
    "scene_scale": {
        "type": "float",
        "default": 1.0,
        "source": ":scene_scale",
        "to": ["SubsurfaceSceneScale:1"]
    },
    "displacement_on": {
        "type": "float",
        "default": 0.0,
        "source": ":displacement_on",
        "to": ["DisplacementShader:Scale"]
    }
}

PROP_DICT = {
    "IOR": {
        "default": 1.5,
        "source": "specular_IOR"
    },
    "Coat IOR": {
        "default": 1.5,
        "source": "coat_IOR"
    },
}
