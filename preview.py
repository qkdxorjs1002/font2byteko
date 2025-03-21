import numpy as np
import matplotlib.pyplot as plt


def parse_bitmap_line(line, width, height):
    """
    한 줄의 텍스트(예, 0x00, 0x00, ... // ᄀ (U+1100))에서
    16진수 바이트 배열을 추출하여 width×height 크기의 2D numpy 배열(픽셀 값 0 또는 1)로 변환합니다.
    여기서 1은 글자(원래 검정)이고, 0은 배경입니다.
    """
    hex_part = line.split("//")[0].strip()
    hex_values = [item.strip() for item in hex_part.split(",") if item.strip()]
    bytes_list = [int(item, 16) for item in hex_values]

    bytes_per_row = (width + 7) // 8
    rows = []
    for r in range(height):
        row_bytes = bytes_list[r * bytes_per_row : (r + 1) * bytes_per_row]
        row_bits = "".join(f"{b:08b}" for b in row_bytes)
        row_bits = row_bits[:width]
        row = [int(bit) for bit in row_bits]
        rows.append(row)
    return np.array(rows, dtype=np.uint8)


def load_component_bitmap_file(filename, width, height):
    """
    파일 내 각 줄의 데이터를 파싱하여 해당 구성요소(초성, 중성, 종성)를
    키(문자)와 2D numpy 배열(비트맵)로 구성한 딕셔너리를 반환합니다.
    """
    comp_dict = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip() and "//" in line:
                comment = line.split("//")[1].strip()
                tokens = comment.split()
                if tokens:
                    jamo = tokens[0]
                    bitmap = parse_bitmap_line(line, width, height)
                    comp_dict[jamo] = bitmap
    return comp_dict


def decompose_hangul(syllable):
    """
    완성형 한글 음절을 초성, 중성, 종성(종성 없으면 None)으로 분해합니다.
    Unicode 공식 분해 규칙을 따릅니다.
    """
    code = ord(syllable) - 0xAC00
    if code < 0 or code > 11171:
        return None
    choseong_index = code // (21 * 28)
    jungseong_index = (code % (21 * 28)) // 28
    jongseong_index = code % 28
    choseong = chr(0x1100 + choseong_index)
    jungseong = chr(0x1161 + jungseong_index)
    jongseong = None
    if jongseong_index != 0:
        jongseong = chr(0x11A7 + jongseong_index)  # 첫 종성: U+11A8
    return choseong, jungseong, jongseong


def shift_bitmap(bitmap, dx, dy):
    """
    bitmap을 (dx, dy) 만큼 평행이동(시프트)한 새로운 배열을 반환합니다.
    빈 영역은 0(배경)으로 채웁니다.
    """
    h, w = bitmap.shape
    new_img = np.zeros_like(bitmap)
    # X 방향
    if dx >= 0:
        src_x_start, dst_x_start = 0, dx
        src_x_end, dst_x_end = w - dx, w
    else:
        src_x_start, dst_x_start = -dx, 0
        src_x_end, dst_x_end = w, w + dx
    # Y 방향
    if dy >= 0:
        src_y_start, dst_y_start = 0, dy
        src_y_end, dst_y_end = h - dy, h
    else:
        src_y_start, dst_y_start = -dy, 0
        src_y_end, dst_y_end = h, h + dy

    new_img[dst_y_start:dst_y_end, dst_x_start:dst_x_end] = bitmap[
        src_y_start:src_y_end, src_x_start:src_x_end
    ]
    return new_img


def composite_syllable(syllable, width, height, comp_dicts):
    """
    한 음절을 분해한 후, 각 구성요소의 비트맵(값: 1=글자, 0=배경)을
    지정한 위치(offset)로 이동하여 np.maximum으로 오버레이하여 합성합니다.
    중성이 ㅚ(U+315A) 또는 ㅞ(U+315E)인 경우엔 초성은 choseong 대신 jungseong 폰트를 사용합니다.
    """
    decomp = decompose_hangul(syllable)
    if decomp is None:
        return np.zeros((height, width), dtype=np.uint8)
    cho, jung, jong = decomp

    initial_bmp = comp_dicts["choseong"].get(
        cho, np.zeros((height, width), dtype=np.uint8)
    )
    jung_bmp = comp_dicts["jungseong"].get(
        jung, np.zeros((height, width), dtype=np.uint8)
    )
    if jong is not None:
        jong_bmp = comp_dicts["jongseong"].get(
            jong, np.zeros((height, width), dtype=np.uint8)
        )
    else:
        jong_bmp = np.zeros((height, width), dtype=np.uint8)

    # --- 구성요소의 위치 오프셋 (픽셀 단위) ---
    # 아래 값들은 필요에 따라 미세 조정할 수 있습니다.
    offset_initial = (0, 0)  # 초성: 좌측 상단
    offset_jung = (width // 8, 0)  # 중성: 우측 상단 (대략)
    if any(jung is chr(item) for item in [0x1169, 0x1173, 0x116E]):
        offset_jung = (width // 4, 0)  # 중성: 우측 상단 (대략)
    offset_jong = (width // 4, height - height // 3)  # 종성: 하단 중앙

    shifted_initial = shift_bitmap(initial_bmp, offset_initial[0], offset_initial[1])
    shifted_jung = shift_bitmap(jung_bmp, offset_jung[0], offset_jung[1])
    shifted_jong = shift_bitmap(jong_bmp, offset_jong[0], offset_jong[1])

    composite = np.maximum(np.maximum(shifted_initial, shifted_jung), shifted_jong)
    return composite


def composite_string(text, width, height, comp_dicts):
    """
    입력 문자열의 각 음절에 대해 합성된 비트맵을 좌우로 이어붙여 하나의 이미지로 만듭니다.
    """
    syllable_bitmaps = []
    for ch in text:
        bmp = composite_syllable(ch, width, height, comp_dicts)
        syllable_bitmaps.append(bmp)
    composite_img = np.hstack(syllable_bitmaps)
    return composite_img


def main():
    # 사용할 폰트 비트맵 크기 (예: 24x24)
    width = 24
    height = 24
    # 각 구성요소 파일 경로 (이전에 생성한 파일)
    choseong_file = "hangul_24x24_choseong.txt"
    jungseong_file = "hangul_24x24_jungseong.txt"
    jongseong_file = "hangul_24x24_jongseong.txt"

    comp_dicts = {
        "choseong": load_component_bitmap_file(choseong_file, width, height),
        "jungseong": load_component_bitmap_file(jungseong_file, width, height),
        "jongseong": load_component_bitmap_file(jongseong_file, width, height),
    }

    # 합성할 문자열 (예시)
    text = "한글테스트"
    composite_img = composite_string(text, width, height, comp_dicts)
    # 현재 composite_img는 각 음절에서 글자 픽셀이 1, 배경이 0입니다.
    # 검정 글자(0), 흰색 배경(1)으로 보기 위해 반전합니다.
    display_img = 1 - composite_img

    plt.figure(figsize=(len(text) * 2, 3))
    plt.imshow(display_img, cmap="gray", vmin=0, vmax=1)
    plt.axis("off")
    plt.title("Composite Hangul: " + text)
    plt.show()


if __name__ == "__main__":
    main()
