import bpy
import bmesh
import math
import os

print("=== Starting Fast Optimized Blender JATUA Dark Video Render ===")

# 1. Reset Scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = "JatuaCombatScene"

# 2. Render Engine & Performance Optimization for CPU
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 360 # 12 seconds animation

# Optimize samples for fast CPU rendering (4 samples is crisp and renders 50x faster)
if hasattr(scene, 'eevee'):
    scene.eevee.taa_render_samples = 4
    scene.eevee.use_bloom = True
    scene.eevee.use_gtao = False
    scene.eevee.use_ssr = False

# Output Video Settings (H.264 MP4)
output_video_path = "/home/antonio/Video/JATUA_Dark_Cinematic_Combat_Restoration.mp4"
os.makedirs("/home/antonio/Video", exist_ok=True)
scene.render.filepath = output_video_path
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'HIGH'
scene.render.ffmpeg.ffmpeg_preset = 'REALTIME'

# 3. Create World Atmosphere & Sky
world = bpy.data.worlds.new("CyberpunkAtmosphere")
scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs['Color'].default_value = (0.05, 0.08, 0.10, 1.0) # Slate-teal
    bg_node.inputs['Strength'].default_value = 0.9

# 4. Build Authentic JATUA Dark Spaceship Mesh
ship_mesh = bpy.data.meshes.new("JatuaDarkMesh")
ship_obj = bpy.data.objects.new("JatuaDark", ship_mesh)
scene.collection.objects.link(ship_obj)

bm = bmesh.new()

slices = [
    (-20.0, 0.04, 0.04, 0.0),   # Razor Tip
    (-14.0, 0.55, 0.38, 0.0),   # Forebody
    (-7.0,  1.25, 0.78, 0.04),  # Forward Chine
    (0.0,   1.80, 1.10, 0.08),  # Midbody
    (5.5,   1.95, 1.24, 0.10),  # Wing Root Base
    (8.5,   1.55, 1.08, 0.06)   # Engine Base
]

rings = []
for s in slices:
    z, hw, hh, y = s[0], s[1], s[2], s[3]
    p0 = bm.verts.new((-hw * 0.55, y + hh, z))
    p1 = bm.verts.new(( hw * 0.55, y + hh, z))
    p2 = bm.verts.new(( hw,        y + hh * 0.25, z))
    p3 = bm.verts.new(( hw * 0.85, y - hh * 0.7, z))
    p4 = bm.verts.new(( 0,         y - hh, z))
    p5 = bm.verts.new((-hw * 0.85, y - hh * 0.7, z))
    p6 = bm.verts.new((-hw,        y + hh * 0.25, z))
    rings.append([p0, p1, p2, p3, p4, p5, p6])

for i in range(len(rings) - 1):
    r1 = rings[i]
    r2 = rings[i+1]
    for j in range(len(r1)):
        next_j = (j + 1) % len(r1)
        bm.faces.new([r1[j], r1[next_j], r2[next_j], r2[j]])

bm.faces.new([rings[0][0], rings[0][1], rings[0][2], rings[0][3], rings[0][4], rings[0][5], rings[0][6]])

# 4 Stabilizer Fins
def add_fin(angle_rad, x_pos, y_pos, z_pos):
    v1 = bm.verts.new((x_pos, y_pos, z_pos))
    dx = math.cos(angle_rad) * 2.8
    dy = math.sin(angle_rad) * 2.8
    v2 = bm.verts.new((x_pos + dx, y_pos + dy, z_pos + 1.6))
    v3 = bm.verts.new((x_pos + dx * 0.85, y_pos + dy * 0.85, z_pos + 3.4))
    v4 = bm.verts.new((x_pos, y_pos, z_pos + 2.7))
    bm.faces.new([v1, v2, v3, v4])

add_fin(math.radians(45),   0.9,  0.45, 4.2)
add_fin(math.radians(135), -0.9,  0.45, 4.2)
add_fin(math.radians(-45),  0.85,-0.35, 4.5)
add_fin(math.radians(-135),-0.85,-0.35, 4.5)

# Dorsal Spine
sv0 = bm.verts.new((0, 1.4, 0.5))
sv1 = bm.verts.new((0, 1.82, 6.5))
sv2 = bm.verts.new((0.38, 1.15, 6.5))
sv3 = bm.verts.new((-0.38, 1.15, 6.5))
sv4 = bm.verts.new((0, 1.35, 8.2))
bm.faces.new([sv0, sv1, sv2])
bm.faces.new([sv0, sv3, sv1])
bm.faces.new([sv1, sv4, sv2])
bm.faces.new([sv1, sv3, sv4])

bm.to_mesh(ship_mesh)
bm.free()

# Spaceship Titanium PBR Material
hull_mat = bpy.data.materials.new("JatuaHullPBR")
hull_mat.use_nodes = True
bsdf = hull_mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.28, 0.35, 0.36, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.55
    bsdf.inputs['Roughness'].default_value = 0.42
ship_obj.data.materials.append(hull_mat)

# 5. Glowing Cyan Plasma Thruster Flame
flame_mesh = bpy.data.meshes.new("PlasmaFlameMesh")
flame_obj = bpy.data.objects.new("PlasmaFlame", flame_mesh)
scene.collection.objects.link(flame_obj)

bm_flame = bmesh.new()
bmesh.ops.create_cone(bm_flame, cap_ends=False, segments=12, radius1=0.85, radius2=0.05, depth=11.0)
bm_flame.to_mesh(flame_mesh)
bm_flame.free()

flame_mat = bpy.data.materials.new("PlasmaEmissive")
flame_mat.use_nodes = True
flame_nodes = flame_mat.node_tree.nodes
flame_nodes.clear()
emission = flame_nodes.new(type='ShaderNodeEmission')
emission.inputs['Color'].default_value = (0.0, 0.75, 1.0, 1.0)
emission.inputs['Strength'].default_value = 6.0
output = flame_nodes.new(type='ShaderNodeOutputMaterial')
flame_mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
flame_obj.data.materials.append(flame_mat)

flame_obj.parent = ship_obj
flame_obj.location = (0, 0.1, 14.5)
flame_obj.rotation_euler = (math.pi / 2, 0, 0)

# Thruster Light
thruster_light_data = bpy.data.lights.new(name="ThrusterLight", type='POINT')
thruster_light_data.energy = 4000
thruster_light_data.color = (0.0, 0.8, 1.0)
thruster_light_obj = bpy.data.objects.new(name="ThrusterLightObj", object_data=thruster_light_data)
scene.collection.objects.link(thruster_light_obj)
thruster_light_obj.parent = ship_obj
thruster_light_obj.location = (0, 0.1, 11.5)

# 6. Build Megacity Buildings along the Canyon
building_mat = bpy.data.materials.new("BrutalistConcrete")
building_mat.use_nodes = True
b_bsdf = building_mat.node_tree.nodes.get("Principled BSDF")
if b_bsdf:
    b_bsdf.inputs['Base Color'].default_value = (0.09, 0.12, 0.14, 1.0)
    b_bsdf.inputs['Roughness'].default_value = 0.65

# Generate buildings left & right of flight corridor
for i in range(40):
    z_pos = -300 + (i * 40)
    for side in [-1, 1]:
        x_pos = side * (50 + (i % 4) * 15)
        h = 190 + (i % 6) * 50
        w = 32 + (i % 3) * 12
        d = 32 + (i % 4) * 10
        
        b_mesh = bpy.data.meshes.new(f"Bld_{i}_{side}")
        b_obj = bpy.data.objects.new(f"BldObj_{i}_{side}", b_mesh)
        scene.collection.objects.link(b_obj)
        
        bm_b = bmesh.new()
        bmesh.ops.create_cube(bm_b, size=1.0)
        bmesh.ops.scale(bm_b, vec=(w, d, h), verts=bm_b.verts)
        bmesh.ops.translate(bm_b, vec=(x_pos, 0, z_pos), verts=bm_b.verts)
        bm_b.to_mesh(b_mesh)
        bm_b.free()
        
        b_obj.data.materials.append(building_mat)
        b_obj.location.y = -h / 2 + 10

# 7. Keyframe Combat Flight Choreography
keyframe_points = [
    (1,    0.0,   12.0, -250.0,  0.0,    0.0,   0.0),    # Entry
    (60,  15.0,   10.0, -120.0, -5.0,  -45.0,  10.0),    # Banking right
    (120, -18.0,  14.0,   10.0,  5.0,   75.0, -15.0),    # Hard bank left
    (180,  0.0,   16.0,  140.0,  0.0,  360.0,   0.0),    # 360 Evasive Barrel Roll
    (240,  0.0,   22.0,  230.0, 85.0,    0.0,   0.0),    # Pugachev Cobra Maneuver
    (290,  0.0,   15.0,  270.0,  5.0,    0.0,   0.0),    # Recovery
    (360,  0.0,   10.0,  450.0,  0.0,    0.0,   0.0)     # Hypersonic Exit
]

for frame, x, y, z, pitch_deg, roll_deg, yaw_deg in keyframe_points:
    ship_obj.location = (x, y, z)
    ship_obj.rotation_euler = (math.radians(pitch_deg), math.radians(yaw_deg), math.radians(roll_deg))
    ship_obj.keyframe_insert(data_path="location", frame=frame)
    ship_obj.keyframe_insert(data_path="rotation_euler", frame=frame)

# 8. Set up Cinematic Follow Camera
cam_data = bpy.data.cameras.new("CinematicCam")
cam_data.lens = 35
cam_obj = bpy.data.objects.new("CinematicCamObj", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

cam_keyframes = [
    (1,    12.0, 18.0, -285.0),
    (60,   26.0, 16.0, -155.0),
    (120, -28.0, 20.0,  -25.0),
    (180,   8.0, 24.0,  105.0),
    (240, -14.0, 30.0,  190.0),
    (290,   0.0, 22.0,  230.0),
    (360,   6.0, 18.0,  410.0)
]

for frame, cx, cy, cz in cam_keyframes:
    cam_obj.location = (cx, cy, cz)
    cam_obj.keyframe_insert(data_path="location", frame=frame)

track_constraint = cam_obj.constraints.new(type='TRACK_TO')
track_constraint.target = ship_obj
track_constraint.track_axis = 'TRACK_NEGATIVE_Z'
track_constraint.up_axis = 'UP_Y'

# 9. Lighting
sun_data = bpy.data.lights.new(name="SunLight", type='SUN')
sun_data.energy = 4.5
sun_data.color = (0.75, 0.88, 1.0)
sun_obj = bpy.data.objects.new(name="SunLightObj", object_data=sun_data)
scene.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.radians(45), math.radians(30), 0)

print(f"Rendering optimized animation to {output_video_path}...")
bpy.ops.render.render(animation=True)
print("=== Rendering Complete! ===")
