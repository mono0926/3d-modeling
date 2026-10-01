"""
無針標本用極薄マウントシート (0.2mmノズル / AMSマルチカラー対応)

概要:
    昆虫針を使わずに標本をボンド固定・ケース底面に両面テープ貼り付けできる極薄シート。
    0.2mmノズルによる極めて精密な文字出力と、白ベースシート上に黒文字ラベルを
    AMSマルチカラー印刷（2ボディCompound）で成形します。

設計特徴:
    - レイヤー高さ: 0.08mm (0.2mmノズルの高精細標準レイヤー)
    - 白ベースシート: 厚み 0.40mm (5層、下地の黒ケースが絶対に透けない純白)
    - 黒テキスト(エンボス): 厚み 0.16mm (2層、白ベースから浮き出るレリーフ文字)
    - 総厚み: わずか 0.56mm (超軽量・ペラペラで反りゼロ)
    - マルチボディ構造: 白ベースと黒文字が別ソリッドとしてCompoundに格納され、
      Bambu Studioで開くだけで自動的にマルチパーツ認識され、スロット色を指定可能。
    - 四隅R: 2.0mm (角が立ってめくれ上がらないよう品のあるフィレット)
    - 20cm四方ケース(大中/小中レイアウト)および現行小型ケース(内寸72.8×123.8mm)両対応。
"""

import os
from pathlib import Path
from typing import Optional, Tuple
from build123d import *

# ==============================================================================
# 基本パラメーター (0.2mm ノズル用 / 単位: mm)
# ==============================================================================

LAYER_HEIGHT = 0.08         # 0.2mmノズル用レイヤー高さ (0.08mm Standard)
BASE_LAYERS = 5             # 白ベース層数 (5層 = 0.40mm、完全遮光純白)
TEXT_LAYERS = 2             # 黒文字層数 (2層 = 0.16mm、上品なレリーフ浮き彫り)

BASE_THICKNESS = BASE_LAYERS * LAYER_HEIGHT   # 0.40mm
TEXT_THICKNESS = TEXT_LAYERS * LAYER_HEIGHT   # 0.16mm
TOTAL_THICKNESS = BASE_THICKNESS + TEXT_THICKNESS  # 0.56mm

SHEET_CORNER_R = 2.0        # シート四隅のめくれ防止フィレット半径

# ==============================================================================
# 日本語フォント探索
# ==============================================================================

def find_japanese_font_path() -> str:
    """
    環境内の適切な日本語フォントパスを自動探索します。
    3Dプリント文字に適した、視認性の高い太めのゴシック体を優先します。
    """
    candidates = [
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W5.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("適切な日本語フォントファイルが見つかりませんでした。")


# ==============================================================================
# マウントシート生成ロジック
# ==============================================================================

def build_mount_sheet(
    sheet_width: float,
    sheet_length: float,
    label_text: str = "",
    font_size: float = 4.2,
    label_bottom_margin: float = 6.0,
    font_path: Optional[str] = None
) -> Compound:
    """
    単一の無針標本用マウントシートを生成します。

    戻り値:
        Compound: [0] = base_sheet (白), [1] = label_text (黒、テキストがある場合)
    """
    if font_path is None and label_text:
        font_path = find_japanese_font_path()

    # 1. 白ベースシート (Z=0.00 〜 BASE_THICKNESS)
    with BuildPart() as base:
        with BuildSketch() as sk:
            r = Rectangle(sheet_width, sheet_length)
            fillet(r.vertices(), radius=SHEET_CORNER_R)
        extrude(amount=BASE_THICKNESS)

    children = [base.part]

    # 2. 黒文字エンボス (Z=BASE_THICKNESS 〜 BASE_THICKNESS + TEXT_THICKNESS)
    if label_text:
        # 下端からのマージン位置にテキスト中心を配置
        text_center_y = -(sheet_length / 2) + label_bottom_margin + (font_size / 2)
        with BuildPart() as text_part:
            with BuildSketch(Plane.XY.offset(BASE_THICKNESS)):
                with Locations((0, text_center_y)):
                    Text(
                        label_text,
                        font_size=font_size,
                        font_path=font_path,
                        text_align=(TextAlign.CENTER, TextAlign.CENTER)
                    )
            extrude(amount=TEXT_THICKNESS)

        children.append(text_part.part)

    # マルチボディ Compound として結合
    sheet_compound = Compound(children=children)
    return sheet_compound


# ==============================================================================
# プリセット定義 (大・中・小)
# ==============================================================================

def build_sheet_large(label_text: str = "ヤマトカブトムシ") -> Compound:
    """
    【大】ヤマトカブトムシ等（虫想定 100mm × 50mm）
    シート外寸: 66.0mm × 120.0mm
    ※現行小型ケース(内寸72.8×123.8mm)にもジャストフィット！
    """
    return build_mount_sheet(
        sheet_width=66.0,
        sheet_length=120.0,
        label_text=label_text,
        font_size=4.2,
        label_bottom_margin=5.5
    )


def build_sheet_medium(label_text: str = "ノコギリクワガタ") -> Compound:
    """
    【中】クワガタ類・中型甲虫等（虫想定 65mm × 42mm）
    シート外寸: 66.0mm × 85.0mm
    """
    return build_mount_sheet(
        sheet_width=66.0,
        sheet_length=85.0,
        label_text=label_text,
        font_size=3.8,
        label_bottom_margin=6.0
    )


def build_sheet_small(label_text: str = "アオカナブン") -> Compound:
    """
    【小】カナブン・コガネムシ・小型甲虫等（虫想定 35mm × 26mm）
    シート外寸: 66.0mm × 55.0mm
    """
    return build_mount_sheet(
        sheet_width=66.0,
        sheet_length=55.0,
        label_text=label_text,
        font_size=3.5,
        label_bottom_margin=5.5
    )


def build_20cm_case_layout() -> Compound:
    """
    20cm四方ケース (内寸 196mm × 196mm) 用の「大中 / 小中」4枚配置レイアウト
        左列: 大 (上) + 小 (下)
        右列: 中 (上) + 中 (下)
    """
    sheet_large = build_sheet_large("ヤマトカブトムシ")
    sheet_small = build_sheet_small("アオカナブン")
    sheet_med_top = build_sheet_medium("ノコギリクワガタ")
    sheet_med_bottom = build_sheet_medium("ヒラタクワガタ")

    # 配置座標 (ケース中心を 0, 0 とする)
    col_x_left = -45.0      # 左列中心 X
    col_x_right = 45.0      # 右列中心 X

    # 左列: 大 (Y=+32.0mm) + 小 (Y=-63.5mm)
    placed_large = sheet_large.moved(Location((col_x_left, 32.0, 0)))
    placed_small = sheet_small.moved(Location((col_x_left, -63.5, 0)))

    # 右列: 中上 (Y=+45.5mm) + 中下 (Y=-49.5mm)
    placed_med_top = sheet_med_top.moved(Location((col_x_right, 45.5, 0)))
    placed_med_bottom = sheet_med_bottom.moved(Location((col_x_right, -49.5, 0)))

    return Compound(children=[placed_large, placed_small, placed_med_top, placed_med_bottom])


# ==============================================================================
# メイン実行 & エクスポート
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("無針標本用極薄マウントシート (0.2mmノズル / AMS対応) 生成")
    print("=" * 60)

    font_path = find_japanese_font_path()
    print(f"・使用フォント: {font_path}")
    print(f"・積層設定: レイヤー高さ {LAYER_HEIGHT}mm (0.2mmノズル)")
    print(f"・厚み構成: 白ベース {BASE_THICKNESS:.2f}mm ({BASE_LAYERS}層) + 黒文字 {TEXT_THICKNESS:.2f}mm ({TEXT_LAYERS}層) = 総厚 {TOTAL_THICKNESS:.2f}mm")

    # 1. 単体「大」シート (ヤマトカブトムシ) - 現行ケース実機テスト用
    large_sheet = build_sheet_large("ヤマトカブトムシ")
    bbox_large = large_sheet.bounding_box()
    print(f"\n【大シート (ヤマトカブトムシ)】")
    print(f"  寸法: {bbox_large.size.X:.1f} × {bbox_large.size.Y:.1f} × {bbox_large.size.Z:.2f} mm")
    print(f"  ソリッド数: {len(large_sheet.children)} (白ベース + 黒テキスト)")

    # 2. 20cmケース 4枚配置レイアウト
    layout_20cm = build_20cm_case_layout()
    bbox_20cm = layout_20cm.bounding_box()
    print(f"\n【20cmケース用 4枚配置レイアウト (大中/小中)】")
    print(f"  専有寸法: {bbox_20cm.size.X:.1f} × {bbox_20cm.size.Y:.1f} × {bbox_20cm.size.Z:.2f} mm (内寸196mm内に完璧に収束)")
    print(f"  シート数: {len(layout_20cm.children)} (計4シート、各2ソリッド)")

    # STEP エクスポート
    output_dir = os.path.dirname(__file__)
    single_step_path = os.path.join(output_dir, "specimen_mount_sheet.step")
    set_step_path = os.path.join(output_dir, "specimen_mount_sheet_20cm_set.step")

    export_step(large_sheet, single_step_path)
    print(f"\nSuccessfully exported single sheet to: {single_step_path}")

    export_step(layout_20cm, set_step_path)
    print(f"Successfully exported 20cm layout set to: {set_step_path}")
    print("=" * 60)

    try:
        from ocp_vscode import show, Camera
        show(large_sheet, layout_20cm, names=["mount_sheet_large", "layout_20cm_set"], reset_camera=Camera.RESET)
        print("OCP CAD Viewer にモデルを転送しました！")
    except Exception as e:
        print(f"OCP CAD Viewer 表示スキップ: {e}")
