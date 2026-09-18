from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
MODEL = ROOT / "CAD" / "Starfall_Fully_Assembled_Colored.glb"
SCALE = 1


def font(size):
    windows = Path("C:/Windows/Fonts/arial.ttf")
    linux = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    return ImageFont.truetype(str(windows if windows.exists() else linux), size * SCALE)


def basis(camera):
    camera = np.asarray(camera, dtype=float)
    camera /= np.linalg.norm(camera)
    if abs(camera[2]) > 0.98:
        right = np.array([1.0, 0.0, 0.0])
        up = np.array([0.0, 1.0, 0.0])
    else:
        right = np.cross([0.0, 0.0, 1.0], camera)
        right /= np.linalg.norm(right)
        up = np.cross(camera, right)
    return camera, right, up


def exploded_offset(name):
    if name in {"Top", "Purple_Inlays", "Keycaps", "Encoder_Knob", "M3_Screws", "Illustrative_Keycap_Legends"}:
        return 26.0
    if name in {"Actual_OLED_Glass", "OLED_STARFALL"}:
        return 17.0
    if name == "Electronics":
        return 8.0
    if name == "Middle_Purple":
        return 3.0
    return 0.0


def render_model(size, camera, margin=70, exploded=False, background=(242, 244, 248)):
    width, height = size
    scene = trimesh.load(MODEL, force="scene")
    meshes = dict(scene.geometry)
    camera, right, up = basis(camera)
    light = np.array([-0.25, -0.55, 1.0])
    light /= np.linalg.norm(light)

    triangles = []
    for name, mesh in meshes.items():
        vertices = mesh.vertices.copy()
        if exploded:
            vertices[:, 2] += exploded_offset(name)
        base = tuple(int(v) for v in mesh.visual.vertex_colors[0][:3])
        for face, normal in zip(mesh.faces, mesh.face_normals):
            if normal @ camera <= 0:
                continue
            tri = vertices[face]
            shade = 0.58 + 0.42 * max(0.0, normal @ light)
            color = tuple(int(channel * shade) for channel in base)
            triangles.append((float(tri.mean(axis=0) @ camera), tri, color))

    all_vertices = np.concatenate([item[1] for item in triangles])
    projected_x = all_vertices @ right
    projected_y = all_vertices @ up
    available_w = (width - 2 * margin) * SCALE
    available_h = (height - 2 * margin) * SCALE
    render_scale = min(
        available_w / (projected_x.max() - projected_x.min()),
        available_h / (projected_y.max() - projected_y.min()),
    )
    center_x = width * SCALE / 2
    center_y = height * SCALE / 2
    midpoint_x = (projected_x.max() + projected_x.min()) / 2
    midpoint_y = (projected_y.max() + projected_y.min()) / 2

    image = Image.new("RGB", (width * SCALE, height * SCALE), background)
    pixels = np.array(image)
    zbuffer = np.full((height * SCALE, width * SCALE), -np.inf, dtype=np.float32)

    for _, tri, color in triangles:
        coords = np.column_stack(
            (
                center_x + (tri @ right - midpoint_x) * render_scale,
                center_y - (tri @ up - midpoint_y) * render_scale,
            )
        )
        xmin, ymin = np.maximum(np.floor(coords.min(axis=0)).astype(int), [0, 0])
        xmax, ymax = np.minimum(
            np.ceil(coords.max(axis=0)).astype(int), [width * SCALE - 1, height * SCALE - 1]
        )
        if xmax < xmin or ymax < ymin:
            continue
        xx, yy = np.meshgrid(np.arange(xmin, xmax + 1) + 0.5, np.arange(ymin, ymax + 1) + 0.5)
        a, b, c = coords
        denominator = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(denominator) < 1e-9:
            continue
        u = ((b[1] - c[1]) * (xx - c[0]) + (c[0] - b[0]) * (yy - c[1])) / denominator
        v = ((c[1] - a[1]) * (xx - c[0]) + (a[0] - c[0]) * (yy - c[1])) / denominator
        w = 1 - u - v
        depth = tri @ camera
        zz = u * depth[0] + v * depth[1] + w * depth[2]
        buffer = zbuffer[ymin : ymax + 1, xmin : xmax + 1]
        mask = (u >= -1e-8) & (v >= -1e-8) & (w >= -1e-8) & (zz > buffer)
        buffer[mask] = zz[mask]
        pixels[ymin : ymax + 1, xmin : xmax + 1][mask] = color

    return Image.fromarray(pixels).resize((width, height), Image.Resampling.LANCZOS)


def save_plain(name, camera, exploded=False):
    image = render_model((1000, 800), camera, margin=75, exploded=exploded)
    image.save(ASSETS / name)
    print(ASSETS / name)


def save_preview():
    width, height = 800, 1020
    image = Image.new("RGB", (width * SCALE, height * SCALE), (242, 244, 248))
    model = render_model((800, 735), [1.0, -1.3, 1.6], margin=58)
    image.paste(model.resize((800 * SCALE, 735 * SCALE)), (0, 135 * SCALE))
    draw = ImageDraw.Draw(image)
    draw.text((60 * SCALE, 35 * SCALE), "Starfall - Celestial Edition", (27, 31, 42), font=font(35))
    draw.text((60 * SCALE, 84 * SCALE), "Latest corrected production case", (67, 75, 91), font=font(23))
    draw.text((60 * SCALE, 145 * SCALE), "ASSEMBLED", (96, 67, 140), font=font(18))
    draw.text((60 * SCALE, 919 * SCALE), "114.4 x 116 x 22.9 mm  -  PCB layout preserved", (37, 42, 55), font=font(23))
    draw.text((60 * SCALE, 958 * SCALE), "Rendered from the current production assembly.", (89, 96, 110), font=font(18))
    image.resize((width, height), Image.Resampling.LANCZOS).save(ASSETS / "fully_assembled_preview.png")
    print(ASSETS / "fully_assembled_preview.png")


ASSETS.mkdir(exist_ok=True)
save_preview()
save_plain("case_iso.png", [1.0, -1.3, 1.6])
save_plain("case_top.png", [0.0, 0.0, 1.0])
save_plain("case_exploded.png", [1.0, -1.3, 1.35], exploded=True)
