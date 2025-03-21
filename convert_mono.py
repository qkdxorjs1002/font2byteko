from PIL import Image, ImageFont, ImageDraw
import numpy as np

# 사용할 폰트 및 크기 설정
font_paths = {
    10: "font/NotoSansMonoCJKkr-Regular.otf",
    16: "font/NotoSansMonoCJKkr-Regular.otf",
    24: "font/NotoSansMonoCJKkr-Regular.otf",
}


def generate_component_bitmap(component, size, component_type):
    """
    단일 컴포넌트(초성, 중성, 종성)를 주어진 size의 비트맵 이미지에
    전체 영역(0, 0, size, size)에 중앙 정렬하여 그립니다.
    """
    font = ImageFont.truetype(font_paths[size], size)
    # 1비트 흰색 배경 이미지 생성
    img = Image.new("1", (size, size), 1)
    draw = ImageDraw.Draw(img)

    # 텍스트의 바운딩 박스 (x0, y0, x1, y1)와 실제 텍스트 크기 계산
    bbox = font.getbbox(component)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 전체 이미지 영역을 사용하여 중앙 정렬
    box = (0, 0, size, size)
    box_width = box[2] - box[0]
    box_height = box[3] - box[1]

    # 폰트의 음수 오프셋 보정
    base_x = -bbox[0]
    base_y = -bbox[1]

    # 전체 영역 내 중앙 정렬
    x_offset = base_x + box[0] + (box_width - text_width) // 2
    y_offset = base_y + box[1] + (box_height - text_height) // 2

    draw.text((x_offset, y_offset), component, font=font, fill=0)

    # 생성된 이미지의 1비트 배열을 numpy 배열로 변환 후 바이트 배열로 전환
    bitmap = np.array(img, dtype=np.uint8)
    byte_array = []
    for row in bitmap:
        byte_value = 0
        for i, pixel in enumerate(row):
            if pixel == 0:
                byte_value |= 1 << (7 - (i % 8))
            if i % 8 == 7:
                byte_array.append(byte_value)
                byte_value = 0
        if len(row) % 8 != 0:
            byte_array.append(byte_value)
    return byte_array


# 각 컴포넌트의 코드 범위 (완성형 제외)
choseong_list = [chr(i) for i in range(0x1100, 0x1113)]
jungseong_list = [chr(i) for i in range(0x1161, 0x1176)]
jongseong_list = [chr(i) for i in range(0x11A8, 0x11C3)]

sizes = [10, 16, 24]
# 각 크기별로 초성, 중성, 종성 비트맵을 생성
component_bitmap_data = {size: {} for size in sizes}
for size in sizes:
    component_bitmap_data[size]["choseong"] = {
        c: generate_component_bitmap(c, size, "choseong") for c in choseong_list
    }
    component_bitmap_data[size]["jungseong"] = {
        c: generate_component_bitmap(c, size, "jungseong") for c in jungseong_list
    }
    component_bitmap_data[size]["jongseong"] = {
        c: generate_component_bitmap(c, size, "jongseong") for c in jongseong_list
    }


def save_component_bitmap_to_file(filename, size, component_type):
    with open(filename, "w", encoding="utf-8") as file:
        for char, data in component_bitmap_data[size][component_type].items():
            hex_data = ", ".join(f"0x{byte:02X}" for byte in data)
            file.write(f"    {hex_data}, // {char} (U+{ord(char):04X})\n")


# 파일 저장 (크기별, 컴포넌트별)
for size in sizes:
    save_component_bitmap_to_file(
        f"hangul_{size}x{size}_choseong.txt", size, "choseong"
    )
    save_component_bitmap_to_file(
        f"hangul_{size}x{size}_jungseong.txt", size, "jungseong"
    )
    save_component_bitmap_to_file(
        f"hangul_{size}x{size}_jongseong.txt", size, "jongseong"
    )
