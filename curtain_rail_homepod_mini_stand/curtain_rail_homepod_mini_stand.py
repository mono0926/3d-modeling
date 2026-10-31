"""
設計要件:
    - リビング後方のC型ダブルカーテンレール（厚さ実測9.5mm・1本幅約20.4mm・前後2本外寸スパン約70.0mm）の上に、
      HomePod mini 2（第2世代・球体直径97.9mm・底面シリコン足約φ48.0mm・重量335g）を両面テープ無しで常設する機械ロック式スタンド。
    - 設置推奨位置である「金属ダブルブラケットのすぐ左側（白キャップ〜ブラケット間のフラット区間）」に最適化し、
      壁穴ゼロ・カーテンランナー完全非干渉・地震やコード引っ張りでの落下リスクゼロを実現する。
    - 2段階機械ロック機構:
      1. 奥レール側: 背面〜底面外側3.5mmを抱え込む固定C字外爪（ランナー走行溝6.5mmと片側3.4mm以上離間）。
      2. 手前レール側: PETG一体バネ外爪（底面回り込み2.6mm・下端45°導入テーパー）により高所でも片手でパチンと仮固定でき、
         手前外枠のM3六角ナット＋M3×12mm（または16mm）黒六角穴付きボルトを締め込むことでガタつき・低音ビビり音をゼロ化しつつ、
         バネ爪背面の開き空間を物理的に塞ぐデッドロック構造（外寸スパン68.5〜71.8mmの写真採寸誤差を吸収）。
    - 音響ミニマル設計:
      球体メッシュ側面およびパッシブラジエーターを遮る横ガードを一切設けず（0mm）、底面の360°アコースティックウェーブガイドに
      必要なソリッド水平反射床（厚み6.9mm）と、底面シリコン足（φ48.0mm）用の極浅センタリング溝（深さ1.5mm・45°テーパー縁）のみを設ける。
    - 左側面下部（白キャップ側）に45°傾斜ガセット付きの電源コード抜け止めC字クリップ（内径φ4.5mm・導入スリット2.9mm）を一体造形。
    - 右側面（ブラケット側端面）をビルドプレート接地面（Z=0）にした横向き一体造形で、分割なしの1パーツ完結・サポート材完全ゼロ（0g）・
      一筆書き連続ループ積層によるツメ破断リスクゼロを達成する。
    - 最新の3Dプリンター（Bambu Lab P2S Combo 等）での出力を想定し、M3ボルト＆ナット実装確認も可能な薄切り嵌合テストピース（幅12.0mm）も同時出力する。

推奨フィラメント:
    - 非CFの純粋な PETG（Bambu PETG HF / Bambu PETG Basic 等、または ASA）
    - 窓際・天井付近の高温環境（45〜55℃）に耐える耐熱性・耐クリープ性と、一体バネ外爪に適したしなやかな弾性・制振性を兼ね備える。
    - PLAでも形状出力は可能だが窓際の熱クリープの観点で非推奨。また天井付近（約2m）から室内斜め下方向にあるルーター・Apple TV 4K・
      iPhone との Wi-Fi 6E (6GHz) / Bluetooth 6 / Thread / UWB 通信を減衰させないよう、炭素繊維を含まない純粋な PETG を推奨。

推奨スライサー設定:
    - ノズル径 (Nozzle): 0.6mm
    - レイヤー高さ (Layer height): 0.30mm Standard（初期レイヤー高さ 0.30mm / 全幅66.00mm＝220層、テストピース12.00mm＝40層の完全整数倍）
    - 壁面生成器 (Wall generator): Arachne（1.8mm厚の一体バネ外爪を隙間なく3周の連続壁ループで充填）
    - 壁ループ (Wall loops): 3〜4（フック首元およびM3デッドロック外枠の高剛性確保）
    - トップ / ボトムシェル (Top/Bottom shells): 各 4 層（1.20mm）
    - インフィル (Sparse infill): 20〜25% (Gyroid または Cross Hatch — 音響反射天板のソリッド感と制振性を向上)
    - サポート (Supports): なし (None / 全形状オーバーハング45°以下の完全サポートフリー設計)
    - ブリム (Brim): 不要（Z=0に約90×21mmの広いフラット接地面があるため安定）

印刷統計（予想）:
    - curtain_rail_homepod_mini_stand.step: 印刷時間 約45〜55分、フィラメント使用量 約42g
    - curtain_rail_homepod_mini_stand_fit_test.step: 印刷時間 約8〜10分、フィラメント使用量 約6g

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

import math
import os
from pathlib import Path
from build123d import *

try:
    from ocp_vscode import show_object
except ImportError:  # pragma: no cover

    def show_object(*_args, **_kwargs) -> None:
        pass


# ==============================================================================
# 定数パラメーター定義 (単位: mm)
# ==============================================================================

# --- 積層ピッチ・造形方向幅 (Z軸: 右側面 Z=0 → 左側面 Z=STAND_WIDTH) ---
LAYER_HEIGHT = 0.30
STAND_WIDTH = 220 * LAYER_HEIGHT        # 66.00mm (本番スタンド横幅)
FIT_TEST_WIDTH = 40 * LAYER_HEIGHT      # 12.00mm (M3ナット＆ボルト実装確認対応の薄切りテストピース幅)

# --- C型ダブルカーテンレール基準寸法 (u軸: 奥レール背面 u=0 → 手前 +u / v軸: レール上面 v=0 → 上 +v) ---
RAIL_THICKNESS = 9.5                    # レール高さ (ノギス/実測値)
RAIL_VERTICAL_CLEARANCE = 0.3           # 装着スムーズさとクランプ密着を両立する縦クリアランス
RAIL_SLOT_HEIGHT = RAIL_THICKNESS + RAIL_VERTICAL_CLEARANCE  # 9.80mm (v = -9.80 〜 0.00mm)

RAIL_WIDTH = 20.4                       # C型レール1本の奥行 (写真定規読み取り＆TOSO C型規格値)
RAIL_RUNNER_SLOT_WIDTH = 6.5            # C型レール底面中央のランナー走行溝幅
NOMINAL_RAIL_SPAN = 70.0                # 前後2本跨ぎの標準外寸スパン (対応範囲: 68.5〜71.8mm)

# --- 奥側固定C字外爪 & レール上面ソリッド受け座 ---
REAR_WALL_THICKNESS = 5.0               # 奥レール背面を抱える壁厚 (u = -5.00 〜 0.00mm)
REAR_HOOK_LIP_DEPTH = 3.5               # 奥レール底面外側への回り込み量 (ランナー溝まで約3.45mm余裕)
HOOK_LIP_THICKNESS = 3.2                # 前後下ツメの縦肉厚 (v = -13.00 〜 -9.80mm)
SOLID_BEARING_END_U = 66.5              # レール上面が直接当たる連続ソリッド受け座の前端u座標

# --- 手前側 PETG一体バネ外爪 (片手スナップ仮固定アーム) ---
FRONT_FLEX_REST_U = 72.0                # ボルト緩め時(自由状態)の手前バネ爪内壁u座標
FLEX_ARM_THICKNESS = 1.8                # バネ腕の肉厚 (0.6mmノズル × 3周の連続ループ壁)
FRONT_HOOK_LIP_DEPTH = 2.6              # 手前レール底面外側への回り込み量 (先端 u = 69.40mm)
FRONT_SNAP_RAMP_SIZE = 1.8              # 下端内角の45°スナップ導入テーパー寸法
FLEX_RELIEF_CEILING_V = 5.2             # バネ腕根元の掘り上げ天井v座標 (有効片持ち長 18.2mm)
FLEX_RELIEF_INNER_U = 68.2              # バネ腕が内側(68.5mm)へ押し込まれた際の逃げ天井内端u座標
FLEX_OUTER_GAP = 2.4                    # スナップ装着時にバネ腕が外側へ逃げる隙間幅 (u = 73.80 〜 76.20mm)

FLEX_BOLT_PAD_THICKNESS = 0.6           # ボルト先端が当たる中央部の背面肉盛り厚
FLEX_BOLT_PAD_HEIGHT = 8.0              # ボルト受けパッドのv方向高さ
FLEX_BOLT_PAD_WIDTH = 9.6               # ボルト受けパッドのz方向幅
FLEX_BOLT_DIMPLE_RADIUS = 1.3           # ボルト先端センタリング円錐窪み半径
FLEX_BOLT_DIMPLE_DEPTH = 0.8            # ボルト先端センタリング円錐窪み深さ

# --- 手前外側 高剛性M3デッドロック枠 (M3×12mm / 16mm 六角穴付きボルト + M3六角ナット) ---
OUTER_FRAME_INNER_U = FRONT_FLEX_REST_U + FLEX_ARM_THICKNESS + FLEX_OUTER_GAP  # 76.20mm
OUTER_FRAME_THICKNESS = 9.0             # 外枠のu方向厚み (u = 76.20 〜 85.20mm)
OUTER_FRAME_FRONT_U = OUTER_FRAME_INNER_U + OUTER_FRAME_THICKNESS              # 85.20mm

M3_AXIS_V = -4.9                        # M3ボルト・ナット中心高さ (レール厚9.5mmのほぼ中央)
M3_SHANK_CLEARANCE_RADIUS = 1.70        # M3ボルト貫通穴半径 (φ3.40mm ティアドロップ付き)
M3_CBORE_RADIUS = 3.30                  # M3キャップボルト頭ザグリ半径 (φ6.60mm ティアドロップ付き)
M3_CBORE_DEPTH = 3.40                   # 前面からのザグリ深さ (底面 u = 81.80mm、M3×12mm頭ツライチ対応)

M3_NUT_SLOT_U_START = 77.55             # M3六角ナットスロット内端u座標 (内壁1.35mm確保)
M3_NUT_SLOT_THICKNESS = 2.65            # M3六角ナット(厚2.4mm)用のスロット厚み (u = 77.55 〜 80.20mm)
M3_NUT_ACROSS_FLATS = 5.65              # M3六角ナット(二面幅5.5mm)の回転止め幅 (z方向二面幅)

# --- 音響ミニマル天板 & HomePod mini 2 底面シリコン足浅溝 ---
DECK_TOP_HEIGHT = 8.4                   # レール上面(v=0)からの天板上面高さ (ソリッド反射床厚 6.9mm)
HOMEPOD_FOOT_DIA = 48.0                 # HomePod mini 2 底面シリコン足直径
POCKET_FLOOR_CLEARANCE = 1.5            # シリコン足直径に対する浅溝底面クリアランス (片側0.75mm)
POCKET_FLOOR_DIA = HOMEPOD_FOOT_DIA + POCKET_FLOOR_CLEARANCE  # 49.50mm
POCKET_DEPTH = 1.5                      # 横滑り防止用の極浅くぼみ深さ (音響メッシュ遮蔽 0mm)
POCKET_TOP_DIA = POCKET_FLOOR_DIA + 2.0 * POCKET_DEPTH        # 52.50mm (45°テーパー縁)
POCKET_CENTER_U = 38.0                  # スピーカー載置中心u座標 (レール中央35mmより3mm室内側で壁余裕確保)

# --- 左側面下部 電源コード抜け止めC字クリップ (ストレインリリーフ) ---
CABLE_CLIP_PROTRUSION = 7.2             # 奥壁外面(u=-5.0)からの後方張り出し量 (u = -12.20 〜 -5.00mm)
CABLE_CLIP_TOP_Z_SPAN = 10.0            # フル断面クリップ長 (z = 56.00 〜 66.00mm)
CABLE_CLIP_GUSSET_START_Z = (
    STAND_WIDTH - CABLE_CLIP_TOP_Z_SPAN - CABLE_CLIP_PROTRUSION
)  # 48.80mm (45°傾斜ガセット開始z座標)
CABLE_CLIP_BORE_DIA = 4.5               # 編み込み電源コード(約φ3.5〜3.8mm)保持ボア内径
CABLE_CLIP_CENTER_U = -REAR_WALL_THICKNESS - CABLE_CLIP_PROTRUSION / 2.0  # -8.60mm
CABLE_CLIP_CENTER_V = -8.5              # コード保持ボア中心v座標
CABLE_CLIP_SLIT_GAP = 2.9               # 背面からのコード押し込みスリット幅
CABLE_CLIP_TOP_V = -3.6                 # クリップ耳部の上端フラット高さ

# --- 算出全体外寸およびXY原点センタリングオフセット ---
BOTTOM_V = -(RAIL_SLOT_HEIGHT + HOOK_LIP_THICKNESS)            # -13.00mm
MAIN_BODY_DEPTH = OUTER_FRAME_FRONT_U + REAR_WALL_THICKNESS    # 90.20mm (u = -5.00 〜 +85.20mm)
TOTAL_DEPTH_WITH_CLIP = MAIN_BODY_DEPTH + CABLE_CLIP_PROTRUSION  # 97.40mm (u = -12.20 〜 +85.20mm)
TOTAL_HEIGHT = DECK_TOP_HEIGHT - BOTTOM_V                      # 21.40mm (v = -13.00 〜 +8.40mm)

MAIN_U_OFFSET = -(OUTER_FRAME_FRONT_U + (-REAR_WALL_THICKNESS - CABLE_CLIP_PROTRUSION)) / 2.0  # -36.50mm
FIT_U_OFFSET = -(OUTER_FRAME_FRONT_U - REAR_WALL_THICKNESS) / 2.0                              # -40.10mm
V_OFFSET = -(DECK_TOP_HEIGHT + BOTTOM_V) / 2.0                                                 # +2.30mm


def _main_profile_points_and_fillets(
    u_offset: float,
) -> tuple[list[tuple[float, float]], list[tuple[float, float, float]]]:
    """2段階ロック断面の2Dポリライン頂点リストと (X, Y, R) フィレット定義を返す."""
    flex_back_u = FRONT_FLEX_REST_U + FLEX_ARM_THICKNESS
    front_lip_tip_u = FRONT_FLEX_REST_U - FRONT_HOOK_LIP_DEPTH
    front_ramp_bottom_u = front_lip_tip_u + FRONT_SNAP_RAMP_SIZE
    front_ramp_top_v = BOTTOM_V + FRONT_SNAP_RAMP_SIZE

    rear_ramp_size = 1.6
    rear_ramp_bottom_u = REAR_HOOK_LIP_DEPTH - rear_ramp_size
    rear_ramp_top_v = BOTTOM_V + rear_ramp_size

    raw_uv_with_r: list[tuple[float, float, float]] = [
        # 天板上面〜手前M3外枠外面
        (-REAR_WALL_THICKNESS, DECK_TOP_HEIGHT, 1.6),
        (OUTER_FRAME_FRONT_U, DECK_TOP_HEIGHT, 1.6),
        (OUTER_FRAME_FRONT_U, BOTTOM_V, 1.0),
        (OUTER_FRAME_INNER_U, BOTTOM_V, 0.7),
        # バネ逃げ空間天井 (u = 76.2 -> 73.8, v = +5.2)
        (OUTER_FRAME_INNER_U, FLEX_RELIEF_CEILING_V, 1.0),
        (flex_back_u, FLEX_RELIEF_CEILING_V, 1.0),
        # 手前バネ外爪下端 & 45°スナップ導入テーパー
        (flex_back_u, BOTTOM_V, 0.7),
        (front_ramp_bottom_u, BOTTOM_V, 0.5),
        (front_lip_tip_u, front_ramp_top_v, 0.3),
        (front_lip_tip_u, -RAIL_SLOT_HEIGHT, 0.25),
        (FRONT_FLEX_REST_U, -RAIL_SLOT_HEIGHT, 0.5),
        # 手前バネ腕内壁〜バネ押し込みリリーフ空間
        (FRONT_FLEX_REST_U, FLEX_RELIEF_CEILING_V, 1.0),
        (FLEX_RELIEF_INNER_U, FLEX_RELIEF_CEILING_V, 1.0),
        (SOLID_BEARING_END_U, 0.0, 0.8),
        # レール上面ソリッド受け座〜奥レール上角の応力緩和逃げ(ドッグボーンR)
        (0.6, 0.0, 0.2),
        (0.0, 0.4, 0.2),
        (-0.4, 0.4, 0.2),
        (-0.4, -0.4, 0.2),
        (0.0, -0.8, 0.2),
        # 奥レール背面突き当て壁〜奥側固定下ツメ
        (0.0, -RAIL_SLOT_HEIGHT, 0.25),
        (REAR_HOOK_LIP_DEPTH, -RAIL_SLOT_HEIGHT, 0.25),
        (REAR_HOOK_LIP_DEPTH, rear_ramp_top_v, 0.3),
        (rear_ramp_bottom_u, BOTTOM_V, 0.5),
        (-REAR_WALL_THICKNESS, BOTTOM_V, 1.2),
    ]

    pts = [(u + u_offset, v + V_OFFSET) for u, v, _ in raw_uv_with_r]
    fillets = [(u + u_offset, v + V_OFFSET, r) for u, v, r in raw_uv_with_r if r > 0.0]
    return pts, fillets


def _fillet_2d_vertices_by_coords(
    fillet_specs: list[tuple[float, float, float]], tol: float = 0.05
) -> None:
    """現在アクティブな BuildSketch 内の頂点を座標一致で検索して2Dフィレットを適用する."""
    for tx, ty, radius in fillet_specs:
        matched = [
            v
            for v in vertices()
            if math.hypot(v.X - tx, v.Y - ty) < tol
        ]
        if matched:
            fillet(matched[0], radius=radius)


def _build_teardrop_x_cutter(
    u_start: float,
    u_end: float,
    center_v: float,
    center_z: float,
    radius: float,
    u_offset: float,
) -> Part:
    """+Z頂点45°ティアドロップ断面を持つX方向(u方向)貫通穴カッターソリッドを返す."""
    x_min = u_start + u_offset
    length = u_end - u_start
    cy = center_v + V_OFFSET
    s45 = radius * math.sqrt(0.5)
    apex_z = radius * math.sqrt(2.0)

    plane = Plane(origin=(x_min, cy, center_z), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    with BuildPart() as cutter_bp:
        with BuildSketch(plane):
            Circle(radius=radius)
            Polygon(
                (s45, s45),
                (0.0, apex_z),
                (-s45, s45),
                (0.0, 0.0),
                align=None,
            )
        extrude(amount=length)
    return cutter_bp.part


def _build_m3_nut_slot_cutter(center_z: float, u_offset: float) -> Part:
    """下端面(-Y)から差し込む回転止めM3六角ナットスロット(45°山形屋根付き)カッターを返す."""
    half_flat_z = M3_NUT_ACROSS_FLATS / 2.0               # 2.825mm (Z方向二面幅半分)
    circum_r_v = M3_NUT_ACROSS_FLATS / math.sqrt(3.0)     # 3.262mm (V方向頂点半径)
    half_side_v = circum_r_v / 2.0                        # 1.631mm

    x_start = M3_NUT_SLOT_U_START + u_offset
    cy = M3_AXIS_V + V_OFFSET
    y_bottom_open = BOTTOM_V + V_OFFSET - 1.0

    # 1. XY平面で下端開口〜六角先端Vストップ形状をZ方向(二面幅5.65mm)に押し出し
    with BuildPart() as slot_bp:
        with BuildSketch(Plane.XY.offset(center_z - half_flat_z)):
            Polygon(
                (x_start, y_bottom_open),
                (x_start + M3_NUT_SLOT_THICKNESS, y_bottom_open),
                (x_start + M3_NUT_SLOT_THICKNESS, cy + half_side_v),
                (x_start, cy + half_side_v),
                align=None,
            )
        extrude(amount=M3_NUT_ACROSS_FLATS)

    # 2. ナット奥側(+Y側)の60°六角回り止めポケット部 (YZ平面断面をX方向に押し出し)
    nut_yz_plane = Plane(origin=(x_start, cy, center_z), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    with BuildPart() as hex_bp:
        with BuildSketch(nut_yz_plane):
            Polygon(
                (-half_side_v, -half_flat_z),
                (half_side_v, -half_flat_z),
                (circum_r_v, 0.0),
                (half_side_v, half_flat_z),
                (-half_side_v, half_flat_z),
                (-circum_r_v, 0.0),
                align=None,
            )
        extrude(amount=M3_NUT_SLOT_THICKNESS)

    # 3. スロット上端(+Z面)の2.65mm幅フラットブリッジを完全にゼロにする45°山形屋根リリーフ
    roof_height = M3_NUT_SLOT_THICKNESS / 2.0
    roof_xz_plane = Plane(
        origin=(x_start + M3_NUT_SLOT_THICKNESS / 2.0, cy + half_side_v, center_z + half_flat_z),
        x_dir=(1, 0, 0),
        z_dir=(0, -1, 0),
    )
    with BuildPart() as roof_bp:
        with BuildSketch(roof_xz_plane):
            Polygon(
                (-M3_NUT_SLOT_THICKNESS / 2.0, 0.0),
                (M3_NUT_SLOT_THICKNESS / 2.0, 0.0),
                (0.0, roof_height),
                align=None,
            )
        extrude(amount=(cy + half_side_v) - y_bottom_open)

    return slot_bp.part + hex_bp.part + roof_bp.part


def _build_flex_bolt_pad_and_dimple(
    total_width: float, u_offset: float
) -> tuple[Part, Part]:
    """バネ爪背面のボルト受け補強パッド(+Z/-Z 45°テーパー付き)とセンタリング円錐窪みを返す."""
    z_mid = total_width / 2.0
    flex_back_x = FRONT_FLEX_REST_U + FLEX_ARM_THICKNESS + u_offset
    cy = M3_AXIS_V + V_OFFSET

    pad_half_w = min(FLEX_BOLT_PAD_WIDTH / 2.0, total_width / 2.0 - 0.6)
    ramp = FLEX_BOLT_PAD_THICKNESS

    # XZ平面(-Y方向押し出し, local y = +Z)で上下45°テーパー付きの台形パッドを形成 (サポート不要)
    pad_xz_plane = Plane(
        origin=(flex_back_x, cy + FLEX_BOLT_PAD_HEIGHT / 2.0, z_mid),
        x_dir=(1, 0, 0),
        z_dir=(0, -1, 0),
    )
    with BuildPart() as pad_bp:
        with BuildSketch(pad_xz_plane):
            Polygon(
                (-0.4, -(pad_half_w + ramp)),
                (FLEX_BOLT_PAD_THICKNESS, -pad_half_w),
                (FLEX_BOLT_PAD_THICKNESS, pad_half_w),
                (-0.4, pad_half_w + ramp),
                align=None,
            )
        extrude(amount=FLEX_BOLT_PAD_HEIGHT)

    # ボルト先端を受ける円錐窪み (pad表面から内側へ深さ0.8mm)
    pad_outer_x = flex_back_x + FLEX_BOLT_PAD_THICKNESS
    dimple_plane = Plane(origin=(pad_outer_x + 0.05, cy, z_mid), x_dir=(0, 1, 0), z_dir=(-1, 0, 0))
    with BuildPart() as dimple_bp:
        with BuildSketch(dimple_plane):
            Circle(radius=FLEX_BOLT_DIMPLE_RADIUS)
        extrude(amount=FLEX_BOLT_DIMPLE_DEPTH + 0.05, taper=45.0)

    return pad_bp.part, dimple_bp.part


def _build_cable_clip_ear_and_cutter(u_offset: float) -> tuple[Part, Part]:
    """左側面下部の45°傾斜ガセット付き電源コード抜け止めクリップ耳部とC字開口カッターを返す."""
    x_wall = -REAR_WALL_THICKNESS + u_offset
    x_outer = x_wall - CABLE_CLIP_PROTRUSION
    y_bottom = BOTTOM_V + V_OFFSET
    y_top_flat = CABLE_CLIP_TOP_V + V_OFFSET
    y_top_blend = y_top_flat + 2.4

    # 1. XY断面(外側上下角R1.2mm＋上端壁面ブレンド付き)を Z=48.8〜66.0mm まで押し出し
    ear_height_z = STAND_WIDTH - CABLE_CLIP_GUSSET_START_Z
    with BuildPart() as ear_uv_bp:
        with BuildSketch(Plane.XY.offset(CABLE_CLIP_GUSSET_START_Z)):
            with BuildLine():
                Polyline(
                    (x_wall + 1.2, y_bottom),
                    (x_outer, y_bottom),
                    (x_outer, y_top_flat),
                    (x_wall, y_top_blend),
                    (x_wall + 1.2, y_top_blend),
                    close=True,
                )
            make_face()
            _fillet_2d_vertices_by_coords(
                [
                    (x_outer, y_bottom, 1.2),
                    (x_outer, y_top_flat, 1.2),
                ]
            )
        extrude(amount=ear_height_z)

    # 2. XZ平面(local x = +X, local y = +Z, z_dir = -Y)の45°サポートフリー傾斜ウェッジとの共通部分をとる
    wedge_xz_plane = Plane(
        origin=(0.0, y_top_blend + 1.0, 0.0),
        x_dir=(1, 0, 0),
        z_dir=(0, -1, 0),
    )
    with BuildPart() as wedge_bp:
        with BuildSketch(wedge_xz_plane):
            Polygon(
                (x_wall + 1.5, CABLE_CLIP_GUSSET_START_Z),
                (x_wall, CABLE_CLIP_GUSSET_START_Z),
                (x_outer, CABLE_CLIP_GUSSET_START_Z + CABLE_CLIP_PROTRUSION),
                (x_outer, STAND_WIDTH),
                (x_wall + 1.5, STAND_WIDTH),
                align=None,
            )
        extrude(amount=(y_top_blend - y_bottom) + 2.0)

    ear_solid = ear_uv_bp.part & wedge_bp.part

    # 3. φ4.5mm コード保持ボア ＋ 背面(-X側)導入スリット(幅2.9mm)のカッター (各Z層で上下顎が壁面に単連結)
    bore_cx = CABLE_CLIP_CENTER_U + u_offset
    bore_cy = CABLE_CLIP_CENTER_V + V_OFFSET
    with BuildPart() as cutter_bp:
        with BuildSketch(Plane.XY.offset(CABLE_CLIP_GUSSET_START_Z - 0.5)):
            with Locations((bore_cx, bore_cy)):
                Circle(radius=CABLE_CLIP_BORE_DIA / 2.0)
            with Locations(((x_outer - 1.0 + bore_cx) / 2.0, bore_cy)):
                Rectangle(bore_cx - (x_outer - 1.0), CABLE_CLIP_SLIT_GAP)
        extrude(amount=ear_height_z + 1.0)

    return ear_solid, cutter_bp.part


def _build_core_body(width: float, u_offset: float) -> Part:
    """指定幅で2段階ロック本体(M3ボルト穴・ナットスロット・バネ受けパッド込み)を生成する."""
    pts, fillets = _main_profile_points_and_fillets(u_offset)
    z_mid = width / 2.0

    with BuildPart() as bp:
        with BuildSketch(Plane.XY):
            with BuildLine():
                Polyline(*pts, close=True)
            make_face()
            _fillet_2d_vertices_by_coords(fillets)
        extrude(amount=width)

    part = bp.part
    pad_part, dimple_cutter = _build_flex_bolt_pad_and_dimple(width, u_offset)
    part = part + pad_part - dimple_cutter

    shank_cutter = _build_teardrop_x_cutter(
        u_start=OUTER_FRAME_INNER_U - 0.5,
        u_end=OUTER_FRAME_FRONT_U + 0.5,
        center_v=M3_AXIS_V,
        center_z=z_mid,
        radius=M3_SHANK_CLEARANCE_RADIUS,
        u_offset=u_offset,
    )
    cbore_cutter = _build_teardrop_x_cutter(
        u_start=OUTER_FRAME_FRONT_U - M3_CBORE_DEPTH,
        u_end=OUTER_FRAME_FRONT_U + 0.5,
        center_v=M3_AXIS_V,
        center_z=z_mid,
        radius=M3_CBORE_RADIUS,
        u_offset=u_offset,
    )
    nut_cutter = _build_m3_nut_slot_cutter(center_z=z_mid, u_offset=u_offset)

    part = part - shank_cutter - cbore_cutter - nut_cutter
    return part


def build_stand() -> Part:
    """カーテンレール上用 HomePod mini 2 機械ロック式スタンド（本番モデル）を生成して返す."""
    part = _build_core_body(width=STAND_WIDTH, u_offset=MAIN_U_OFFSET)

    # 1. 天板上面の HomePod mini 2 底面シリコン足センタリング浅溝 (深さ1.5mm・全周45°テーパー)
    pocket_cx = POCKET_CENTER_U + MAIN_U_OFFSET
    pocket_top_y = DECK_TOP_HEIGHT + V_OFFSET
    overcut = 0.05
    pocket_plane = Plane(
        origin=(pocket_cx, pocket_top_y + overcut, STAND_WIDTH / 2.0),
        x_dir=(1, 0, 0),
        z_dir=(0, -1, 0),
    )
    with BuildPart() as pocket_bp:
        with BuildSketch(pocket_plane):
            Circle(radius=POCKET_TOP_DIA / 2.0 + overcut)
        extrude(amount=POCKET_DEPTH + overcut, taper=45.0)

    part = part - pocket_bp.part

    # 2. 左側面下部の電源コード抜け止めクリップ (45°サポートフリーガセット一体型)
    clip_ear, clip_cutter = _build_cable_clip_ear_and_cutter(u_offset=MAIN_U_OFFSET)
    part = (part + clip_ear) - clip_cutter

    part.label = "curtain_rail_homepod_mini_stand"
    return part


def build_fit_test_piece() -> Part:
    """本番造形前にレール嵌合とM3ボルト＆ナットロックを約8分で実機確認できる薄切りテストピースを返す."""
    part = _build_core_body(width=FIT_TEST_WIDTH, u_offset=FIT_U_OFFSET)
    part.label = "curtain_rail_homepod_mini_stand_fit_test"
    return part


def export_models(output_dir: Path | None = None) -> tuple[Path, Path]:
    """本番モデルと事前嵌合テストピースの両方を STEP ファイルとして出力する."""
    target_dir = (
        Path(output_dir)
        if output_dir is not None
        else Path(os.path.dirname(os.path.abspath(__file__)))
    )
    target_dir.mkdir(parents=True, exist_ok=True)

    stand = build_stand()
    fit_test = build_fit_test_piece()

    main_step = target_dir / "curtain_rail_homepod_mini_stand.step"
    fit_step = target_dir / "curtain_rail_homepod_mini_stand_fit_test.step"

    export_step(stand, str(main_step))
    export_step(fit_test, str(fit_step))
    return main_step, fit_step


if __name__ == "__main__":
    stand_part = build_stand()
    fit_test_part = build_fit_test_piece()

    main_path, fit_path = export_models()
    print(f"本番モデルを出力しました: {main_path}")
    print(f"  外形寸法 (X×Y×Z): {stand_part.bounding_box().size}")
    print(f"  体積: {stand_part.volume / 1000.0:.2f} cm^3")
    print(f"嵌合テストモデルを出力しました: {fit_path}")
    print(f"  外形寸法 (X×Y×Z): {fit_test_part.bounding_box().size}")
    print(f"  体積: {fit_test_part.volume / 1000.0:.2f} cm^3")

    try:
        show_object(stand_part, name="curtain_rail_homepod_mini_stand")
        show_object(
            Pos(0.0, 35.0, 0.0) * fit_test_part,
            name="curtain_rail_homepod_mini_stand_fit_test",
        )
    except Exception as exc:  # pragma: no cover
        print(f"OCP CAD Viewer 未接続のためプレビュー送信をスキップしました: {exc}")
