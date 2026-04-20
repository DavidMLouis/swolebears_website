import random
import math

colors = ['#E21E26', '#111111', '#2A2A2A', '#1A1A1A', '#333333', '#444444', '#E21E26', '#111111', '#111111']

# Generate a massive canvas (8000x6000) so it never tiles on any screen
width = 8000
height = 6000

# Keep the hexagons a good size
hex_width = 100
hex_height = hex_width * math.sqrt(3) / 2
dx = hex_width * 0.75
dy = hex_height

svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid slice">\n'
svg += f'<rect width="{width}" height="{height}" fill="#0b0b0b" />\n'

# Just fill the whole thing uniformly, but with random drop-outs (prob > 0.35)
for row in range(-1, int(height/dy) + 2):
    for col in range(-1, int(width/dx) + 2):
        x = col * dx
        y = row * dy
        if col % 2 == 1:
            y += dy / 2
            
        color = random.choice(colors)
        
        # 35% empty space to look like a scattered pattern
        if random.random() > 0.35:
            scaled_pts = []
            for i in range(6):
                angle = math.pi / 3 * i
                px = x + (hex_width/2 - 2) * math.cos(angle)
                py = y + (hex_width/2 - 2) * math.sin(angle)
                scaled_pts.append(f"{px:.2f},{py:.2f}")
                
            svg += f'<polygon points="{" ".join(scaled_pts)}" fill="{color}" stroke="none" />\n'

svg += '</svg>'

with open('static/images/hex_pattern_wide.svg', 'w') as f:
    f.write(svg)
