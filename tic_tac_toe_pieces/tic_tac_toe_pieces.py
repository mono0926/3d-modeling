"""
設計要件:
    - 三目並べ（Tic Tac Toe）用の駒（イチゴとチーズ）を設計。
    - イチゴ: 真の雫型（💧）を追求。上部を滑らかな円弧、下部の一点のみを鋭角に設計。
    - チーズ: 三角形ウェッジ型の単色モデル。物理的な貫通穴を持つ。
    - 印刷最適化: イチゴは 0-2mm を赤、2-4mm を緑とする2層構造（色替え1回）。

推奨フィラメント:
    - PLA (赤、緑、黄)

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

import cadquery as cq
import os

# --- 定数定義 ---
SIZE = 16.0
BASE_HEIGHT = 2.0
DECO_HEIGHT = 2.0
TOTAL_HEIGHT = BASE_HEIGHT + DECO_HEIGHT

# 出力ディレクトリの設定
OUTPUT_DIR = os.path.dirname(__file__)

def create_strawberry():
    """真の雫型（💧）のイチゴを作成（鋭角は先端の1点のみ）"""
    w = SIZE * 1.0
    h = SIZE * 1.1

    # 雫型の輪郭: 下端(0, -h/2)を起点とし、左右の肩(w/2, h/8)まで直線、
    # そこから上端(0, h/2)を経由して反対の肩まで円弧でつなぐ。
    strawberry_outline = (
        cq.Workplane("XY")
        .moveTo(0, -h/2) # 鋭角となる先端
        .lineTo(w/2, h/8) # 直線で肩へ
        .threePointArc((0, h/2), (-w/2, h/8)) # 滑らかな円弧で頂点を通る
        .close() # 最後に直線で先端へ戻ることで角ができる
    )

    # 全体形状を高さいっぱいに作成
    full_body = strawberry_outline.extrude(TOTAL_HEIGHT)

    # ヘタ部分の定義 (2.0mm - 4.0mm)
    # 円弧などを用いて本体の曲線に馴染むヘタの境界を作る
    leaves_boundary = (
        cq.Workplane("XY")
        .workplane(offset=BASE_HEIGHT)
        .center(0, h/3)
        .circle(w * 0.6) # 円形に抜くことで境界を滑らかに
        .extrude(DECO_HEIGHT)
    )

    # ヘタの実際の形状
    leaves = (
        leaves_boundary.intersect(full_body)
    )

    # 赤い本体: 0-2mm は全域、2-4mm はヘタ以外の領域
    strawberry_red = full_body.cut(leaves)
    strawberry_green = leaves

    return [
        ("strawberry_red_body", strawberry_red),
        ("strawberry_green_stem", strawberry_green)
    ]

def create_cheese():
    """物理的な貫通穴を持つウェッジ型のチーズを作成"""
    c_size = SIZE * 1.1
    cheese_outline = (
        cq.Workplane("XY")
        .moveTo(-c_size/2, -c_size/2)
        .lineTo(c_size/2, -c_size/2)
        .lineTo(c_size/2, c_size/2)
        .close()
    )

    cheese_body = cheese_outline.extrude(TOTAL_HEIGHT)

    # かじり跡
    bite = (
        cq.Workplane("XY")
        .center(c_size/2, 0)
        .circle(c_size*0.2)
        .extrude(TOTAL_HEIGHT)
    )

    # 穴(貫通)
    hole_positions = [
        (c_size/4, -c_size/4, c_size*0.12),
        (-c_size/8, -c_size/3, c_size*0.08),
        (c_size/2.5, c_size/4, c_size*0.07)
    ]

    holes = cq.Workplane("XY")
    for x, y, r in hole_positions:
        hole = cq.Workplane("XY").center(x, y).circle(r).extrude(TOTAL_HEIGHT)
        holes = holes.union(hole)

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
