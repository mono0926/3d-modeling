import cadquery as cq
import os
import math

"""
設計要件:
    - ベーゴマの土俵の丸い骨格（分解組み立て式・接着剤不要）。
    - 256x256mmプレート（Bambu Lab P2S）に収まるよう、半径240mmの1/4円（90度）パーツとして設計。
    - 4つの同一形状パーツを印刷し、組み合わせたあとに外周を紐で縛る力（フープ応力）だけで固定して遊びます。
    - 外周には、シートを被せて紐で縛るための溝（幅6mm、深さ3mm）を配置。
    - 接着剤なしでも適度に仮組み保持できるよう、ジョイント部に高精度なピン（オス）と穴（メス）を配置（クリアランス0.25mm）。

推奨フィラメント:
    - PETG (屋外使用での耐衝撃性、および分解・組み立てを繰り返す際のピンの靭性・柔軟性を考慮し、本設計の前提とします)
    - PLA Basic (代用可能ですが、抜き差しを繰り返す際にピンが摩耗・破損しやすくなる可能性があります)

推奨スライサー設定 (Bambu Studio):
    - インフィル (Infill): 15% 程度 (Grid または Gyroid)
    - ウォール (Wall loops): 3層 (強度確保のため)
    - 積層ピッチ (Layer height): 0.20mm Standard (面取り部分や円弧が綺麗に印刷されます)
    - サポート (Support): 不要 (紐用の溝はブリッジ可能、ジョイントピンも面取りが施されており、サポートなしで印刷可能です)

印刷統計（予想）:
    - beigoma_dohyo_frame.step: 印刷時間 約4〜5時間 (1パーツあたり)、フィラメント使用量 約220g (1パーツあたり)

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照.
"""

# --- 設計パラメーター ---
# フレーム寸法
R_OUT = 240.0         # 外径半径 (mm)
R_IN = 224.0          # 内径半径 (mm)
HEIGHT = 30.0         # フレーム高さ (mm) - 溝を上部に寄せることで30mm高でも十分なたわみ空間を確保

# 紐用溝寸法
GROOVE_WIDTH = 6.0    # 溝の幅 (mm)
GROOVE_DEPTH = 3.0    # 溝の深さ (mm)
GROOVE_TOP_OFFSET = 4.0 # フレーム上端から溝上端までの距離 (mm)

# ジョイント（ピン）寸法
PIN_WIDTH = 8.0       # ピンの幅 (X方向) (mm)
PIN_HEIGHT = 6.0      # ピンの高さ (Z方向) (mm) - 溝との干渉を避けるため6mmに設定
PIN_LENGTH = 10.0     # ピンの長さ (押し出し長さ) (mm)
CHAMFER_VAL = 1.0     # ピン先端の面取り量 (mm)
PIN_Z_GLOBAL = 10.0   # ピンの中心のZ座標 (mm) - 溝との干渉を避けて下側に配置

# ジョイント穴（クリアランス込）寸法
CLEARANCE = 0.25      # ジョイントクリアランス (mm) - 接着剤不要で適度にホールドしつつ、抜き差ししやすい絶妙な値に設定
HOLE_WIDTH = PIN_WIDTH + 2 * CLEARANCE
HOLE_HEIGHT = PIN_HEIGHT + 2 * CLEARANCE
HOLE_LENGTH = PIN_LENGTH + CLEARANCE

# -----------------
# 1/4円筒フレームの作成
# -----------------
# 2Dスケッチで1/4円環（第一象限：0〜90度）を描き、高さ分だけ押し出します。
# 0度端面は Y=0 (X軸上)、90度端面は X=0 (Y軸上) に配置されます。

# 45度の位置における円弧の中点を計算
sin45 = math.sin(math.radians(45))
cos45 = math.cos(math.radians(45))

p_out_mid = (R_OUT * cos45, R_OUT * sin45)
p_in_mid = (R_IN * cos45, R_IN * sin45)

# メインの円弧フレーム
frame = (
    cq.Workplane("XY")
    .moveTo(R_IN, 0)
    .lineTo(R_OUT, 0)
    .threePointArc(p_out_mid, (0, R_OUT))
    .lineTo(0, R_IN)
    .threePointArc(p_in_mid, (R_IN, 0))
    .close()
    .extrude(HEIGHT)
)

# -----------------
# 外周紐用溝のカット
# -----------------
# 外径 R_OUT から内側に GROOVE_DEPTH 削る1/4円筒形状を作り、メインフレームから引きます。
# 溝は上端から GROOVE_TOP_OFFSET 下がった位置に配置されます。
groove_z_offset = HEIGHT - GROOVE_WIDTH - GROOVE_TOP_OFFSET
r_groove_inner = R_OUT - GROOVE_DEPTH

# 溝用円弧 (確実にはみ出すように外側は R_OUT + 1mm とします)
r_groove_outer = R_OUT + 1.0
p_groove_out_mid = (r_groove_outer * cos45, r_groove_outer * sin45)
p_groove_in_mid = (r_groove_inner * cos45, r_groove_inner * sin45)

groove_tool = (
    cq.Workplane("XY")
    .workplane(offset=groove_z_offset)
    .moveTo(r_groove_inner, 0)
    .lineTo(r_groove_outer, 0)
    .threePointArc(p_groove_out_mid, (0, r_groove_outer))
    .lineTo(0, r_groove_inner)
    .threePointArc(p_groove_in_mid, (r_groove_inner, 0))
    .close()
    .extrude(GROOVE_WIDTH)
)

frame = frame.cut(groove_tool)

# -----------------
# ジョイントピン（オス）の実装 (Y=0面)
# -----------------
# Y=0面の中心 (X=232.0, Y=0, Z=10.0) から -Y 方向に伸びるピンを直方体として作成します。
pin_center_x = (R_IN + R_OUT) / 2.0
pin_center_y = -PIN_LENGTH / 2.0
pin_center_z = PIN_Z_GLOBAL

pin = (
    cq.Workplane("XY")
    .box(PIN_WIDTH, PIN_LENGTH, PIN_HEIGHT, centered=(True, True, True))
    .translate((pin_center_x, pin_center_y, pin_center_z))
)
# ピンの先端面（Yが最小の面）を選択して面取り
pin = pin.faces("<Y").edges().chamfer(CHAMFER_VAL)

# メインフレームに結合
frame = frame.union(pin)

# -----------------
# ジョイント穴（メス）の実装 (X=0面)
# -----------------
# X=0面の中心 (X=0, Y=232.0, Z=10.0) から内側（+X方向）に掘る穴（ツールボディ）を作成します。
hole_center_x = HOLE_LENGTH / 2.0
hole_center_y = (R_IN + R_OUT) / 2.0
hole_center_z = PIN_Z_GLOBAL

hole_tool = (
    cq.Workplane("XY")
    .box(HOLE_LENGTH, HOLE_WIDTH, HOLE_HEIGHT, centered=(True, True, True))
    .translate((hole_center_x, hole_center_y, hole_center_z))
)

# メインフレームからカット
frame = frame.cut(hole_tool)

# -----------------
# プレビューと出力
# -----------------
# VSCodeの拡張機能（ocp-vscode）用
try:
    from ocp_vscode import show_object
    show_object(frame, name="beigoma_dohyo_frame")
except ImportError:
    pass

# STEPファイルの出力先を設定
# 実行環境に依存せずスクリプトと同じフォルダに出力されるよう、絶対パスを指定します。
dir_path = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(dir_path, "beigoma_dohyo_frame.step")

cq.exporters.export(frame, output_file)
print(f"Exported STEP file to: {output_file}")
