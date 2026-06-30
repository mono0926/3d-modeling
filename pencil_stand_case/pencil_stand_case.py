"""
設計要件:
    - 12本の色鉛筆（長さ17.5cm、最大径7.4mm）を収納するケース。
    - 持ち運び時は筆箱として、開けると縦型のペンスタンドとして機能する。
    - 2列×6本の配置で、スリムでカバンに入れやすい角丸長方形デザイン。
    - 各鉛筆が独立した穴に収まるため、カチャカチャ音が鳴らず芯が折れにくい。
    - スリップフィット（摩擦）によるキャップの固定。

推奨フィラメント:
    - PLA または PETG (適度な弾性がありスリップフィットに適しているため)

推奨スライサー設定:
    - 層の高さ (Layer Height): 0.20 mm
    - インフィル (Infill): 15% (ジャイロイド推奨)
    - サポート (Supports): 不要 (キャップの内側天井はブリッジで印刷可能)
    - ブリッジが不安な場合は、キャップを印刷する際だけツリーサポートを少量有効にするか、天井の角度にテーパーを付けることも考えられますが、幅23mm程度なら最新プリンターであればブリッジで綺麗に印刷可能です。

印刷統計（予想）:
    - ベース: 約 50g, 印刷時間 約1.5時間
    - キャップ: 約 40g, 印刷時間 約1時間

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

import cadquery as cq
import os

# ==========================================
# パラメーター定義 (単位: mm)
# ==========================================

# 鉛筆の寸法
PENCIL_LENGTH = 175.0
PENCIL_DIAMETER = 7.4

# 穴の寸法と配置
PENCIL_CLEARANCE = 0.6  # 3Dプリントの収縮と抜き差しのスムーズさを考慮した余裕分（直径）
HOLE_DIAMETER = PENCIL_DIAMETER + PENCIL_CLEARANCE  # 穴の直径（8.0mm）
HOLE_DEPTH = 75.0  # ベースに挿さる深さ
COLUMNS = 4
ROWS = 3
PITCH_X = 10.5
PITCH_Y = 10.5

# 構造の寸法
WALL_THICKNESS = 1.2
BASE_BOTTOM_THICKNESS = 1.2
CAP_TOP_THICKNESS = 1.2
LIP_HEIGHT = 10.0  # ベースの上部に設ける、キャップと重なる段差の高さ

# スリップフィットのクリアランス (片側)
# 印刷済みのベース（設計上の隙間なし）に対してキャップをキツめにするため、
# マイナスの値を設定してキャップの内寸を物理的に小さくします。
LIP_CLEARANCE = -0.03

# キャップの内寸深さ
# ベース段差（Z=67）からの鉛筆露出長 = 175 - 75 (挿入深さ) + 10 (リップ高) = 110mm
# それに天井の余裕として3mm足す
CAP_INNER_HEIGHT = 113.0

# ------------------------------------------
# 計算値
# ------------------------------------------
# リップ部（段差部分）の外形寸法
LIP_WIDTH = (COLUMNS - 1) * PITCH_X + HOLE_DIAMETER + 4.0  # 65.0
LIP_DEPTH = (ROWS - 1) * PITCH_Y + HOLE_DIAMETER + 4.0   # 23.0
LIP_FILLET_R = 4.0

# ベース下部（外装）の外形寸法
BASE_WIDTH = LIP_WIDTH + 2 * WALL_THICKNESS  # 69.0
BASE_DEPTH = LIP_DEPTH + 2 * WALL_THICKNESS  # 27.0
BASE_FILLET_R = LIP_FILLET_R + WALL_THICKNESS  # 6.0

# キャップの外形寸法（ベース外装と同じ）
CAP_WIDTH = BASE_WIDTH
CAP_DEPTH = BASE_DEPTH
CAP_FILLET_R = BASE_FILLET_R

# ベースとキャップの高さ
BASE_TOTAL_HEIGHT = HOLE_DEPTH + BASE_BOTTOM_THICKNESS
BASE_BODY_HEIGHT = BASE_TOTAL_HEIGHT - LIP_HEIGHT
CAP_TOTAL_HEIGHT = CAP_INNER_HEIGHT + CAP_TOP_THICKNESS

# ==========================================
# ベース部品（スタンド）の生成
# ==========================================
def create_base():
    # 1. 下部（外装部分）
    base_body = (
        cq.Workplane("XY")
        .box(BASE_WIDTH, BASE_DEPTH, BASE_BODY_HEIGHT)
        .edges("|Z").fillet(BASE_FILLET_R)
    )

    # 2. リップ部（キャップが被さる細い部分）
    lip = (
        cq.Workplane("XY").workplane(offset=BASE_BODY_HEIGHT/2)
        .box(LIP_WIDTH, LIP_DEPTH, LIP_HEIGHT, centered=(True, True, False))
        .edges("|Z").fillet(LIP_FILLET_R)
    )

    # リップ部と結合
    base = base_body.union(lip)

    # 3. 鉛筆用の穴を開ける
    # 穴の座標リストを生成
    pts = []
    start_x = -((COLUMNS - 1) * PITCH_X) / 2
    start_y = -((ROWS - 1) * PITCH_Y) / 2
    for c in range(COLUMNS):
        for r in range(ROWS):
            pts.append((start_x + c * PITCH_X, start_y + r * PITCH_Y))

    # 上面から穴を掘る
    base = (
        base.faces(">Z").workplane()
        .pushPoints(pts)
        .hole(HOLE_DIAMETER, HOLE_DEPTH)
    )

    # 4. 面取り（キャップが入りやすいようにリップの上端を面取り）
    # リップ部の上面外周エッジを取得して面取り
    base = base.edges(">Z and %LINE").chamfer(0.8)

    # 底面の面取り
    base = base.edges("<Z").chamfer(1.0)

    # Z軸方向の位置を調整して、底面がZ=0になるようにする
    base = base.translate((0, 0, BASE_BODY_HEIGHT/2))

    return base

# ==========================================
# キャップ部品の生成
# ==========================================
def create_cap():
    # 1. キャップの外形
    cap = (
        cq.Workplane("XY")
        .box(CAP_WIDTH, CAP_DEPTH, CAP_TOTAL_HEIGHT)
        .edges("|Z").fillet(CAP_FILLET_R)
    )

    # 2. 内側をくり抜くための形状を作成
    inner_width = LIP_WIDTH + 2 * LIP_CLEARANCE
    inner_depth = LIP_DEPTH + 2 * LIP_CLEARANCE
    inner_fillet = LIP_FILLET_R + LIP_CLEARANCE

    inner_box = (
        cq.Workplane("XY")
        .box(inner_width, inner_depth, CAP_INNER_HEIGHT, centered=(True, True, False))
        .edges("|Z").fillet(inner_fillet)
        .translate((0, 0, -CAP_TOTAL_HEIGHT/2))
    )

    # くり抜く
    cap = cap.cut(inner_box)

    # 3. 面取り（ベースに入りやすいように開口部の内側エッジを面取り）
    # 底面の内側エッジを選択して面取り
    cap = cap.faces("<Z").edges("%LINE").chamfer(0.8)

    # 天面の外周面取り
    cap = cap.faces(">Z").edges("%LINE").chamfer(1.0)

    # 底面がZ=0になるように調整
    cap = cap.translate((0, 0, CAP_TOTAL_HEIGHT/2))
    return cap

# ==========================================
# テストフィット用部品の生成
# ==========================================
def create_test_fit():
    # ベース側のリップ部のみ（高さ10mm）
    test_base = (
        cq.Workplane("XY")
        .box(LIP_WIDTH, LIP_DEPTH, 10.0)
        .edges("|Z").fillet(LIP_FILLET_R)
        .edges(">Z").chamfer(0.8)
        .translate((0, 40, 5)) # 少しY方向にずらす
    )

    # キャップ側の下部のみ（高さ10mm）
    cap_inner_w = LIP_WIDTH + 2 * LIP_CLEARANCE
    cap_inner_d = LIP_DEPTH + 2 * LIP_CLEARANCE
    cap_inner_r = LIP_FILLET_R + LIP_CLEARANCE

    test_cap_inner = (
        cq.Workplane("XY")
        .box(cap_inner_w, cap_inner_d, 20.0) # 貫通させるため長めに
        .edges("|Z").fillet(cap_inner_r)
    )

    test_cap = (
        cq.Workplane("XY")
        .box(CAP_WIDTH, CAP_DEPTH, 10.0)
        .edges("|Z").fillet(CAP_FILLET_R)
        .cut(test_cap_inner)
        .faces("<Z").edges("%LINE").chamfer(0.8)
        .faces(">Z").edges("%LINE").chamfer(0.8)
        .translate((0, -40, 5)) # 反対にずらす
    )

    return test_base, test_cap

# ==========================================
# 実行とエクスポート
# ==========================================
base = create_base()
cap = create_cap()
test_base, test_cap = create_test_fit()

# VSCode等でのプレビュー用
try:
    from ocp_vscode import show_object
    show_object(base, name="Base", options={"color": (150, 150, 150), "alpha": 0.0})
    # キャップはZ方向に浮かせて表示
    show_object(cap.translate((0, 0, BASE_TOTAL_HEIGHT + 20)), name="Cap", options={"color": (100, 150, 200), "alpha": 0.3})
    show_object(test_base, name="Test_Base")
    show_object(test_cap, name="Test_Cap")
except Exception as e:
    print("ocp_vscode is not available:", e)

# Stepファイルの出力
out_dir = os.path.dirname(os.path.abspath(__file__))
cq.exporters.export(base, os.path.join(out_dir, "base.step"))
cq.exporters.export(cap, os.path.join(out_dir, "cap.step"))
cq.exporters.export(test_base, os.path.join(out_dir, "test_base.step"))
cq.exporters.export(test_cap, os.path.join(out_dir, "test_cap.step"))

print("Export completed successfully.")
