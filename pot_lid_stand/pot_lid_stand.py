"""
設計要件:
    - 鍋蓋（直径20-30cm、厚さ4cmまで）を支えるための壁掛け用スタンド。
    - 鉄の壁に対して背面に磁石テープを貼付け可能。
    - **安定性の工夫（スロープ）**:
      底面（アームの溝）を手前方向に下る傾斜とし、蓋の最下端が自然に手前に滑り、
      結果的に蓋の上部が壁側へ寄りかかる（傾く）力学構造を持たせる。
    - **安定性の工夫（アーチ型アーム）**:
      アーム内側に巨大なフィレット（R30）を持ったU字の空間をくり抜くことで、
      接触面が直線的ではなく曲面になり、円形の蓋が自然と中央にフィット・安定する。
    - サポート材不要で印刷できるように壁付け面を下（Z=0）にして設計。
    - フルパラメトリックになっており、各種寸法の自由な調整が可能。

推奨フィラメント:
    - PLA, PETG (実用強度として十分。台所なので耐熱性が必要ならPETG推奨)

推奨スライサー設定:
    - 壁面（背面）を下にしてビルドプレートへ配置。
    - ウォールループ（Wall loops）: 4 (アーム部の強度確保のため)
    - インフィル（Infill）: 15%〜20% Gyroid
    - サポート（Support）: なし

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

import cadquery as cq
import os
from ocp_vscode import show_object

# ==========================================
# Parameter Definitions (パラメーター設定)
# ==========================================

STAND_WIDTH = 160.0    # スタンドの全幅（30cmの蓋に対応できる広さ）
STAND_HEIGHT = 80.0    # ベースプレートの縦幅（テコの原理に耐える高さを確保）

BASE_THICKNESS = 4.0   # 壁接地面のベース肉厚 (磁石テープを貼る平面)
INNER_DEPTH = 45.0     # 蓋が入る溝の奥行き（厚さ40mmの蓋が余裕で入る空間）
LIP_THICKNESS = 6.0    # 手前のこぼれ止めリップ自体の厚み

TOTAL_DEPTH = BASE_THICKNESS + INNER_DEPTH + LIP_THICKNESS

# ＝ Y軸方向の座標（高さ） ＝
Y_WALL_BOTTOM = 0.0          # 壁面最下部
Y_UNDERSIDE_FRONT = 10.0     # アーム下側の最前部（ここまでの斜め上がりでサポート不要に）
Y_GROOVE_FRONT = 33.0        # 溝の手前側（一番高い。ここから壁へ下る）
Y_GROOVE_WALL = 20.0         # 溝の壁側（一番低い。蓋が寄りかかるように深く）
Y_LIP_TOP = 43.0             # こぼれ止めリップの頂点高さ

# ==========================================
# Geometry Generation (幾何学モデル生成)
# ==========================================

# 1. YZ平面でのプロファイル（側面図）を作成し、左右対称（X方向）に押し出す。
pts = [
    (Y_WALL_BOTTOM, 0.0),                           # P0: 背面下端
    (Y_WALL_BOTTOM, BASE_THICKNESS),                # P1: 表面下端
    (Y_UNDERSIDE_FRONT, TOTAL_DEPTH),               # P2: アーム下側フロント
    (Y_LIP_TOP, TOTAL_DEPTH),                       # P3: リップ外側頂点
    (Y_LIP_TOP, TOTAL_DEPTH - LIP_THICKNESS),       # P4: リップ内側頂点
    (Y_GROOVE_FRONT, TOTAL_DEPTH - LIP_THICKNESS),  # P5: 溝の手前側（高い）
    (Y_GROOVE_WALL, BASE_THICKNESS),                # P6: 溝の壁側（低い） -> 蓋が壁に寄りかかる
    (STAND_HEIGHT, BASE_THICKNESS),                 # P7: 表面上端
    (STAND_HEIGHT, 0.0),                            # P8: 背面上端
]

body = (
    cq.Workplane("YZ")
    .polyline(pts).close()
    .extrude(STAND_WIDTH / 2.0, both=True)
)
# ここではまだフィレットをかけない（後の交差エッジ選択を正確にするため）

# 2. 中央部分の突き出し（樋）をカットして、左右の「アーム」に分割する。
cut_w = 80.0          # くり抜きの幅（アーム間の距離）
Y_CUT_BOTTOM = 18.0   # くり抜きの最下点（U字の底）

# 完全なU字の美しい曲線を作るため、円弧を持つSlot（長円形）でくり抜く
# 半径は幅の半分
cut_r = cut_w / 2.0
# Slotの中心Y座標（最下点より半径分上）
cut_center_y = Y_CUT_BOTTOM + cut_r

cutter = (
    cq.Workplane("XY", origin=(0, cut_center_y, BASE_THICKNESS))
    .slot2D(STAND_HEIGHT * 4.0, cut_w, 90) # Y方向に長いSlotを作ることで上部は開いたU字になる
    .extrude(TOTAL_DEPTH * 2.0)
)

# ブーリアン減算による切り抜き（これで曲線アームが完成）
holder = body.cut(cutter)

# 3. 滑らかさの付与（面取り加工）
# 残った直線的な角をマイルドに面取りし、安全性を確保
try:
    holder = holder.edges("%LINE").fillet(1.5)
except Exception as e:
    print(f"Outer Fillet Warning: {e}")

# ==========================================
# Export (ファイル出力)
# ==========================================

try:
    show_object(holder, name="Pot Lid Stand Curved")
except Exception:
    pass

output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pot_lid_stand.step")
print(f"Exporting to: {output_file}")
cq.exporters.export(holder, output_file)
print("Done!")
