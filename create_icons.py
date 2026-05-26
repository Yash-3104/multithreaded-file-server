from PIL import Image, ImageDraw
import os

def create_icon(filename, shape_func, bg_color, shape_color):
    """Create a 24x24 PNG icon with a specified shape."""
    # Create a new 24x24 image with transparent background
    img = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw background
    draw.rectangle([0, 0, 23, 23], fill=bg_color)
    
    # Draw the shape
    shape_func(draw, shape_color)
    
    # Save the image
    img.save(filename, "PNG")

def draw_floppy(draw, color):
    """Draw a simple floppy disk shape for save icon."""
    draw.rectangle([6, 6, 17, 17], fill=color)  # Disk body
    draw.rectangle([8, 8, 15, 10], fill=(0, 0, 0))  # Label

def draw_arrow_up(draw, color):
    """Draw an upward arrow for load icon."""
    draw.polygon([(12, 6), (17, 11), (12, 16), (7, 11)], fill=color)  # Arrow

def draw_gear(draw, color):
    """Draw a simple gear shape for process icon."""
    # Approximate gear with a circle and protrusions
    draw.ellipse([6, 6, 17, 17], outline=color, width=2)
    for i in range(0, 24, 6):
        draw.rectangle([11+i//6, 2, 12+i//6, 4], fill=color)  # Teeth (simplified)

def main():
    # Create icons directory if it doesn't exist
    if not os.path.exists("icons"):
        os.makedirs("icons")
    
    # Define colors
    bg_colors = {
        "save": (74, 144, 226),    # Blue #4A90E2
        "load": (46, 204, 113),    # Green #2ECC71
        "process": (149, 165, 166) # Gray #95A5A6
    }
    shape_color = (255, 255, 255)  # White
    
    # Create each icon
    create_icon("icons/save.png", draw_floppy, bg_colors["save"], shape_color)
    create_icon("icons/load.png", draw_arrow_up, bg_colors["load"], shape_color)
    create_icon("icons/process.png", draw_gear, bg_colors["process"], shape_color)
    
    print("Icons created successfully in the 'icons' folder.")

if __name__ == "__main__":
    main()