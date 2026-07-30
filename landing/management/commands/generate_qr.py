import os
from pathlib import Path
from django.core.management.base import BaseCommand
from landing.models import QRCodeCampaign

# Import helper functions from QR_code generator script
sys_path_added = False
QR_CODE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "QR_code"
if QR_CODE_DIR.exists() and str(QR_CODE_DIR) not in os.sys.path:
    os.sys.path.insert(0, str(QR_CODE_DIR))

from generate_qr import create_vector_svg_qr, create_raster_png_qr, DEFAULT_SVG_LOGO, DEFAULT_PNG_LOGO

class Command(BaseCommand):
    help = "Generate high-resolution vector (SVG) and raster (PNG) QR codes for Swole Bears campaigns."

    def add_arguments(self, parser):
        parser.add_argument('--code-id', type=str, required=True, help="Short code ID for redirect URL (e.g., launch-batch-1)")
        parser.add_argument('--name', type=str, default="", help="Campaign name for database entry")
        parser.add_argument('--target-url', type=str, default="", help="Target destination URL for dynamic redirect")
        parser.add_argument('--base-url', type=str, default="https://swolebears.com", help="Base URL domain (default: https://swolebears.com)")
        parser.add_argument('--fg', type=str, default="#000000", help="Foreground color in hex")
        parser.add_argument('--bg', type=str, default="#FFFFFF", help="Background color in hex")
        parser.add_argument('--eye-color', type=str, default="", help="Corner square / eye color in hex or name (e.g. #E52225 or swole-red)")
        parser.add_argument('--output-dir', type=str, default=".", help="Directory to output generated QR files")
        parser.add_argument('--format', type=str, choices=['svg', 'png', 'both'], default='both', help="File output format")

    def handle(self, *args, **options):
        code_id = options['code_id']
        target_url = options['target_url']
        name = options['name'] or f"Campaign {code_id}"
        base_url = options['base_url'].rstrip('/')
        fg = options['fg']
        bg = options['bg']
        eye_color = options['eye_color']
        output_dir = Path(options['output_dir'])
        fmt = options['format']

        # 1. Update or create campaign in database if target_url specified or check existing
        campaign, created = QRCodeCampaign.objects.get_or_create(
            code_id=code_id,
            defaults={
                'name': name,
                'target_url': target_url if target_url else f"{base_url}/",
                'fg_color': fg,
                'bg_color': bg,
                'eye_color': eye_color
            }
        )

        if not created and (target_url or fg or bg or eye_color):
            campaign.target_url = target_url if target_url else campaign.target_url
            campaign.name = name if options['name'] else campaign.name
            campaign.fg_color = fg
            campaign.bg_color = bg
            campaign.eye_color = eye_color
            campaign.save()
            self.stdout.write(self.style.SUCCESS(f"Updated database entry for campaign '{code_id}' -> {campaign.target_url}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Database entry active for campaign '{code_id}' -> {campaign.target_url}"))

        # 2. Build tracking URL
        tracking_url = f"{base_url}/s/{code_id}"

        # 3. Logo path resolution
        logo_path = str(DEFAULT_SVG_LOGO) if DEFAULT_SVG_LOGO.exists() else str(DEFAULT_PNG_LOGO)

        output_dir.mkdir(parents=True, exist_ok=True)
        prefix = f"swole_bears_qr_{code_id}"

        if fmt in ['svg', 'both']:
            svg_content = create_vector_svg_qr(
                url=tracking_url,
                fg_color=fg,
                bg_color=bg,
                eye_color=eye_color,
                logo_path=logo_path,
                logo_ratio=0.22
            )
            svg_path = output_dir / f"{prefix}.svg"
            with open(svg_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            self.stdout.write(self.style.SUCCESS(f"✓ SVG Vector QR created: {svg_path}"))

        if fmt in ['png', 'both']:
            png_path = output_dir / f"{prefix}.png"
            create_raster_png_qr(
                url=tracking_url,
                fg_color=fg,
                bg_color=bg,
                eye_color=eye_color,
                logo_path=logo_path,
                logo_ratio=0.22,
                output_path=str(png_path)
            )
            self.stdout.write(self.style.SUCCESS(f"✓ PNG Raster QR created: {png_path}"))

        self.stdout.write(self.style.SUCCESS(f"All done! Code ID '{code_id}' points to '{campaign.target_url}' via redirect '{tracking_url}'."))
