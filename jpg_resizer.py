import os
import sys
from PIL import Image, ExifTags, ImageDraw, ImageFont
from fractions import Fraction

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

def get_metadata_str(img):
    """
    이미지의 EXIF 메타데이터에서 카메라 바디, 렌즈, 조리개, 셔터스피드, ISO 정보를 추출하여
    포맷팅된 문자열로 반환합니다.
    """
    metadata_str = ""
    if not hasattr(img, '_getexif'):
        return metadata_str
    exif_data = img._getexif()
    if not exif_data:
        return metadata_str
    
    # 태그 id와 이름을 매핑하여 새로운 dict 구성
    exif = {}
    for tag_id, value in exif_data.items():
        tag = ExifTags.TAGS.get(tag_id, tag_id)
        exif[tag] = value
    
    # 카메라 바디: Model (존재할 경우)
    camera_body = lens = exif.get("Model", "")
    
    # 카메라 렌즈: LensModel (존재할 경우)
    lens = exif.get("LensModel", "")
    
    # 초점 거리: FocalLength
    focal = exif.get("FocalLength", None)
    focal_val = None
    if focal is not None:
        if isinstance(focal, tuple) and focal[1] != 0:
            focal_val = round(focal[0] / focal[1], 1)
        else:
            focal_val = float(focal)
    
    # 조리개: FNumber
    aperture = exif.get("FNumber", None)
    if aperture is not None:
        if isinstance(aperture, tuple) and aperture[1] != 0:
            aperture = round(aperture[0] / aperture[1], 1)
        else:
            aperture = float(aperture)
    
    # 셔터스피드: ExposureTime
    shutter = exif.get("ExposureTime", None)
    if shutter is not None:
        try:
            # tuple 형태이면 그대로 Fraction으로 변환, 아니면 float로 변환 후 Fraction 적용
            if isinstance(shutter, tuple) and shutter[1] != 0:
                shutter_fraction = Fraction(shutter[0], shutter[1])
            else:
                shutter_fraction = Fraction(shutter).limit_denominator(100000)
            shutter = f"{shutter_fraction.numerator}/{shutter_fraction.denominator}sec"
        except Exception:
            try:
                shutter_float = float(shutter)
                shutter = f"{shutter_float:.5f}sec"
            except Exception:
                shutter = f"{shutter}"[:7] if len(f"{shutter}") > 7 else f"{shutter}" + "sec"
    
    # ISO: ISOSpeedRatings
    iso = exif.get("ISOSpeedRatings", "")
    if isinstance(iso, tuple):
        iso = iso[0]
    
    meta_lines = []
    
    if camera_body:
        meta_lines.append(f"{camera_body}")
    if lens:
        meta_lines.append(f"{lens}")
        
    exposure_values = []
    if focal_val is not None:
        exposure_values.append(f"{focal_val}mm")
    if aperture is not None:
        exposure_values.append(f"f/{aperture}")
    if shutter is not None:
        exposure_values.append(f"{shutter}")
    if iso:
        exposure_values.append(f"ISO{iso}")
    if exposure_values:
        exposure_str = "  ".join(exposure_values)
        meta_lines.append(exposure_str)
    
    metadata_str = "\n".join(meta_lines)
    
    return metadata_str

def wrap_text(text, font, max_width, draw):
    """
    주어진 폰트와 draw 객체를 사용하여, 텍스트가 max_width(픽셀)를 넘지 않도록 
    단어 단위로 개행하여 리스트(각 항목이 한 줄)를 반환합니다.
    """
    lines = []
    # 기존 개행(\n) 기준으로 단락 나누기
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        if not words:
            lines.append("")
            continue
        current_line = words[0]
        for word in words[1:]:
            test_line = current_line + " " + word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            test_width = bbox[2] - bbox[0]
            if test_width > max_width - 20:  # 여유 마진 고려 (양쪽 10픽셀)
                lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        lines.append(current_line)
    return lines

def add_watermark(img, watermark_text, meta_str):
    """
    전달된 watermark_text와 이미지의 EXIF 메타데이터를 합쳐 워터마크 텍스트를 만들고,
    이미지의 우측 하단에 배경 밝기에 따라 대비가 있는 반투명 텍스트로 추가합니다.
    텍스트가 이미지 폭을 초과하면 자동 개행합니다.
    """
    # 사용자 지정 워터마크와 메타데이터를 결합 (둘 다 존재하면 개행 처리)
    if watermark_text and meta_str:
        final_text = meta_str + "\n" + watermark_text
    elif watermark_text:
        final_text = watermark_text
    elif meta_str:
        final_text = meta_str
    else:
        # 추가할 워터마크 텍스트가 없으면 그대로 반환
        return img

    # RGBA 모드로 변환 (투명도 적용을 위해)
    img = img.convert("RGBA")
    
    # 워터마크 레이어 생성
    watermark_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark_layer)
    
    # 폰트 설정 (한글 폰트가 필요하면 해당 폰트를 지정)
    try:
        font = ImageFont.truetype("./asset/NanumGothicExtraBold.ttf", 20)
    except IOError:
        font = ImageFont.load_default()
    
    # 텍스트의 최대 폭 (여백 고려)
    available_width = img.width - 20  # 양쪽 10픽셀 여백
    lines = wrap_text(final_text, font, available_width, draw)
    
    # 각 줄의 폭과 높이를 측정하여 텍스트 블록의 전체 크기 계산
    line_widths = []
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]
        line_widths.append(line_width)
        line_heights.append(line_height)
    
    block_width = max(line_widths) if line_widths else 0
    spacing = 4  # 줄 간격 (픽셀)
    block_height = sum(line_heights) + spacing * (len(lines) - 1)
    
    # 텍스트 블록을 이미지의 우측 하단 (여백 10픽셀) 위치에 배치
    x = img.width - block_width - 10
    y = img.height - block_height - 10

    # 워터마크가 들어갈 영역의 평균 밝기 계산
    region = img.crop((x, y, x + block_width, y + block_height))
    region_gray = region.convert("L")
    avg_brightness = sum(region_gray.getdata()) / (block_width * block_height)
    
    # 배경 밝기에 따라 워터마크 텍스트 색상 결정 (밝으면 어두운색, 어두우면 밝은색)
    if avg_brightness > 128:
        watermark_color = (0, 0, 0, 128)  # 어두운 색 (배경이 밝을 때)
    else:
        watermark_color = (255, 255, 255, 160)  # 밝은 색 (배경이 어두울 때)
    
    # 각 줄을 순차적으로 그리기
     # 각 줄을 순차적으로 그리기 (오른쪽 정렬)
    current_y = y
    for i, line in enumerate(lines):
        # 각 줄의 폭 측정
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        # 오른쪽 정렬: 각 줄의 x 좌표는 이미지의 오른쪽 여백 10픽셀을 고려하여 계산
        line_x = img.width - line_width - 10
        draw.text((line_x, current_y), line, fill=watermark_color, font=font)
        current_y += line_heights[i] + spacing

    # 워터마크 레이어와 원본 이미지 합성
    watermarked_image = Image.alpha_composite(img, watermark_layer)
    
    # RGB 모드로 변환 후 반환
    return watermarked_image.convert("RGB")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: make run {target image size (kb)} {max image width(pixel)} {max image height(pixel)} {true | false(optional: default=false)} {watermark text(optional: default='')}")
        sys.exit(1)
        
    current_file_path = os.path.abspath(sys.argv[0])
    current_dir = os.path.dirname(current_file_path)

    input_dir = os.path.join(current_dir, "images")
    output_dir = os.path.join(current_dir, "resized_images")
    tmp_dir = os.path.join(current_dir, "tmp")
    
    max_size_kb = int(sys.argv[1])
    max_width_pixel = int(sys.argv[2])
    max_height_pixel = int(sys.argv[3])
    use_meta_watermark = sys.argv[4] if len(sys.argv) >= 5 else ""
    if use_meta_watermark.lower() == "true":
        use_meta_watermark = True
    else:
        use_meta_watermark = False
    watermark_text = sys.argv[5] if len(sys.argv) >= 6 else None
        
    max_size_bytes = max_size_kb * 1024
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith((".jpg", ".jpeg")):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            img = Image.open(input_path)
            if use_meta_watermark:
                meta_str = get_metadata_str(img)
            else:
                meta_str = None
            img = rotate_image(img)
            img = resize_pixel(img, max_width_pixel, max_height_pixel)
            img = add_watermark(img, watermark_text, meta_str)
            final_quality = find_quality(img, tmp_dir, max_size_bytes)
            
            img.save(output_path, "JPEG", quality=final_quality)
            print(f"{filename} resized and saved with final quality {final_quality}")
           
    tmp_file_path = os.path.join(tmp_dir, tmp_file_name)
    if os.path.exists(tmp_file_path):
        os.remove(tmp_file_path)
    if os.path.exists(tmp_dir):
        os.rmdir(tmp_dir)

