import cadquery as cq
import os

"""
設計要件:
    - Arrtxアクリルマーカー64色用の色見本パレット。
    - 120mm x 120mm x 1.2mm の板を4枚作成。
        - 印刷時間・フィラメント節約のため、厚みを2.0mmから1.2mmに変更。凹み底の厚みは0.8mm（4レイヤー）確保されており強度は十分。
    - 1枚あたり16色（4列×4行）を配置。
    - 各色には、実際に塗るための凹み（24x14mm、深さ0.4mm）と、少し浮き出た色名のテキスト（高さ0.6mm）を配置。
    - ユーザーの手間を省くため、ベースとテキストを別部品とする「アセンブリ（Assembly）」としてSTEP出力。
        - Bambu Studio 読み込み時に自動でマルチパーツ認識され、黒色フィラメントを手軽に割り当て可能。

推奨フィラメント:
    - ベース: PLA Basic (White) など、インクの発色が分かりやすい白色系。
    - テキスト部分: PLA Basic (Black) などをAMSで割り当てる。

推奨スライサー設定 (Bambu Studio):
    - ウォールジェネレーター: Arachne (細かい文字の線幅を最適化するため)
    - 積層ピッチ: 0.20mm Standard (文字は垂直に押し出されるためXY解像度には影響せず0.20mmで十分綺麗に出力可能)
    - スピード: 文字のエッジをシャープにするため、Top surface を 50 mm/s、Outer wall を 100 mm/s 程度に減速推奨。
    - アイロニング: 「最上層のみ (Topmost surface only)」をオンにすると文字の天面が滑らかに仕上がる。
    - パージ量 (Flushing Volumes): 今回はZ方向で「白→黒」の1回しか切り替えが発生しない上、黒が圧倒的に勝ちやすいため、マルチプライヤはデフォルトの 1.00 または 0.5 等に下げても全く問題なく綺麗に発色する。

印刷統計（予想）:
    - 1枚あたり: 印刷時間 約45分、フィラメント使用量 約20g

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

PLATE_SIZE = 120.0
PLATE_THICKNESS = 1.2
CELL_SIZE = 30.0
RECESS_WIDTH = 24.0
RECESS_HEIGHT = 14.0
RECESS_DEPTH = 0.4
TEXT_HEIGHT = 0.6
FONT_SIZE = 6.0

# 4セットのカラー定義
COLOR_SETS = [
    [
        "A0", "A1", "A2", "A3",
        "A4", "A5", "A7", "A8",
        "A9", "A13", "A14", "A15",
        "A17", "A20", "A21", "A30"
    ],
    [
        "A33", "A34", "A35", "A40",
        "A45", "A46", "A49", "A50",
        "A51", "A52", "A54", "A55",
        "A56", "A57", "A58", "A59"
    ],
    [
        "A60", "A65", "A66", "A67",
        "A68", "A69c", "A69", "A70",
        "A71", "A72", "A73", "A75",
        "A83", "A84", "A85", "A86"
    ],
    [
        "A89", "A90", "A91", "A95",
        "A97", "A99", "A103", "A111",
        "A115", "A118", "A120", "A140",
        "A150", "A160", "A190", "A200"
    ]
]

# セル（4x4）の中心座標を計算
locs = []
for row in range(4):
    for col in range(4):
        # 120mmの板の中心が(0,0)の場合、各セルの中心を求める
        x = -45.0 + col * 30.0
        y = 45.0 - row * 30.0
        locs.append((x, y))

def create_plate(colors):
    # ベースの板を作成（Z=0からPLATE_THICKNESSまで）
    plate = cq.Workplane("XY").rect(PLATE_SIZE, PLATE_SIZE).extrude(PLATE_THICKNESS)

    # 角を少し丸める（フィレット）
    plate = plate.edges("|Z").fillet(2.0)

    # 凹みエリアの座標（セル中心からY方向に少しずらす）
    recess_locs = [(x, y + 2.0) for x, y in locs]

    # トップ面から凹みをカット
    top_plane = cq.Workplane("XY").workplane(offset=PLATE_THICKNESS)
    recesses = top_plane.pushPoints(recess_locs).rect(RECESS_WIDTH, RECESS_HEIGHT).extrude(-RECESS_DEPTH)
    plate = plate.cut(recesses)

    # テキストを作成して結合
    texts_compound = None
    for i, color_name in enumerate(colors):
        x, y = locs[i]
        # テキストは凹みの左端に合わせ、下部に配置
        text_x = x - (RECESS_WIDTH / 2.0)
        text_y = y - 9.0  # 微調整：凹みの下

        # distance は押し出しの高さ
        t = cq.Workplane("XY").workplane(offset=PLATE_THICKNESS).center(text_x, text_y).text(
            txt=color_name,
            fontsize=FONT_SIZE,
            distance=TEXT_HEIGHT,
            halign="left",
            valign="center",
            font="Arial"
        )
        if texts_compound is None:
            texts_compound = t.val()
        else:
            texts_compound = texts_compound.fuse(t.val())

    # Assemblyを利用して色を分ける
    assy = cq.Assembly()
    assy.add(plate, name="Base", color=cq.Color(0.9, 0.9, 0.9, 1.0)) # 少しグレー寄りの白の方が見やすい
    if texts_compound is not None:
        assy.add(texts_compound, name="Text", color=cq.Color(0.1, 0.1, 0.1, 1.0)) # 黒

    return assy

# ocp_vscodeがインポート可能かチェック（プレビュー用）
try:
    from ocp_vscode import show_object
    has_ocp = True
except ImportError:
    has_ocp = False

# 各プレートの生成とエクスポート
output_dir = os.path.dirname(os.path.abspath(__file__))
main_assy = cq.Assembly()

for idx, color_set in enumerate(COLOR_SETS):
    print(f"Generating Plate {idx + 1}...")
    assy = create_plate(color_set)

    # STEPファイルの出力
    step_filename = os.path.join(output_dir, f"acrylic_marker_palette_{idx + 1}.step")
    assy.save(step_filename, "STEP")
    print(f"Exported {step_filename}")

    # プレビュー用メインアセンブリに追加
    offset_y = -idx * (PLATE_SIZE + 10)
    main_assy.add(assy, name=f"Plate_{idx+1}", loc=cq.Location((0, offset_y, 0)))

# プレビュー
if has_ocp:
    show_object(main_assy, name="Acrylic_Marker_Palette_Sets")
