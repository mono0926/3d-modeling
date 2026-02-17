"""
設計要件:
    - 三目並べ（Tic Tac Toe）用の駒（イチゴとチーズ）を設計。
    - 盤面 18x18mm に対して、駒サイズを 約16x16mm、厚さ 4mm に設定。
    - イチゴ: ベジェ曲線を使用した滑らかな雫型（💧）+ 2層構造のヘタ。
    - チーズ: 三角形ウェッジ型の単色モデル。装飾ではなく物理的な「穴（空洞）」を持つ。
    - 印刷最適化: イチゴは 0-2mm を赤、2-4mm を緑とする2層構造。

推奨フィラメント:
    - PLA (赤、緑、黄)

印刷統計（予想）:
    - strawberry.step: 印刷時間 約10分（色替え1回）、フィラメント使用量 約2g
    - cheese.step: 印刷時間 約5分（単色）、フィラメント使用量 約1.5g

Bambu Studioでの設定:
    - strawberry: 2パーツとしてインポート。レイヤー高さ 2.0mm で色を切り替える。
    - cheese: 単色としてインポート。

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

import cadquery as cq
import os

# --- 定数定義 ---
SIZE = 16.0  # 駒の最大幅/高さ(mm)
BASE_HEIGHT = 2.0  # ベース部分の厚み(mm)
DECO_HEIGHT = 2.0  # 装飾部分の厚み(mm)
TOTAL_HEIGHT = BASE_HEIGHT + DECO_HEIGHT

# 出力ディレクトリの設定
OUTPUT_DIR = os.path.dirname(__file__)

def create_strawberry():
    """滑らかな雫型（💧）のイチゴを作成"""
    # 雫型の輪郭をベジェ曲線で定義
    # 下部を丸く、上部を緩やかに絞る
    w = SIZE * 1.0
    h = SIZE * 1.1

    strawberry_outline = (
        cq.Workplane("XY")
        .moveTo(0, -h/2)
        .bezier([
            (-w/2, -h/4),
            (-w/2, h/4),
            (0, h/2),
            (w/2, h/4),
            (w/2, -h/4),
            (0, -h/2)
        ])
        .close()
    )

    # 全体形状を高さいっぱいに作成
    full_body = strawberry_outline.extrude(TOTAL_HEIGHT)

    # ヘタ部分の定義 (2.0mm - 4.0mm)
    # 上部に重なるギザギザ
    leaves_outline = (
        cq.Workplane("XY")
        .workplane(offset=BASE_HEIGHT)
        .center(0, h/4)
        .rect(w*0.8, h*0.5)
        .toPending()
    )

    # ヘタの実際の形状（上部1/3程度を覆う）
    leaves = (
        leaves_outline.extrude(DECO_HEIGHT)
        .intersect(full_body)
    )

    # 赤い本体: 0-2mm は全域、2-4mm はヘタ以外の領域
    strawberry_red = full_body.cut(leaves)
    strawberry_green = leaves

    return [
        ("strawberry_red_body", strawberry_red),
        ("strawberry_green_stem", strawberry_green)
    ]

def create_cheese():
    """物理的な穴を持つウェッジ型のチーズを作成"""
    # イチゴとボリューム感を合わせるためサイズ調整
    c_size = SIZE * 1.1

    cheese_outline = (
        cq.Workplane("XY")
        .moveTo(-c_size/2, -c_size/2)
        .lineTo(c_size/2, -c_size/2)
        .lineTo(c_size/2, c_size/2)
        .close()
    )

    # 形状の押し出し
    cheese_body = cheese_outline.extrude(TOTAL_HEIGHT)

    # かじり跡
    bite = (
        cq.Workplane("XY")
        .center(c_size/2, 0)
        .circle(c_size*0.2)
        .extrude(TOTAL_HEIGHT)
    )

    # 物理的な空洞としての穴
    hole_positions = [
        (c_size/4, -c_size/4, c_size*0.12),
        (-c_size/8, -c_size/3, c_size*0.08),
        (c_size/2.5, c_size/4, c_size*0.07)
    ]

    holes = cq.Workplane("XY")
    for x, y, r in hole_positions:
        hole = cq.Workplane("XY").center(x, y).circle(r).extrude(TOTAL_HEIGHT)
        holes = holes.union(hole)

    # 全ての空洞を本体から引く
    cheese_final = cheese_body.cut(bite).cut(holes)

    return [
        ("cheese_yellow_single", cheese_final)
    ]

def export_step(name, pieces):
    path = os.path.normpath(os.path.join(OUTPUT_DIR, f"{name}.step"))
    assembly = cq.Assembly()
    for sub_name, part in pieces:
        assembly.add(part, name=sub_name)
    assembly.save(path, "STEP")
    print(f"Exported: {path}")

if __name__ == "__main__":
    export_step("strawberry", create_strawberry())
    export_step("cheese", create_cheese())
