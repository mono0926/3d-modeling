import cadquery as cq
import os
import math

"""
設計要件:
    - ベーゴマの土俵の丸い骨格（分割接着式）。
    - 256x256mmプレート（Bambu Lab P2S）に収まるよう、半径240mmの1/4円（90度）パーツとして設計。
    - 4つの同一形状パーツを印刷し、回転させて接着するだけで直径480mmの円形骨格が完成。
    - 外周には、シートを被せて紐で縛るための溝（幅6mm、深さ3mm）を配置。
    - 位置合わせを容易にするため、0度端面にジョイントピン（オス）、90度端面にジョイント穴（メス）を配置（クリアランス0.2mm）。

推奨フィラメント:
    - PLA Basic (強度と印刷しやすさのバランスが良い)
    - PETG (屋外使用や耐衝撃性をより重視する場合。接着強度の確保のため少し調整が必要な場合があります)

推奨スライサー設定 (Bambu Studio):
    - インフィル (Infill): 15% 程度 (Grid または Gyroid)
    - ウォール (Wall loops): 3層 (強度確保のため)
    - 積層ピッチ (Layer height): 0.20mm Standard (面取り部分や円弧が綺麗に印刷されます)
    - サポート (Support): 不要 (紐用の溝はブリッジ可能、ジョイントピンも面取りが施されており、サポートなしで印刷可能です)

印刷統計（予想）:
    - beigoma_dohyo_frame.step: 印刷時間 約2〜3時間 (1パーツあたり)、フィラメント使用量 約80g (1パーツあたり)

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

# --- 設計パラメーター ---
# フレーム寸法
R_OUT = 240.0         # 外径半径 (mm)
R_IN = 224.0          # 内径半径 (mm)
HEIGHT = 15.0         # フレーム高さ (mm)

# 紐用溝寸法
GROOVE_WIDTH = 6.0    # 溝の幅 (mm)
GROOVE_DEPTH = 3.0    # 溝の深さ (mm)

# ジョイント（ピン）寸法
PIN_WIDTH = 6.0       # ピンの幅 (X方向) (mm)
PIN_HEIGHT = 6.0      # ピンの高さ (Z方向) (mm)
PIN_LENGTH = 10.0     # ピンの長さ (押し出し長さ) (mm)
CHAMFER_VAL = 1.0     # ピン先端の面取り量 (mm)

# ジョイント穴（クリアランス込）寸法
CLEARANCE = 0.2       # ジョイントクリアランス (mm)
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
# 外径 R_OUT から内側に GROOVE_DEPTH Dunk 削る1/4円筒形状を作り、メインフレームから引きます。
# 溝は高さ方向の中央に配置されます。
groove_z_offset = (HEIGHT - GROOVE_WIDTH) / 2.0
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
# Y=0面（0度端面）を選択して、-Y方向（面法線の外側）にピンを押し出します。
# 選択した面（Y=0平面）はグローバルでYが最小なので、セレクター "<Y" で選択できます。
frame = (
    frame.faces("<Y")
    .workplane()
    # 面の中心を基準に、PIN_WIDTH (X方向) x PIN_HEIGHT (Z方向) の矩形を描く
    .rect(PIN_WIDTH, PIN_HEIGHT)
    # 外向きに PIN_LENGTH 押し出す
    .extrude(PIN_LENGTH)
)

# 押し出したピンの先端を面取りします。
# 押し出したことにより、グローバルでYが最も小さい面がピンの先端面になります。
# 再度 "<Y" セレクターで先端面を選び、そのエッジを面取りします。
frame = frame.faces("<Y").edges().chamfer(CHAMFER_VAL)

# -----------------
# ジョイント穴（メス）の実装 (X=0面)
# -----------------
# X=0面（90度端面）を選択して、内側に穴を掘ります。
# この面はグローバルでXが最小なので、セレクター "<X" で選択できます。
# 選択した面を基準にした作業平面から、cutBlind() を使って内側（-Xの逆方向、つまり+X方向）に穴を掘ります。
frame = (
    frame.faces("<X")
    .workplane()
    .rect(HOLE_WIDTH, HOLE_HEIGHT)
    .cutBlind(-HOLE_LENGTH)
)

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
