"""
Swole Bears Programmatic QR Code Generator Service
Generates customized, high-resolution vector (SVG) and raster (PNG) QR codes
with embedded brand logos and Error Correction Level H.
"""

import os
import sys
import base64
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    import qrcode
    import qrcode.image.svg
    from PIL import Image, ImageDraw
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_STATIC_DIR = BASE_DIR / "static" / "images"
DEFAULT_PNG_LOGO = DEFAULT_STATIC_DIR / "Swole_Bears_RGB_Logomark.png"
DEFAULT_SVG_LOGO = DEFAULT_STATIC_DIR / "Swole_Bears_RGB_Logomark.png"  # Fallback to PNG logomark in static/images

SWOLE_BEAR_RED = "#E52225"


def resolve_color(color_name: str, fallback: str = "#000000") -> str:
    """Resolves color preset names (e.g., 'swole-red') or returns valid color string."""
    if not color_name:
        return fallback
    normalized = color_name.strip().lower().replace('_', '-').replace(' ', '-')
    if normalized in ['swole-red', 'swole-bear-red', 'swole-bears-red', 'red']:
        return SWOLE_BEAR_RED
    return color_name


def get_finder_pattern_part(r: int, c: int, num_modules: int):
    """
    Returns 'outer' for outer ring of 7x7 corner square,
    'inner' for 3x3 inner pupil of corner square,
    or None if module is outside finder patterns.
    """
    if r < 7 and c < 7:
        rel_r, rel_c = r, c
    elif r < 7 and c >= num_modules - 7:
        rel_r, rel_c = r, c - (num_modules - 7)
    elif r >= num_modules - 7 and c < 7:
        rel_r, rel_c = r - (num_modules - 7), c
    else:
        return None

    if rel_r in (0, 6) or rel_c in (0, 6):
        return 'outer'
    elif 2 <= rel_r <= 4 and 2 <= rel_c <= 4:
        return 'inner'
    return None


def create_vector_svg_qr(
    url: str,
    fg_color: str = "#000000",
    bg_color: str = "#FFFFFF",
    eye_color: str = None,
    eye_outer_color: str = None,
    eye_inner_color: str = None,
    logo_path: str = None,
    logo_ratio: float = 0.22
) -> str:
    """
    Generates a pure vector SVG QR code with embedded logo centered inside.
    Supports separate colors for baseline lines (fg_color) and corner squares (eye_color).
    Uses Level H error correction (30% recovery tolerance).
    """
    fg_resolved = resolve_color(fg_color, "#000000")
    bg_resolved = resolve_color(bg_color, "#FFFFFF")
    
    base_eye = resolve_color(eye_color, fg_resolved) if eye_color else fg_resolved
    eye_outer_resolved = resolve_color(eye_outer_color, base_eye) if eye_outer_color else base_eye
    eye_inner_resolved = resolve_color(eye_inner_color, base_eye) if eye_inner_color else base_eye

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    num_modules = len(qr.modules)
    border = qr.border
    box_size = qr.box_size
    total_size = (num_modules + (2 * border)) * box_size

    body_paths = []
    eye_outer_paths = []
    eye_inner_paths = []

    for r in range(num_modules):
        for c in range(num_modules):
            if qr.modules[r][c]:
                x = (c + border) * box_size
                y = (r + border) * box_size
                path_rect = f"M{x},{y}h{box_size}v{box_size}h-{box_size}z"
                
                part = get_finder_pattern_part(r, c, num_modules)
                if part == 'outer':
                    eye_outer_paths.append(path_rect)
                elif part == 'inner':
                    eye_inner_paths.append(path_rect)
                else:
                    body_paths.append(path_rect)

    svg_parts = [
        f'<?xml version="1.0" encoding="utf-8"?>',
        f'<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {total_size} {total_size}" width="{total_size}" height="{total_size}">'
    ]

    if bg_resolved and bg_resolved != 'transparent':
        svg_parts.append(f'  <rect width="100%" height="100%" fill="{bg_resolved}"/>')

    if body_paths:
        svg_parts.append(f'  <path id="qr-body-modules" fill="{fg_resolved}" d="{" ".join(body_paths)}"/>')

    if eye_outer_paths:
        svg_parts.append(f'  <path id="qr-corner-outer" fill="{eye_outer_resolved}" d="{" ".join(eye_outer_paths)}"/>')

    if eye_inner_paths:
        svg_parts.append(f'  <path id="qr-corner-inner" fill="{eye_inner_resolved}" d="{" ".join(eye_inner_paths)}"/>')

    svg_parts.append('</svg>')
    svg_str = "\n".join(svg_parts)

    effective_logo_path = logo_path if logo_path else str(DEFAULT_PNG_LOGO)
    if not effective_logo_path or not os.path.exists(effective_logo_path):
        return svg_str

    try:
        ET.register_namespace('', "http://www.w3.org/2000/svg")
        tree_root = ET.fromstring(svg_str)
        
        width, height = float(total_size), float(total_size)

        logo_w = width * logo_ratio
        logo_h = height * logo_ratio
        logo_x = (width - logo_w) / 2.0
        logo_y = (height - logo_h) / 2.0

        badge_pad = logo_w * 0.12
        badge_w = logo_w + (badge_pad * 2)
        badge_h = logo_h + (badge_pad * 2)
        badge_x = (width - badge_w) / 2.0
        badge_y = (height - badge_h) / 2.0
        rx = badge_w * 0.20

        with open(effective_logo_path, 'rb') as f:
            logo_data = f.read()

        is_svg = effective_logo_path.lower().endswith('.svg')
        mime = 'image/svg+xml' if is_svg else 'image/png'
        b64_logo = base64.b64encode(logo_data).decode('utf-8')
        data_uri = f"data:{mime};base64,{b64_logo}"

        g_elem = ET.Element('{http://www.w3.org/2000/svg}g', {'id': 'swole-bears-logo-group'})
        
        badge_elem = ET.Element('{http://www.w3.org/2000/svg}rect', {
            'x': f"{badge_x:.2f}",
            'y': f"{badge_y:.2f}",
            'width': f"{badge_w:.2f}",
            'height': f"{badge_h:.2f}",
            'rx': f"{rx:.2f}",
            'ry': f"{rx:.2f}",
            'fill': bg_resolved if bg_resolved != 'transparent' else '#FFFFFF',
            'stroke': fg_resolved,
            'stroke-width': f"{(badge_w * 0.03):.2f}"
        })
        g_elem.append(badge_elem)

        img_elem = ET.Element('{http://www.w3.org/2000/svg}image', {
            'x': f"{logo_x:.2f}",
            'y': f"{logo_y:.2f}",
            'width': f"{logo_w:.2f}",
            'height': f"{logo_h:.2f}",
            'href': data_uri,
            '{http://www.w3.org/1999/xlink}href': data_uri
        })
        g_elem.append(img_elem)

        tree_root.append(g_elem)
        return ET.tostring(tree_root, encoding='utf-8', xml_declaration=True).decode('utf-8')

    except Exception as e:
        print(f"Warning: Failed to embed logo into SVG: {e}. Returning plain SVG QR code.")
        return svg_str


def create_raster_png_qr(
    url: str,
    fg_color: str = "#000000",
    bg_color: str = "#FFFFFF",
    eye_color: str = None,
    eye_outer_color: str = None,
    eye_inner_color: str = None,
    logo_path: str = None,
    logo_ratio: float = 0.22,
    output_path: str = "qr.png"
):
    """
    Generates a high-res raster PNG QR code with embedded logo and custom corner square colors.
    """
    fg_resolved = resolve_color(fg_color, "#000000")
    bg_resolved = resolve_color(bg_color, "#FFFFFF")
    
    base_eye = resolve_color(eye_color, fg_resolved) if eye_color else fg_resolved
    eye_outer_resolved = resolve_color(eye_outer_color, base_eye) if eye_outer_color else base_eye
    eye_inner_resolved = resolve_color(eye_inner_color, base_eye) if eye_inner_color else base_eye

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    num_modules = len(qr.modules)
    border = qr.border
    box_size = qr.box_size
    total_size = (num_modules + (2 * border)) * box_size

    img = Image.new('RGBA', (total_size, total_size), bg_resolved if bg_resolved != 'transparent' else (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for r in range(num_modules):
        for c in range(num_modules):
            if qr.modules[r][c]:
                x0 = (c + border) * box_size
                y0 = (r + border) * box_size
                x1 = x0 + box_size - 1
                y1 = y0 + box_size - 1
                
                part = get_finder_pattern_part(r, c, num_modules)
                if part == 'outer':
                    color = eye_outer_resolved
                elif part == 'inner':
                    color = eye_inner_resolved
                else:
                    color = fg_resolved
                
                draw.rectangle([x0, y0, x1, y1], fill=color)

    effective_logo_path = logo_path if logo_path else str(DEFAULT_PNG_LOGO)
    if effective_logo_path and os.path.exists(effective_logo_path):
        try:
            if not effective_logo_path.lower().endswith('.svg'):
                logo = Image.open(effective_logo_path).convert('RGBA')
                
                qr_w, qr_h = img.size
                target_logo_w = int(qr_w * logo_ratio)
                target_logo_h = int(qr_h * logo_ratio)

                try:
                    resample_filter = Image.Resampling.LANCZOS
                except AttributeError:
                    resample_filter = Image.LANCZOS
                logo.thumbnail((target_logo_w, target_logo_h), resample_filter)

                lw, lh = logo.size

                pad = int(lw * 0.12)
                badge_w = lw + (pad * 2)
                badge_h = lh + (pad * 2)
                badge_x = (qr_w - badge_w) // 2
                badge_y = (qr_h - badge_h) // 2

                bg_c = bg_resolved if bg_resolved != 'transparent' else '#FFFFFF'
                draw.rounded_rectangle(
                    [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
                    radius=int(badge_w * 0.20),
                    fill=bg_c,
                    outline=fg_resolved,
                    width=max(2, int(badge_w * 0.03))
                )

                logo_x = (qr_w - lw) // 2
                logo_y = (qr_h - lh) // 2
                img.paste(logo, (logo_x, logo_y), logo)
        except Exception as e:
            print(f"Warning: Failed to overlay logo on PNG: {e}")

    img.save(output_path)
    return output_path
