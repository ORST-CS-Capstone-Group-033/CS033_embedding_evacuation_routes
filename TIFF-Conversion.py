import sys
import os
import rasterio
import cv2
import numpy as np

def remove_extension(filename):
    """Remove the file extension from the filename."""
    return os.path.splitext(filename)[0]

def normalize_image(img_data):
    """Normalize image data to 0-255 range for non-HDR images."""
    img_min = np.min(img_data)
    img_max = np.max(img_data)

    # Avoid division by zero
    if img_min == img_max:
        return np.zeros(img_data.shape, dtype=np.uint8)
    
    normalized_img = (img_data - img_min) / (img_max - img_min) * 255.0
    return normalized_img.astype(np.uint8)

def process_geotiff(input_filename, output_filename):
    """Process the GeoTIFF file to display metadata and save as an image."""
    try:
        with rasterio.open(input_filename) as src:
            # Get metadata
            metadata = src.meta
            print("Metadata:")
            print(f"Coordinate Reference System: {metadata['crs']}")
            print(f"Width: {metadata['width']}")
            print(f"Height: {metadata['height']}")
            print(f"Latitude and Longitude Info: {src.bounds}")
            print(f"Transform Info: {src.transform}")

            # Read the image data
            img_data = src.read()

            # Check if the data is more than one band
            if img_data.ndim > 2:
                img_data = img_data.transpose(1, 2, 0)  # Convert to HxWxC format
            
            # Normalize the image data
            normalized_img = normalize_image(img_data)

            # Save the image
            cv2.imwrite(output_filename, normalized_img)

            print(f"File saved as: {output_filename}")

    except Exception as e:
        print(f"Error processing file: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python TIFF-Conversion.py <input_filename> [<output_filename>]")
        sys.exit(1)
    
    input_filename = sys.argv[1]
    output_filename = sys.argv[2] if len(sys.argv) > 2 else remove_extension(input_filename) + '.jpg'

    process_geotiff(input_filename, output_filename)

    # change whats commented for testing purposes
    # process_geotiff("sample.tif", "sample.jpg")
