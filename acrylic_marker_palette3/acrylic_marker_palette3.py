import cadquery as cq
import os
import unicodedata
from OCP.Font import Font_SystemFont, Font_FontMgr, Font_FontAspect
from OCP.TCollection import TCollection_AsciiString

"""
設計要件:
    - アクリルマーカーの「基本6色」および「メタリック6色」用の色見本パレット。
    - 220mm x 110mm x 1.6mm の板を1枚作成。
        - 上段（基本6色）、下段（メタリック6色）の2セクション構成。
        - 各行の上部にセクション見出し（"BASIC", "METALLIC"）を浮き彫りで配置。
    - 各色には、実際に塗るための凹み（12x12mm、深さ0.4mm）と、少し浮き出た日本語色名のテキスト（高さ0.6mm）を配置。
    - ユーザーの手間を省くため、ベースとテキストを別部品とする「アセンブリ（Assembly）」としてSTEP出力。
        - Bambu Studio 読み込み時に自动でマルチパーツ認識され、黒色フィラメントを手軽に割り当て可能。

推奨フィラメント:
    - ベース: PLA Basic (White) など、インクの発色が分かりやすい白色系。
    - テキスト部分: PLA Basic (Black) などをAMSで割り当てる。

推奨スライサー設定 (Bambu Studio):
    - ウォールジェネレーター (Wall generator): Arachne (細かい文字の線幅を最適化するため)
    - 積層ピッチ (Layer height): 0.20mm Standard (文字は垂直に押し出されるためXY解像度には影響せず0.20mmで十分綺麗に出力可能)
    - スピード (Speed): 文字のエッジをシャープにするため、Top surface を 50 mm/s、Outer wall を 100 mm/s 程度に減速推奨。
    - アイロニング (Ironing): 「最上層のみ (Topmost surface only)」をオンにすると文字の天面が滑らかに仕上がる。
    - パージ量 (Flushing Volumes): Z方向で「白→黒」の1回しか切り替えが発生しないため、マルチプライヤを 0.5 等に下げても問題なく綺麗に発色。

印刷統計（予想）:
    - acrylic_marker_palette3.step: 印刷時間 約70分、フィラメント使用量 約35g

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

# --- 日本語フォントの登録 ---
# OCP (Open Cascade) が日本語フォントを検出できるように、システムフォントを明示的に登録します。
def register_japanese_font():
    candidates = [
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
    ]
    
    font_path = None
    for p in candidates:
        nfd_path = unicodedata.normalize('NFD', p)
        if os.path.exists(nfd_path):
            font_path = nfd_path
            break
            
    if font_path:
        mgr = Font_FontMgr.GetInstance_s()
        system_font = Font_SystemFont(TCollection_AsciiString("CustomJapanese"))
        system_font.SetFontPath(Font_FontAspect.Font_FA_Regular, TCollection_AsciiString(font_path))
        system_font.SetFontPath(Font_FontAspect.Font_FA_Bold, TCollection_AsciiString(font_path))
        mgr.RegisterFont(system_font, True)
        print(f"Registered custom font: CustomJapanese from {font_path}")
    else:
        print("Warning: No Japanese font found in system paths. CJK characters might render as squares.")

# 実行時にフォントを登録
register_japanese_font()

# --- 設計パラメーター ---
PLATE_WIDTH = 220.0
PLATE_HEIGHT = 110.0
PLATE_THICKNESS = 1.6
PLATE_CORNER_RADIUS = 3.0

# セル（バレット）設定
RECESS_WIDTH = 12.0
RECESS_HEIGHT = 12.0
RECESS_DEPTH = 0.4

# セル配置設定
CELL_SPACING_X = 32.0
CELL_COLS = 6

# セクションごとのY座標
BASIC_HEADER_Y = 38.0
BASIC_CELL_Y = 22.0
METALLIC_HEADER_Y = -12.0
METALLIC_CELL_Y = -28.0

# テキスト設定
FONT_SIZE_LABEL = 6.0  # セクション見出しのフォントサイズ
FONT_SIZE_COLOR = 3.2  # 色名のフォントサイズ
TEXT_HEIGHT = 0.6      # 浮き出し高さ
FONT_NAME = "CustomJapanese"  # 登録したフォント名を使用

# 色名定義
BASIC_COLORS = [
    "セルリアンブルー",
    "イエロー",
    "オレンジ",
    "コーラルレッド",
    "マゼンタ",
    "バイオレット"
]

METALLIC_COLORS = [
    "オールドローズ",
    "ローズゴールド",
    "ブルー",
    "ターコイズブルー",
    "オレンジゴールド",
    "ピンク"
]

# X座標の計算 (6列を左右対称に配置)
# -80.0, -48.0, -16.0, 16.0, 48.0, 80.0
x_coords = [(col - (CELL_COLS - 1) / 2.0) * CELL_SPACING_X for col in range(CELL_COLS)]

def create_palette():
    # 1. ベースプレートの作成（Z=0からPLATE_THICKNESSまで）
    plate = cq.Workplane("XY").rect(PLATE_WIDTH, PLATE_HEIGHT).extrude(PLATE_THICKNESS)
    plate = plate.edges("|Z").fillet(PLATE_CORNER_RADIUS)

    # 2. 凹みエリアの座標リストを作成
    recess_locs = []
    # BASIC セル
    for x in x_coords:
        recess_locs.append((x, BASIC_CELL_Y))
    # METALLIC セル
    for x in x_coords:
        recess_locs.append((x, METALLIC_CELL_Y))

    # トップ面から凹みをカット
    top_plane = cq.Workplane("XY").workplane(offset=PLATE_THICKNESS)
    recesses = top_plane.pushPoints(recess_locs).rect(RECESS_WIDTH, RECESS_HEIGHT).extrude(-RECESS_DEPTH)
    plate = plate.cut(recesses)

    # 3. テキストの作成と結合
    texts_compound = None

    def add_text_to_compound(compound, txt, x, y, size, font_name, height):
        t = cq.Workplane("XY").workplane(offset=PLATE_THICKNESS).center(x, y).text(
            txt=txt,
            fontsize=size,
            distance=height,
            halign="center",
            valign="center",
            font=font_name
        )
        if compound is None:
            return t.val()
        else:
            return compound.fuse(t.val())

    # セクション見出しの追加
    texts_compound = add_text_to_compound(texts_compound, "BASIC", 0.0, BASIC_HEADER_Y, FONT_SIZE_LABEL, FONT_NAME, TEXT_HEIGHT)
    texts_compound = add_text_to_compound(texts_compound, "METALLIC", 0.0, METALLIC_HEADER_Y, FONT_SIZE_LABEL, FONT_NAME, TEXT_HEIGHT)

    # BASICの色名を追加
    for i, color_name in enumerate(BASIC_COLORS):
        x = x_coords[i]
        y = BASIC_CELL_Y - (RECESS_HEIGHT / 2.0 + 5.0)  # 凹みの下
        texts_compound = add_text_to_compound(texts_compound, color_name, x, y, FONT_SIZE_COLOR, FONT_NAME, TEXT_HEIGHT)

    # METALLICの色名を追加
    for i, color_name in enumerate(METALLIC_COLORS):
        x = x_coords[i]
        y = METALLIC_CELL_Y - (RECESS_HEIGHT / 2.0 + 5.0)  # 凹みの下
        texts_compound = add_text_to_compound(texts_compound, color_name, x, y, FONT_SIZE_COLOR, FONT_NAME, TEXT_HEIGHT)

    # 4. Assemblyを利用して色を分ける
    assy = cq.Assembly()
    assy.add(plate, name="Base", color=cq.Color(0.9, 0.9, 0.9, 1.0)) # 白系
    if texts_compound is not None:
        assy.add(texts_compound, name="Text", color=cq.Color(0.1, 0.1, 0.1, 1.0)) # 黒

    return assy

# ocp_vscodeがインポート可能かチェック（プレビュー用）
try:
    from ocp_vscode import show_object
    has_ocp = True
except ImportError:
    has_ocp = False

# プレートの生成とエクスポート
output_dir = os.path.dirname(os.path.abspath(__file__))

print("Generating Acrylic Marker Palette 3...")
assy = create_palette()

# STEPファイルの出力
step_filename = os.path.join(output_dir, "acrylic_marker_palette3.step")
assy.save(step_filename, "STEP")
print(f"Exported {step_filename}")

# プレビュー
if has_ocp:
    show_object(assy, name="Acrylic_Marker_Palette_3")
