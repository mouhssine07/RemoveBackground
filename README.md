# Background Remover

Remove image backgrounds using AI (rembg / U2Net) with no quality loss. Output is saved as PNG with full transparency.

## Installation

```bash
pip install rembg pillow onnxruntime
```

**GPU acceleration (optional):**

```bash
pip install onnxruntime-gpu  # instead of onnxruntime
```

## Usage

### Single image

```bash
python remove_background.py --input photo.jpg --output out.png --model silueta
```

The output file will be named `photo_noBg.png` (based on the input file name).

### Batch (entire folder)

```bash
python remove_background.py --input ./my_images --output ./results --model silueta
```

Each output file will keep its original name with `_noBg` appended, e.g. `image1_noBg.png`.

### Available models

| Model               | Description                             |
| ------------------- | --------------------------------------- |
| `u2net`             | General purpose (default, best quality) |
| `u2netp`            | Lightweight, faster                     |
| `u2net_human_seg`   | Optimized for people / portraits        |
| `isnet-general-use` | Alternative high-quality general model  |
| `silueta`           | Optimized for humans, smaller model     |

## Supported formats

JPG, JPEG, PNG, WEBP, BMP, TIFF
