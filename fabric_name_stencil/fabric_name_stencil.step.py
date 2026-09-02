"""
設計要件:
    - 布に「おなまえ」と書くためのステンシルプレート。
    - 薄い平面プレートに、文字「おなまえ」の形状をくり抜いた構造。
    - フォント: ヒラギノ角ゴシック W4（/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc）。
    - 布サイズ: 4×8cm（40mm×80mm）に書くことを想定。
    - テキストはプレート中央に配置。
    - 最新の3Dプリンター（Bambu Lab P2S 等）での出力を想定。
    - モデルごとに専用ディレクトリで管理し、STEPファイルを出力する。

    寸法設計:
        - font_size=18mm → テキスト幅 約68mm、高さ 約15mm
        - プレート: 80mm(W) × 25mm(H) × 1.2mm(厚さ)
        - テキスト上下センタリング: バウンディングボックス補正オフセット -4.77mm

推奨フィラメント:
    - PLA（扱いやすく精度が出やすい。ステンシルの薄板に最適）
    - PETG でも代用可能だが、薄板の反り対策としてPLAを推奨。

推奨スライサー設定:
    - 積層ピッチ (Layer Height): 0.15mm（精細モード、文字エッジの品質向上）
    - 外壁数 (Wall Loops): 3（薄板の強度確保）
    - インフィル (Infill): 15%（薄板なのでほぼ外壁のみだが安定のため）
    - サポート (Support): なし（フラットな造形のためサポート不要）
    - ブリム (Brim): あり（薄板の反り防止）

印刷統計（予想）:
    - fabric_name_stencil.step: 印刷時間 約10〜15分、フィラメント使用量 約3〜5g

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

import os
from build123d import *

# ============================================================
# パラメーター定義
# ============================================================

# フォント設定
FONT_PATH = "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc"
TEXT_STR = "おなまえ"
FONT_SIZE = 18.0          # テキストサイズ [mm]（幅 約75mm, 高さ 約17mm）

# プレート寸法
PLATE_WIDTH = 80.0        # 幅 [mm]（布80mmより少し大きく）
PLATE_HEIGHT = 25.0       # 高さ [mm]（テキスト高さ17mm + 上下余白各4mm）
PLATE_THICKNESS = 0.4     # 厚さ [mm]（薄い平面。布にあてやすい）

# 角丸（取り扱いやすさのため）
CORNER_RADIUS = 2.0       # [mm]


# ============================================================
# gen_step() 定義 — CADスキルが呼び出すエントリーポイント
# ============================================================

def gen_step():
    """
    ヒラギノ角ゴシック W4 で「おなまえ」をくり抜いた薄板ステンシルを生成する。

    座標系:
        Origin: プレート中心（XY中央、Z=0が底面）
        XY: 主スケッチ面
        +Z: 押し出し方向（上方向）
    """

    # ----------------------------------------------------------
    # 1. ベースプレート（角丸矩形を押し出し）
    # ----------------------------------------------------------
    with BuildPart() as part:
        with BuildSketch() as plate_sk:
            # XY中心を原点とした角丸矩形
            RectangleRounded(PLATE_WIDTH, PLATE_HEIGHT, CORNER_RADIUS)

        # 底面 Z=0 からプレート厚さ分押し出す
        extrude(amount=PLATE_THICKNESS)

        # ----------------------------------------------------------
        # 2. 文字「おなまえ」をくり抜く（subtract）
        # ----------------------------------------------------------
        # 上面（+Z向きの面の中で最も高い位置にあるもの）にスケッチを配置
        top_face = part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
        with BuildSketch(top_face) as text_sk:
            # ヒラギノ角ゴシック W4 で中央配置テキスト
            # TextAlign.CENTER はベースライン基準のため、ひらがなは視覚的に上寄りになる。
            # バウンディングボックスから算出した補正オフセット（-4.77mm）でY方向を調整する。
            TEXT_Y_OFFSET = -4.77  # 視覚的上下センタリング補正 [mm]
            with Locations([(0, TEXT_Y_OFFSET)]):
                Text(
                    TEXT_STR,
                    font_size=FONT_SIZE,
                    font_path=FONT_PATH,
                    text_align=(TextAlign.CENTER, TextAlign.CENTER),
                    mode=Mode.ADD,
                )

        # テキストをプレート厚さ + 0.2mm 分 subtract（確実に貫通）
        extrude(amount=-(PLATE_THICKNESS + 0.2), mode=Mode.SUBTRACT)

    stencil = part.part
    stencil.label = "fabric_name_stencil"

    return stencil


# ============================================================
# スクリプト直接実行時: STEPファイルを出力してプレビュー
# ============================================================

if __name__ == "__main__":
    from ocp_vscode import show_object
    import os

    result = gen_step()

    # スクリプトと同じディレクトリに STEP 出力
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "fabric_name_stencil.step")
    export_step(result, output_path)
    print(f"STEP exported to: {output_path}")

    show_object(result, name="fabric_name_stencil")
