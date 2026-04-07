"""
Image Processing Pipeline
Processes images through multiple stages: crop, resize, grayscale, and enhancements.
Uses Pillow, OpenCV, and scikit-image libraries.
"""

import os
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance
import cv2
import numpy as np
from skimage import exposure, filters
from skimage.util import img_as_ubyte


# Supported image extensions
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}


def get_image_files(directory: str) -> list[Path]:
    """Get all supported image files from the given directory."""
    dir_path = Path(directory)
    image_files = []
    for ext in SUPPORTED_EXTENSIONS:
        image_files.extend(dir_path.glob(f'*{ext}'))
        image_files.extend(dir_path.glob(f'*{ext.upper()}'))
    return sorted(set(image_files))


def ensure_directory(directory: str) -> Path:
    """Create directory if it doesn't exist."""
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def crop_center_square(image: Image.Image, size: int = 512) -> Image.Image:
    """Crop image to a square from the center."""
    width, height = image.size

    # Calculate the crop box
    min_dim = min(width, height)
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim

    # Crop to square first
    cropped = image.crop((left, top, right, bottom))

    # Resize to target size if needed
    if min_dim != size:
        cropped = cropped.resize((size, size), Image.Resampling.LANCZOS)

    return cropped


def resize_image(image: Image.Image, size: tuple[int, int] = (256, 256)) -> Image.Image:
    """Resize image to the specified size."""
    return image.resize(size, Image.Resampling.LANCZOS)


def convert_to_grayscale(image: Image.Image) -> Image.Image:
    """Convert image to grayscale."""
    return image.convert('L')


def apply_histogram_equalization(image: np.ndarray) -> np.ndarray:
    """Apply histogram equalization using OpenCV for enhanced contrast."""
    if len(image.shape) == 3:
        # Convert to grayscale if color
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return cv2.equalizeHist(image)


def apply_clahe(image: np.ndarray, clip_limit: float = 2.0, tile_size: int = 8) -> np.ndarray:
    """Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)."""
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
    return clahe.apply(image)


def apply_unsharp_mask(image: np.ndarray, radius: float = 1.0, amount: float = 1.5) -> np.ndarray:
    """Apply unsharp mask for sharpening using scikit-image."""
    # Apply unsharp mask
    sharpened = filters.unsharp_mask(image, radius=radius, amount=amount)
    return img_as_ubyte(sharpened)


def apply_gaussian_blur(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """Apply Gaussian blur using OpenCV."""
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)


def apply_edge_detection(image: np.ndarray) -> np.ndarray:
    """Apply Canny edge detection using OpenCV."""
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return cv2.Canny(image, 100, 200)


def apply_sobel_edge(image: np.ndarray) -> np.ndarray:
    """Apply Sobel edge detection."""
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.sqrt(sobelx**2 + sobely**2)
    return np.uint8(np.clip(magnitude, 0, 255))


def apply_laplacian_edge(image: np.ndarray) -> np.ndarray:
    """Apply Laplacian edge detection."""
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    laplacian = cv2.Laplacian(image, cv2.CV_64F)
    return np.uint8(np.clip(np.abs(laplacian), 0, 255))


def apply_emboss(image: Image.Image) -> Image.Image:
    """Apply emboss filter using Pillow."""
    return image.filter(ImageFilter.EMBOSS)


def adjust_brightness_contrast(image: np.ndarray, brightness: int = 30, contrast: float = 1.3) -> np.ndarray:
    """Adjust brightness and contrast using OpenCV."""
    return cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)


def pil_to_cv2(image: Image.Image) -> np.ndarray:
    """Convert PIL Image to OpenCV format (numpy array)."""
    return np.array(image)


def cv2_to_pil(image: np.ndarray) -> Image.Image:
    """Convert OpenCV format (numpy array) to PIL Image."""
    if len(image.shape) == 2:
        return Image.fromarray(image, mode='L')
    return Image.fromarray(image)


def process_pipeline(input_dir: str, output_base_dir: str):
    # Setup output directories
    cropped_dir = ensure_directory(os.path.join(output_base_dir, '01_cropped_512'))
    resized_dir = ensure_directory(os.path.join(output_base_dir, '02_resized_256'))
    grayscale_dir = ensure_directory(os.path.join(output_base_dir, '03_grayscale'))
    enhanced_dir = ensure_directory(os.path.join(output_base_dir, '03_grayscale', 'enhanced'))
    effects_dir = ensure_directory(os.path.join(output_base_dir, '04_effects'))

    # Get all image files
    image_files = get_image_files(input_dir)

    if not image_files:
        print(f"No supported image files found in '{input_dir}'")
        return

    print(f"Found {len(image_files)} image(s) to process")
    print(f"Output directory: {output_base_dir}")
    print("-" * 60)

    for img_path in image_files:
        filename = img_path.stem
        print(f"\nProcessing: {img_path.name}")

        try:
            # Load image with Pillow
            original = Image.open(img_path)

            # Convert to RGB if necessary (handles RGBA, palette modes, etc.)
            if original.mode not in ('RGB', 'L'):
                original = original.convert('RGB')

            cropped = crop_center_square(original, 512)
            cropped.save(cropped_dir / f"{filename}_cropped.png")

            resized = resize_image(cropped, (256, 256))
            resized.save(resized_dir / f"{filename}_resized.png")

            grayscale = convert_to_grayscale(resized)
            grayscale.save(grayscale_dir / f"{filename}_grayscale.png")

            gray_array = pil_to_cv2(grayscale)

            # Histogram equalization
            hist_eq = apply_histogram_equalization(gray_array)
            cv2.imwrite(str(enhanced_dir / f"{filename}_hist_eq.png"), hist_eq)

            # CLAHE
            clahe = apply_clahe(gray_array)
            cv2.imwrite(str(enhanced_dir / f"{filename}_clahe.png"), clahe)

            # Unsharp mask (sharpened)
            sharpened = apply_unsharp_mask(gray_array, radius=2.0, amount=1.5)
            cv2.imwrite(str(enhanced_dir / f"{filename}_sharpened.png"), sharpened)

            # Combined: CLAHE + Unsharp mask
            clahe_sharp = apply_unsharp_mask(clahe, radius=1.5, amount=1.2)
            cv2.imwrite(str(enhanced_dir / f"{filename}_clahe_sharp.png"), clahe_sharp)

            # Gaussian blur
            blurred = apply_gaussian_blur(gray_array, kernel_size=7)
            cv2.imwrite(str(effects_dir / f"{filename}_blur.png"), blurred)

            # Canny edge detection
            edges_canny = apply_edge_detection(gray_array)
            cv2.imwrite(str(effects_dir / f"{filename}_edges_canny.png"), edges_canny)

            print(f"  ✓ Completed: {filename}")

        except Exception as e:
            print(f"  ✗ Error processing {img_path.name}: {e}")

    print("Pipeline completed!")

def main():
    """Main entry point."""
    # Default paths (relative to script location)
    script_dir = Path(__file__).parent
    input_dir = script_dir / "images"
    output_dir = script_dir / "output"

    print("Image Processing Pipeline")

    # Run the pipeline
    process_pipeline(str(input_dir), str(output_dir))


if __name__ == "__main__":
    main()