import bpy
from . import shared


def _group_input_names(group):
    # Try several access patterns because different Blender builds expose
    # the node group interface differently.
    try:
        return [i.name for i in group.inputs]
    except Exception:
        pass

    iface = getattr(group, 'interface', None)
    if iface is None:
        return []

    # common pattern: group.interface.inputs
    try:
        if hasattr(iface, 'inputs'):
            return [i.name for i in iface.inputs]
    except Exception:
        pass

    # some variants expose a sockets collection or similar
    try:
        if hasattr(iface, 'sockets'):
            return [s.name for s in iface.sockets if getattr(s, 'in_out', '').upper() == 'INPUT']
    except Exception:
        pass

    # last resort: attempt to read any attribute-like items
    try:
        return [getattr(s, 'name', str(s)) for s in iface]
    except Exception:
        return []


def _group_output_names(group):
    try:
        return [o.name for o in group.outputs]
    except Exception:
        pass

    iface = getattr(group, 'interface', None)
    if iface is None:
        return []

    try:
        if hasattr(iface, 'outputs'):
            return [o.name for o in iface.outputs]
    except Exception:
        pass

    try:
        if hasattr(iface, 'sockets'):
            return [s.name for s in iface.sockets if getattr(s, 'in_out', '').upper() == 'OUTPUT']
    except Exception:
        pass

    try:
        return [getattr(s, 'name', str(s)) for s in iface]
    except Exception:
        return []


def _group_new_input(group, socket_type, name):
    try:
        return group.inputs.new(socket_type, name)
    except Exception:
        pass

    iface = getattr(group, 'interface', None)
    if iface is None:
        return None

    # try interface.new_socket signature
    try:
        if hasattr(iface, 'new_socket'):
            return iface.new_socket(name, in_out='INPUT', socket_type=socket_type)
        if hasattr(iface, 'new'):
            return iface.new_socket(name, in_out='INPUT', socket_type=socket_type)
    except Exception:
        pass

    return None


def _group_new_output(group, socket_type, name):
    try:
        return group.outputs.new(socket_type, name)
    except Exception:
        pass

    iface = getattr(group, 'interface', None)
    if iface is None:
        return None

    try:
        if hasattr(iface, 'new_socket'):
            return iface.new_socket(name, in_out='OUTPUT', socket_type=socket_type)
    except Exception:
        pass

    return None


def _get_input(group, name):
    try:
        return group.inputs[name]
    except Exception:
        pass

    iface = getattr(group, 'interface', None)
    if iface is None:
        return None

    try:
        if hasattr(iface, 'inputs'):
            return iface.inputs[name]
    except Exception:
        pass

    try:
        if hasattr(iface, 'sockets'):
            for s in iface.sockets:
                if getattr(s, 'in_out', '').upper() == 'INPUT' and getattr(s, 'name', '') == name:
                    return s
    except Exception:
        pass

    return None


def _get_output(group, name):
    try:
        return group.outputs[name]
    except Exception:
        pass

    iface = getattr(group, 'interface', None)
    if iface is None:
        return None

    try:
        if hasattr(iface, 'outputs'):
            return iface.outputs[name]
    except Exception:
        pass

    try:
        if hasattr(iface, 'sockets'):
            for s in iface.sockets:
                if getattr(s, 'in_out', '').upper() == 'OUTPUT' and getattr(s, 'name', '') == name:
                    return s
    except Exception:
        pass

    return None

def create_m3_3dprint_geonode_group():
    """
    Creates the 'M3 3D Print Prep' Geometry Node group.
    This group performs adaptive subdivision and displacement based on a relief map.
    """
    group_name = "M3 3D Print Prep (Adaptive)"
    if group_name in bpy.data.node_groups:
        group = bpy.data.node_groups[group_name]
        group.interface.clear()
        group.nodes.clear()
    else:
        group = bpy.data.node_groups.new(group_name, 'GeometryNodeTree')

    # Create group inputs/outputs using compatible API paths
    # Inputs
    if 'Geometry' not in _group_input_names(group):
        mesh_in = _group_new_input(group, 'NodeSocketGeometry', 'Geometry')
    else:
        mesh_in = _get_input(group, 'Geometry')

    if 'Texture' not in _group_input_names(group):
        tex_in = _group_new_input(group, 'NodeSocketImage', 'Texture')
    else:
        tex_in = _get_input(group, 'Texture')

    if 'Strength' not in _group_input_names(group):
        strength_in = _group_new_input(group, 'NodeSocketFloat', 'Strength')
        try:
            strength_in.default_value = 0.05
        except Exception:
            pass
    else:
        strength_in = _get_input(group, 'Strength')

    if 'Mid Level' not in _group_input_names(group):
        mid_in = _group_new_input(group, 'NodeSocketFloat', 'Mid Level')
        try:
            mid_in.default_value = 0.5
        except Exception:
            pass
    else:
        mid_in = _get_input(group, 'Mid Level')

    if 'Contrast' not in _group_input_names(group):
        contrast_in = _group_new_input(group, 'NodeSocketFloat', 'Contrast')
        try:
            contrast_in.default_value = 2.0
        except Exception:
            pass
    else:
        contrast_in = _get_input(group, 'Contrast')

    if 'Subdivision Levels' not in _group_input_names(group):
        subdiv_in = _group_new_input(group, 'NodeSocketInt', 'Subdivision Levels')
        try:
            subdiv_in.default_value = 3
            subdiv_in.min_value = 0
            subdiv_in.max_value = 6
        except Exception:
            pass
    else:
        subdiv_in = _get_input(group, 'Subdivision Levels')

    if 'Detail Threshold' not in _group_input_names(group):
        thresh_in = _group_new_input(group, 'NodeSocketFloat', 'Detail Threshold')
        try:
            thresh_in.default_value = 0.1
        except Exception:
            pass
    else:
        thresh_in = _get_input(group, 'Detail Threshold')

    if 'Smoothness' not in _group_input_names(group):
        smoothness_in = _group_new_input(group, 'NodeSocketInt', 'Smoothness')
        try:
            smoothness_in.default_value = 1
            smoothness_in.min_value = 0
            smoothness_in.max_value = 10
        except Exception:
            pass
    else:
        smoothness_in = _get_input(group, 'Smoothness')

    # Outputs: ensure a geometry output named 'Result' exists
    if 'Result' not in _group_output_names(group):
        mesh_out = _group_new_output(group, 'NodeSocketGeometry', 'Result')
    else:
        mesh_out = _get_output(group, 'Result')

    nodes = group.nodes
    links = group.links

    # 1. Input Node
    input_node = nodes.new('NodeGroupInput')
    input_node.location = (-600, 0)

    # 2. Output Node
    output_node = nodes.new('NodeGroupOutput')
    output_node.is_active_output = True
    output_node.location = (1000, 0)

    # 3. Image Texture Node (Using GeometryNodeImageTexture for 5.0)
    tex_node = nodes.new('GeometryNodeImageTexture')
    tex_node.location = (-400, 200)
    links.new(input_node.outputs["Texture"], tex_node.inputs["Image"])

    # 4. Math Logic
    # We use Luminance/Value for detail detection
    sep_rgb = nodes.new('FunctionNodeSeparateColor') # Color processing
    sep_rgb.location = (-200, 200)
    links.new(tex_node.outputs["Color"], sep_rgb.inputs[0])

    # Power/Contrast node
    math_contrast = nodes.new('ShaderNodeMath')
    math_contrast.operation = 'POWER'
    math_contrast.location = (0, 200)
    links.new(sep_rgb.outputs[0], math_contrast.inputs[0])
    links.new(input_node.outputs["Contrast"], math_contrast.inputs[1])

    # Threshold comparison
    math_thresh = nodes.new('ShaderNodeMath')
    math_thresh.operation = 'GREATER_THAN'
    math_thresh.location = (200, 200)
    links.new(math_contrast.outputs[0], math_thresh.inputs[0])
    links.new(input_node.outputs["Detail Threshold"], math_thresh.inputs[1])

    # 5. Subdivision Node (Subdivision Surface - Catmull-Clark for smoothing)
    subdiv_node = nodes.new('GeometryNodeSubdivisionSurface')
    subdiv_node.location = (400, 0)
    links.new(input_node.outputs["Geometry"], subdiv_node.inputs["Mesh"])
    links.new(input_node.outputs["Subdivision Levels"], subdiv_node.inputs["Level"])

    # 6. Smooth Displacement Logic
    # Calculate raw displacement vector
    # Offset Logic: (Value - MidLevel) * Strength * Normal
    # A. Texture Value - Mid Level
    math_sub = nodes.new('ShaderNodeMath')
    math_sub.operation = 'SUBTRACT'
    math_sub.location = (200, -200)
    links.new(sep_rgb.outputs[0], math_sub.inputs[0])
    links.new(input_node.outputs["Mid Level"], math_sub.inputs[1])

    # B. Result * Strength
    math_mul = nodes.new('ShaderNodeMath')
    math_mul.operation = 'MULTIPLY'
    math_mul.location = (400, -200)
    links.new(math_sub.outputs[0], math_mul.inputs[0])
    links.new(input_node.outputs["Strength"], math_mul.inputs[1])

    # C. Multiply by Normal
    norm_node = nodes.new('GeometryNodeInputNormal')
    norm_node.location = (200, -400)

    vec_math = nodes.new('ShaderNodeVectorMath')
    vec_math.operation = 'MULTIPLY'
    vec_math.location = (400, -400)
    links.new(math_mul.outputs[0], vec_math.inputs[0])
    links.new(norm_node.outputs["Normal"], vec_math.inputs[1])

    # 7. Blur Attribute Node (Magic for Smooth 3D Printing)
    blur_node = nodes.new('GeometryNodeBlurAttribute')
    blur_node.data_type = 'FLOAT'
    blur_node.location = (600, -200)
    links.new(vec_math.outputs["Vector"], blur_node.inputs["Value"])
    links.new(input_node.outputs["Smoothness"], blur_node.inputs["Iterations"])

    # 8. Displacement (Set Position)
    set_pos = nodes.new('GeometryNodeSetPosition')
    set_pos.location = (800, 0)
    links.new(subdiv_node.outputs["Mesh"], set_pos.inputs["Geometry"])
    # Apply Detail Threshold selection
    links.new(math_thresh.outputs[0], set_pos.inputs["Selection"])
    # Connect blurred vector to Offset
    links.new(blur_node.outputs["Value"], set_pos.inputs["Offset"])

    # 9. Smooth Shading Node
    smooth_node = nodes.new('GeometryNodeSetShadeSmooth')
    smooth_node.location = (1000, 0)
    links.new(set_pos.outputs["Geometry"], smooth_node.inputs["Geometry"])
    smooth_node.inputs["Shade Smooth"].default_value = True

    # Final Output
    # Link final geometry to the group's named output socket ('Result').
    # Be defensive: if the named socket is not present, link to the first
    # geometry-type output socket we can find.
    linked = False
    try:
        if 'Result' in [i.name for i in output_node.inputs]:
            links.new(smooth_node.outputs["Geometry"], output_node.inputs["Result"])
            linked = True
    except Exception:
        linked = False

    if not linked:
        # find first geometry input on the output node
        for inp in output_node.inputs:
            # socket.bl_idname may differ across versions; check compatible names
            if getattr(inp, 'type', None) == 'GEOMETRY' or 'Geometry' in inp.name or 'Geo' in inp.name:
                try:
                    links.new(smooth_node.outputs["Geometry"], inp)
                    linked = True
                    break
                except Exception:
                    continue
        # last resort: link to index 0
        if not linked:
            try:
                links.new(smooth_node.outputs["Geometry"], output_node.inputs[0])
            except Exception:
                # give up silently; operator should still return the group
                pass

    return group

def apply_geonode_3dprint_prep(obj):
    """
    Applies the Geometry Nodes modifier to the object and sets up the node group.
    """
    if obj.type != 'MESH':
        return False

    # Create/Get Group
    group = create_m3_3dprint_geonode_group()

    # Add Modifier
    mod = obj.modifiers.new(name="M3_3DPrint_Prep_GeoNodes", type='NODES')
    mod.node_group = group
    
    # Try to find an existing normal/height map image with shared utility
    img, dtype = shared.find_best_displacement_image(obj)
    if img:
        # If it's a normal map, generate a height map from it and use that instead
        if dtype == 'normal':
            try:
                height_img = shared.normal_to_height_image(img)
                img_to_use = height_img or img
            except Exception:
                img_to_use = img
        else:
            img_to_use = img
        # Mesh (0), Texture (1)
        mod["Socket_1"] = img_to_use
    else:
        # No texture found: leave the socket empty but don't fail
        # Caller/operator may warn the user
        pass

    return True


def apply_classic_enhanced_prep(obj):
    """Classic enhanced: more robust modifiers pipeline to retain detail
    while reducing faceting. Returns True on success."""
    if obj is None or obj.type != 'MESH':
        return False

    img, dtype = shared.find_best_displacement_image(obj)
    if not img:
        # No image found, fail gracefully
        return False

    # If the found image is a normal map, convert to a height map for displacement
    if dtype == 'normal':
        try:
            img = shared.normal_to_height_image(img)
        except Exception:
            # fallback to original image if conversion fails
            pass

    # Create/get vertex group
    vg_name = "3DPrint_Detail_Mask"
    if vg_name not in obj.vertex_groups:
        obj.vertex_groups.new(name=vg_name)

    # NOTE: EdgeSplit was previously applied before displacement which caused
    # duplicated vertices to move apart when displaced, creating visible gaps
    # along sharp edges. We now add EdgeSplit after displacement/smoothing so
    # the displacement operates on a continuous surface and sharp edges are
    # preserved afterwards.

    # Subdivision: Catmull-Clark for smoother volumetry
    subsurf = obj.modifiers.new(name='M3_Enhanced_Subsurf', type='SUBSURF')
    try:
        subsurf.subdivision_type = 'CATMULL_CLARK'
    except Exception:
        subsurf.subdivision_type = 'SIMPLE'
    subsurf.levels = 3
    subsurf.render_levels = 3

    # Displacement modifier using image
    disp_tex = bpy.data.textures.new('M3_Enhanced_DispTex', type='IMAGE')
    disp_tex.image = img

    disp = obj.modifiers.new(name='M3_Enhanced_Displace', type='DISPLACE')
    disp.texture = disp_tex
    disp.texture_coords = 'UV'
    disp.vertex_group = vg_name
    disp.strength = 0.04
    disp.mid_level = 0.5

    # Create Vertex Weight Edit modifier to generate mask from the image (so vertex group is filled)
    if 'M3_Enhanced_Mask' not in obj.modifiers:
        vwe = obj.modifiers.new(name='M3_Enhanced_Mask', type='VERTEX_WEIGHT_EDIT')
        vwe.vertex_group = vg_name
        vwe.use_add = True
        vwe.add_threshold = 0.01
        weight_tex = bpy.data.textures.get('M3_Enhanced_Weight_Tex') or bpy.data.textures.new('M3_Enhanced_Weight_Tex', type='IMAGE')
        weight_tex.image = img
        # choose mask channel based on image channels (use alpha if present,
        # otherwise fall back to red channel which often holds grayscale height)
        try:
            chan = getattr(weight_tex.image, 'channels', None)
        except Exception:
            chan = None
        if chan is not None and chan >= 4:
            vwe.mask_tex_use_channel = 'ALPHA'
        else:
            vwe.mask_tex_use_channel = 'R'
        vwe.mask_texture = weight_tex
        vwe.mask_tex_mapping = 'UV'

    # Smoothing modifier to reduce faceting while preserving displaced detail
    if 'M3_Enhanced_Smooth' not in obj.modifiers:
        smooth_mod = obj.modifiers.new(name='M3_Enhanced_Smooth', type='SMOOTH')
        try:
            smooth_mod.factor = 0.6
            smooth_mod.iterations = 8
        except Exception:
            # some blender versions may expose different properties
            pass

    # Smooth shading to reduce faceting
    mesh = obj.data
    for p in mesh.polygons:
        p.use_smooth = True

    # Edge split after displacement/smoothing to preserve sharp edges without
    # introducing gaps caused by moving already-split vertices.
    if 'M3_Enhanced_EdgeSplit' not in obj.modifiers:
        edge = obj.modifiers.new(name='M3_Enhanced_EdgeSplit', type='EDGE_SPLIT')
        try:
            edge.split_angle = 0.523599  # 30 degrees
        except Exception:
            pass

    return True


def apply_geonode_enhanced_prep(obj):
    """Modern enhanced: Geometry Nodes pipeline with micro-detail preservation.
    Creates a separate node group 'M3 3D Print Prep (Adaptive v2)'."""
    if obj.type != 'MESH':
        return False

    group_name = "M3 3D Print Prep (Adaptive v2)"
    if group_name in bpy.data.node_groups:
        group = bpy.data.node_groups[group_name]
        group.interface.clear()
        group.nodes.clear()
    else:
        group = bpy.data.node_groups.new(group_name, 'GeometryNodeTree')

    # Build a node graph similar to v1 but with micro-displacement pass
    # Create the group inputs/outputs using compatible API paths
    if 'Mesh' not in _group_input_names(group):
        mesh_in = _group_new_input(group, 'NodeSocketGeometry', 'Mesh')
    else:
        mesh_in = _get_input(group, 'Mesh')

    if 'Texture' not in _group_input_names(group):
        tex_in = _group_new_input(group, 'NodeSocketImage', 'Texture')
    else:
        tex_in = _get_input(group, 'Texture')

    if 'Result' not in _group_output_names(group):
        result_out = _group_new_output(group, 'NodeSocketGeometry', 'Result')
    else:
        result_out = _get_output(group, 'Result')

    if 'Strength' not in _group_input_names(group):
        strength_in = _group_new_input(group, 'NodeSocketFloat', 'Strength')
        try:
            strength_in.default_value = 0.05
        except Exception:
            pass
    else:
        strength_in = _get_input(group, 'Strength')

    if 'Subdivision Levels' not in _group_input_names(group):
        subdiv_in = _group_new_input(group, 'NodeSocketInt', 'Subdivision Levels')
        try:
            subdiv_in.default_value = 3
        except Exception:
            pass
    else:
        subdiv_in = _get_input(group, 'Subdivision Levels')

    if 'Detail Threshold' not in _group_input_names(group):
        thresh_in = _group_new_input(group, 'NodeSocketFloat', 'Detail Threshold')
        try:
            thresh_in.default_value = 0.1
        except Exception:
            pass
    else:
        thresh_in = _get_input(group, 'Detail Threshold')

    nodes = group.nodes
    links = group.links

    input_node = nodes.new('NodeGroupInput')
    output_node = nodes.new('NodeGroupOutput')
    input_node.location = (-600, 0)
    output_node.location = (1000, 0)

    # Image Texture
    tex_node = nodes.new('GeometryNodeImageTexture')
    tex_node.location = (-400, 200)
    links.new(input_node.outputs['Texture'], tex_node.inputs['Image'])

    # Luminance/value extraction
    sep_rgb = nodes.new('FunctionNodeSeparateColor')
    sep_rgb.location = (-200, 200)
    links.new(tex_node.outputs['Color'], sep_rgb.inputs[0])

    # Lowpass (blur) to extract low-frequency shape
    blur_node = nodes.new('GeometryNodeBlurAttribute')
    blur_node.data_type = 'FLOAT'
    blur_node.location = (0, 200)
    links.new(sep_rgb.outputs[0], blur_node.inputs['Value'])

    # High-frequency = Value - Blur(Value)
    math_sub = nodes.new('ShaderNodeMath')
    math_sub.operation = 'SUBTRACT'
    math_sub.location = (200, 200)
    links.new(sep_rgb.outputs[0], math_sub.inputs[0])
    links.new(blur_node.outputs['Value'], math_sub.inputs[1])

    # Micro displacement (before subdiv)
    micro_vec = nodes.new('ShaderNodeVectorMath')
    micro_vec.operation = 'MULTIPLY'
    micro_vec.location = (400, 200)
    norm_node = nodes.new('GeometryNodeInputNormal')
    norm_node.location = (200, 0)
    links.new(math_sub.outputs[0], micro_vec.inputs[0])
    links.new(norm_node.outputs['Normal'], micro_vec.inputs[1])

    # Subdivision (Catmull-Clark)
    subdiv_node = nodes.new('GeometryNodeSubdivisionSurface')
    subdiv_node.location = (600, 0)
    links.new(input_node.outputs['Mesh'], subdiv_node.inputs['Mesh'])
    links.new(input_node.outputs['Subdivision Levels'], subdiv_node.inputs['Level'])

    # Apply micro displacement to input mesh
    set_pos_micro = nodes.new('GeometryNodeSetPosition')
    set_pos_micro.location = (500, 0)
    links.new(input_node.outputs['Mesh'], set_pos_micro.inputs['Geometry'])
    links.new(micro_vec.outputs['Vector'], set_pos_micro.inputs['Offset'])

    # Final displacement after subdivided mesh using blurred/threshold selection
    # Compute mid-level adjusted value * strength
    math_mid = nodes.new('ShaderNodeMath')
    math_mid.operation = 'SUBTRACT'
    math_mid.location = (800, -200)
    links.new(sep_rgb.outputs[0], math_mid.inputs[0])
    # mid level is hardcoded to .5 for simplicity
    math_mid.inputs[1].default_value = 0.5

    math_mul = nodes.new('ShaderNodeMath')
    math_mul.operation = 'MULTIPLY'
    math_mul.location = (1000, -200)
    links.new(math_mid.outputs[0], math_mul.inputs[0])
    links.new(input_node.outputs['Strength'], math_mul.inputs[1])

    vec_math = nodes.new('ShaderNodeVectorMath')
    vec_math.operation = 'MULTIPLY'
    vec_math.location = (1000, 0)
    links.new(math_mul.outputs[0], vec_math.inputs[0])
    links.new(norm_node.outputs['Normal'], vec_math.inputs[1])

    set_pos = nodes.new('GeometryNodeSetPosition')
    set_pos.location = (1200, 0)
    links.new(subdiv_node.outputs['Mesh'], set_pos.inputs['Geometry'])
    links.new(vec_math.outputs['Vector'], set_pos.inputs['Offset'])

    smooth_node = nodes.new('GeometryNodeSetShadeSmooth')
    smooth_node.location = (1400, 0)
    links.new(set_pos.outputs['Geometry'], smooth_node.inputs['Geometry'])
    smooth_node.inputs['Shade Smooth'].default_value = True

    # Link final geometry to the group's 'Result' output, defensively.
    linked = False
    try:
        if 'Result' in [i.name for i in output_node.inputs]:
            links.new(smooth_node.outputs['Geometry'], output_node.inputs['Result'])
            linked = True
    except Exception:
        linked = False

    if not linked:
        for inp in output_node.inputs:
            if getattr(inp, 'type', None) == 'GEOMETRY' or 'Geometry' in inp.name or 'Geo' in inp.name:
                try:
                    links.new(smooth_node.outputs['Geometry'], inp)
                    linked = True
                    break
                except Exception:
                    continue
    if not linked:
        try:
            links.new(smooth_node.outputs['Geometry'], output_node.inputs[0])
        except Exception:
            pass

    # Attach modifier
    mod = obj.modifiers.new(name="M3_3DPrint_Prep_GeoNodes_v2", type='NODES')
    mod.node_group = group

    # Try to find an existing normal/height map image
    img, dtype = shared.find_best_displacement_image(obj)
    if img:
        # If it's a normal map, generate a height map and use that
        if dtype == 'normal':
            try:
                img = shared.normal_to_height_image(img)
            except Exception:
                pass
        mod["Socket_1"] = img

    return True
