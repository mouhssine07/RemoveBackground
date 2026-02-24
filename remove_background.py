"""
Background Remover - High Quality
Uses rembg (U2Net AI model) to remove backgrounds without quality loss.
Output is saved as PNG with full transparency and no compression artifacts.

Install dependencies:
    pip install rembg pillow onnxruntime

Usage:
    python remove_background.py --input image.jpg --output output.png
    python remove_background.py --input ./images_folder --output ./output_folder
"""

import argparse
import os
from pathlib import Path
from PIL import Image
from rembg import remove, new_session


SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}


def remove_background(input_path: Path, output_path: Path, session, bg_color: str = None) -> None:
    """Remove background from a single image and save as high-quality PNG."""
    print(f"Processing: {input_path.name}")

    # Open image and convert to RGBA to preserve any existing transparency
    with Image.open(input_path) as img:
        img = img.convert("RGBA")

        # Remove background — rembg works on PIL Images directly
        result: Image.Image = remove(img, session=session)

        # Optionally composite onto a solid color background
        if bg_color:
            bg = Image.new("RGBA", result.size, bg_color)
            bg.paste(result, mask=result.split()[3])
            result = bg.convert("RGB")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save as PNG (lossless) with maximum quality — no quality loss
        result.save(output_path, format="PNG", compress_level=1)
        print(f"  ✅ Saved: {output_path}")


def process_path(input_path: str, output_path: str, model: str = "u2net", bg_color: str = None) -> None:
    """
    Process a single image file or an entire folder of images.

    Models available:
        u2net         - General purpose (default, best quality)
        u2netp        - Lightweight, faster but slightly lower quality
        u2net_human_seg - Optimized for people/portraits
        isnet-general-use - Alternative high-quality general model
        silueta       - Optimized for humans, smaller model
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    print(f"Loading model: {model} (first run downloads the model ~170MB) ...")
    session = new_session(model)

    if input_path.is_file():
        # Single image
        if input_path.suffix.lower() not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {input_path.suffix}")
        # Always name the output after the input file with _noBg suffix
        out_name = input_path.stem + "_noBg.png"
        if output_path.suffix:
            # --output points to a file → use its parent directory
            out_file = output_path.parent / out_name
        else:
            # --output points to a directory
            out_file = output_path / out_name
        remove_background(input_path, out_file, session, bg_color)

    elif input_path.is_dir():
        # Batch process all images in the folder
        images = [f for f in input_path.iterdir() if f.suffix.lower() in SUPPORTED_FORMATS]
        if not images:
            print("No supported images found in the folder.")
            return
        print(f"Found {len(images)} image(s) to process...\n")
        output_path.mkdir(parents=True, exist_ok=True)
        for img_file in images:
            out_file = output_path / (img_file.stem + "_noBg.png")
            remove_background(img_file, out_file, session, bg_color)
        print(f"\n✅ Done! Processed {len(images)} image(s).")
    else:
        raise FileNotFoundError(f"Input path not found: {input_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove image background with no quality loss.")
    parser.add_argument("--input",  "-i", required=True, help="Input image file or folder")
    parser.add_argument("--output", "-o", required=True, help="Output image file or folder")
    parser.add_argument(
        "--model", "-m",
        default="u2net",
        choices=["u2net", "u2netp", "u2net_human_seg", "isnet-general-use", "silueta"],
        help="AI model to use (default: u2net)"
    )
    parser.add_argument(
        "--bg-color", "-bg",
        default=None,
        help="Background color hex code, e.g. #FF0000 for red. Omit for transparent."
    )
    args = parser.parse_args()
    process_path(args.input, args.output, args.model, args.bg_color)