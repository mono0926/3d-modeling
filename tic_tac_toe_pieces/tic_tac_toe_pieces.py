"""
設計要件:
    - 三目並べ（Tic Tac Toe）用の駒（イチゴとチーズ）を設計。
    - 盤面 18x18mm に対して、駒サイズを 約16x16mm、厚さ 4mm に設定。
    - イチゴ: 鋭角のない滑らかな雫型（💧）+ 上部に重なるヘタ。
    - チーズ: ウェッジ型（三角形）+ 上部に重なる穴の装飾。
    - 印刷最適化: 下部(0-2mm)をベース色、上部(2-4mm)を装飾色とするレイヤー構造。
      これにより、フィラメント交換回数を最小限（1回）に抑える。

推奨フィラメント:
    - PLA (発色が良く、細かい造形に適しているため)
    - 赤、緑、黄、白の4色が必要。

印刷統計（予想）:
    - strawberry.step: 印刷時間 約10分（1個、色替え1回）、フィラメント使用量 約2g
    - cheese.step: 印刷時間 約10分（1個、色替え1回）、フィラメント使用量 約2g

Bambu Studioでの設定:
    1. STEPファイルをインポートする（マルチパーツオブジェクトとして）。
    2. 下層パーツにベース色、上層パーツに装飾色を割り当てる。

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
    """雫型（💧）のイチゴを作成"""
    # 雫型の輪郭
    path = [
        (0, -SIZE/2),
        (-SIZE/2, -SIZE/4),
        (-SIZE/4, SIZE/2),
        (0, SIZE/2),
        (SIZE/4, SIZE/2),
        (SIZE/2, -SIZE/4),
        (0, -SIZE/2)
    ]

    # 輪郭となるWireを作成
    strawberry_wire = cq.Workplane("XY").spline(path, includeCurrent=True).close().toPending()

    # 0-4mm 全体を赤で作る
    full_body = strawberry_wire.extrude(TOTAL_HEIGHT)

    # ヘタ(緑) の形状: 上部に重なる部分を定義
    # 2.0mmから4.0mmの範囲に緑を配置
    leaves_shape = (
        cq.Workplane("XY")
        .workplane(offset=BASE_HEIGHT)
        .center(0, SIZE/4)
        .rect(SIZE*0.8, SIZE*0.5)
        .extrude(DECO_HEIGHT)
        .intersect(full_body)
    )

    # 本体(赤) から ヘタ(緑) を引く（マルチボディ化）
    strawberry_red = full_body.cut(leaves_shape)
    strawberry_green = leaves_shape

    return [
        ("strawberry_red_base", strawberry_red),
        ("strawberry_green_deco", strawberry_green)
    ]

def create_cheese():
    """ウェッジ型のチーズを作成"""
    c_size = SIZE * 1.1
    cheese_wire = (
        cq.Workplane("XY")
        .moveTo(-c_size/2, -c_size/2)
        .lineTo(c_size/2, -c_size/2)
        .lineTo(c_size/2, c_size/2)
        .close()
        .toPending()
    )

    # 0-4mm 全体
    full_cheese = cheese_wire.extrude(TOTAL_HEIGHT)

    # かじり跡を抜く
    bite = (
        cq.Workplane("XY")
        .center(c_size/2, 0)
        .circle(c_size*0.2)
        .extrude(TOTAL_HEIGHT)
    )
    full_cheese = full_cheese.cut(bite)

    # 穴(白) の装飾: 2mmから4mmの高さに配置される
    hole_positions = [
        (c_size/4, -c_size/4, c_size*0.12),
        (-c_size/8, -c_size/3, c_size*0.08),
        (c_size/2.5, c_size/4, c_size*0.07)
    ]

    cheese_white = cq.Workplane("XY").workplane(offset=BASE_HEIGHT)
    for i, (x, y, r) in enumerate(hole_positions):
        hole = (
            cq.Workplane("XY")
            .workplane(offset=BASE_HEIGHT)
            .center(x, y)
            .circle(r)
            .extrude(DECO_HEIGHT)
        )
        if i == 0:
            cheese_white = hole
        else:
            cheese_white = cheese_white.union(hole)

    # チーズ本体との交差部分のみを白とする
    cheese_white = cheese_white.intersect(full_cheese)

    # 本体(黄) から 穴(白) を引く
    cheese_yellow = full_cheese.cut(cheese_white)

    return [
        ("cheese_yellow_base", cheese_yellow),
        ("cheese_white_deco", cheese_white)
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
