"""
設計要件:
    - 鍋蓋（直径200~300mm、厚さ40mmまで）を支えるための壁掛け用スタンド。
    - 鉄の壁に対して背面に磁石テープを貼付可能。
    - **印刷最適化**: 仰向け（ベース背面 Z=0 を下）にしてサポート材なしで一発印刷可能。
    - **フィット感の向上**:
        - アームを深いV字型（谷）にし、分厚い鍋蓋も自重でしっかり壁側にホールド。
        - カッターで中央をアーチ状にくり抜き、円形の蓋が自然と馴染むクレードル（揺りかご）構造を採用。

推奨フィラメント:
    - PLA, PETG (実用強度として十分。台所なので耐熱性が必要ならPETG推奨)

推奨スライサー設定:
    - 配置: 背面（平らな面）をビルドプレートに設置。
    - ウォールループ（Wall loops）: 4 (アーム剛性向上)
    - インフィル: 15%〜20% Gyroid
    - サポート: なし

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

import cadquery as cq
import os
from ocp_vscode import show_object

# ==========================================
# Parameter Definitions (パラメーター設定)
# ==========================================

STAND_WIDTH = 140.0    # スタンド全幅 (20~30cm蓋に対応する適度な広さ)
STAND_HEIGHT = 80.0    # スタンド全高 (テコの原理に耐える広さを確保)
BASE_THICKNESS = 6.0   # ベース厚（磁石貼付面）

ARM_WIDTH = 25.0       # 各アームの幅

# ジオメトリ算出用の主要 Y(高さ), Z(壁からの距離) 座標
# Y=0が下、Y=80が上。Z=0が壁(裏面)、Z=6が表面。
Y_VALLEY = 42.0        # V字溝の谷底の高さ (Y)
Z_VALLEY = 26.0        # V字溝の谷底の深さ (Z)

Y_WALL_LIP = 55.0      # V字溝の壁側の頂点高さ (Y)

Y_LIP_TIP = 70.0       # 前方リップの頂点高さ (Y)
Z_LIP_TIP = 68.0       # 前方リップの先端の深さ (Z) 厚さ40mmを余裕で入れ込む

TOTAL_DEPTH = Z_LIP_TIP

# ==========================================
# Geometry Generation (幾何学モデル生成)
# ==========================================

# 1. 断面プロファイル作成
# サポートなしで印刷するため、Z軸方向へのオーバーハングが45度(勾配1)以下になるよう配慮。
pts = [
    (0, 0),                           # P0: 背面下端
    (0, BASE_THICKNESS),              # P1: 表面下端
    (Y_LIP_TIP, Z_LIP_TIP),           # P2: アーム先端 (約45度の安全なせり出し)
    (Y_VALLEY, Z_VALLEY),             # P3: V字溝の谷底 (V字を形成)
    (Y_WALL_LIP, BASE_THICKNESS),     # P4: 溝の壁側頂点
    (STAND_HEIGHT, BASE_THICKNESS),   # P5: 表面上端
    (STAND_HEIGHT, 0)                 # P6: 背面上端
]

# 左右(X軸方向)に押し出し
body = (
    cq.Workplane("YZ")
    .polyline(pts).close()
    .extrude(STAND_WIDTH / 2.0, both=True)
)

# YZプロファイルの角（X軸と平行なエッジ）をすべて丸める（安全性・美観）
try:
    body = body.edges("|X").fillet(2.5)
except Exception as e:
    print(f"Profile Fillet Warning: {e}")

# 2. 中央のくり抜きアーチカット
cut_w = STAND_WIDTH - (ARM_WIDTH * 2)
cut_h = STAND_HEIGHT * 2.0
# 下から15mm残して上部すべてを切り抜く
cut_y_center = 15.0 + (cut_h / 2.0)

# くり抜き用のBoxを作成し、Z軸平行なエッジに巨大なフィレットをかけてアーチ状にする
cutter = (
    cq.Workplane("XY", origin=(0, cut_y_center, BASE_THICKNESS))
    .box(cut_w, cut_h, TOTAL_DEPTH * 2)
    .edges("|Z").fillet(25.0)  # 25mmの巨大なRで鍋蓋の円弧にフィットするクレードルになる
)

holder = body.cut(cutter)

# カット後のエッジ角丸め（ユーザースキンへの配慮）
try:
    holder = holder.edges("|Y").fillet(2.0)
except Exception as e:
    print(f"Inner Cut Fillet Warning: {e}")

# ==========================================
# Export (ファイル出力)
# ==========================================

# ocp_vscodeが利用可能な場合は表示
try:
    show_object(holder, name="Pot Lid Stand V2")
except Exception:
    pass

output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pot_lid_stand.step")
print(f"Exporting to: {output_file}")
cq.exporters.export(holder, output_file)
print("Done!")
