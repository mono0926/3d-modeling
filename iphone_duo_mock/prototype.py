"""
iPhone Duo モックモデルのプロトタイプ検証スクリプト
"""
import os
from build123d import *

# ============================================================
# 寸法定数 (mm)
# ============================================================
OVERALL_WIDTH_OPEN = 164.6
OVERALL_HEIGHT = 117.8
BODY_THICKNESS = 5.2

OVERALL_WIDTH_CLOSED = 84.1
OVERALL_THICKNESS_CLOSED = 11.3

# 半身の寸法
HALF_WIDTH = OVERALL_WIDTH_OPEN / 2.0  # 82.3 mm
CORNER_RADIUS_OUTER = 11.0             # 外側コーナーR (iPhoneの丸み)
CORNER_RADIUS_INNER = 1.0              # ヒンジ側コーナーR

# ヒンジ設計
PIN_DIAMETER = 2.0                     # 1.75mm フィラメント用ピン穴径
HINGE_RADIUS = 2.0                     # ナックル外径半径 (閉じた時 82.3 + 2.0 = 84.3mm ≒ 84.1mm)
NUM_SEGMENTS = 7                       # ナックル分割数
HINGE_GAP_Y = 0.3                      # Y方向クリアランス (mm)

print(f"HALF_WIDTH: {HALF_WIDTH:.2f} mm")
print(f"OVERALL_HEIGHT: {OVERALL_HEIGHT:.2f} mm")
print(f"BODY_THICKNESS: {BODY_THICKNESS:.2f} mm")

