import matplotlib.pyplot as plt
import numpy as np


def parse_bitmap_line(line, width, height):
    """
    한 줄의 텍스트(예, 0x00, 0x00, ... // ᄀ (U+1100))에서
    16진수 바이트 배열을 추출하여 width×height 크기의 2D numpy 배열(픽셀 값 0 또는 1)로 변환합니다.
    """
    # '//'를 기준으로 앞부분(바이트 데이터)만 사용
    hex_part = line.split("//")[0].strip()
    # 쉼표로 분리하여 각 항목을 정리
    hex_values = [item.strip() for item in hex_part.split(",") if item.strip()]
    # 16진수 문자열을 정수로 변환
    bytes_list = [int(item, 16) for item in hex_values]

    # 한 행에 몇 바이트가 사용되었는지 (width 픽셀, 8픽셀=1바이트)
    bytes_per_row = (width + 7) // 8
    rows = []
    for r in range(height):
        # r번째 행에 해당하는 바이트들 추출
        row_bytes = bytes_list[r * bytes_per_row : (r + 1) * bytes_per_row]
        # 각 바이트를 8자리 이진수 문자열로 변환하여 이어 붙임
        row_bits = "".join(f"{b:08b}" for b in row_bytes)
        # width만큼의 비트만 사용 (뒷부분은 패딩일 수 있음)
        row_bits = row_bits[:width]
        row = [int(bit) for bit in row_bits]
        rows.append(row)
    return np.array(rows, dtype=np.uint8)


# 검증할 파일 경로와 이미지 크기 지정
filename = "hangul_16x16_jungseong.txt"
img_width = 16
img_height = 16

# 파일 읽기: 각 줄은 하나의 문자에 해당하는 데이터입니다.
with open(filename, "r", encoding="utf-8") as f:
    lines = [line for line in f if line.strip()]

# 전체 문자를 그릴 그리드 설정 (예: 5열)
n_chars = len(lines)
cols = 5
rows_grid = (n_chars + cols - 1) // cols

fig, axs = plt.subplots(rows_grid, cols, figsize=(cols * 2, rows_grid * 2))
# axs가 2D 배열일 경우 flatten, 단일 플롯이면 리스트로 만듦
if rows_grid * cols > 1:
    axs = axs.flatten()
else:
    axs = [axs]

for i, line in enumerate(lines):
    # 파일 내 한 줄을 파싱하여 10×10 numpy 배열로 복원
    bitmap = parse_bitmap_line(line, img_width, img_height)
    axs[i].imshow(bitmap, cmap="gray", vmin=0, vmax=1)
    axs[i].axis("off")
    # 주석 부분에서 문자 정보(예: ᄀ (U+1100)) 추출하여 타이틀로 표시
    if "//" in line:
        info = line.split("//")[1].strip()
        axs[i].set_title(info, fontsize=6)
# 남은 서브플롯은 숨김
for j in range(i + 1, len(axs)):
    axs[j].axis("off")

plt.tight_layout()
plt.show()
