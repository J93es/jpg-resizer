import os
import sys
from PIL import Image, ExifTags,  ImageDraw, ImageFont

tmp_file_name = "tmp.jpg"

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
    tmp_path = os.path.join(tmp_dir, tmp_file_name)
    
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

def add_watermark(img, watermark_text):
    
    scale_factor = 0.1
    img = img.convert("RGBA")
    
   # 워터마크 레이어 생성
    watermark_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark_layer)
    
    # 폰트 설정
    try:
        font = ImageFont.truetype("./asset/NanumGothicExtraBold.ttf", 20)
    except IOError:
        font = ImageFont.load_default()
    
    # 텍스트 크기 계산
    text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (img.width - text_width) - 10
    y = (img.height - text_height) - 10

    # 워터마크 텍스트 추가
    draw.text((x, y), watermark_text, fill=(255, 255, 255, 128), font=font)

    # 원본 이미지와 병합
    watermarked_image = Image.alpha_composite(img, watermark_layer)

    # RGBA -> RGB 변환 후 반환
    return watermarked_image.convert("RGB")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python file.py <max_size_kb> <max-width-pixel> <max-height-pixel> <watermark_text(optional)>")
        print("Usage: make run kb={target image size per kb} max_width={max image width pixel} max_height={max image height pixel}")
        sys.exit(1)
        
    current_file_path = os.path.abspath(sys.argv[0])
    current_dir = os.path.dirname(current_file_path)

    input_dir = os.path.join(current_dir, "images")
    output_dir = os.path.join(current_dir, "resized_images")
    tmp_dir = os.path.join(current_dir, "tmp")
    
    max_size_kb = int(sys.argv[1])
    max_width_pixel = int(sys.argv[2])
    max_height_pixel = int(sys.argv[3])
    watermark_text = sys.argv[4] if len(sys.argv) >= 5 else ""
        
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
            img = add_watermark(img, watermark_text)
            final_quality = find_quality(img, tmp_dir, max_size_bytes)
            
            img.save(output_path, "JPEG", quality=final_quality)
            print(f"{filename} resized and saved with final quality {final_quality}")
           
    tmp_file_path = os.path.join(tmp_dir, tmp_file_name)
    os.remove(tmp_file_path)
    os.rmdir(tmp_dir)
