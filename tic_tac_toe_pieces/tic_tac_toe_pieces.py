"""
設計要件:
    - 三目並べ（Tic Tac Toe）用の駒（イチゴとチーズ）を設計。
    - 盤面 18x18mm に対して、駒サイズを 約16x16mm、厚さ 3mm に設定。
    - イチゴ: Apple絵文字風の丸みのあるしずく型 + 有機的なヘタ。
    - チーズ: ウェッジ型（三角形）の断面が見えるデザイン。
    - マルチカラー印刷（Bambu Lab P2S/AMS等）に対応するため、各色を別々のボディとして一括出力。

推奨フィラメント:
    - PLA (発色が良く、細かい造形に適しているため)
    - 赤、緑、黄、白の4色が必要。

印刷統計（予想）:
    - strawberry.step: 印刷時間 約15分（1個、色替え含む）、フィラメント使用量 約2g
    - cheese.step: 印刷時間 約15分（1個、色替え含む）、フィラメント使用量 約2g

Bambu Studioでの設定:
    1. STEPファイルをインポートする。
    2. オブジェクトリストで各ボディを右クリックし、「パーツを変更」を選択。
    3. 適切なフィラメント（赤、緑、黄、白）を割り当てる。

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

import cadquery as cq
import os

# --- 定数定義 ---
SIZE = 16.0  # 駒の最大幅/高さ(mm)
THICKNESS = 4.0  # 駒の厚み(mm) - 立体感を出すため 4mm に設定

# 出力ディレクトリの設定（スクリプトと同じ場所）
OUTPUT_DIR = os.path.dirname(__file__)

def create_strawberry():
    """イチゴの駒を作成 (Apple絵文字風)"""
    # 本体（赤）
    # よりふっくらしたしずく型
    body = (
        cq.Workplane("XY")
        .moveTo(0, -SIZE/2 + 0.5)
        .bezier([
            (-SIZE/2 * 1.2, -SIZE/4),
            (-SIZE/2 * 0.8, SIZE/2),
            (0, SIZE/2),
            (SIZE/2 * 0.8, SIZE/2),
            (SIZE/2 * 1.2, -SIZE/4),
            (0, -SIZE/2 + 0.5)
        ])
        .close()
        .extrude(THICKNESS)
    )

    # ヘタ（緑）
    # ギザギザの葉を複数作成
    leaves = cq.Workplane("XY").workplane(offset=0)
    leaf_count = 5
    for i in range(leaf_count):
        angle = -30 + (60 / (leaf_count - 1)) * i
        leaf = (
            cq.Workplane("XY")
            .center(0, SIZE/2 - 2)
            .rotate((0, 0, 0), (0, 0, 1), angle)
            .moveTo(0, 0)
            .line(-2, 4)
            .line(2, 2)
            .line(2, -2)
            .line(-2, -4)
            .close()
            .extrude(THICKNESS)
        )
        leaves = leaves.add(leaf)

    stem_base = (
        cq.Workplane("XY")
        .center(0, SIZE/2 - 1)
        .rect(SIZE*0.5, 2)
        .extrude(THICKNESS)
    )
    stem = leaves.union(stem_base)

    # 重なりを解消
    body = body.cut(stem)

    return [
        ("strawberry_body_red", body),
        ("strawberry_stem_green", stem)
    ]

def create_cheese():
    """チーズの駒を作成 (ウェッジ型)"""
    # 本体（黄）
    # 三角形のウェッジ型。面積をイチゴに合わせるため少し大きめに調整。
    c_size = SIZE * 1.1
    base_tri = (
        cq.Workplane("XY")
        .moveTo(-c_size/2, -c_size/2)
        .lineTo(c_size/2, -c_size/2)
        .lineTo(c_size/2, c_size/2)
        .close()
        .extrude(THICKNESS)
    )

    # かじり跡（大きな穴）
    bite_r = c_size * 0.2
    bite = (
        cq.Workplane("XY")
        .center(c_size/2, 0)
        .circle(bite_r)
        .extrude(THICKNESS)
    )

    body = base_tri.cut(bite)

    # 小さな穴（白）- インセットパーツ
    hole_positions = [
        (c_size/4, -c_size/4, c_size*0.12),
        (-c_size/8, -c_size/3, c_size*0.08),
        (c_size/2.5, c_size/4, c_size*0.07)
    ]

    holes = []
    for i, (x, y, r) in enumerate(hole_positions):
        hole = (
            cq.Workplane("XY")
            .center(x, y)
            .circle(r)
            .extrude(THICKNESS)
        )
        holes.append((f"cheese_hole_white_{i}", hole))
        body = body.cut(hole)

    pieces = [("cheese_body_yellow", body)]
    pieces.extend(holes)

    return pieces

def export_step(name, pieces):
    """複数のパーツを一括してSTEPに出力"""
    path = os.path.normpath(os.path.join(OUTPUT_DIR, f"{name}.step"))

    assembly = cq.Assembly()
    for sub_name, part in pieces:
        assembly.add(part, name=sub_name)

    assembly.save(path, "STEP")
    print(f"Exported: {path}")

if __name__ == "__main__":
    # イチゴの生成
    strawberry_parts = create_strawberry()
    export_step("strawberry", strawberry_parts)

    # チーズの生成
    cheese_parts = create_cheese()
    export_step("cheese", cheese_parts)
