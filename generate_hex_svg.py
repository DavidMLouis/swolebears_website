import random
import math

# Hexagon colors for Swole Bears branding (reds, dark grays, blacks)
colors = ['#E21E26', '#111111', '#2A2A2A', '#1A1A1A', '#333333', '#444444', '#E21E26', '#111111', '#111111']

# Generate a MASSIVE responsive background that never cuts off
# We make it huge so it scales well
width = 6000
height = 6000

# We want hexagons that are a decent size
hex_width = 150
hex_height = hex_width * math.sqrt(3) / 2
dx = hex_width * 0.75
dy = hex_height

svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid slice">\n'
svg += f'<rect width="{width}" height="{height}" fill="#0b0b0b" />\n'

# We will NOT draw hexagons near the edges. We leave a massive black padding
# so the image cleanly fades out into the website background and no hexagons are "sliced".
pad_cols = 5
pad_rows = 5

for row in range(-1, int(height/dy) + 2):
    for col in range(-1, int(width/dx) + 2):
        x = col * dx
        y = row * dy
        if col % 2 == 1:
            y += dy / 2
            
        color = random.choice(colors)
        
        # Determine how far we are from the center
        cx_norm = (x - width/2) / (width/2)
        cy_norm = (y - height/2) / (height/2)
        distance_from_center = math.sqrt(cx_norm**2 + cy_norm**2)
        
        # Taper off generation probability near the edges so it fades into nothing naturally
        # If distance > 0.8, probability drops to 0 quickly
        prob = 0.4
        if distance_from_center > 0.7:
            prob *= max(0, 1 - (distance_from_center - 0.7) * 4) # Fades out completely by 0.95
            
        if random.random() < prob:
            # Add a small gap by scaling down slightly
            scaled_pts = []
            for i in range(6):
                angle = math.pi / 3 * i
                px = x + (hex_width/2 - 3) * math.cos(angle)
                py = y + (hex_width/2 - 3) * math.sin(angle)
                scaled_pts.append(f"{px:.2f},{py:.2f}")
                
            svg += f'<polygon points="{" ".join(scaled_pts)}" fill="{color}" stroke="none" />\n'

svg += '</svg>'

with open('static/images/hex_pattern.svg', 'w') as f:
    f.write(svg)
