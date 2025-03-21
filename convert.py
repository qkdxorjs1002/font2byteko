from PIL import Image, ImageFont, ImageDraw
import numpy as np

# 사용할 폰트 및 크기 설정
font_paths = {
    10: "font/DOSGothic.ttf",
    16: "font/DOSGothic.ttf",
    24: "font/DOSGothic.ttf",
}


def generate_complete_bitmap(hangul_char, size):
    """
    완성형 한글 음절을 주어진 size의 비트맵 이미지에
    전체 영역(0, 0, size, size)에 중앙 정렬하여 렌더링한 후,
    OLED에 출력할 바이트 배열로 변환합니다.
    """
    font = ImageFont.truetype(font_paths[size], size)
    # 1비트 흰색 배경 이미지 생성
    img = Image.new("1", (size, size), 1)
    draw = ImageDraw.Draw(img)

    # 폰트에서 해당 음절의 바운딩 박스를 구함
    bbox = font.getbbox(hangul_char)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    # 음수 오프셋 보정
    base_x = -bbox[0]
    base_y = -bbox[1]

    # 전체 영역 (0,0,size,size) 내에서 중앙 정렬
    x_offset = base_x + (size - text_width) // 2
    y_offset = base_y + (size - text_height) // 2
    draw.text((x_offset, y_offset), hangul_char, font=font, fill=0)

    # 이미지를 1비트 numpy 배열로 변환
    bitmap = np.array(img, dtype=np.uint8)
    byte_array = []
    for row in bitmap:
        byte_value = 0
        for i, pixel in enumerate(row):
            if pixel == 0:  # 픽셀이 검정이면
                byte_value |= 1 << (7 - (i % 8))
            if i % 8 == 7:
                byte_array.append(byte_value)
                byte_value = 0
        if len(row) % 8 != 0:
            byte_array.append(byte_value)
    return byte_array


# 예제로 완성형 한글 음절 중 일부만 생성 (전체 범위는 U+AC00~U+D7A3)
# 주의: 전체 11,172자는 생성하기에는 많으므로, 여기서는 처음 100개 음절만 사용합니다.
hangul_chars = [chr(i) for i in range(0xAC00, 0xAC00 + 11172)]

# 크기별(10, 16, 24)로 각 음절의 비트맵 데이터를 생성
complete_bitmap_data = {size: {} for size in [10, 16, 24]}
for size in [10, 16, 24]:
    for char in hangul_chars:
        complete_bitmap_data[size][char] = generate_complete_bitmap(char, size)


def save_complete_bitmap_to_file(filename, size):
    with open(filename, "w", encoding="utf-8") as file:
        for char, data in complete_bitmap_data[size].items():
            hex_data = ", ".join(f"0x{byte:02X}" for byte in data)
            char_info = f"{char} (U+{ord(char):04X})"
            file.write(f"    {hex_data}, // {char_info}\n")


# 파일 저장 (크기별)
for size in [10, 16, 24]:
    save_complete_bitmap_to_file(f"hangul_complete_{size}x{size}.txt", size)
