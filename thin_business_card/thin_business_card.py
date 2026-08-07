"""
設計要件:
    - build123d を使用して構築された、0.2mmノズルおよびBambu Lab P2S (AMS) 想定のトランプ並み極薄2色名刺（迷子札・連絡先カード）。
    - クレジットカードサイズ (85.6mm x 54.0mm, 総厚み 0.50mm, R3mm 角丸)。
    - ベース厚: 0.30mm (0.10mm層高で3層)、文字およびQRコード浮き出し高さ: 0.20mm (Z=0.30mm〜0.50mm)。
    - 【パーフェクト・バランス設計】:
      QRコードと右側テキスト群の全体幅を精密計算し、カード全体の左右余白(約14.5mm)が完全に均等になる完璧なセンタリング配置を導入。
    - 【Bambu Studio / AMS 全自動2色刷り対応】:
      マルチパーツ構造 (CardBase + CardEmboss) にそれぞれ Color 属性を埋め込んで STEP 出力。
      Bambu Studio に読み込むだけでパーツごとに自動認識され、AMSのフィラメントを各パーツに割り当てるだけで全自動印刷可能。
    - 【自動フィッティング機能】: テキスト長さを自動検出し、カード幅からはみ出さないよう動的にフォントサイズを最適化。
    - 個人情報保護のため、標準値は汎用ダミー値。コマンドライン引数 (--name, --tel, --ice) で一時的に任意のデータ指定が可能。

推奨フィラメント:
    - PLA (発色が良く微細な形状の歪みが少ないため推奨)
    - スロット1: ベース色 (例: 白/ゴールド/黒)
    - スロット2: 文字・QR色 (例: 黒/赤/白)

推奨スライサー設定 (Bambu Studio):
    - インポート時ダイアログ: 「複数のオブジェクトを含むファイルです。アセンブリとして読み込みますか？」 -> **【はい (Yes)】** を選択
    - オブジェクトツリー割り当て:
      - `CardBase` -> フィラメント 1
      - `CardEmboss` -> フィラメント 2
    - ノズル径 (Nozzle size): 0.2mm (細部再現用)
    - 壁面生成器 (Wall generator): **Arachne** (可変線幅により細かい文字やQRコードのエッジ・輪郭を最適化するため必須推奨)
    - 層高 (Layer height): 0.10mm (または 0.08mm)
    - 初期層高 (First layer height): 0.10mm
    - アイロニング (Ironing): 最上面 (Top surfaces) オプションをONにすると文字上面が美しく仕上がります

印刷統計（予想）:
    - thin_business_card.step: 印刷時間 約6〜8分、フィラメント使用量 約3g

使用例（実データで一時的にSTEP生成する場合）:
    python thin_business_card.py --name "ご希望の名前" --tel "070-XXXX-XXXX" --ice "090-XXXX-XXXX"

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

import argparse
import os
import unicodedata
from build123d import *
import qrcode
from OCP.Font import Font_FontAspect, Font_FontMgr, Font_SystemFont
from OCP.TCollection import TCollection_AsciiString

# --- 日本語フォントの明示的登録 ---
FONT_NAME = "CustomJapanese"


def register_japanese_font():
    candidates = [
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]

    font_path = None
    for p in candidates:
        nfd_path = unicodedata.normalize("NFD", p)
        if os.path.exists(nfd_path):
            font_path = nfd_path
            break

    if font_path:
        mgr = Font_FontMgr.GetInstance_s()
        system_font = Font_SystemFont(TCollection_AsciiString(FONT_NAME))
        system_font.SetFontPath(Font_FontAspect.Font_FA_Regular, TCollection_AsciiString(font_path))
        system_font.SetFontPath(Font_FontAspect.Font_FA_Bold, TCollection_AsciiString(font_path))
        mgr.RegisterFont(system_font, True)
        print(f"Registered custom font: {FONT_NAME} from {font_path}")
    else:
        print("Warning: No Japanese font found in system paths.")


# 実行時にフォントを登録
register_japanese_font()

# --- パラメーター定義 ---
CARD_WIDTH = 85.6       # クレジットカード標準幅 (mm)
CARD_HEIGHT = 54.0      # クレジットカード標準高さ (mm)
CORNER_RADIUS = 3.0     # 角丸半径 (mm)

BASE_THICKNESS = 0.30   # ベースプレートの厚み (mm)
EMBOSS_HEIGHT = 0.20    # 浮き出し高さ (mm)
TOTAL_THICKNESS = BASE_THICKNESS + EMBOSS_HEIGHT  # 計 0.50mm

QR_CELL_SIZE = 0.65     # QRコードのセル1個のサイズ (mm)
ELEMENT_MARGIN = 5.5    # QRコードとテキスト間の余白 (mm)


def get_fitted_font_size(text_str: str, initial_size: float, max_width: float, font_name: str) -> float:
    """テキストが最大可用幅(max_width)を超える場合、動的にフォントサイズを縮小スケールする"""
    with BuildSketch() as sk:
        Text(text_str, font_size=initial_size, font=font_name)
    bb = sk.sketch.bounding_box()
    width = bb.max.X - bb.min.X
    if width > max_width and width > 0:
        return initial_size * (max_width / width)
    return initial_size


def generate_card(name_text: str, tel_text: str, ice_text: str, qr_data: str):
    # --- 1. ベースカードの生成 ---
    with BuildPart() as base_builder:
        with BuildSketch() as sk:
            Rectangle(CARD_WIDTH, CARD_HEIGHT)
            fillet(sk.vertices(), radius=CORNER_RADIUS)
        extrude(amount=BASE_THICKNESS)

    card_base = base_builder.part
    card_base.label = "CardBase"
    card_base.color = Color("gold")

    # --- 2. QRコードデータの生成 ---
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=1,
        border=0,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    matrix = qr.get_matrix()

    grid_size = len(matrix)
    QR_TOTAL_SIZE = grid_size * QR_CELL_SIZE  # 約 21.45mm

    # --- 3. パーフェクト・レイアウトの動的センタリング計算 ---
    formatted_tel = tel_text if tel_text.startswith("TEL:") else f"TEL: {tel_text}"
    formatted_ice = ice_text if ice_text.startswith("緊急:") else f"緊急: {ice_text}"

    # TELテキストの標準サイズ(3.2mm)での幅を測定
    with BuildSketch() as sk_measure:
        Text(formatted_tel, font_size=3.2, font=FONT_NAME)
    tel_width = sk_measure.sketch.bounding_box().max.X - sk_measure.sketch.bounding_box().min.X

    # コンテンツ全体の総幅と両端余白の計算
    total_content_width = QR_TOTAL_SIZE + ELEMENT_MARGIN + tel_width
    side_margin = (CARD_WIDTH - total_content_width) / 2.0  # 左右均等余白 (約 14.0mm 〜 14.5mm)

    # 各エレメントのX座標確定
    QR_CENTER_X = -CARD_WIDTH / 2.0 + side_margin + (QR_TOTAL_SIZE / 2.0)
    QR_RIGHT_X = QR_CENTER_X + (QR_TOTAL_SIZE / 2.0)
    TEXT_START_X = QR_RIGHT_X + ELEMENT_MARGIN
    MAX_TEXT_WIDTH = CARD_WIDTH / 2.0 - 4.5 - TEXT_START_X

    # --- 4. QRコードのソリッド化 ---
    qr_points = []
    for row in range(grid_size):
        for col in range(grid_size):
            if matrix[row][col]:
                x = (col - grid_size / 2.0 + 0.5) * QR_CELL_SIZE + QR_CENTER_X
                y = (grid_size / 2.0 - row - 0.5) * QR_CELL_SIZE
                qr_points.append((x, y))

    with BuildPart() as qr_builder:
        with BuildSketch(Plane.XY.offset(BASE_THICKNESS)) as sk_qr:
            with Locations(qr_points):
                Rectangle(QR_CELL_SIZE, QR_CELL_SIZE)
        extrude(amount=EMBOSS_HEIGHT)

    qr_part = qr_builder.part

    # --- 5. テキストの生成（左揃え・完全バランス配置） ---
    # 名前
    name_font_size = get_fitted_font_size(name_text, 5.8, MAX_TEXT_WIDTH, FONT_NAME)
    with BuildPart() as name_builder:
        with BuildSketch(Plane.XY.offset(BASE_THICKNESS)) as sk_name:
            with Locations((TEXT_START_X, 11.0)):
                Text(name_text, font_size=name_font_size, font=FONT_NAME, align=(Align.MIN, Align.CENTER))
        extrude(amount=EMBOSS_HEIGHT)

    # TEL
    tel_font_size = get_fitted_font_size(formatted_tel, 3.2, MAX_TEXT_WIDTH, FONT_NAME)
    with BuildPart() as tel_builder:
        with BuildSketch(Plane.XY.offset(BASE_THICKNESS)) as sk_tel:
            with Locations((TEXT_START_X, -2.0)):
                Text(formatted_tel, font_size=tel_font_size, font=FONT_NAME, align=(Align.MIN, Align.CENTER))
        extrude(amount=EMBOSS_HEIGHT)

    # 緊急連絡先 (ICE)
    ice_font_size = get_fitted_font_size(formatted_ice, 3.2, MAX_TEXT_WIDTH, FONT_NAME)
    with BuildPart() as ice_builder:
        with BuildSketch(Plane.XY.offset(BASE_THICKNESS)) as sk_ice:
            with Locations((TEXT_START_X, -13.0)):
                Text(formatted_ice, font_size=ice_font_size, font=FONT_NAME, align=(Align.MIN, Align.CENTER))
        extrude(amount=EMBOSS_HEIGHT)

    # 凸要素（QR + 名前 + TEL + 緊急）の統合
    emboss_part = qr_part + name_builder.part + tel_builder.part + ice_builder.part
    emboss_part.label = "CardEmboss"
    emboss_part.color = Color("black")

    # 全体を Compound としてまとめる (Bambu Studio / AMS 全自動マルチカラー認識用)
    card_compound = Compound(label="ThinBusinessCard", children=[card_base, emboss_part])
    return card_compound


def main():
    parser = argparse.ArgumentParser(description="build123dによる極薄2色名刺（迷子札・連絡先カード）生成スクリプト")
    parser.add_argument("--name", default="名刺 太郎", help="表示するお名前 (デフォルト: 名刺 太郎)")
    parser.add_argument("--tel", default="070-0000-0000", help="電話番号 (デフォルト: 070-0000-0000)")
    parser.add_argument("--ice", default="090-0000-0000", help="緊急連絡先 (デフォルト: 090-0000-0000)")
    parser.add_argument("--qr-data", default=None, help="QRコードに込めるデータ (未指定時はMeCARDフォーマットで自動生成)")
    args = parser.parse_args()

    name_text = args.name
    tel_text = args.tel
    ice_text = args.ice

    if args.qr_data:
        qr_data = args.qr_data
    else:
        clean_tel = "".join(filter(str.isdigit, tel_text))
        clean_ice = "".join(filter(str.isdigit, ice_text))
        qr_data = f"MECARD:N:{name_text};TEL:{clean_tel};NOTE:緊急連絡先 {ice_text} (TEL:{clean_ice});;"

    card_compound = generate_card(name_text, tel_text, ice_text, qr_data)

    # ocp_vscode プレビュー表示
    try:
        from ocp_vscode import show_object
        show_object(card_compound, name="thin_business_card")
    except Exception:
        pass

    # STEPファイル出力
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(current_dir, "thin_business_card.step")

    export_step(card_compound, output_path)
    print(f"build123d (AMS全自動対応・0.50mm極薄) モデルを出力しました: {output_path}")
    print(f"  [名]: {name_text}")
    print(f"  [TEL]: {tel_text}")
    print(f"  [緊急]: {ice_text}")


if __name__ == "__main__":
    main()
