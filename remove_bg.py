from PIL import Image, ImageDraw

def floodfill_transparent(image_path, output_path):
    img = Image.open(image_path).convert("RGBA")
    
    # Create a mask using flood fll from the top left corner.
    # We will fill white areas connected to the background with transparent.
    # To do this safely, we will create a mask image first.
    
    # Get image dimensions
    width, height = img.size
    
    # Get pixel data
    pixels = img.load()
    
    # Pick the color of the top left pixel, assuming it's the background color
    bg_color = pixels[0, 0]
    
    # If the background isn't basically white or a solid color, this might not work perfectly,
    # but let's assume it's white or off-white.
    print(f"Background color detected at (0,0): {bg_color}")
    
    # Use ImageDraw to do a flood fill on a copy
    # We'll flood fill the image with a distinct color (e.g., magenta)
    # Then we replace magenta with transparent
    
    magenta = (255, 0, 255, 255)
    ImageDraw.floodfill(img, (0, 0), magenta, thresh=20)
    # also try other corners just in case
    ImageDraw.floodfill(img, (width-1, 0), magenta, thresh=20)
    ImageDraw.floodfill(img, (0, height-1), magenta, thresh=20)
    ImageDraw.floodfill(img, (width-1, height-1), magenta, thresh=20)
    
    # Now iterate and replace magenta with transparent
    new_data = []
    for item in img.getdata():
        if item[0] == 255 and item[1] == 0 and item[2] == 255:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    
    # Crop to bounding box
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        
    img.save(output_path, "PNG")
    print("Saved to", output_path)

if __name__ == "__main__":
    floodfill_transparent("static/images/product_bag.png", "static/images/product_bag.png")
