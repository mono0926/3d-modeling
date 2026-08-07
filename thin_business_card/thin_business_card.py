"""
設計要件:
    - 0.2mmノズルおよびBambu Lab P2S (AMS) での印刷を想定した極薄2色名刺（迷子札・連絡先カード）。
    - クレジットカードサイズ (85.6mm x 54.0mm, 厚み 1.0mm, R3mm)。
    - ベース厚: 0.6mm、文字およびQRコード浮き出し高さ: 0.4mm (Z=0.6mm〜1.0mm)。
    - Z=0.6mmでのフィラメントチェンジ（パージロスなしの高速2色刷り）に対応。
    - 左側にQRコード（スキャンで直感的にテキスト表示）、右側に視認性の高い日本語テキスト（名前・TEL・緊急連絡先）を配置。
    - 個人情報保護のため、コードおよびリポジトリ上の標準値は汎用ダミー値として設計。
      コマンドライン引数 (--name, --tel, --ice) を渡すことで一時的に任意のデータでSTEPファイルを生成可能。

推奨フィラメント:
    - PLA (発色が良く微細な形状の歪みが少ないため推奨)
    - ベースと文字で高コントラストな色を選択（例：黒ベース × 白文字 / 白ベース × 赤文字など）

推奨スライサー設定:
    - ノズル径 (Nozzle size): 0.2mm (細部再現用)
    - 層高 (Layer height): 0.10mm (または 0.08mm)
    - 初期層高 (First layer height): 0.10mm
    - 変化層 (Color change height): Z = 0.60mm (全7層目でフィラメント変更を追加)
    - アイロニング (Ironing): 最上面 (Top surfaces) オプションをONにすると文字上面が美しく仕上がります

印刷統計（予想）:
    - thin_business_card.step: 印刷時間 約12分、フィラメント使用量 約6g

使用例（実データで一時的にSTEP生成する場合）:
    python thin_business_card.py --name "ご希望の名前" --tel "070-XXXX-XXXX" --ice "090-XXXX-XXXX"

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

import argparse
import os
import cadquery as cq
import qrcode
from ocp_vscode import show_object

# --- パラメーター定義 ---
CARD_WIDTH = 85.6       # クレジットカード標準幅 (mm)
CARD_HEIGHT = 54.0      # クレジットカード標準高さ (mm)
CORNER_RADIUS = 3.0     # 角丸半径 (mm)

BASE_THICKNESS = 0.6    # ベースプレートの厚み (mm) (0.1mm層高で6レイヤー)
EMBOSS_HEIGHT = 0.4     # 文字・QRコードの浮き出し高さ (mm)
TOTAL_THICKNESS = BASE_THICKNESS + EMBOSS_HEIGHT

FONT_NAME = "Hiragino Sans"  # macOS標準の視認性の高い日本語フォント


def generate_card(name_text: str, tel_text: str, ice_text: str, qr_data: str):
    # --- 1. ベースプレートの作成 ---
    card_base = (
        cq.Workplane("XY")
        .box(CARD_WIDTH, CARD_HEIGHT, BASE_THICKNESS, centered=(True, True, False))
        .edges("|Z")
        .fillet(CORNER_RADIUS)
    )

    # --- 2. QRコードの生成とソリッド化 ---
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
    CELL_SIZE = 0.75
    QR_TOTAL_SIZE = grid_size * CELL_SIZE  # 約 24.75mm

    QR_CENTER_X = -CARD_WIDTH / 2.0 + 8.0 + (QR_TOTAL_SIZE / 2.0)
    QR_CENTER_Y = 0.0

    qr_points = []
    for row in range(grid_size):
        for col in range(grid_size):
            if matrix[row][col]:
                x = (col - grid_size / 2.0 + 0.5) * CELL_SIZE + QR_CENTER_X
                y = (grid_size / 2.0 - row - 0.5) * CELL_SIZE + QR_CENTER_Y
                qr_points.append((x, y))

    qr_solids = (
        card_base.faces(">Z")
        .workplane(offset=-0.05)
        .pushPoints(qr_points)
        .rect(CELL_SIZE, CELL_SIZE)
        .extrude(EMBOSS_HEIGHT + 0.05)
    )

    # --- 3. テキストの追加 ---
    TEXT_CENTER_X = CARD_WIDTH / 4.0 + 3.0

    # 名前
    name_solid = (
        card_base.faces(">Z")
        .workplane(offset=-0.05)
        .center(TEXT_CENTER_X, 12.0)
        .text(
            name_text,
            fontsize=7.5,
            distance=EMBOSS_HEIGHT + 0.05,
            font=FONT_NAME,
            halign="center",
            valign="center",
            kind="bold",
        )
    )

    # TEL
    formatted_tel = tel_text if tel_text.startswith("TEL:") else f"TEL: {tel_text}"
    tel_solid = (
        card_base.faces(">Z")
        .workplane(offset=-0.05)
        .center(TEXT_CENTER_X, -2.0)
        .text(
            formatted_tel,
            fontsize=4.2,
            distance=EMBOSS_HEIGHT + 0.05,
            font=FONT_NAME,
            halign="center",
            valign="center",
            kind="regular",
        )
    )

    # 緊急連絡先 (ICE)
    formatted_ice = ice_text if ice_text.startswith("緊急:") else f"緊急: {ice_text}"
    ice_solid = (
        card_base.faces(">Z")
        .workplane(offset=-0.05)
        .center(TEXT_CENTER_X, -13.0)
        .text(
            formatted_ice,
            fontsize=4.2,
            distance=EMBOSS_HEIGHT + 0.05,
            font=FONT_NAME,
            halign="center",
            valign="center",
            kind="bold",
        )
    )

    # 全パーツをブーリアン結合
    result = card_base.union(qr_solids).union(name_solid).union(tel_solid).union(ice_solid)
    return result


def main():
    parser = argparse.ArgumentParser(description="極薄2色名刺（迷子札・連絡先カード）生成スクリプト")
    parser.add_argument("--name", default="名刺 太郎", help="表示するお名前 (デフォルト: 名刺 太郎)")
    parser.add_argument("--tel", default="070-0000-0000", help="電話番号 (デフォルト: 070-0000-0000)")
    parser.add_argument("--ice", default="090-0000-0000", help="緊急連絡先 (デフォルト: 090-0000-0000)")
    parser.add_argument("--qr-data", default=None, help="QRコードに込めるデータ (未指定時は名前・電話番号・緊急連絡先から自動生成)")
    args = parser.parse_args()

    name_text = args.name
    tel_text = args.tel
    ice_text = args.ice

    if args.qr_data:
        qr_data = args.qr_data
    else:
        formatted_tel = tel_text if tel_text.startswith("TEL:") else f"TEL: {tel_text}"
        formatted_ice = ice_text if ice_text.startswith("緊急:") else f"緊急: {ice_text}"
        qr_data = f"名前: {name_text}\n{formatted_tel}\n{formatted_ice}"

    result = generate_card(name_text, tel_text, ice_text, qr_data)

    # ocp_vscode プレビュー表示
    try:
        show_object(result, name="thin_business_card")
    except Exception:
        pass

    # STEPファイル出力
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(current_dir, "thin_business_card.step")

    cq.exporters.export(result, output_path)
    print(f"モデルを出力しました: {output_path}")
    print(f"  [名]: {name_text}")
    print(f"  [TEL]: {tel_text}")
    print(f"  [緊急]: {ice_text}")


if __name__ == "__main__":
    main()
