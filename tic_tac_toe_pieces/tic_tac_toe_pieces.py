"""
設計要件:
    - 三目並べ（Tic Tac Toe）用の駒（イチゴとチーズ）を設計。
    - 盤面 18x18mm に対して、駒サイズを 約16x16mm、厚さ 3mm に設定。
    - マルチカラー印刷（Bambu Lab P2S/AMS等）に対応するため、各色を別々のボディとして一括出力。
    - イチゴ: 赤（本体）+ 緑（ヘタ）の2色。
    - チーズ: 黄（本体）+ 白（穴）の2色。
    - 各駒はスライサー（Bambu Studio）で「パーツ」として認識され、個別に着色可能。

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
THICKNESS = 3.0  # 駒の厚み(mm)

# 出力ディレクトリの設定（スクリプトと同じ場所）
OUTPUT_DIR = os.path.dirname(__file__)

def create_strawberry():
    """イチゴの駒を作成"""
    # 本体（赤）
    # しずく型をスケッチで作成
    body = (
        cq.Workplane("XY")
        .moveTo(0, -SIZE/2 + 1)
        .bezier([
            (-SIZE/2, 0),
            (0, SIZE/2),
            (SIZE/2, 0),
            (0, -SIZE/2 + 1)
        ])
        .close()
        .extrude(THICKNESS)
    )

    # ヘタ（緑）
    # 上部にギザギザの形状
    top_w = SIZE * 0.7
    top_h = SIZE * 0.35
    stem = (
        cq.Workplane("XY")
        .center(0, SIZE/2 - top_h/2)
        .rect(top_w, top_h)
        .extrude(THICKNESS)
    )

    # 重なりを解消（ヘタの部分を本体から引く）
    body = body.cut(stem)

    return [
        ("strawberry_body_red", body),
        ("strawberry_stem_green", stem)
    ]

def create_cheese():
    """チーズの駒を作成"""
    # 本体（黄）
    # かじり跡のある四角形
    base_rect = (
        cq.Workplane("XY")
        .rect(SIZE, SIZE)
        .extrude(THICKNESS)
    )

    # かじり跡（円柱で切り欠く）
    bite_r = SIZE * 0.25
    bite = (
        cq.Workplane("XY")
        .center(SIZE/2, SIZE/4)
        .circle(bite_r)
        .extrude(THICKNESS)
    )

    body = base_rect.cut(bite)

    # 穴（白）
    hole_positions = [
        (-SIZE/4, SIZE/4, SIZE*0.15),
        (SIZE/8, -SIZE/4, SIZE*0.1),
        (-SIZE/3, -SIZE/6, SIZE*0.08)
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
