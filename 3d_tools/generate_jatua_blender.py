import bpy
import bmesh
import math

# Clear existing mesh objects
bpy.ops.wm.read_factory_settings(use_empty=True)

# Create JATUA Dark Spaceship Mesh
mesh = bpy.data.meshes.new("JatuaDarkMesh")
obj = bpy.data.objects.new("JatuaDark", mesh)
bpy.context.collection.objects.link(obj)

bm = bmesh.new()

# Slices along Z axis (from tip to nozzle)
# Format: (z, width, height, y_offset)
slices = [
    (-20.0, 0.05, 0.05, 0.0),   # Razor Tip
    (-14.0, 0.55, 0.38, 0.0),   # Forebody
    (-7.0,  1.25, 0.78, 0.04),  # Forward Chine
    (0.0,   1.80, 1.10, 0.08),  # Midbody
    (5.5,   1.95, 1.24, 0.10),  # Wing Root Base
    (8.5,   1.55, 1.08, 0.06)   # Engine Base
]

rings = []
for s in slices:
    z, hw, hh, y = s[0], s[1], s[2], s[3]
    # 8 Faceted points
    p0 = bm.verts.new((-hw * 0.55, y + hh, z))
    p1 = bm.verts.new(( hw * 0.55, y + hh, z))
    p2 = bm.verts.new(( hw,        y + hh * 0.25, z))
    p3 = bm.verts.new(( hw * 0.85, y - hh * 0.7, z))
    p4 = bm.verts.new(( 0,         y - hh, z))
    p5 = bm.verts.new((-hw * 0.85, y - hh * 0.7, z))
    p6 = bm.verts.new((-hw,        y + hh * 0.25, z))
    rings.append([p0, p1, p2, p3, p4, p5, p6])

# Build Quad Faces between rings
for i in range(len(rings) - 1):
    r1 = rings[i]
    r2 = rings[i+1]
    for j in range(len(r1)):
        next_j = (j + 1) % len(r1)
        bm.faces.new([r1[j], r1[next_j], r2[next_j], r2[j]])

# Tip cap
bm.faces.new([rings[0][0], rings[0][1], rings[0][2], rings[0][3], rings[0][4], rings[0][5], rings[0][6]])

# Add 4 Cruciform Canted Stabilizer Fins
def add_fin(angle_rad, x_pos, y_pos, z_pos):
    v1 = bm.verts.new((x_pos, y_pos, z_pos))
    # Sweep out
    dx = math.cos(angle_rad) * 2.8
    dy = math.sin(angle_rad) * 2.8
    v2 = bm.verts.new((x_pos + dx, y_pos + dy, z_pos + 1.6))
    v3 = bm.verts.new((x_pos + dx * 0.85, y_pos + dy * 0.85, z_pos + 3.4))
    v4 = bm.verts.new((x_pos, y_pos, z_pos + 2.7))
    bm.faces.new([v1, v2, v3, v4])

# 4 Fins at 45 deg angles
add_fin(math.radians(45),   0.9,  0.45, 4.2)
add_fin(math.radians(135), -0.9,  0.45, 4.2)
add_fin(math.radians(-45),  0.85,-0.35, 4.5)
add_fin(math.radians(-135),-0.85,-0.35, 4.5)

bm.to_mesh(mesh)
bm.free()

# Create Material
mat = bpy.data.materials.new("JatuaDarkTitanium")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.28, 0.35, 0.35, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.5
    bsdf.inputs['Roughness'].default_value = 0.45
obj.data.materials.append(mat)

# Save .blend and export .gltf
blend_path = "/home/antonio/3d_tools/jatua_dark.blend"
gltf_path = "/home/antonio/3d_tools/jatua_dark.gltf"

bpy.ops.wm.save_as_mainfile(filepath=blend_path)
bpy.ops.export_scene.gltf(filepath=gltf_path, export_format='GLB')

print(f"Exported successfully to {blend_path} and {gltf_path}")
