from pathlib import Path
from typing import List, Tuple
from PIL import Image
import shutil
import sys
from icnsutil import IcnsFile  # Ensure icnsutil is installed

# Configuration
DEFAULT_SOURCE = "icon.png"
OUTPUT_DIR = Path("src-tauri/icons")
ICON_SIZES = {
    "linux": [
        (32, 32, "32x32.png"),
        (128, 128, "128x128.png"),
        (256, 256, "128x128@2x.png"),
        (256, 256, "256x256.png"),
        (512, 512, "512x512.png"),
    ],
    "windows": [
        (16, 16),
        (32, 32),
        (48, 48),
        (64, 64),
        (256, 256),
    ],
    "macos": [
        ("icon_16x16.png", 16),
        ("icon_16x16@2x.png", 32),
        ("icon_32x32.png", 32),
        ("icon_32x32@2x.png", 64),
        ("icon_128x128.png", 128),
        ("icon_128x128@2x.png", 256),
        ("icon_256x256.png", 256),
        ("icon_256x256@2x.png", 512),
        ("icon_512x512.png", 512),
        ("icon_512x512@2x.png", 1024),
    ]
}

def validate_image(image: Image.Image) -> Image.Image:
    """Validates and adjusts image dimensions"""
    if image.size != (1024, 1024):
        print("Warning: Image is not 1024x1024. Auto-resizing...")
        return image.resize((1024, 1024), Image.Resampling.LANCZOS)
    return image

def generate_linux_icons(image: Image.Image, output_dir: Path) -> None:
    """Generates icons for Linux"""
    for width, height, filename in ICON_SIZES["linux"]:
        resized = image.resize((width, height), Image.Resampling.LANCZOS)
        resized.save(output_dir / filename, optimize=True)

def generate_windows_icon(image: Image.Image, output_dir: Path) -> None:
    """Generates .ico file for Windows"""
    ico_images = [image.resize(size, Image.Resampling.LANCZOS) for size in ICON_SIZES["windows"]]
    ico_images[0].save(
        output_dir / "icon.ico",
        append_images=ico_images[1:],
        format="ICO",
        optimize=True
    )

def generate_macos_icon(image: Image.Image, output_dir: Path) -> None:
    iconset_dir = output_dir / "icon.iconset"
    iconset_dir.mkdir(exist_ok=True)

    try:
        # Generate .iconset files
        for filename, size in ICON_SIZES["macos"]:
            img = image.resize((size, size), Image.Resampling.LANCZOS)
            img.save(iconset_dir / filename, optimize=True)

        # Build .icns using icnsutil
        icns = IcnsFile()
        for file in iconset_dir.glob("*.png"):
            icns.add_media(file=str(file))  # Explicit file= parameter
        icns.write(output_dir / "icon.icns")
        
    except Exception as e:
        print(f"Error generating .icns: {str(e)}")
        raise
    finally:
        shutil.rmtree(iconset_dir, ignore_errors=True)

def generate_icons(source_path: str = DEFAULT_SOURCE) -> None:
    """Main icon generation function"""
    try:
        # Initialization and checks
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source}")

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Image processing
        with Image.open(source) as img:
            image = validate_image(img.convert("RGBA"))
            
            # Generate icons
            generate_linux_icons(image, OUTPUT_DIR)
            generate_windows_icon(image, OUTPUT_DIR)
            generate_macos_icon(image, OUTPUT_DIR)

        print("✓ All icons generated successfully!")

    except Exception as e:
        sys.exit(f"✗ Error: {str(e)}")

if __name__ == "__main__":
    generate_icons()
