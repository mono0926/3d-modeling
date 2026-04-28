import cadquery as cq
import os

"""
設計要件:
    - Arrtxアクリルマーカー64色用の色見本パレット。
    - 120mm x 120mm x 2mm の板を4枚作成。
    - 1枚あたり16色（4列×4行）を配置。
    - 各色には、実際に塗るための凹み（24x14mm、深さ0.4mm）と、少し浮き出た色名のテキスト（高さ0.6mm）を配置。
    - 最新の3Dプリンター（Bambu Lab P2S 等）での出力を想定。
    - スライサーにて、ベース部分と文字部分の色を塗り分けて印刷することを想定。

推奨フィラメント:
    - PLA Basic (White) など、色が映える白系のベースを推奨。
    - テキスト部分は PLA Basic (Black) などをAMSで割り当てる。

推奨スライサー設定:
    - 0.16mm Optimal @BBL X1C (または P2S) などの細かい積層ピッチ（テキストをきれいに印刷するため）。
    - 印刷時の着色: 「塗りつぶし（Fill）」ツールで角度（Angle）を利用し、浮き出たテキスト部分を一括で色指定するか、高さモディファイアでレイヤーごとの色変更を行う。

印刷統計（予想）:
    - 1枚あたり: 印刷時間 約1時間、フィラメント使用量 約30g

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

PLATE_SIZE = 120.0
PLATE_THICKNESS = 2.0
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
            
    if texts_compound is not None:
        plate = plate.union(texts_compound)
        
    return plate

# ocp_vscodeがインポート可能かチェック（プレビュー用）
try:
    from ocp_vscode import show_object
    has_ocp = True
except ImportError:
    has_ocp = False

# 各プレートの生成とエクスポート
output_dir = os.path.dirname(os.path.abspath(__file__))

plates = []
for idx, color_set in enumerate(COLOR_SETS):
    print(f"Generating Plate {idx + 1}...")
    plate = create_plate(color_set)
    plates.append(plate)
    
    # STEPファイルの出力
    step_filename = os.path.join(output_dir, f"acrylic_marker_palette_{idx + 1}.step")
    cq.exporters.export(plate, step_filename)
    print(f"Exported {step_filename}")

# プレビュー
if has_ocp:
    for idx, plate in enumerate(plates):
        offset_y = -idx * (PLATE_SIZE + 10)
        show_object(plate.translate((0, offset_y, 0)), name=f"Plate_{idx+1}")
