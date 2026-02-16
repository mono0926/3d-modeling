"""
設計要件:
    - 縦2cm（20mm）程度の任意の文字列（顔文字）ネームプレート。
    - 文字列は定数定義し「(　´･‿･｀)」とする。
    - 2色刷（ベース：黒、文字：白）を想定し、文字を物理的に浮き出させる（1.5mm）。
    - 最新の3Dプリンター（Bambu Lab P2S 等）での出力を想定。
    - モデルごとに専用ディレクトリで管理し、STEPファイルを出力する。

推奨フィラメント:
    - PLA (扱いやすさと発色の良さから推奨)
    - PETG (屋外利用など耐候性が必要な場合)

印刷統計（予想）:
    - nameplate_kaomoji.step: 印刷時間 約15分、フィラメント使用量 約5g

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

import cadquery as cq
import os

# --- パラメーター定義 ---
# 文字列は定数定義
TEXT_STR = "(　´･‿･｀)"
PLATE_WIDTH = 60.0
PLATE_HEIGHT = 20.0
PLATE_THICKNESS = 3.0
CORNER_RADIUS = 2.0

TEXT_SIZE = 12.0
TEXT_HEIGHT = 1.5  # 文字の浮き出し量
FONT_NAME = "Sans"  # システムに依存するが、一般的に視認性の良いフォントを指定

# --- モデリング ---

# 1. ベースプレートの作成
# XY平面の中心(0,0)に配置し、Z=0を底面とする
result = (
    cq.Workplane("XY")
    .box(PLATE_WIDTH, PLATE_HEIGHT, PLATE_THICKNESS, centered=(True, True, False))
    .edges("|Z")
    .fillet(CORNER_RADIUS)
)

# 2. 文字の追加
# プレートの上面(Z=PLATE_THICKNESS)に文字を配置
result = (
    result.faces(">Z")
    .workplane()
    .center(0, 0)
    .text(
        TEXT_STR,
        TEXT_SIZE,
        TEXT_HEIGHT,
        font=FONT_NAME,
        halign="center",
        valign="center",
        kind="bold" # 視認性向上のためボールド
    )
)

# --- 出力 ---

# スクリプトと同じディレクトリに保存するためのパス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
# 実行環境に依存せず、常にスクリプトと同じディレクトリに出力されるように絶対パスを指定
output_path = os.path.join(current_dir, "nameplate_kaomoji.step")

# STEPファイルとして出力
cq.exporters.export(result, output_path)

print(f"Model exported to: {output_path}")
