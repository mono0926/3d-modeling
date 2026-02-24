"""
設計要件:
    - 鍋蓋（直径200mmなど）を支えるための壁掛け用スタンド。
    - 鉄の壁に対して背面に磁石テープを貼付け可能。
    - サイズ違いの鍋蓋にも対応しやすいようにアーム2点支持機構を採用。
    - サポート材不要で印刷できるように壁付け面を下（Z=0）にして設計。
    - フルパラメトリックになっており、各種寸法の自由な調整が可能。

推奨フィラメント:
    - PLA, PETG (実用強度として十分。台所なので耐熱性が必要ならPETG推奨)

推奨スライサー設定:
    - 壁面を下にしてビルドプレートへ配置。
    - ウォールループ（Wall loops）: 3〜4 (アーム部の強度確保のため)
    - インフィル（Infill）: 15%〜20% Gyroid
    - サポート（Support）: なし

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

import cadquery as cq
import os

# ==========================================
# Parameter Definitions (パラメーター設定)
# ==========================================

LID_DIAMETER = 200.0   # 想定する鍋蓋の直径（参考値、2点支持なので厳密でなくても可）
LID_THICKNESS = 18.0   # 鍋蓋の縁の厚み（余裕をもたせた数値）

STAND_WIDTH = 130.0    # スタンドの全幅
STAND_HEIGHT = 45.0    # ベースプレートの縦幅（壁に貼る面の高さ）
BASE_THICKNESS = 4.0   # 壁接地面のベース肉厚 (磁石テープを貼る平面)

ARM_WIDTH = 25.0       # 各アーム(蓋を受けるフック部)の幅
ARM_LENGTH = 32.0      # ベース表面からのアーム突き出し長(奥行き)
LIP_HEIGHT = 16.0      # 手前に蓋が落ちないようにするこぼれ止めの高さ
LIP_THICKNESS = 6.0    # リップ部品自体の前方厚み
BOTTOM_THICKNESS = 8.0 # アーム底面の肉厚

# ＝ 導出値 ＝
TOTAL_DEPTH = BASE_THICKNESS + ARM_LENGTH  # 壁から一番手前までの総合距離

# アームの溝（谷）を壁に向かって傾斜させ、蓋が壁に寄りかかるようにする
SLOPE_DROP = 2.0  # 手前側の底から奥側（壁側）の底への落差

# ==========================================
# Geometry Generation (幾何学モデル生成)
# ==========================================

# 1. YZ平面でのプロファイル（側面図）を作成し、左右対称（X方向）に押し出す。
# Y軸: 上下方向 (u), Z軸: 壁から手前への奥行き方向 (v)
# 壁への貼付面（裏面）が Z=0 となる。

pts = [
    (0, 0),                           # P0: 壁面下端・裏面
    (0, BASE_THICKNESS),              # P1: 壁面下端・表面
    (BOTTOM_THICKNESS, TOTAL_DEPTH),  # P2: アーム底外側 (斜めに手前へ立ち上がる)
    (BOTTOM_THICKNESS + LIP_HEIGHT, TOTAL_DEPTH), # P3: リップ外側頂点
    (BOTTOM_THICKNESS + LIP_HEIGHT, TOTAL_DEPTH - LIP_THICKNESS), # P4: リップ内側頂点
    (BOTTOM_THICKNESS, TOTAL_DEPTH - LIP_THICKNESS - 2.0), # P5: 谷底・手前側 (少し面取り)
    (BOTTOM_THICKNESS - SLOPE_DROP, BASE_THICKNESS), # P6: 谷底・壁側 (奥へ向かって下る)
    (STAND_HEIGHT, BASE_THICKNESS),   # P7: 壁面上端・表面
    (STAND_HEIGHT, 0),                # P8: 壁面上端・裏面
]

# プロファイルをXの法線方向(左右)にSTAND_WIDTHの半分ずつ両側へ押し出す
# これで、まっすぐな受け樋を持ったベース構造ができる。
body = (
    cq.Workplane("YZ")
    .polyline(pts).close()
    .extrude(STAND_WIDTH / 2.0, both=True)
)

# 押し出し直後の2Dエッジ（X軸に平行なエッジ＝谷底やリップ）にフィレットをかける
# これにより、後でカットした内面が滑らかに繋がる
try:
    body = body.edges("|X").fillet(1.5)
except Exception as e:
    print(f"Base Fillet Warning: {e}")

# 2. 中央部分の突き出し（樋）をカットして、左右の「アーム」に分割する。
# カットする幅
cut_w = STAND_WIDTH - (ARM_WIDTH * 2)

# カッターとなるBoxを作成
# 位置: Z=BASE_THICKNESS から手前をすべて切り抜くためそこに配置
cutter = (
    cq.Workplane("XY", origin=(0, 0, BASE_THICKNESS))
    .rect(cut_w, STAND_HEIGHT * 3) # Yを十分大きくカバー
    .extrude(TOTAL_DEPTH * 2)      # Zを十分手前までカバー
)

# ブーリアン減算による切り抜き
holder = body.cut(cutter)

# 3. 切り欠きによって生じた縦・横のエッジの角丸め（フィレット）
try:
    # ユーザーが触れる外側の角や切り抜き部のエッジをマイルドにする
    holder = holder.edges("|Z").fillet(1.5)
    holder = holder.edges("|Y").fillet(1.5)
except Exception as e:
    print(f"Cut Inner Fillet Warning: {e}")

# ==========================================
# Export (ファイル出力)
# ==========================================
# 壁面をZ=0に置いているため、スライサーにインポートするだけで
# そのままサポートなしの最適な印刷姿勢となる。

print("Exporting...")
output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pot_lid_stand.step")
print(f"File path: {output_file}")
cq.exporters.export(holder, output_file)
print("Done!")
