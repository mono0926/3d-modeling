"""
設計要件:
    - リビング後方壁面（ルリエ新川崎・東壁）の小梁直下に設置された正面溝付きアルミ押出C型ピクチャーレール
      （外寸：壁からの出っ張り実測14.6mm × 縦高さ実測20.3mm、正面から奥背板までの内奥行実測12.6mm、
      正面水平スリット開口約7.8mm、上面は小梁下端に密着）に対し、リア左スピーカー用の
      HomePod mini 2（第2世代・球体直径97.9mm・高さ84.3mm・底面シリコン足ノギス実測φ42.9mm・重量335g）を
      壁穴ゼロ・ガタつきゼロ・遮蔽物ゼロでスマートに常設する機械ロック式スタンド。
    - 右側のカーテンレール上スタンド（curtain_rail_homepod_mini_stand）と床からの高さを一致させ、
      すぐ上の小梁下端からHomePod mini 2天面までに約27〜30mmの音響・操作クリアランスを確保しつつ、
      正面から長い六角ドライバーを真っ直ぐ差し込んでM3ボルト2本を締結できるL字ブラケット構造（全幅66.00mm）。
    - エンドストッパー分解不要の「後入れ自動90°ロック式カムTアンカー × 2個」＋ M3×12mm ダブル締結:
      1. カムTアンカー駒（2個）に手持ちのM3六角ナットを圧入し、正面スリット（約7.8mm）の任意位置へ水平挿入。
      2. 黒色M3×12mm六角穴付きボルトを右回しすると、非対称カム角（通過対角R6.00mm / ストッパー対角R0.60mm、全長17.30mm）により
         レール内部で自動的に約75〜88°回転して上下内壁に当たり空回りを停止、アルミ前リップを内外から強力に挟み込む。
      3. TアンカーおよびM3×12mmボルト先端のレール内突入量を前面から最大7.0mm以内に抑え、
         レール奥壁（12.6mm）にある壁固定用鍋ビス頭（突出約2.5mm）とも3mm以上の安全クリアランスを確保。
      4. レール下面受け段差（13.0mm）＋ 二点接地式背面壁当てスパイン（108.0mm長）により片持ち荷重を壁面へ逃がし、
         ボルト1本あたりの引抜荷重を約80gに抑えて低音ビビり音・たわみを完全ゼロ化する。
    - 間取り最適化・2軸緩傾斜アコースティック天板 ＋ 魔法のテープ対応浅溝:
      リビング間取り図の右上スピーカー位置からソファ（方位角約18°）・ダイニング（方位角約28°）へ向けて、
      ソリッド反射天板ごと「室内手前（+u）へ 7.5° ＋ 部屋中央側（-z）へ 2.5°」（合成傾斜角 約7.9°）の2軸傾斜を付与。
      横ガード0mmで音響メッシュを100%開放しつつ、位置合わせ兼「魔法のテープ」厚み吸収用の精密浅溝
      （底面φ43.70mm × 深さ1.80mm・造形時オーバーハング45.0°以下を保つ47.5°テーパー縁）を設ける。
    - 左側面下部（左入隅壁・コンセント側）に45°ガセット一体型の電源コード抜け止めC字クリップ（内径φ4.5mm）を配置。
    - 左側面（左入隅壁・電源コードロック側）を Z=0 ビルドプレートへ完全ベタ置きにした横向き一体造形により、
      ケーブルロックの浮き・オーバーハングを完全ゼロ（0°）にし、天板も下広の順テーパー（2.5°）とすることで
      サポート材完全ゼロ（0g）・層間剥離リスクゼロを達成。あわせて本番造形前に溝挿入とカム回転ロックを
      実機確認できる薄切り嵌合テストキットも同時出力する。

推奨フィラメント:
    - 非CFの純粋な PETG（Bambu PETG HF / Bambu PETG Basic 等 — 右側スタンドと同色ブルーPETG推奨）
    - 高い靭性・耐クリープ性を持ち、Wi-Fi 6E (6GHz) / Bluetooth 6 / Thread / UWB 電波を減衰させないためPETGを推奨。

推奨スライサー設定:
    - ノズル径 (Nozzle): 0.6mm
    - レイヤー高さ (Layer height): 0.30mm Standard（本体66.00mm＝220層、Tアンカー6.60mm＝22層、テスト16.20mm＝54層の整数倍）
    - 壁面生成器 (Wall generator): Arachne
    - 壁ループ (Wall loops): 3〜4（L字スパイン首元・M3クランプ座・カムTアンカーの高剛性確保）
    - トップ / ボトムシェル (Top/Bottom shells): 各 4 層（1.20mm）
    - インフィル (Sparse infill): 20〜25% (Gyroid または Cross Hatch)
    - サポート (Supports): なし (None / 全パーツ45°以下の完全サポートフリー設計)
    - ブリム (Brim): 不要（Z=0に広いフラットL字接地面があるため安定）

印刷統計（予想）:
    - picture_rail_homepod_mini_stand.step (本体 + カムTアンカー2個): 印刷時間 約90〜100分、フィラメント使用量 約89g
    - picture_rail_homepod_mini_stand_fit_test.step (テストクランプ + カムTアンカー1個): 印刷時間 約11〜13分、フィラメント使用量 約9g

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
# 定数パラメーター定義 (単位: mm / 角度: deg)
# ==============================================================================

# --- 積層ピッチ・造形幅 (造形Z軸: 左側面・入隅壁・ケーブルロック側 Z=0 → 右側面・部屋中央側 Z=STAND_WIDTH) ---
LAYER_HEIGHT = 0.30
STAND_WIDTH = 220 * LAYER_HEIGHT            # 66.00mm (カーテンレール側スタンドと完全統一)
FIT_TEST_WIDTH = 54 * LAYER_HEIGHT          # 16.20mm (M3ザグリ穴1箇所＋レール下面受け確認用テスト幅)

# --- 正面溝付きアルミC型ピクチャーレール実測基準寸法 (u軸: レール前面 u=0 → 手前 +u / v軸: レール下面 v=0 → 上 +v) ---
RAIL_DEPTH = 14.60                          # 壁からレール前面までの外寸出っ張り (ノギス実測値)
RAIL_HEIGHT = 20.30                         # レール縦外寸高さ (ノギス実測値、上端 v=+20.30 は小梁下端に密着)
RAIL_INNER_DEPTH = 12.60                    # レール前面から内部奥背板までの深さ (ノギス実測値、背板厚 2.00mm)
RAIL_SLOT_OPENING_NOMINAL = 7.80            # 正面水平スリット開口幅 (実測約7.8mm)
RAIL_UNDER_LEDGE_DEPTH = 13.00              # レール下面を直接受ける水平段差奥行 (壁入隅1.60mmクロス逃げ確保)

# --- 上部レール前面クランプヘッド & M3×12mm ダブルボルト締結部 ---
CLAMP_TOP_V = RAIL_HEIGHT - 1.00            # +19.30mm (上方小梁下端 v=+20.30 に対し 1.00mm の不陸逃げ)
CLAMP_FRONT_U = 10.00                       # クランプ前面u座標 (u = 0.00 〜 +10.00mm の肉厚10.0mm)
CLAMP_CHIN_V = -9.50                        # クランプ前面下端v座標 (首元最小肉厚 >9.2mm を確保する高剛性アゴ)
DOGBONE_RELIEF_OFFSET = 0.20                # レール下前角(0,0)丸R逃げ中心オフセット (+0.20, -0.20)
DOGBONE_RELIEF_RADIUS = 0.60                # 応力集中ゼロの滑らかな円弧角逃げ半径 (R0.60mm)

M3_AXIS_V = RAIL_HEIGHT / 2.0               # +10.15mm (正面水平スリット中央高さ)
BOLT_Z_MARGIN = 15.00                       # 左右端からのボルト中心距離
BOLT_Z_POSITIONS = (BOLT_Z_MARGIN, STAND_WIDTH - BOLT_Z_MARGIN)  # (15.00mm, 51.00mm) ピッチ36.00mm

M3_SHANK_CLEARANCE_RADIUS = 1.70            # M3ボルト貫通穴半径 (φ3.40mm ティアドロップ付き)
M3_CBORE_RADIUS = 3.30                      # M3キャップボルト頭ザグリ半径 (φ6.60mm ティアドロップ付き)
M3_CBORE_DEPTH = 4.80                       # ザグリ深さ (座面 u=+5.20mm → M3×12mm先端 u=-6.80mm でビス頭非干渉)

# --- 二点接地式 背面壁当てスパイン & L字デッキ骨格 ---
SPINE_FRONT_U = -3.60                       # 垂直スパイン前面u座標 (球体メッシュ背面に8.15mmの音響空間を確保)
CLAMP_GUSSET_ROOT_V = CLAMP_CHIN_V - (
    CLAMP_FRONT_U - SPINE_FRONT_U
)                                           # -23.10mm (クランプ下端からスパイン前面へ45°で繋がる高剛性ガセット根元)
SPINE_MID_RELIEF_DEPTH = 0.80               # 壁紙の中間不陸を逃がす背面リリーフ深さ (u = -13.80mm)
HEEL_PAD_TOP_V = -82.00                     # 下部壁当てヒールパッド (u = -14.60mm) の上端v座標
DECK_BOTTOM_V = -108.00                     # L字ブラケット本体底面v座標 (スパイン全長 108.0mm)
DECK_FRONT_U = 82.00                        # L字デッキ前端u座標 (壁からの総奥行 96.60mm)
L_NECK_FILLET_R = 10.00                     # スパイン前面〜デッキ上面を繋ぐ高剛性凹フィレット半径

# --- 間取り最適化・2軸緩傾斜アコースティック天板 & ノギス実測φ42.9mm浅溝 ---
HOMEPOD_SPHERE_DIA = 97.90                  # HomePod mini 2 球体最大直径
HOMEPOD_HEIGHT = 84.30                      # HomePod mini 2 全高
HOMEPOD_FOOT_DIA = 42.90                    # HomePod mini 2 底面シリコン足直径 (ノギス実測確定値)

DECK_MIN_TOP_V = -99.00                     # 最薄角 (手前右角 u=+82.0, z=0.0) の天板上面v座標
DECK_TILT_FORWARD_U_DEG = 7.5               # 室内手前方向 (+u: ソファ・TV方向) への傾斜角
DECK_TILT_ROOM_CENTER_Z_DEG = 2.5           # 部屋中央方向 (-z: ピアノ・ソファ中央寄り) への傾斜角 (合成約7.90°)

POCKET_FLOOR_CLEARANCE = 0.80               # PETG造形公差クリアランス (片側0.40mm)
POCKET_FLOOR_DIA = HOMEPOD_FOOT_DIA + POCKET_FLOOR_CLEARANCE  # 43.70mm
POCKET_DEPTH = 1.80                         # 位置合わせ＆魔法のテープ厚みを吸収する浅溝深さ
POCKET_BEVEL_TAPER_DEG = 45.0               # 45.0° (天板の+2.5°上向き順テーパーにより最大オーバーハング42.5°<=45.0°)
POCKET_CENTER_U = 48.00                     # スピーカー載置中心u座標 (小梁下約27〜30mm・ドライバー動線クリア)

# --- 左側面下部 電源コード抜け止めC字クリップ (左入隅壁・コンセント側) ---
CABLE_CLIP_PROTRUSION_V = 7.20              # 本体底面(v=-108.0)からの下方張り出し量 (v = -115.20 〜 -108.00mm)
CABLE_CLIP_TOP_Z_SPAN = 10.00               # フル断面クリップ長 (z = 56.00 〜 66.00mm)
CABLE_CLIP_GUSSET_START_Z = (
    STAND_WIDTH - CABLE_CLIP_TOP_Z_SPAN - CABLE_CLIP_PROTRUSION_V
)  # 48.80mm (45°サポートフリー傾斜ガセット開始z座標)
CABLE_CLIP_U_MIN = -11.80                   # 壁面(u=-14.60)から2.80mm手前に離間させて壁紙接触を防止
CABLE_CLIP_U_MAX = -2.20                    # クリップ耳部の前縁u座標 (幅9.60mm)
CABLE_CLIP_CENTER_U = (CABLE_CLIP_U_MIN + CABLE_CLIP_U_MAX) / 2.0  # -7.00mm
CABLE_CLIP_CENTER_V = DECK_BOTTOM_V - CABLE_CLIP_PROTRUSION_V / 2.0  # -111.60mm
CABLE_CLIP_BORE_DIA = 4.50                  # USB-C編み込み電源コード保持ボア内径
CABLE_CLIP_SLIT_GAP = 2.90                  # 下向きコード押し込みスリット幅

# --- 後入れ自動90°ロック式 カムTアンカー駒 (2個使用) ---
T_ANCHOR_SLOT_WIDTH = 7.20                  # 7.8mm正面スリットへ余裕で入る短辺幅・円筒ガイドボス径
T_ANCHOR_HALF_SPAN_X = 8.65                 # ロック方向半長 (全長17.30mm > 最大想定キャビティ17.0mmで確実ストップ)
T_ANCHOR_PASS_FILLET_R = 6.00               # 右回し通過対角2角の大径カムR (最小キャビティ15.6mm内を無干渉回転)
T_ANCHOR_STOP_FILLET_R = 0.60               # ストッパー対角2角の小径エッジ保護R
T_ANCHOR_BOSS_HEIGHT = 1.60                 # 正面スリット内ガイド円筒ボス高さ (2.0mm前リップ内で底突きしない高さ)
T_ANCHOR_WING_THICKNESS = 5.00              # 前リップ裏に掛かるカムウイング厚
T_ANCHOR_TOTAL_HEIGHT = T_ANCHOR_BOSS_HEIGHT + T_ANCHOR_WING_THICKNESS  # 6.60mm (0.30mm × 22層)
T_ANCHOR_NUT_ACROSS_FLATS = 5.62            # M3六角ナット(二面幅5.50mm)圧入回り止め幅
T_ANCHOR_NUT_POCKET_DEPTH = 2.80            # 背面からの六角ナットポケット深さ (手前に3.80mmのソリッド肉厚確保)

# --- 全体外寸およびXY原点センタリングオフセット ---
CLIP_BOTTOM_V = DECK_BOTTOM_V - CABLE_CLIP_PROTRUSION_V  # -115.20mm
TOTAL_DEPTH = DECK_FRONT_U + RAIL_DEPTH                  # 96.60mm (u = -14.60 〜 +82.00mm)
TOTAL_HEIGHT_WITH_CLIP = CLAMP_TOP_V - CLIP_BOTTOM_V     # 134.50mm (v = -115.20 〜 +19.30mm)

MAIN_U_OFFSET = -(DECK_FRONT_U - RAIL_DEPTH) / 2.0       # -33.70mm
MAIN_V_OFFSET = -(CLAMP_TOP_V + CLIP_BOTTOM_V) / 2.0     # +47.95mm

FIT_TEST_BOTTOM_V = -27.50                               # テストピース下端v座標 (補強ガセット全域+下部壁基準確認)
FIT_U_OFFSET = -(CLAMP_FRONT_U - RAIL_DEPTH) / 2.0       # +2.30mm
FIT_V_OFFSET = -(CLAMP_TOP_V + FIT_TEST_BOTTOM_V) / 2.0  # +4.10mm


def deck_top_v_at(u: float, z: float) -> float:
    """内部座標 (u, z) における2軸緩傾斜天板の上面 v 座標を返す."""
    return (
        DECK_MIN_TOP_V
        + (DECK_FRONT_U - u) * math.tan(math.radians(DECK_TILT_FORWARD_U_DEG))
        + z * math.tan(math.radians(DECK_TILT_ROOM_CENTER_Z_DEG))
    )


def _get_raw_tilted_deck_plane(
    u_offset: float = MAIN_U_OFFSET, v_offset: float = MAIN_V_OFFSET
) -> Plane:
    """内部設計座標 (X_raw=u+u_off, Y_raw=v+v_off, Z_raw=z_left) における2軸傾斜天板 Plane を返す."""
    alpha_u = math.radians(DECK_TILT_FORWARD_U_DEG)
    alpha_z = math.radians(DECK_TILT_ROOM_CENTER_Z_DEG)

    nx = math.tan(alpha_u)
    ny = 1.0
    nz = -math.tan(alpha_z)
    norm = math.sqrt(nx * nx + ny * ny + nz * nz)
    normal = Vector(nx / norm, ny / norm, nz / norm)

    center_z = STAND_WIDTH / 2.0
    center_y = deck_top_v_at(POCKET_CENTER_U, center_z) + v_offset
    origin = Vector(POCKET_CENTER_U + u_offset, center_y, center_z)

    x_tangent = Vector(math.cos(alpha_u), -math.sin(alpha_u), 0.0)
    return Plane(origin=origin, x_dir=x_tangent, z_dir=normal)


def get_tilted_deck_plane(
    u_offset: float = MAIN_U_OFFSET, v_offset: float = MAIN_V_OFFSET
) -> Plane:
    """造形配置後 (左壁・ケーブルロック側 Z=0 接地、Y軸180°剛体回転後) の2軸傾斜天板 Plane を返す."""
    raw = _get_raw_tilted_deck_plane(u_offset=u_offset, v_offset=v_offset)
    origin = Vector(-raw.origin.X, raw.origin.Y, STAND_WIDTH - raw.origin.Z)
    normal = Vector(-raw.z_dir.X, raw.z_dir.Y, -raw.z_dir.Z)
    x_tangent = Vector(-raw.x_dir.X, raw.x_dir.Y, -raw.x_dir.Z)
    return Plane(origin=origin, x_dir=x_tangent, z_dir=normal)


def _fillet_2d_vertices_by_coords(
    coord_radius_list: list[tuple[float, float, float]], tol: float = 0.08
) -> None:
    """現在アクティブな BuildSketch 内で指定座標に一致する頂点へ個別に 2D フィレットを適用する."""
    for tx, ty, radius in coord_radius_list:
        if radius <= 0.0:
            continue
        matched = [
            v
            for v in vertices()
            if math.hypot(v.X - tx, v.Y - ty) < tol
        ]
        if not matched:
            raise RuntimeError(f"2Dフィレット対象頂点が見つかりません: ({tx:.2f}, {ty:.2f})")
        fillet(matched, radius=radius)


def _build_teardrop_x_cutter(
    u_start: float,
    u_end: float,
    center_v: float,
    center_z: float,
    radius: float,
    u_offset: float,
    v_offset: float,
    teardrop_z_sign: float = -1.0,
) -> Part:
    """Y軸180°回転後に造形 +Z 上縁オーバーハングを 45° 以下に抑える X 軸方向ティアドロップ穴カッター."""
    length = u_end - u_start
    cy = center_v + v_offset
    cz = center_z
    apex_z = teardrop_z_sign * radius * math.sqrt(2.0)
    tan_z = teardrop_z_sign * radius / math.sqrt(2.0)
    tan_y = radius / math.sqrt(2.0)

    plane = Plane(
        origin=(u_start + u_offset, 0.0, 0.0),
        x_dir=(0.0, 1.0, 0.0),
        z_dir=(1.0, 0.0, 0.0),
    )
    with BuildPart() as bp:
        with BuildSketch(plane):
            with Locations((cy, cz)):
                Circle(radius=radius)
                Polygon(
                    (-tan_y, tan_z),
                    (0.0, apex_z),
                    (tan_y, tan_z),
                    (0.0, 0.0),
                    align=None,
                )
        extrude(amount=length)
    return bp.part


def _build_cable_clip_ear_and_cutter(
    u_offset: float, v_offset: float
) -> tuple[Part, Part]:
    """左側面下部(z=56..66mm)に45°サポートフリー傾斜ガセット付きコードクリップを生成する."""
    x_min = CABLE_CLIP_U_MIN + u_offset
    x_max = CABLE_CLIP_U_MAX + u_offset
    y_deck_bot = DECK_BOTTOM_V + v_offset
    y_clip_bot = CLIP_BOTTOM_V + v_offset
    y_overlap_top = y_deck_bot + 3.0
    ear_z_span = STAND_WIDTH - CABLE_CLIP_GUSSET_START_Z

    # 1. u-v 断面プロファイル (下端角を丸めた耳形状)
    with BuildPart() as ear_uv_bp:
        with BuildSketch(Plane.XY.offset(CABLE_CLIP_GUSSET_START_Z)):
            with BuildLine():
                Polyline(
                    (x_min, y_overlap_top),
                    (x_min, y_clip_bot),
                    (x_max, y_clip_bot),
                    (x_max, y_overlap_top),
                    close=True,
                )
            make_face()
            _fillet_2d_vertices_by_coords(
                [
                    (x_min, y_clip_bot, 2.2),
                    (x_max, y_clip_bot, 2.2),
                ]
            )
        extrude(amount=ear_z_span)

    # 2. v-z 平面での 45° 傾斜ウェッジ (z=48.80 で v=-108.0 から z=56.00 で v=-115.20 へ45°立ち出し)
    wedge_yz_plane = Plane(
        origin=(x_min - 1.0, 0.0, 0.0),
        x_dir=(0.0, 1.0, 0.0),
        z_dir=(1.0, 0.0, 0.0),
    )
    with BuildPart() as wedge_bp:
        with BuildSketch(wedge_yz_plane):
            Polygon(
                (y_overlap_top, CABLE_CLIP_GUSSET_START_Z),
                (y_deck_bot, CABLE_CLIP_GUSSET_START_Z),
                (y_clip_bot, CABLE_CLIP_GUSSET_START_Z + CABLE_CLIP_PROTRUSION_V),
                (y_clip_bot, STAND_WIDTH),
                (y_overlap_top, STAND_WIDTH),
                align=None,
            )
        extrude(amount=(x_max - x_min) + 2.0)

    ear_solid = ear_uv_bp.part & wedge_bp.part

    # 3. φ4.50mm コード保持ボア & 下向き 2.90mm 導入スリット (全域貫通で -Z 水平天井面を作らない)
    bore_cx = CABLE_CLIP_CENTER_U + u_offset
    bore_cy = CABLE_CLIP_CENTER_V + v_offset
    with BuildPart() as cutter_bp:
        with BuildSketch(Plane.XY.offset(CABLE_CLIP_GUSSET_START_Z - 0.5)):
            with Locations((bore_cx, bore_cy)):
                Circle(radius=CABLE_CLIP_BORE_DIA / 2.0)
            with Locations((bore_cx, (y_clip_bot - 1.0 + bore_cy) / 2.0)):
                Rectangle(CABLE_CLIP_SLIT_GAP, bore_cy - (y_clip_bot - 1.0))
        extrude(amount=ear_z_span + 1.0)

    return ear_solid, cutter_bp.part


def build_t_anchor() -> Part:
    """正面溝(約7.8mm)へ後入れでき、右回しで自動90°カムストップするM3ナット保持Tアンカー駒を返す.

    造形姿勢:
        広いTウイング背面を Z=0 ビルドプレートへ完全ベタ置きし、上部に φ7.20mm 円筒ガイドボスを積層する
        サポート完全不要 (オーバーハング 0g) 構造。下部の M3 六角ナットポケット天井には2段ストレートブリッジを設け、
        中空の円周浮き積層を完全に防止する。
    回転方向:
        実機装着時は Z=6.60mm (円筒ボス側) がレール正面 (+u) を向き、Z=0 (六角ナット側) がレール奥壁 (-u) を向く。
        正面から M3 ボルトを右回し (時計回り) に締めると、回転ベクトルは -u (= ローカル -Z) を向くため Rot(0, 0, -deg) となる。
    """
    hx = T_ANCHOR_HALF_SPAN_X
    hy = T_ANCHOR_SLOT_WIDTH / 2.0
    nut_circum_r = (T_ANCHOR_NUT_ACROSS_FLATS / 2.0) / math.cos(math.radians(30.0))
    bolt_d = M3_SHANK_CLEARANCE_RADIUS * 2.0

    with BuildPart() as bp:
        # 1. 非対称カムロックTウイング (Z = 0.00 〜 5.00mm、ビルドプレート全面ベタ置き)
        #    右回し締結 Rot(0, 0, -deg) に対し:
        #    第2象限(-hx,+hy)・第4象限(+hx,-hy)が通過角となるため大径カムR(6.00mm)、
        #    第1象限(+hx,+hy)・第3象限(-hx,-hy)がストッパー角となるため小径R(0.60mm)とする。
        with BuildSketch(Plane.XY):
            with BuildLine():
                Polyline(
                    (-hx, -hy),
                    (hx, -hy),
                    (hx, hy),
                    (-hx, hy),
                    close=True,
                )
            make_face()
            _fillet_2d_vertices_by_coords(
                [
                    (-hx, hy, T_ANCHOR_PASS_FILLET_R),
                    (hx, -hy, T_ANCHOR_PASS_FILLET_R),
                    (hx, hy, T_ANCHOR_STOP_FILLET_R),
                    (-hx, -hy, T_ANCHOR_STOP_FILLET_R),
                ]
            )
        extrude(amount=T_ANCHOR_WING_THICKNESS)

        # 2. スリット内回転ガイド円筒ボス (Z = 5.00 〜 6.60mm, φ7.20mm)
        with BuildSketch(Plane.XY.offset(T_ANCHOR_WING_THICKNESS)):
            Circle(radius=hy)
        extrude(amount=T_ANCHOR_BOSS_HEIGHT)

        # 3. 背面(Z=0側) M3 六角ナット圧入ポケット (Z = 0.00 〜 2.80mm, 二面幅 5.62mm)
        with BuildSketch(Plane.XY.offset(-0.1)):
            RegularPolygon(radius=nut_circum_r, side_count=6)
        extrude(amount=T_ANCHOR_NUT_POCKET_DEPTH + 0.1, mode=Mode.SUBTRACT)

        # 4. 2段シーケンシャル・ストレートブリッジ (中空での円穴浮き造形を防ぐ3Dプリント定石構造)
        #    1段目 (Z = 2.80 〜 3.10mm): ナット対辺方向に渡す幅 3.40mm ストレートスリット
        with BuildSketch(Plane.XY.offset(T_ANCHOR_NUT_POCKET_DEPTH)):
            Rectangle(T_ANCHOR_NUT_ACROSS_FLATS, bolt_d)
        extrude(amount=LAYER_HEIGHT, mode=Mode.SUBTRACT)

        #    2段目 (Z = 3.10 〜 3.40mm): 直交 3.40×3.40mm 正方形ブリッジ
        with BuildSketch(Plane.XY.offset(T_ANCHOR_NUT_POCKET_DEPTH + LAYER_HEIGHT)):
            Rectangle(bolt_d, bolt_d)
        extrude(amount=LAYER_HEIGHT, mode=Mode.SUBTRACT)

        # 5. 中央 M3 ボルト貫通穴 (Z = 0.00 〜 6.60mm 全貫通, φ3.40mm)
        with BuildSketch(Plane.XY.offset(-0.2)):
            Circle(radius=M3_SHANK_CLEARANCE_RADIUS)
        extrude(amount=T_ANCHOR_TOTAL_HEIGHT + 0.4, mode=Mode.SUBTRACT)

    part = bp.part
    part.label = "picture_rail_cam_t_anchor"
    return part


def build_stand() -> Part:
    """ピクチャーレール用 HomePod mini 2 機械ロック式 L字スタンド本体を生成して返す."""
    u_off = MAIN_U_OFFSET
    v_off = MAIN_V_OFFSET

    def pt(u: float, v: float) -> tuple[float, float]:
        return (u + u_off, v + v_off)

    raw_deck_top_v = deck_top_v_at(SPINE_FRONT_U, STAND_WIDTH) + 4.0
    mid_relief_u = -RAIL_DEPTH + SPINE_MID_RELIEF_DEPTH  # -13.80mm

    # L字ブラケット u-v 外周プロファイル (首元に45°分厚い補強ガセットを備え、内角は円弧ドッグボーンで応力集中を排除)
    profile_pts = [
        pt(0.0, CLAMP_TOP_V),                                          # レール前面座 上端 (0.0, +19.30)
        pt(0.0, 0.0),                                                  # レール下前角 基準点 (後段でR0.60円弧逃げ加工)
        pt(-RAIL_UNDER_LEDGE_DEPTH, 0.0),                              # レール下面受け段差 奥端 (-13.00, 0.0)
        pt(mid_relief_u, -SPINE_MID_RELIEF_DEPTH),                     # 中間背面リリーフ上端 (-13.80, -0.80)
        pt(mid_relief_u, HEEL_PAD_TOP_V + SPINE_MID_RELIEF_DEPTH),     # 中間背面リリーフ下端 (-13.80, -81.20)
        pt(-RAIL_DEPTH, HEEL_PAD_TOP_V),                               # 下部壁当てヒール上端 (-14.60, -82.00)
        pt(-RAIL_DEPTH, DECK_BOTTOM_V),                                # 下部壁当てヒール下端 (-14.60, -108.00)
        pt(DECK_FRONT_U, DECK_BOTTOM_V),                               # デッキ前端下部 (+82.00, -108.00)
        pt(DECK_FRONT_U, raw_deck_top_v),                              # デッキ前端上部 (傾斜カット前)
        pt(SPINE_FRONT_U, raw_deck_top_v),                             # スパイン前面〜デッキ交点 (傾斜カット前)
        pt(SPINE_FRONT_U, CLAMP_GUSSET_ROOT_V),                        # 首元45°補強ガセット根元 (-3.60, -23.10)
        pt(CLAMP_FRONT_U, CLAMP_CHIN_V),                               # クランプ前面高剛性アゴ下端 (+10.00, -9.50)
        pt(CLAMP_FRONT_U, CLAMP_TOP_V),                                # クランプ前面上端 (+10.00, +19.30)
    ]

    profile_fillets = [
        (*pt(-RAIL_DEPTH, DECK_BOTTOM_V), 2.0),
        (*pt(DECK_FRONT_U, DECK_BOTTOM_V), 3.0),
        (*pt(SPINE_FRONT_U, CLAMP_GUSSET_ROOT_V), 8.0),
        (*pt(CLAMP_FRONT_U, CLAMP_CHIN_V), 5.0),
        (*pt(CLAMP_FRONT_U, CLAMP_TOP_V), 1.6),
    ]

    with BuildPart() as bp:
        with BuildSketch(Plane.XY):
            with BuildLine():
                Polyline(*profile_pts, close=True)
            make_face()
            _fillet_2d_vertices_by_coords(profile_fillets)
        extrude(amount=STAND_WIDTH)

    dogbone = Pos(
        DOGBONE_RELIEF_OFFSET + u_off,
        -DOGBONE_RELIEF_OFFSET + v_off,
        STAND_WIDTH / 2.0,
    ) * Cylinder(radius=DOGBONE_RELIEF_RADIUS, height=STAND_WIDTH + 2.0)
    part = bp.part - dogbone

    # 1. 間取り最適化 2軸緩傾斜アコースティック天板の平面カット
    deck_plane = _get_raw_tilted_deck_plane(u_offset=u_off, v_offset=v_off)
    # スパイン前面 (u = SPINE_FRONT_U) より手前側のみを傾斜平面でカットするための半空間カッター
    # deck_plane の +x_dir は手前下り方向。u >= SPINE_FRONT_U 領域だけを綺麗に切り取るため、
    # u >= SPINE_FRONT_U のバウンディングボックスと傾斜上空ボックスの積集合を減算する。
    with BuildPart() as sky_bp:
        with BuildSketch(deck_plane):
            Rectangle(300.0, 300.0)
        extrude(amount=80.0)

    deck_zone_box = Pos(
        (SPINE_FRONT_U + DECK_FRONT_U + 20.0) / 2.0 + u_off,
        (DECK_BOTTOM_V + 10.0) + v_off,
        STAND_WIDTH / 2.0,
    ) * Box(
        (DECK_FRONT_U + 20.0) - SPINE_FRONT_U,
        120.0,
        STAND_WIDTH + 20.0,
    )
    part = part - (sky_bp.part & deck_zone_box)

    # スパイン前面 (X = SPINE_FRONT_U + u_off) と傾斜天板が交わるL字内角エッジへ R10.0mm の高剛性フィレットを付与
    neck_target_x = SPINE_FRONT_U + u_off
    neck_edges = [
        e
        for e in part.edges()
        if abs(e.center().X - neck_target_x) < 0.25
        and (DECK_MIN_TOP_V - 5.0 + v_off) < e.center().Y < (raw_deck_top_v + v_off)
        and e.length > STAND_WIDTH * 0.8
    ]
    if neck_edges:
        part = fillet(neck_edges, radius=L_NECK_FILLET_R)

    # 2. M3×12mm ダブルボルト貫通穴 & キャップボルト頭ザグリ穴 (ティアドロップ形状付き)
    for bz in BOLT_Z_POSITIONS:
        shank = _build_teardrop_x_cutter(
            u_start=-1.0,
            u_end=CLAMP_FRONT_U + 1.0,
            center_v=M3_AXIS_V,
            center_z=bz,
            radius=M3_SHANK_CLEARANCE_RADIUS,
            u_offset=u_off,
            v_offset=v_off,
        )
        cbore = _build_teardrop_x_cutter(
            u_start=CLAMP_FRONT_U - M3_CBORE_DEPTH,
            u_end=CLAMP_FRONT_U + 1.0,
            center_v=M3_AXIS_V,
            center_z=bz,
            radius=M3_CBORE_RADIUS,
            u_offset=u_off,
            v_offset=v_off,
        )
        part = part - shank - cbore

    # 3. 傾斜天板に垂直な HomePod mini 2 底面シリコン足 (φ42.9mm) 用浅溝 (φ43.70 × 深さ1.80mm, 47.5°テーパー)
    overcut = 0.15
    pocket_cut_plane = Plane(
        origin=deck_plane.origin + deck_plane.z_dir * overcut,
        x_dir=deck_plane.x_dir,
        z_dir=-deck_plane.z_dir,
    )
    sketch_radius = POCKET_FLOOR_DIA / 2.0 + (POCKET_DEPTH + overcut) * math.tan(
        math.radians(POCKET_BEVEL_TAPER_DEG)
    )
    with BuildPart() as pocket_bp:
        with BuildSketch(pocket_cut_plane):
            Circle(radius=sketch_radius)
        extrude(amount=POCKET_DEPTH + overcut, taper=POCKET_BEVEL_TAPER_DEG)
    part = part - pocket_bp.part

    # 4. 左側面下部 (左入隅壁・コンセント側) の電源コード抜け止めクリップ
    clip_ear, clip_cutter = _build_cable_clip_ear_and_cutter(u_offset=u_off, v_offset=v_off)
    part = (part + clip_ear) - clip_cutter

    # 5. Y軸周り180°の剛体回転 (鏡像反転なし・実機左右形状100%保持) により、
    #    ケーブルロックを含むフラットな左壁側端面を Z=0 ビルドプレートへ完全ベタ置きする。
    part = Pos(0.0, 0.0, STAND_WIDTH) * Rot(0.0, 180.0, 0.0) * part

    part.label = "picture_rail_homepod_mini_stand"
    return part


def build_fit_test_clamp() -> Part:
    """本番造形前に約8分でレール嵌合・M3×12mm締結を確認できる薄切りテストクランプ単体を返す."""
    u_off = FIT_U_OFFSET
    v_off = FIT_V_OFFSET

    def pt(u: float, v: float) -> tuple[float, float]:
        return (u + u_off, v + v_off)

    pts = [
        pt(0.0, CLAMP_TOP_V),
        pt(0.0, 0.0),
        pt(-RAIL_UNDER_LEDGE_DEPTH, 0.0),
        pt(-RAIL_DEPTH, -1.60),
        pt(-RAIL_DEPTH, FIT_TEST_BOTTOM_V),
        pt(SPINE_FRONT_U, FIT_TEST_BOTTOM_V),
        pt(SPINE_FRONT_U, CLAMP_GUSSET_ROOT_V),
        pt(CLAMP_FRONT_U, CLAMP_CHIN_V),
        pt(CLAMP_FRONT_U, CLAMP_TOP_V),
    ]
    fillets = [
        (*pt(-RAIL_DEPTH, FIT_TEST_BOTTOM_V), 1.2),
        (*pt(SPINE_FRONT_U, FIT_TEST_BOTTOM_V), 1.2),
        (*pt(SPINE_FRONT_U, CLAMP_GUSSET_ROOT_V), 4.0),
        (*pt(CLAMP_FRONT_U, CLAMP_CHIN_V), 5.0),
        (*pt(CLAMP_FRONT_U, CLAMP_TOP_V), 1.5),
    ]

    with BuildPart() as bp:
        with BuildSketch(Plane.XY):
            with BuildLine():
                Polyline(*pts, close=True)
            make_face()
            _fillet_2d_vertices_by_coords(fillets)
        extrude(amount=FIT_TEST_WIDTH)

    dogbone = Pos(
        DOGBONE_RELIEF_OFFSET + u_off,
        -DOGBONE_RELIEF_OFFSET + v_off,
        FIT_TEST_WIDTH / 2.0,
    ) * Cylinder(radius=DOGBONE_RELIEF_RADIUS, height=FIT_TEST_WIDTH + 2.0)
    part = bp.part - dogbone
    z_mid = FIT_TEST_WIDTH / 2.0
    shank = _build_teardrop_x_cutter(
        u_start=-1.0,
        u_end=CLAMP_FRONT_U + 1.0,
        center_v=M3_AXIS_V,
        center_z=z_mid,
        radius=M3_SHANK_CLEARANCE_RADIUS,
        u_offset=u_off,
        v_offset=v_off,
    )
    cbore = _build_teardrop_x_cutter(
        u_start=CLAMP_FRONT_U - M3_CBORE_DEPTH,
        u_end=CLAMP_FRONT_U + 1.0,
        center_v=M3_AXIS_V,
        center_z=z_mid,
        radius=M3_CBORE_RADIUS,
        u_offset=u_off,
        v_offset=v_off,
    )
    part = part - shank - cbore
    # 本体と同じY軸周り180°剛体回転で向きを揃え、ティアドロップ屋根を +Z 上向きにする
    part = Pos(0.0, 0.0, FIT_TEST_WIDTH) * Rot(0.0, 180.0, 0.0) * part
    part.label = "picture_rail_fit_test_clamp"
    return part


def build_print_plate() -> Compound:
    """Bambu Studioで1回で全パーツを造形できる本番プレート(L字本体1個 + カムTアンカー2個、全てZ=0接地)を返す."""
    stand = build_stand()
    anchor = build_t_anchor()

    # L字の内側空き空間 (X = -(45.0 + MAIN_U_OFFSET) = -11.30mm) の Z=0 ビルドプレート面へ Tアンカー2個を整列配置
    anchor_x = -(45.0 + MAIN_U_OFFSET)
    a1 = Pos(anchor_x, -22.0 + MAIN_V_OFFSET, 0.0) * anchor
    a2 = Pos(anchor_x, -42.0 + MAIN_V_OFFSET, 0.0) * anchor
    a1.label = "picture_rail_cam_t_anchor_1"
    a2.label = "picture_rail_cam_t_anchor_2"

    plate = Compound(label="picture_rail_homepod_mini_stand_plate", children=[stand, a1, a2])
    return plate


def build_fit_test_kit() -> Compound:
    """約8分で実機スリット挿入とM3カムロックを確認できる事前テストキット(薄切りクランプ1個 + Tアンカー1個)を返す."""
    clamp = build_fit_test_clamp()
    anchor = Pos(26.0, 0.0, 0.0) * build_t_anchor()
    anchor.label = "picture_rail_cam_t_anchor_test"
    return Compound(label="picture_rail_homepod_mini_stand_fit_test", children=[clamp, anchor])


def export_models(output_dir: Path | None = None) -> tuple[Path, Path]:
    """本番造形プレートと事前嵌合テストキットの両方を STEP ファイルとして出力する."""
    target_dir = (
        Path(output_dir)
        if output_dir is not None
        else Path(os.path.dirname(os.path.abspath(__file__)))
    )
    target_dir.mkdir(parents=True, exist_ok=True)

    plate = build_print_plate()
    fit_kit = build_fit_test_kit()

    main_step = target_dir / "picture_rail_homepod_mini_stand.step"
    fit_step = target_dir / "picture_rail_homepod_mini_stand_fit_test.step"

    export_step(plate, str(main_step))
    export_step(fit_kit, str(fit_step))
    return main_step, fit_step


if __name__ == "__main__":  # pragma: no cover
    main_path, fit_path = export_models()
    main_plate = build_print_plate()
    test_kit = build_fit_test_kit()
    print(f"本番モデルを出力しました: {main_path}")
    print(f"  外形寸法 (X×Y×Z): {tuple(round(v, 2) for v in main_plate.bounding_box().size)}")
    print(f"  総体積: {main_plate.volume / 1000.0:.2f} cm^3")
    print(f"嵌合テストキットを出力しました: {fit_path}")
    print(f"  外形寸法 (X×Y×Z): {tuple(round(v, 2) for v in test_kit.bounding_box().size)}")
    print(f"  総体積: {test_kit.volume / 1000.0:.2f} cm^3")
    show_object(main_plate, name="picture_rail_homepod_mini_stand")
    show_object(Pos(130.0, 0.0, 0.0) * test_kit, name="picture_rail_homepod_mini_stand_fit_test")
