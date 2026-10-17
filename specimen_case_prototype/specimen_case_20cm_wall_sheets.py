"""
20cm標本ケース用 内壁ホワイトシート（平置き4枚一括配置・0.24mm厚仕様）

概要:
    20cm本番用大型標本ケース（specimen_case_20cm.py: 内寸 196.80mm × 196.80mm × 深さ 45.00mm）の
    四方の黒い横壁（内壁）を白くするための極薄ホワイトシート（4枚1セット）。
    底面に敷く厚さ 5.60mm の白いレフ板の上端から内壁上端までをカバーし、
    ビルドプレート側の美しいマット転写面を表面（内側）にして両面テープで貼り付ける方式です。

設計特徴:
    - Single Source of Truth:
      `specimen_case_20cm.py` から `INNER_W` (196.80mm) および `INNER_DEPTH` (45.00mm) を直接参照し、
      本体ケースとの寸法不整合（ドリフト）を防止。
    - 0.4mmノズル × 2層 = 厚さ 0.24mm (クロスハッチ構造):
      0.12mm × 2層により、走査線が直交（+45° / -45°）して裂けない最小厚みを実現しつつ、
      0.4mmノズルで約12〜15分の高速印刷が可能。
    - 有効高さ 39.00mm:
      ケース深さ (45.00mm) − 底面レフ板厚 (5.60mm) = 39.40mm に対し、
      上端がケース天面から飛び出して蓋の密着を妨げないよう -0.40mm の安全マージンを確保。
    - 四隅の隙間をゼロにする「先貼り2枚 (Long) ＋ 後貼り2枚 (Short)」突き合わせ設計:
      1. 先貼り用対面2枚 (Long): 幅 196.40mm
         ケース内寸 (196.80mm) に対し両端 0.20mm ずつクリアランスを持たせ、対面2辺の端から端まで貼る。
      2. 後貼り用対面2枚 (Short): 幅 195.80mm
         先に貼ったシート厚み (0.24mm × 2) ＋ 薄手両面テープ厚み (約0.15mm × 2) ＋ 微小クリアランス (0.22mm)
         を差し引き、先貼りシートの内側へ挟み込むように突き合わせることで、四隅の黒い隙間を完全ゼロ化。
    - 1プレート4枚一括配置:
      4枚をY方向に 4.0mm 間隔で整列配置（全体専有 196.40mm × 168.00mm）。
      Bambu Lab P2S (256×256mm) で1回で一括出力可能。

推奨スライサー設定 (Bambu Studio):
    - ノズル径: 0.4mm
    - プロファイル: 0.12mm High Quality @BBL P2S
    - 初期レイヤーの高さ (Initial layer height): 0.12mm に変更 (※デフォルト0.20mmから変更して2層化)
    - レイヤー高さ (Layer height): 0.12mm (0.12mm × 2層 = 0.24mm)
"""

import os
from build123d import *

from specimen_case_20cm import INNER_DEPTH, INNER_W

# ==============================================================================
# 基本パラメーター (単位: mm)
# ==============================================================================

# --- レイヤー・厚み設定 (0.4mmノズル / 0.12mm × 2層 = 0.24mm) ---
LAYER_HEIGHT = 0.12
SHEET_LAYERS = 2
SHEET_THICKNESS = SHEET_LAYERS * LAYER_HEIGHT   # 0.24mm

# --- 高さ方向の設計 ---
REFLECTOR_THICKNESS = 5.60                      # 底面に敷く白レフ板の厚み (5.60mm)
TOP_MARGIN = 0.40                               # 上端が天面から飛び出さないための安全マージン
EFFECTIVE_WALL_H = INNER_DEPTH - REFLECTOR_THICKNESS  # 45.00 - 5.60 = 39.40mm
SHEET_H = EFFECTIVE_WALL_H - TOP_MARGIN         # 39.00mm

# --- 横幅方向の設計 (四隅隙間ゼロ突き合わせ) ---
# 1. 先貼り用対面2枚 (Long): 内寸 196.80mm に対し両端 0.20mm クリアランス (計 -0.40mm)
LONG_CLEARANCE = 0.40
LONG_SHEET_W = INNER_W - LONG_CLEARANCE         # 196.40mm

# 2. 後貼り用対面2枚 (Short): 先貼りシート厚(0.24×2) + 両面テープ厚(0.15×2) + クリアランス(0.22) = -1.00mm
TAPE_THICKNESS = 0.15                           # 薄手両面テープ想定厚 (片側 0.15mm)
SHORT_FIT_CLEARANCE = 0.22                      # 突き合わせ時の微小クリアランス (片側 0.11mm)
SHORT_SHEET_W = (
    INNER_W - 2 * (SHEET_THICKNESS + TAPE_THICKNESS) - SHORT_FIT_CLEARANCE
)                                               # 195.80mm

# --- 1プレート一括配置設定 ---
PLATE_SPACING_Y = 4.0                           # シート間のY方向間隔 (4.0mm)


# ==============================================================================
# モデリング関数
# ==============================================================================

def build_wall_sheet(width: float, height: float, label: str) -> Part:
    """
    指定された幅・高さの極薄内壁ホワイトシート（1枚）を生成します。
    四隅の角まで隙間なく覆うため、ピン角の長方形シートとして造形します。
    """
    with BuildPart() as sheet:
        with BuildSketch():
            Rectangle(width, height)
        extrude(amount=SHEET_THICKNESS)

    part = sheet.part
    part.label = label
    part.color = Color("white")
    return part


def build_wall_sheet_set() -> list[Part]:
    """
    先貼り用 (Long × 2枚) と後貼り用 (Short × 2枚) の計4枚を、
    ビルドプレート中央に1プレート一括配置したリストを生成します。
    """
    sheet_specs = [
        (LONG_SHEET_W, "WallSheet_Long_1"),
        (LONG_SHEET_W, "WallSheet_Long_2"),
        (SHORT_SHEET_W, "WallSheet_Short_1"),
        (SHORT_SHEET_W, "WallSheet_Short_2"),
    ]

    pitch_y = SHEET_H + PLATE_SPACING_Y
    total_span_y = (len(sheet_specs) - 1) * pitch_y
    start_y = -total_span_y / 2.0

    placed_parts: list[Part] = []
    for i, (w, label) in enumerate(sheet_specs):
        y_pos = start_y + i * pitch_y
        part = build_wall_sheet(width=w, height=SHEET_H, label=label)
        placed = part.moved(Location((0.0, y_pos, 0.0)))
        placed.label = label
        placed.color = Color("white")
        placed_parts.append(placed)

    return placed_parts


# ==============================================================================
# 実行とSTEPエクスポート
# ==============================================================================

if __name__ == "__main__":
    output_dir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 68)
    print("20cm標本ケース用 内壁ホワイトシート (0.24mm厚・4枚一括配置) 生成")
    print("=" * 68)

    sheets = build_wall_sheet_set()
    all_compound = Compound(label="WallSheetSet_20cm", children=sheets)
    bbox = all_compound.bounding_box()

    print(f"・ケース内寸基準:     {INNER_W:.2f} × {INNER_W:.2f} × 深さ {INNER_DEPTH:.2f} mm")
    print(f"・底面レフ板厚み:     {REFLECTOR_THICKNESS:.2f} mm (有効内壁高さ {EFFECTIVE_WALL_H:.2f} mm)")
    print(f"・シート厚み:         {SHEET_THICKNESS:.2f} mm (0.12mm × {SHEET_LAYERS}層)")
    print(f"・シート高さ(共通):   {SHEET_H:.2f} mm (上端マージン -{TOP_MARGIN:.2f} mm)")
    print(f"・先貼り用 (Long×2):  幅 {LONG_SHEET_W:.2f} × 高さ {SHEET_H:.2f} × 厚さ {SHEET_THICKNESS:.2f} mm")
    print(f"・後貼り用 (Short×2): 幅 {SHORT_SHEET_W:.2f} × 高さ {SHEET_H:.2f} × 厚さ {SHEET_THICKNESS:.2f} mm")
    print(f"・4枚一括配置外寸:    横 {bbox.size.X:.2f} × 縦 {bbox.size.Y:.2f} × 厚さ {bbox.size.Z:.2f} mm")

    step_path = os.path.join(output_dir, "specimen_case_20cm_wall_sheets.step")
    export_step(all_compound, step_path)
    print(f"\nSuccessfully exported 4-sheet set STEP to:\n  {step_path}")
    print("=" * 68)

    try:
        from ocp_vscode import Camera, show
        show(*sheets, names=[s.label for s in sheets], reset_camera=Camera.RESET)
        print("OCP CAD Viewer にモデルを転送しました！")
    except Exception as e:
        print(f"OCP CAD Viewer 表示スキップ: {e}")
