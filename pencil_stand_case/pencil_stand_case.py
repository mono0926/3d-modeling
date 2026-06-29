import cadquery as cq
import os

# ocp-vscodeのインポート（環境にあれば）
try:
    from ocp_vscode import show_object
except ImportError:
    show_object = None

"""
設計要件:
    - 子供のドリル用色鉛筆（STAEDTLER Noris erasable 12本）のスタンド兼ケース。
    - 塾への持ち運びに適したフラットで頑丈なスライドフタ式ケース。
    - フタを取り外して背面の斜めスロットに差し込むことで、約65度の傾斜スタンドになる。
    - サポート材不要で印刷可能な形状（トレイは底面フラット、フタもプレート状）。

推奨フィラメント:
    - Tough PLA または PETG (持ち運び時の耐衝撃性と耐久性のため推奨)

推奨スライサー設定:
    - 壁ループ (Wall Loops): 3
    - 底面レイヤー (Bottom Shell Layers): 4
    - 上面レイヤー (Top Shell Layers): 4
    - インフィル: 15% (Grid または Gyroid)
    - サポート: 不要 (No support)

印刷統計（予想）:
    - pencil_stand_case_tray: 印刷時間 約2時間30分、フィラメント使用量 約120g
    - pencil_stand_case_lid: 印刷時間 約1時間10分、フィラメント使用量 約45g

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

# ==================== パラメーター定義 ====================
# 色鉛筆の基本寸法
PENCIL_HEX_FLAT = 6.8     # 六角形対辺
PENCIL_HEX_CORNER = 7.4   # 六角形対角
PENCIL_LENGTH = 175.0     # 長さ

# トレイ本体の設計寸法
NUM_PENCILS = 12
SLOT_WIDTH = 8.0          # 各鉛筆スロットの幅（直径、クリアランス込）
SLOT_DEPTH = 5.5          # スロットの深さ
SLOT_SPACING = 1.5        # スロット間のリブ（仕切り）の厚み
SLOT_PITCH = SLOT_WIDTH + SLOT_SPACING  # 9.5mm

TRA_INNER_LENGTH = 178.0  # 鉛筆収納部の長さ（余裕をプラス）
WALL_FRONT = 4.0          # 手前の壁厚
WALL_BACK = 16.0          # 奥の壁厚（スタンドスロット用）
TRA_LENGTH = TRA_INNER_LENGTH + WALL_FRONT + WALL_BACK  # 全長: 198.0mm
TRA_HEIGHT = 12.0         # トレイ全体の厚み

# 左右のレール溝の設計
RAIL_DEPTH = 1.5          # レール溝の深さ
RAIL_WALL_OUTER = 1.2     # レール外側の壁厚
RAIL_WALL_INNER = 1.5     # レール内側（スロット領域との間）の壁厚
SLOTS_TOTAL_WIDTH = SLOT_WIDTH * NUM_PENCILS + SLOT_SPACING * (NUM_PENCILS - 1)  # 112.5mm
TRA_WIDTH = SLOTS_TOTAL_WIDTH + (RAIL_DEPTH + RAIL_WALL_OUTER + RAIL_WALL_INNER) * 2  # 総幅: 120.9mm

RAIL_HEIGHT = 2.2         # レール溝のZ方向の高さ（クリアランス込）
RAIL_Z_OFFSET = 0.5       # トレイ上面からレール溝上面までの距離

# スライドフタの設計寸法
LID_THICKNESS = 2.0       # フタの基本厚み
LID_LENGTH = 181.8        # フタの長さ（奥壁の手前まで）
# レールの底同士 of 幅 (120.9 - 1.2 * 2 = 118.5mm) に対するクリアランス考慮
LID_WIDTH = 118.2         # フタの最大幅
LID_RAIL_RIB_WIDTH = 1.4  # レールに入る耳の幅
LID_BODY_WIDTH = LID_WIDTH - LID_RAIL_RIB_WIDTH * 2  # 中央ボディ幅: 115.4mm
LID_BODY_HEIGHT_ADD = 0.5 # トレイ上面とフラットにするため中央部を高くする厚み

# スタンド用背面スロットの設計
STAND_ANGLE = 65.0        # スタンド自立時のトレイの傾斜角度（水平から）
SLOT_ANGLE = 90.0 - STAND_ANGLE  # 25.0度（垂直からの傾き）
STAND_SLOT_WIDTH = 119.0  # スロットの幅（左右方向、フタ幅118.2に対しクリアランス確保）
STAND_SLOT_THICKNESS = 2.3  # スロットの隙間（フタ厚み2.0に対しクリアランス確保）
STAND_SLOT_DEPTH = 9.0    # 差し込み深さ

# ==================== トレイ（本体）のモデリング ====================
def build_tray():
    # 1. 基本となる直方体ブロックの作成
    tray = cq.Workplane("XY").box(TRA_WIDTH, TRA_LENGTH, TRA_HEIGHT, centered=(True, False, False))
    
    # 角の丸め（フィレット）を先に施す（エッジ選択のロバスト性向上のため）
    # 4隅の縦エッジを丸める
    tray = tray.edges("|Z").fillet(3.0)
    # 底面（Z=0）の外周エッジを丸める
    tray = tray.faces("<Z").edges().fillet(1.5)
    
    # 2. 鉛筆スロット（12本）をカット
    for i in range(NUM_PENCILS):
        x = -SLOTS_TOTAL_WIDTH / 2 + SLOT_WIDTH / 2 + i * SLOT_PITCH
        # 鉛筆スロットのシリンダーを作成
        # 中心Z: TRA_HEIGHT - (SLOT_WIDTH/2 - (SLOT_WIDTH - SLOT_DEPTH)) = 10.5mm
        cylinder = cq.Solid.makeCylinder(
            SLOT_WIDTH / 2,
            TRA_INNER_LENGTH,
            cq.Vector(x, WALL_FRONT, TRA_HEIGHT - (SLOT_WIDTH / 2 - (SLOT_WIDTH - SLOT_DEPTH))),
            cq.Vector(0, 1, 0)
        )
        tray = tray.cut(cylinder)
        
    # 3. 左右のスライドレール溝をカット (Y=182.0で行き止まりにする)
    z_rail_start = TRA_HEIGHT - RAIL_Z_OFFSET - RAIL_HEIGHT
    left_rail = cq.Solid.makeBox(
        RAIL_DEPTH + 1.0,  # 完全に外側までカットするため少し大きくする
        WALL_FRONT + TRA_INNER_LENGTH,  # Y=182.0 (手前壁から鉛筆スロット領域の端まで)
        RAIL_HEIGHT,
        cq.Vector(-TRA_WIDTH/2 - 0.5, 0, z_rail_start)
    )
    right_rail = cq.Solid.makeBox(
        RAIL_DEPTH + 1.0,
        WALL_FRONT + TRA_INNER_LENGTH,
        RAIL_HEIGHT,
        cq.Vector(TRA_WIDTH/2 - RAIL_WALL_OUTER - RAIL_DEPTH, 0, z_rail_start)
    )
    tray = tray.cut(left_rail).cut(right_rail)
    
    # 4. スタンド用の背面スロットを斜めにカット
    # 奥の壁(WALL_BACK)の中央付近に配置
    slot_y_center = TRA_LENGTH - (WALL_BACK / 2)
    # カッターを作成 (X軸を中心に回転させて斜めにする)
    # 深さ方向にはみ出す大きさで作成し、位置調整する
    cutter = cq.Solid.makeBox(
        STAND_SLOT_WIDTH,
        STAND_SLOT_THICKNESS,
        20.0,
        cq.Vector(-STAND_SLOT_WIDTH/2, -STAND_SLOT_THICKNESS/2, 0)
    )
    # X軸周りにSLOT_ANGLE (25度) 回転。Yのプラス方向（奥側）に傾く
    cutter = cutter.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), SLOT_ANGLE)
    # 底面Z=0より少し下(-1.0mm)から差し込んでカット
    cutter = cutter.translate(cq.Vector(0, slot_y_center, -1.0))
    tray = tray.cut(cutter)
    
    # 5. スナップフィット用の半球突起を追加
    # 手前側(Y=8.0mm)のレール内壁に配置
    z_bump = z_rail_start + (RAIL_HEIGHT / 2)
    bump_radius = 1.0
    # 壁面から0.35mm突き出るように球の中心Xをオフセット
    # レール内側壁面 X: TRA_WIDTH/2 - RAIL_WALL_OUTER - RAIL_DEPTH = 57.75mm
    x_wall_inner = SLOTS_TOTAL_WIDTH / 2 + RAIL_WALL_INNER  # 57.75mm
    offset_x = bump_radius - 0.35  # 0.65mm
    
    left_bump = cq.Solid.makeSphere(bump_radius).translate(cq.Vector(-(x_wall_inner + offset_x), 8.0, z_bump))
    right_bump = cq.Solid.makeSphere(bump_radius).translate(cq.Vector((x_wall_inner + offset_x), 8.0, z_bump))
    tray = tray.union(left_bump).union(right_bump)
    
    return tray

# ==================== スライドフタのモデリング ====================
def build_lid():
    # 1. ベースプレート（レールに噛み合う部分を含む幅）
    base_plate = cq.Workplane("XY").box(LID_WIDTH, LID_LENGTH, LID_THICKNESS, centered=(True, False, False))
    
    # 2. 中央の露出部分（トレイ上面と面一にするため厚くする部分）
    center_body = cq.Workplane("XY").box(
        LID_BODY_WIDTH,
        LID_LENGTH,
        LID_BODY_HEIGHT_ADD,
        centered=(True, False, False)
    ).translate(cq.Vector(0, 0, LID_THICKNESS))
    
    lid = base_plate.union(center_body)
    
    # 3. スタンド差し込みをスムーズにするため、後端の底面エッジを面取り
    # 後端 (Y = LID_LENGTH), 底面 (Z = 0) のエッジを選択
    lid = lid.edges(">Y and <Z").chamfer(0.8)
    
    # 4. 角の丸め
    # 手前側の角を落とすため、上面外周エッジ等にフィレットを施す
    lid = lid.edges("|Z").fillet(1.5)
    
    # 5. 指引っ掛け用グリップ溝を上面にカット
    # 手前側の上面(Z=LID_THICKNESS + LID_BODY_HEIGHT_ADD = 2.5mm)にX方向の溝を入れる
    for y_pos in [15.0, 20.0, 25.0]:
        grip_groove = cq.Solid.makeBox(
            80.0,
            2.0,
            0.6,
            cq.Vector(-40.0, y_pos, (LID_THICKNESS + LID_BODY_HEIGHT_ADD) - 0.6)
        )
        lid = lid.cut(grip_groove)
        
    # 6. スナップフィット用の球状凹みを側面にカット
    # トレイの突起（Y=8.0mm）に対応
    z_indent = LID_THICKNESS / 2  # レールリブの厚み中央
    indent_radius = 1.2
    # 凹み深さを0.4mmにするため球の中心をオフセット
    offset_x = indent_radius - 0.4  # 0.8mm
    # フタの端面 X: LID_WIDTH / 2 = 59.1mm
    x_lid_edge = LID_WIDTH / 2
    
    left_indent = cq.Solid.makeSphere(indent_radius).translate(cq.Vector(-(x_lid_edge - offset_x), 8.0, z_indent))
    right_indent = cq.Solid.makeSphere(indent_radius).translate(cq.Vector((x_lid_edge - offset_x), 8.0, z_indent))
    lid = lid.cut(left_indent).cut(right_indent)
    
    return lid

# ==================== メイン処理 ====================
if __name__ == "__main__":
    # モデルのビルド
    tray_model = build_tray()
    lid_model = build_lid()
    
    # 保存先パスの設定
    current_dir = os.path.dirname(__file__)
    tray_output_path = os.path.join(current_dir, "pencil_stand_case_tray.step")
    lid_output_path = os.path.join(current_dir, "pencil_stand_case_lid.step")
    
    # STEPファイルのエクスポート
    cq.exporters.export(tray_model, tray_output_path)
    print(f"Tray model exported to: {tray_output_path}")
    
    cq.exporters.export(lid_model, lid_output_path)
    print(f"Lid model exported to: {lid_output_path}")
    
    # VSCodeプレビュー用
    if show_object:
        show_object(tray_model, name="Tray")
        show_object(lid_model.translate(cq.Vector(0, 0, 20.0)), name="Lid (Raised)")
