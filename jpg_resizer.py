import os
import sys
from PIL import Image, ExifTags

def rotate_image(img):
    if hasattr(img, '_getexif'):
        exif = img._getexif()
        if exif:
            orientation_key = next(
                (k for k, v in ExifTags.TAGS.items() if v == 'Orientation'), None)
            if orientation_key and orientation_key in exif:
                orientation = exif[orientation_key]

                if orientation == 3:
                    return img.rotate(180, expand=True)
                elif orientation == 6:
                    return img.rotate(270, expand=True)
                elif orientation == 8:
                    return img.rotate(90, expand=True)
    return img

def resize_pixel(img, max_width_pixel, max_height_pixel):
    img_width, img_height = img.size
    if img_width <= max_width_pixel and img_height <= max_height_pixel:
        return img
    
    width_ratio = max_width_pixel / img_width
    height_ratio = max_height_pixel / img_height
    
    if width_ratio < height_ratio:
        return img.resize((max_width_pixel, int(img_height * width_ratio)))
    
    return img.resize((int(img_width * height_ratio), max_height_pixel))

def find_quality(img, tmp_dir, max_size_bytes):
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, "tmp.jpg")
    
    low, high = 70, 100
    final_quality = high

    while low <= high:
        mid_quality = (low + high) // 2
        final_quality = mid_quality
        
        img.save(tmp_path, "JPEG", quality=mid_quality)
        output_size = os.path.getsize(tmp_path)

        if output_size <= max_size_bytes:
            low = mid_quality + 1
        else:
            high = mid_quality - 1
            
    return final_quality
    
def resize_and_save_images(input_dir, output_dir, tmp_dir, max_size_kb, max_width_pixel, max_height_pixel):
    max_size_bytes = max_size_kb * 1024
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith((".jpg", ".jpeg")):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            img = Image.open(input_path)
            img = rotate_image(img)
            img = resize_pixel(img, max_width_pixel, max_height_pixel)
            final_quality = find_quality(img, tmp_dir, max_size_bytes)

            img.save(output_path, "JPEG", quality=final_quality)
            print(f"{filename} resized and saved with final quality {final_quality}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python file.py <max_size_kb> <max-width-pixel> <max-height-pixel>")
        sys.exit(1)
        
    current_file_path = os.path.abspath(sys.argv[0])
    current_directory = os.path.dirname(current_file_path)

    input_directory = os.path.join(current_directory, "images")
    output_directory = os.path.join(current_directory, "resized_images")
    tmp_directory = os.path.join(current_directory, "tmp")
    
    max_size_kb = int(sys.argv[1])
    max_width_pixel = int(sys.argv[2])
    max_height_pixel = int(sys.argv[3])
        
    resize_and_save_images(input_directory, output_directory, tmp_directory, max_size_kb, max_width_pixel, max_height_pixel)
