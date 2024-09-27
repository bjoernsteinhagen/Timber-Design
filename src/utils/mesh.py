from specklepy.objects.geometry import Mesh
from specklepy.objects.other import RenderMaterial

def trimesh_to_speckle_mesh(mesh: 'trimesh.Trimesh', opacity: float, color: 'Color'):
    vertices = [item for sublist in mesh.vertices for item in sublist]
    faces, colors = [], []
    for face in mesh.faces:
        faces.append(3)
        for vertex in face:
            faces.append(int(vertex))
            colors.append(color.value)
    mesh = Mesh.create(faces=faces, vertices=vertices)
    mesh['renderMaterial'] = RenderMaterial(opacity=opacity, diffuse=color.value, emissive=color.value)
    return mesh