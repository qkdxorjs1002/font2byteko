from PIL import Image, ImageFont, ImageDraw
import os

# 사용할 폰트 및 크기 설정
font_paths = {
    10: "font/NotoSansMonoCJKkr-Regular.otf",
    16: "font/NotoSansMonoCJKkr-Regular.otf",
    24: "font/NotoSansMonoCJKkr-Regular.otf",
}


def generate_component_bitmap(component, size, mask_region=None):
    """
    단일 컴포넌트를 주어진 size의 1비트 비트맵 이미지에 중앙 정렬하여 그린다.
    만약 mask_region이 지정되면, 해당 영역(튜플: (x0, y0, x1, y1))을 하얀색(배경색)으로 채운다.
    """
    font = ImageFont.truetype(font_paths[size], size)
    # 1비트 흰색 배경 이미지 생성 (모드 "1": 0은 검정, 1은 흰색)
    img = Image.new("1", (size, size), 1)
    draw = ImageDraw.Draw(img)

    # 폰트의 바운딩 박스 계산 (x0, y0, x1, y1)
    bbox = font.getbbox(component)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 폰트의 음수 오프셋 보정 후 중앙 정렬 좌표 계산
    base_x = -bbox[0]
    base_y = -bbox[1]
    x_offset = base_x + (size - text_width) // 2
    y_offset = base_y + (size - text_height) // 2

    # 텍스트 렌더링 (검은색: fill=0)
    draw.text((x_offset, y_offset), component, font=font, fill=0)

    # 사용자가 지정한 영역 마스킹 (하얀색으로 채움)
    if mask_region:
        for mask in mask_region:
            draw.rectangle(mask, fill=1)

    return img


# ==========================================================
# 사용자 지정 유니코드 범위 설정
# 예: 0xAC00부터 0xAC2F 까지 (예시로 완성형 한글 일부)
# unicode_start = 0xAC00
# unicode_end = 0xAC2F
# unicode_list = [chr(i) for i in range(unicode_start, unicode_end + 1)]
unicode_list = [
    "악",
    "앆",
    "앇",
    "안",
    "앉",
    "않",
    "앋",
    "알",
    "앍",
    "앎",
    "앏",
    "앐",
    "앑",
    "앒",
    "암",
    "압",
    "앖",
    "앗",
    "았",
    "앙",
    "앚",
    "앛",
    "앜",
    "앝",
    "앞",
    "앟",

    # "웩",
    # "웪",
    # "웫",
    # "웬",
    # "웭",
    # "웮",
    # "웯",
    # "웰",
    # "웱",
    # "웲",
    # "웳",
    # "웴",
    # "웵",
    # "웶",
    # "웸",
    # "웹",
    # "웺",
    # "웻",
    # "웼",
    # "웽",
    # "웾",
    # "웿",
    # "윀",
    # "윁",
    # "윂",
    # "윃",
]
# ==========================================================
# 처리할 이미지 크기 목록
sizes = [10, 16, 24]

# 각 크기별로, 유니코드 범위의 문자에 대해 이미지를 생성
# 아래 예시에서는 크기별로 마스킹 영역을 지정할 수 있습니다.
# mask_region은 (x0, y0, x1, y1) 형태입니다.
# 예를 들어, 크기 16인 경우 상단 4픽셀을 마스킹하려면 (0, 0, 16, 4)로 지정합니다.
mask_region_for_size = {
    10: (
        (0, 0, 10, 4),
        # (5, 0, 10, 10),
    ),  # 크기 10은 마스킹 없이 렌더링
    16: (
        (0, 0, 16, 8),
        # (10, 0, 16, 16),
    ),  # 크기 16은 상단 4픽셀 영역을 하얀색으로 마스킹
    24: (
        (0, 0, 24, 11),
        # (15, 0, 24, 24),
    ),  # 크기 24는 마스킹 없이 렌더링 (원하는 경우 변경 가능)
}

component_bitmap_data = {size: {} for size in sizes}
for size in sizes:
    mask = mask_region_for_size.get(size)  # 해당 크기에 맞는 마스킹 영역 (없으면 None)
    component_bitmap_data[size] = {
        char: generate_component_bitmap(char, size, mask_region=mask)
        for char in unicode_list
    }


def save_component_bitmap_image(size, output_dir):
    """
    component_bitmap_data에 저장된 PIL 이미지 객체를 BMP 파일로 저장한다.
    파일명 형식: unicode_{size}x{size}_{유니코드코드값}.bmp
    """
    os.makedirs(output_dir, exist_ok=True)
    for char, image in component_bitmap_data[size].items():
        filename = f"unicode_{size}x{size}_{char}.bmp"
        filepath = os.path.join(output_dir, filename)
        image.save(filepath, format="BMP")


# ==========================================================
# BMP 이미지 저장 경로 설정 (원하는 폴더로 변경 가능)
output_directory = "bmp_output"

# 각 크기별 BMP 파일 저장
for size in sizes:
    save_component_bitmap_image(size, output_directory)
