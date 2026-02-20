"""
設計要件:
    - 三目並べ（Tic Tac Toe）用の駒（イチゴとチーズ）を設計。
    - イチゴ: 真の雫型（💧）を追求。数学的に正確な接線を用い、上部を滑らかな円弧、下部の一点のみを鋭角に設計。
    - チーズ: 三角形ウェッジ型の単色モデル。物理的な貫通穴（かじり跡を含む）を持つ。
    - 印刷最適化: イチゴは 0-2mm を赤ベース、2-4mm を緑の有機的な5つ葉ヘタとする2層構造（色替え1回）。

推奨フィラメント:
    - PLA (赤、緑、黄)
    - 収縮や反りを抑えるため、造形ベッドとの密着性に優れたPLAを推奨。

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

import cadquery as cq
import os
import math

# --- 定数定義 ---
SIZE = 16.0
BASE_HEIGHT = 2.0
DECO_HEIGHT = 2.0
TOTAL_HEIGHT = BASE_HEIGHT + DECO_HEIGHT

# 出力ディレクトリの設定
OUTPUT_DIR = os.path.dirname(__file__)

def create_strawberry():
    """真の雫型（💧）のイチゴを作成。数学的に正確な接線を用いて滑らかな形状を実現。"""
    w = SIZE * 1.0
    h = SIZE * 1.1

    # 定義: 最下部の鋭角点(0, -h/2)、上部の半円弧(中心 C=(0, y_c), 半径 R=w/2)
    R = w / 2
    y_t = -h / 2
    y_c = h / 2 - R
    d = y_c - y_t  # 先端から円の中心までの距離

    # 接点の計算
    sin_alpha = R / d
    cos_alpha = math.sqrt(1 - sin_alpha**2)
    px = R * cos_alpha
    py = y_c - R * sin_alpha

    # 雫型の輪郭: 先端から両側の接点まで直線、上部は円弧で結ぶ
    strawberry_outline = (
        cq.Workplane("XY")
        .moveTo(0, y_t)
        .lineTo(px, py)
        .threePointArc((0, y_c + R), (-px, py))
        .close()
    )

    # 全体形状を高さいっぱいに作成
    full_body = strawberry_outline.extrude(TOTAL_HEIGHT)

    # 有機的な5枚の葉を持つヘタを作成
    num_leaves = 5
    R_out = w * 0.45  # 葉の先端（少し控えめにし、雫型にしっかり収まるように）
    R_in = w * 0.15   # 葉の根本
    cx, cy = 0, y_c + R * 0.3  # 上部の円の中心より少し上に配置

    leaf_pts = []
    for i in range(num_leaves * 2):
        # 最初の葉が上(Y軸正方向)を向くように角度を設定
        angle = math.pi / 2 + i * math.pi / num_leaves
        r_current = R_out if i % 2 == 0 else R_in
        leaf_pts.append((cx + r_current * math.cos(angle), cy + r_current * math.sin(angle)))

    leaves_boundary = (
        cq.Workplane("XY")
        .workplane(offset=BASE_HEIGHT)
        .polyline(leaf_pts).close()
        .extrude(DECO_HEIGHT)
    )

    # ヘタの実際の形状（雫型の外側にはみ出さないよう交差をとる）
    leaves = leaves_boundary.intersect(full_body)

    # 赤い本体: 0-2mmは全域、2-4mmはヘタ以外の領域
    strawberry_red = full_body.cut(leaves)
    strawberry_green = leaves

    return [
        ("strawberry_red_body", strawberry_red),
        ("strawberry_green_stem", strawberry_green)
    ]

def create_cheese():
    """物理的な貫通穴（かじり跡を含む）を持つウェッジ型のチーズを作成"""
    c_size = SIZE * 1.1

    # 三角形ウェッジの輪郭
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

    cheese_final = cheese_body.cut(bite)

    # ランダムな大小の貫通穴
    hole_positions = [
        (c_size/4, -c_size/4, c_size*0.12),
        (-c_size/8, -c_size/3, c_size*0.08),
        (c_size/2.5, c_size/4, c_size*0.07)
    ]

    for x, y, r in hole_positions:
        hole = cq.Workplane("XY").center(x, y).circle(r).extrude(TOTAL_HEIGHT)
        cheese_final = cheese_final.cut(hole)

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
