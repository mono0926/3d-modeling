"""
無針標本用極薄マウントシート（極細針フリクション固定・下部ラベル余白付き）

概要:
    虫本体に針を刺さず、虫の縦横サイズ（脚を含む）に合わせた極薄白シートに虫をボンド接着し、
    シートの対角2箇所の極小穴に φ0.32mm の昆虫針を通してレフ板（スチレンボード）へ固定する方式。
    下端には2Dプリンターで印刷した名前ラベル（10pt・1行分）を両面テープで貼るためのスペース（+6.0mm）を備えています。

設計特徴:
    - パラメトリック一括生成:
      単一の生成関数 `build_mount_sheet` に対して虫の寸法リスト `BUG_DIMENSIONS` を渡し、
      コピペなしで各サイズのSTEPファイルおよび一括印刷用セットSTEPを生成します。
    - ラベル1行分の下部スペース (+6.0mm):
      虫の後脚の間の空間が自然な上余白となるため、虫とのマージンは0mmとし、
      純粋に「10pt文字ラベル高さ (4.0mm) + 下端余白 (2.0mm) = +6.0mm」を縦長さに加算。
    - 裏返し（ビルドプレート面＝表面）前提の対角2点ピン穴:
      ビルドプレート接地側（Z=0）の滑らかな面を表（上）として使うため、
      印刷状態を上から見たときに「右上 (+X, +Y)」と「左下 (-X, -Y)」に穴を配置。
      裏返して表面を上にした際、真上から見て「左上」と「右下」に穴が来ます。
    - φ0.32mm 針に最適化したフリクション穴 (CAD径 φ0.20mm / スライサー設定変更不要):
      Bambu P2S (0.2mmノズル) デフォルトのエレファントフット補正 (0.15mm) と樹脂の内径収縮（約0.20mm）を逆算し、
      CAD上で φ0.20mm に設計。スライサーを一切いじらずデフォルトのまま印刷するだけで、
      1層目（表側）は針先を誘導する約 φ0.25〜0.30mm の極小ガイドとなり、
      2〜3層目（裏側）は極小ピンホールとなって φ0.32mm の針を強力に摩擦保持（フリクションホールド）します。
    - シート厚み 0.30mm (3層):
      0.2mmノズル標準プロファイル（0.10mm Standard: 初期レイヤー0.10mm + 0.10mm×2層 = 3層）に完全整合。
      レフ板との段差が目立たない極薄でありながら、剥がす際やボンド接着時に折れ曲がらない適度なコシを確保。
"""

import os
from build123d import *

# ==============================================================================
# 基本パラメーター (単位: mm)
# ==============================================================================

# 作成する虫の縦横サイズリスト: (縦長さ bug_length, 横幅 bug_width)
BUG_DIMENSIONS: list[tuple[float, float]] = [
    (54.0, 43.0),
    (56.0, 51.0),
]

# 下端のラベル1行分スペース (10pt文字高さ約3.5〜4.0mm + 下余白2.0mm = +6.0mm)
LABEL_SPACE_H = 4.0         # 10pt文字ラベル高さ
BOTTOM_MARGIN = 2.0         # シート下端からの余白
EXTRA_LENGTH = LABEL_SPACE_H + BOTTOM_MARGIN  # +6.0mm

# シート基本形状 (0.2mmノズル 0.10mm Standard プロファイル × 3層 = 0.30mm)
LAYER_HEIGHT = 0.10
SHEET_LAYERS = 3
SHEET_THICKNESS = SHEET_LAYERS * LAYER_HEIGHT  # 0.30mm
CORNER_RADIUS = 2.0         # 四隅の角丸半径

# 針穴パラメーター (φ0.32mm 昆虫針用・スライサーデフォルト設定完全適合)
PIN_HOLE_DIAMETER = 0.20    # CAD上の穴径 (P2Sデフォルト設定で1層目がガイド、2〜3層目がタイト保持になる黄金値)
PIN_HOLE_OFFSET = 2.5       # シート外周端から穴中心までの距離 (縦・横共通)


# ==============================================================================
# モデリング関数
# ==============================================================================

def build_mount_sheet(bug_length: float, bug_width: float) -> Part:
    """
    指定された虫の縦横サイズから、下部ラベルスペース(+6.0mm)と対角2箇所の針穴を備えた
    極薄マウントシートを生成します。

    引数:
        bug_length: 虫の縦長さ (Y方向, mm)
        bug_width:  虫の横幅 (X方向, mm)

    戻り値:
        Part: 生成されたマウントシートの3Dソリッド
    """
    sheet_w = bug_width
    sheet_l = bug_length + EXTRA_LENGTH

    # 印刷時に上から見て「右上 (+hx, +hy)」と「左下 (-hx, -hy)」に配置
    # （裏返して滑らかなベッド面を上にした際、「左上」と「右下」になる）
    hx = (sheet_w / 2.0) - PIN_HOLE_OFFSET
    hy = (sheet_l / 2.0) - PIN_HOLE_OFFSET
    hole_locations = [
        (hx, hy),    # 印刷時: 右上 -> 裏返し後(表): 左上
        (-hx, -hy),  # 印刷時: 左下 -> 裏返し後(表): 右下
    ]

    with BuildPart() as sheet:
        with BuildSketch() as sk:
            rect = Rectangle(sheet_w, sheet_l)
            fillet(rect.vertices(), radius=CORNER_RADIUS)
            with Locations(hole_locations):
                Circle(radius=PIN_HOLE_DIAMETER / 2.0, mode=Mode.SUBTRACT)
        extrude(amount=SHEET_THICKNESS)

    part = sheet.part
    part.label = f"MountSheet_Bug_{int(bug_length)}x{int(bug_width)}"
    part.color = Color("white")
    return part


# ==============================================================================
# 実行とSTEPエクスポート
# ==============================================================================

if __name__ == "__main__":
    output_dir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 65)
    print("無針標本用極薄マウントシート (針固定・下部ラベル余白+6mm) 一括生成")
    print("=" * 65)

    placed_parts: list[Part] = []
    current_x = 0.0
    spacing_x = 10.0  # セット配置時のシート間スペース

    for bug_l, bug_w in BUG_DIMENSIONS:
        sheet_part = build_mount_sheet(bug_length=bug_l, bug_width=bug_w)
        bbox = sheet_part.bounding_box()

        # 個別STEPファイルの出力
        filename = f"specimen_mount_sheet_{int(bug_l)}x{int(bug_w)}.step"
        step_path = os.path.join(output_dir, filename)
        export_step(sheet_part, step_path)

        print(
            f"・虫サイズ {bug_l:.0f}×{bug_w:.0f}mm -> "
            f"シート外寸: 縦 {bbox.size.Y:.1f} × 横 {bbox.size.X:.1f} × 厚さ {bbox.size.Z:.2f} mm "
            f"(針穴: 端から{PIN_HOLE_OFFSET}mm, CAD径 φ{PIN_HOLE_DIAMETER}mm)"
        )
        print(f"  -> Exported: {step_path}")

        # 一括配置用の位置計算
        offset_x = current_x + (bbox.size.X / 2.0)
        placed_parts.append(sheet_part.moved(Location((offset_x, 0, 0))))
        current_x += bbox.size.X + spacing_x

    # 全サイズを1プレートに並べたセットSTEPファイルの出力
    all_compound = Compound(label="MountSheetSet", children=placed_parts)
    all_step_path = os.path.join(output_dir, "specimen_mount_sheet_all.step")
    export_step(all_compound, all_step_path)
    print(f"\n・一括印刷用セットSTEP: {all_step_path}")
    print("=" * 65)

    try:
        from ocp_vscode import show, Camera
        show(*placed_parts, names=[p.label for p in placed_parts], reset_camera=Camera.RESET)
        print("OCP CAD Viewer にモデルを転送しました！")
    except Exception as e:
        print(f"OCP CAD Viewer 表示スキップ: {e}")
