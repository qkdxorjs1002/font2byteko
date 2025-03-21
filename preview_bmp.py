import os
import random
from PIL import Image, ImageChops
import matplotlib.pyplot as plt

# 각 폴더 경로 설정
chosung_dir = "bmp_output_chosung"
jungsung_dir = "bmp_output_jungsung"
jongsung_dir = "bmp_output_jongsung"


def get_bmp_files(directory):
    """지정한 디렉토리 내 BMP 파일 경로 목록을 반환합니다."""
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.lower().endswith(".bmp")
    ]


def filter_files_by_char(files, size, allowed_chars):
    """
    파일명에서 마지막 '_' 이후의 문자(확장자 제외)를 추출하여,
    allowed_chars 목록에 포함된 파일만 반환합니다.
    예) 파일명이 "unicode_10x10_가.bmp"인 경우, '가'를 추출하여 비교합니다.
    """
    filtered = []
    for f in files:
        base = os.path.basename(f)
        parts = base.split("_")
        if len(parts) >= 3 and parts[1] == f"{size}x{size}":
            char_with_ext = parts[-1]
            char = os.path.splitext(char_with_ext)[0]
            if char in allowed_chars:
                filtered.append(f)
    return filtered


# ===== 사용자가 지정할 문자 목록 =====
# 예시: 각 폴더에서 사용할 문자 목록을 원하는 대로 수정하세요.
size = 24
chosung_chars = ["궤", "눼", "뒈", "뤠", "뭬", "붸", "쉐", "웨", "줴", "췌", "퀘", "퉤", "풰", "훼"]  # 초성 폴더에서 사용할 문자 필터
jungsung_chars = ["웰", "앨", ]  # 중성 폴더에서 사용할 문자 필터
jongsung_chars = ["앍","앑","악","압","앛","앟","앉","알"]  # 종성 폴더에서 사용할 문자 필터

# 폴더별 전체 BMP 파일 목록을 가져온 후, 필터링 적용
chosung_files_all = get_bmp_files(chosung_dir)
jungsung_files_all = get_bmp_files(jungsung_dir)
jongsung_files_all = get_bmp_files(jongsung_dir)

chosung_files = filter_files_by_char(chosung_files_all, size, chosung_chars)
jungsung_files = filter_files_by_char(jungsung_files_all, size, jungsung_chars)
jongsung_files = filter_files_by_char(jongsung_files_all, size, jongsung_chars)


def merge_random_components():
    """
    각 폴더에서 미리 지정된 파일 목록을 대상으로 무작위로 BMP 파일을 선택하여,
    초성, 중성, 종성 이미지를 Z축(겹침)으로 병합한 최종 이미지를 반환합니다.
    각 픽셀은 세 이미지 중 가장 어두운(검정에 가까운) 값으로 결정됩니다.
    """
    if len(chosung_files) is not 0:
        chosung_file = random.choice(chosung_files)
        chosung_img = Image.open(chosung_file).convert("L")
        merged_img = chosung_img
    if len(jungsung_files) is not 0:
        jungsung_file = random.choice(jungsung_files)
        jungsung_img = Image.open(jungsung_file).convert("L")
        merged_img = ImageChops.darker(merged_img, jungsung_img)
    if len(jongsung_files) is not 0:
        jongsung_file = random.choice(jongsung_files)
        jongsung_img = Image.open(jongsung_file).convert("L")
        merged_img = ImageChops.darker(merged_img, jongsung_img)

    return merged_img


# 총 30개의 병합 이미지를 생성
n_images = 60
merged_images = [merge_random_components() for _ in range(n_images)]

# 그리드 설정: 6행 x 5열 (6*5 = 30)
cols = 10
rows_grid = (n_images + cols - 1) // cols

fig, axs = plt.subplots(rows_grid, cols, figsize=(cols * 2, rows_grid * 2))
# axs가 다차원 배열이면 flatten
axs = axs.flatten() if hasattr(axs, "flatten") else [axs]

for i, merged_img in enumerate(merged_images):
    axs[i].imshow(merged_img, cmap="gray", vmin=0, vmax=255)
    axs[i].axis("off")
    axs[i].set_title(f"Merge {i+1}", fontsize=8)

# 남은 서브플롯 숨김
for j in range(i + 1, len(axs)):
    axs[j].axis("off")

plt.tight_layout()
plt.show()
