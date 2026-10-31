"""
設計要件:
    - 木製スピーカースタンド（BQKOZFIN 高さ80cm・天板厚み15.5mm・背面張り出し実測61.0mm）の背面中央に引っ掛けて、
      Wi-Fi 6Eルーター（NEC Aterm WX7800T8、約800g）を付属スタンド装着のまま正規の縦置き姿勢で吊り下げる一体型ホルダー。
    - 天板の背面張り出し量（61.0mm）とルーター付属スタンド幅（75.0mm → トレイ外寸81.5mm）の差を吸収するため、
      上部は天板後端（61.5mm位置）にピタッと突き当たる「段付きC字フック＋斜めガセット構造」、
      下部はスタンドを無理なく収めつつ壁との余裕を広げるスリム奥行（83.5mm位置、外寸89.5mm）の2段オフセット設計とする。
    - 天板上面へのかかり代を52.0mm（実効51.5mm）確保し、ルーター重心真上をしっかり支持しつつ HomePod（背面空き約75mm）とも約23.5mmの余裕を確保。
    - 左側面から出るLANケーブル・電源ケーブルと一切干渉しない左右貫通U字トレイ構造。
    - 右側面（LED側）をビルドプレート接地面（Z=0）にした横向き一体造形で、分割なしの1パーツ完結・サポート材完全ゼロ（0g）を実現。
    - 段付きC字フック〜斜めガセット〜背面スパイン〜底面U字トレイまで外周ループが一筆書きで連続する積層向きとし、層間剥離による破断リスクを構造的に排除。
    - 1層目の密着（Z=0〜18mm）と上端連続枠（Z=126〜144mm）および荷重伝達ショルダー部を100%ソリッドで維持しつつ、
      垂直太柱＋屋根角40°の五角形ティアドロップアーチ開口を背面（3窓）・底面（1窓）・天板裏フロントアーム（1窓）に配置。
    - 最新の3Dプリンター（Bambu Lab P2S Combo 等）での出力を想定し、事前確認用の薄切り嵌合テストピース（幅12mm）も同時出力する。

推奨フィラメント:
    - Bambu PETG Basic（黒）
    - 黒天板およびルーター筐体と自然に一体化する外観。CF（炭素繊維）を含まない純粋なPETGのため Wi-Fi 6E（2.4/5/6GHz）の電波減衰がゼロであり、
      ルーターの常時発熱（40〜50℃）と800g静荷重に対する耐熱性・耐クリープ性・粘り強さに優れる。

推奨スライサー設定:
    - ノズル径 (Nozzle): 0.6mm（タングステンカーバイドノズル等）
    - レイヤー高さ (Layer height): 0.30mm Standard（初期レイヤー高さ 0.30mm / 全幅144.0mm＝480層、テストピース12.0mm＝40層の完全整数倍）
    - 壁面生成器 (Wall generator): Arachne（ガセット遷移部やフィレット先端まで隙間なく高密度に充填）
    - 壁ループ (Wall loops): 3（5.0〜6.0mm肉厚に対して外周ループが密に連続し、高剛性を発揮）
    - トップ / ボトムシェル (Top/Bottom shells): 各 4 層（1.20mm）
    - インフィル (Sparse infill): 15〜20% (Gyroid または Cross Hatch)
    - サポート (Supports): なし (None / 完全サポートフリー設計)
    - ブリム (Brim): 原則不要（接地面積が広く連続枠のため安定。ビルドプレートの脱脂を推奨、不安な場合のみ外側ブリム 5mm）

印刷統計（予想）:
    - speaker_stand_router_holder.step: 印刷時間 約3時間00分〜3時間30分、フィラメント使用量 約235g
    - speaker_stand_router_holder_fit_test.step: 印刷時間 約12〜15分、フィラメント使用量 約12g

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

# --- 積層ピッチ・全体幅 (造形時のZ方向高さ) ---
LAYER_HEIGHT = 0.30
HOLDER_WIDTH = 480 * LAYER_HEIGHT       # 144.00mm (天板幅183mm/190mmの中央に収まり支柱幅113.8mmをカバー)
FIT_TEST_WIDTH = 40 * LAYER_HEIGHT      # 12.00mm (約12分で刷れる事前嵌合テストピース幅)

# --- スピーカースタンド天板 段付きC字フック・天板裏アーム・支柱当て部 ---
TOP_PLATE_THICKNESS = 15.5              # ノギス実測値
TOP_PLATE_CLEARANCE = 0.3               # テストピース実機確認済みの適正クリアランス
TOP_PLATE_SLOT_GAP = TOP_PLATE_THICKNESS + TOP_PLATE_CLEARANCE  # 15.80mm

TOP_PLATE_OVERHANG = 61.0               # 支柱背面〜天板後端の実測張り出し量
TOP_PLATE_OVERHANG_CLEARANCE = 0.5      # 支柱パッドとCフック奥壁が同時に気持ちよく収まる奥行クリアランス
HOOK_OVERHANG_REACH = (
    TOP_PLATE_OVERHANG + TOP_PLATE_OVERHANG_CLEARANCE
)  # 61.50mm (支柱当て前端〜Cフック奥壁)

TOP_LIP_DEPTH = 52.0                    # Cフック奥壁からの上ツメ長さ (実効51.5mm天板に載り、HomePod背面まで約23.5mm余裕)
TOP_LIP_THICKNESS = 4.8                 # 天板上面ツメの厚み
HOOK_BACK_WALL_THICKNESS = 6.0          # 天板後端を囲う上部Cフック背面リム厚
HOOK_GUSSET_START_X_OFFSET = 12.6       # 上端から斜めガセットを開始する深さ (天板厚み中腹から背面スパインへ滑らかに接続)

UNDER_ARM_THICKNESS = 6.0               # 天板裏アームの厚み
PILLAR_PAD_THICKNESS = 5.5              # 支柱当てパッド厚み
PILLAR_PAD_DROP = 32.0                  # 天板裏アーム下面からの支柱当て垂下長 (総当接高さ 38.0mm)

# --- ルーター収容空間・背面スパイン・底面U字トレイ部 ---
WALL_THICKNESS = 6.0                    # 背面スパインおよび底面トレイ床の基本肉厚
ROUTER_HEIGHT_WITH_STAND = 197.0        # スタンド込み全高実測値 (カタログ196.5mm)
ROUTER_TOP_CLEARANCE = 7.0              # 横スライド出し入れ用の頭上クリアランス
ROUTER_CHAMBER_HEIGHT = ROUTER_HEIGHT_WITH_STAND + ROUTER_TOP_CLEARANCE  # 204.00mm

ROUTER_STAND_WIDTH = 75.0               # 付属スタンド短辺幅実測値 (NEC公称値 約76mm)
ROUTER_STAND_CLEARANCE = 2.0            # 実測75mmに片側1.0mm (公称76mmにも片側0.5mm) のわずかなスライド余裕
STAND_TRAY_INNER_DEPTH = ROUTER_STAND_WIDTH + ROUTER_STAND_CLEARANCE     # 77.00mm

FRONT_LIP_THICKNESS = 5.0               # 底面トレイ前ストッパーリップ厚み
FRONT_LIP_INNER_HEIGHT = 14.0           # 底面トレイ前ストッパーリップ内側立ち上がり高さ (外寸20.0mm)
TRAY_PILLAR_CLEARANCE = 1.5             # 底面トレイ前端と木製支柱背面の干渉逃げクリアランス

SPINE_INNER_REACH = (
    STAND_TRAY_INNER_DEPTH + FRONT_LIP_THICKNESS + TRAY_PILLAR_CLEARANCE
)  # 83.50mm (支柱当て前端〜下部背面スパイン内壁)

# --- 印刷失敗リスクゼロの大開口 (五角形ティアドロップアーチ窓) ---
SOLID_BAND_BOTTOM_Z = 60 * LAYER_HEIGHT                 # 18.00mm (Z=0〜18mmは100%連続ソリッド枠)
SOLID_BAND_TOP_Z = HOLDER_WIDTH - 60 * LAYER_HEIGHT     # 126.00mm (Z=126〜144mmで再び連続ソリッド枠に合流)
WINDOW_ROOF_ANGLE_DEG = 40.0                            # 垂直からの屋根傾斜角 (水平から50°の安全急勾配)
WINDOW_CORNER_FILLET_R = 4.0                            # 開口五角形の全頂点フィレット半径

REAR_WINDOW_COUNT = 3
REAR_WINDOW_WIDTH = 48.0                # 背面各窓の幅
REAR_WINDOW_PILLAR_WIDTH = 16.0         # 窓間の太柱幅 (造形時はベッドから90°垂直に立ち上がる太柱)
REAR_WINDOW_END_MARGIN = 14.0           # 背面有効長204mmの両端マージン (14 + 48*3 + 16*2 + 14 = 204.0mm)

BOTTOM_TRAY_WINDOW_WIDTH = 44.0         # 底面トレイ床面(内寸76.5mm)の中央通気窓幅 (前後各16.25mmレール維持)
UNDER_ARM_WINDOW_WIDTH = 30.0           # 天板裏フロントアーム(有効スパン56.0mm)の中央肉抜き窓幅 (前後各13.0mm＋荷重伝達ショルダー完全ソリッド維持)

# --- 算出全体外寸 ---
TOTAL_HEIGHT = (
    TOP_LIP_THICKNESS
    + TOP_PLATE_SLOT_GAP
    + UNDER_ARM_THICKNESS
    + ROUTER_CHAMBER_HEIGHT
    + WALL_THICKNESS
)  # 236.60mm
TOTAL_DEPTH = SPINE_INNER_REACH + WALL_THICKNESS  # 89.50mm


def _fillet_2d_vertices_by_coords(
    coord_radius_list: list[tuple[float, float, float]],
    tol: float = 0.25,
) -> None:
    """現在の BuildSketch 上で、指定した2D座標 (x, y) に一致する頂点へ順番にフィレット半径を適用する."""
    for tx, ty, radius in coord_radius_list:
        matched = [
            v
            for v in vertices()
            if math.hypot(v.X - tx, v.Y - ty) <= tol
        ]
        if not matched:
            raise ValueError(f"2D頂点 ({tx:.2f}, {ty:.2f}) が見つかりません")
        fillet(matched[0], radius=radius)


def _add_pentagon_window_sketch(window_width: float) -> None:
    """現在の BuildSketch コンテキスト上に、垂直太柱＋屋根角40°の五角形ティアドロップアーチ開口を描く."""
    half_w = window_width / 2.0
    roof_dz = half_w / math.tan(math.radians(WINDOW_ROOF_ANGLE_DEG))
    z_shoulder = SOLID_BAND_TOP_Z - roof_dz
    if z_shoulder <= SOLID_BAND_BOTTOM_Z + 2.0 * WINDOW_CORNER_FILLET_R:
        raise ValueError("窓幅に対して高さが不足しています")

    pts = [
        (-half_w, SOLID_BAND_BOTTOM_Z),
        (half_w, SOLID_BAND_BOTTOM_Z),
        (half_w, z_shoulder),
        (0.0, SOLID_BAND_TOP_Z),
        (-half_w, z_shoulder),
    ]
    Polygon(*pts, align=None)
    fillet(vertices(), radius=WINDOW_CORNER_FILLET_R)


def build_router_holder() -> Part:
    """スピーカースタンド背面ルーター吊り下げホルダー（v2 段付きC字フック本番モデル）を構築して返す."""
    # XY平面の座標定義 (中心(0,0)配置、X: 設置時の上→下、Y: 設置時の支柱側(-Y)→壁側(+Y))
    x_top_outer = -TOTAL_HEIGHT / 2.0
    x_gusset_top = x_top_outer + HOOK_GUSSET_START_X_OFFSET
    x_slot_top = x_top_outer + TOP_LIP_THICKNESS
    x_slot_bot = x_slot_top + TOP_PLATE_SLOT_GAP
    x_chamber_top = x_slot_bot + UNDER_ARM_THICKNESS
    x_pillar_pad_bot = x_chamber_top + PILLAR_PAD_DROP
    x_chamber_bot = x_chamber_top + ROUTER_CHAMBER_HEIGHT
    x_bot_outer = x_chamber_bot + WALL_THICKNESS
    x_front_lip_top = x_chamber_bot - FRONT_LIP_INNER_HEIGHT

    y_pillar_front = -TOTAL_DEPTH / 2.0
    y_pillar_inner = y_pillar_front + PILLAR_PAD_THICKNESS
    y_hook_inner = y_pillar_front + HOOK_OVERHANG_REACH
    y_hook_outer = y_hook_inner + HOOK_BACK_WALL_THICKNESS
    y_top_lip_front = y_hook_inner - TOP_LIP_DEPTH

    y_back_outer = TOTAL_DEPTH / 2.0
    y_spine_inner = y_back_outer - WALL_THICKNESS
    y_tray_inner_front = y_spine_inner - STAND_TRAY_INNER_DEPTH
    y_tray_outer_front = y_tray_inner_front - FRONT_LIP_THICKNESS

    profile_pts = [
        (x_top_outer, y_hook_outer),
        (x_top_outer, y_top_lip_front),
        (x_slot_top, y_top_lip_front),
        (x_slot_top, y_hook_inner),
        (x_slot_bot, y_hook_inner),
        (x_slot_bot, y_pillar_front),
        (x_pillar_pad_bot, y_pillar_front),
        (x_pillar_pad_bot, y_pillar_inner),
        (x_chamber_top, y_pillar_inner),
        (x_chamber_top, y_spine_inner),
        (x_chamber_bot, y_spine_inner),
        (x_chamber_bot, y_tray_inner_front),
        (x_front_lip_top, y_tray_inner_front),
        (x_front_lip_top, y_tray_outer_front),
        (x_bot_outer, y_tray_outer_front),
        (x_bot_outer, y_back_outer),
        (x_chamber_top, y_back_outer),
        (x_gusset_top, y_hook_outer),
    ]

    vertex_fillets = [
        (x_top_outer, y_hook_outer, 3.0),
        (x_top_outer, y_top_lip_front, 2.0),         # 天板上の先端角を滑らかに丸める
        (x_slot_top, y_top_lip_front, 1.5),          # 天板差し込みリードイン
        (x_slot_top, y_hook_inner, 0.8),             # Cフック上奥内角の応力緩和 (角張った15.5mm天板とも完全非干渉)
        (x_slot_bot, y_hook_inner, 0.8),             # Cフック下奥内角の応力緩和 (角張った15.5mm天板とも完全非干渉)
        (x_slot_bot, y_pillar_front, 1.8),           # 支柱差し込み側リードイン
        (x_pillar_pad_bot, y_pillar_front, 2.0),
        (x_pillar_pad_bot, y_pillar_inner, 2.0),
        (x_chamber_top, y_pillar_inner, 2.5),        # 支柱パッド付け根の応力緩和
        (x_chamber_top, y_spine_inner, 3.0),         # 背面スパイン上部内角の応力緩和
        (x_chamber_bot, y_spine_inner, 1.0),         # トレイ奥内角の応力緩和 (75〜76mmスタンド底面が乗り上げない小R)
        (x_chamber_bot, y_tray_inner_front, 1.0),    # トレイ前内角の応力緩和 (75〜76mmスタンド底面が乗り上げない小R)
        (x_front_lip_top, y_tray_inner_front, 2.0),  # 前ストッパーリップ上端丸め
        (x_front_lip_top, y_tray_outer_front, 2.0),  # 前ストッパーリップ上端丸め
        (x_bot_outer, y_tray_outer_front, 3.0),
        (x_bot_outer, y_back_outer, 3.0),
        (x_chamber_top, y_back_outer, 6.0),          # 斜めガセット〜背面スパイン外壁の滑らかな接続
        (x_gusset_top, y_hook_outer, 6.0),           # Cフック背面リム〜斜めガセットの滑らかな接続
    ]

    with BuildPart() as holder_bp:
        # 1. 一筆書き連続段付きループ断面の押し出し (Z = 0.0 -> 144.0mm)
        with BuildSketch(Plane.XY):
            with BuildLine():
                Polyline(*profile_pts, close=True)
            make_face()
            _fillet_2d_vertices_by_coords(vertex_fillets)
        extrude(amount=HOLDER_WIDTH)

        # 2. 背面縦スパインの3連五角形アーチ大開口 (Z=18〜126mm、屋根角40°)
        first_win_center_x = (
            x_chamber_top + REAR_WINDOW_END_MARGIN + REAR_WINDOW_WIDTH / 2.0
        )
        win_pitch_x = REAR_WINDOW_WIDTH + REAR_WINDOW_PILLAR_WIDTH
        for i in range(REAR_WINDOW_COUNT):
            wx = first_win_center_x + i * win_pitch_x
            # local x = +X, z_dir = -Y => local y = z_dir x x_dir = +Z
            rear_plane = Plane(
                origin=(wx, y_back_outer + 1.0, 0.0),
                x_dir=(1.0, 0.0, 0.0),
                z_dir=(0.0, -1.0, 0.0),
            )
            with BuildSketch(rear_plane):
                _add_pentagon_window_sketch(REAR_WINDOW_WIDTH)
            extrude(amount=WALL_THICKNESS + 2.0, mode=Mode.SUBTRACT)

        # 3. 底面U字トレイ床面の五角形アーチ通気窓 (1窓)
        tray_center_y = (y_tray_inner_front + y_spine_inner) / 2.0
        # local x = +Y, z_dir = +X => local y = z_dir x x_dir = +Z
        bottom_plane = Plane(
            origin=(x_chamber_bot - 1.0, tray_center_y, 0.0),
            x_dir=(0.0, 1.0, 0.0),
            z_dir=(1.0, 0.0, 0.0),
        )
        with BuildSketch(bottom_plane):
            _add_pentagon_window_sketch(BOTTOM_TRAY_WINDOW_WIDTH)
        extrude(amount=WALL_THICKNESS + 2.0, mode=Mode.SUBTRACT)

        # 4. 天板裏フロントアームの五角形アーチ肉抜き窓 (1窓、荷重伝達ショルダー部は完全ソリッドで保護)
        under_arm_center_y = (y_pillar_inner + y_hook_inner) / 2.0
        under_arm_plane = Plane(
            origin=(x_slot_bot - 1.0, under_arm_center_y, 0.0),
            x_dir=(0.0, 1.0, 0.0),
            z_dir=(1.0, 0.0, 0.0),
        )
        with BuildSketch(under_arm_plane):
            _add_pentagon_window_sketch(UNDER_ARM_WINDOW_WIDTH)
        extrude(amount=UNDER_ARM_THICKNESS + 2.0, mode=Mode.SUBTRACT)

    result = holder_bp.part
    result.label = "speaker_stand_router_holder"
    return result


def build_fit_test_piece() -> Part:
    """天板厚み(15.5mm)と天板裏張り出し(実測61.0mm)の嵌合チェック用テストピース(幅12mm)を構築して返す."""
    fit_height = (
        TOP_LIP_THICKNESS + TOP_PLATE_SLOT_GAP + UNDER_ARM_THICKNESS + PILLAR_PAD_DROP
    )  # 58.60mm

    x_top_outer = -fit_height / 2.0
    x_gusset_top = x_top_outer + HOOK_GUSSET_START_X_OFFSET
    x_slot_top = x_top_outer + TOP_LIP_THICKNESS
    x_slot_bot = x_slot_top + TOP_PLATE_SLOT_GAP
    x_arm_bot = x_slot_bot + UNDER_ARM_THICKNESS
    x_pad_bot = x_arm_bot + PILLAR_PAD_DROP

    y_pillar_front = -TOTAL_DEPTH / 2.0
    y_pillar_inner = y_pillar_front + PILLAR_PAD_THICKNESS
    y_hook_inner = y_pillar_front + HOOK_OVERHANG_REACH
    y_hook_outer = y_hook_inner + HOOK_BACK_WALL_THICKNESS
    y_top_lip_front = y_hook_inner - TOP_LIP_DEPTH

    y_back_outer = TOTAL_DEPTH / 2.0
    y_spine_inner = y_back_outer - WALL_THICKNESS

    pts = [
        (x_top_outer, y_hook_outer),
        (x_top_outer, y_top_lip_front),
        (x_slot_top, y_top_lip_front),
        (x_slot_top, y_hook_inner),
        (x_slot_bot, y_hook_inner),
        (x_slot_bot, y_pillar_front),
        (x_pad_bot, y_pillar_front),
        (x_pad_bot, y_pillar_inner),
        (x_arm_bot, y_pillar_inner),
        (x_arm_bot, y_spine_inner),
        (x_pad_bot, y_spine_inner),
        (x_pad_bot, y_back_outer),
        (x_arm_bot, y_back_outer),
        (x_gusset_top, y_hook_outer),
    ]

    fillets = [
        (x_top_outer, y_hook_outer, 3.0),
        (x_top_outer, y_top_lip_front, 2.0),
        (x_slot_top, y_top_lip_front, 1.5),
        (x_slot_top, y_hook_inner, 0.8),
        (x_slot_bot, y_hook_inner, 0.8),
        (x_slot_bot, y_pillar_front, 1.8),
        (x_pad_bot, y_pillar_front, 2.0),
        (x_pad_bot, y_pillar_inner, 2.0),
        (x_arm_bot, y_pillar_inner, 2.5),
        (x_arm_bot, y_spine_inner, 2.5),
        (x_pad_bot, y_spine_inner, 2.0),
        (x_pad_bot, y_back_outer, 2.0),
        (x_arm_bot, y_back_outer, 6.0),
        (x_gusset_top, y_hook_outer, 6.0),
    ]

    with BuildPart() as fit_bp:
        with BuildSketch(Plane.XY):
            with BuildLine():
                Polyline(*pts, close=True)
            make_face()
            _fillet_2d_vertices_by_coords(fillets)
        extrude(amount=FIT_TEST_WIDTH)

    result = fit_bp.part
    result.label = "speaker_stand_router_holder_fit_test"
    return result


def export_models(output_dir: Path | None = None) -> tuple[Path, Path]:
    """本番モデルと事前嵌合テストピースの両方を STEP ファイルとして出力する."""
    target_dir = (
        Path(output_dir)
        if output_dir is not None
        else Path(os.path.dirname(os.path.abspath(__file__)))
    )
    target_dir.mkdir(parents=True, exist_ok=True)

    holder = build_router_holder()
    fit_test = build_fit_test_piece()

    main_step = target_dir / "speaker_stand_router_holder.step"
    fit_step = target_dir / "speaker_stand_router_holder_fit_test.step"

    export_step(holder, str(main_step))
    export_step(fit_test, str(fit_step))
    return main_step, fit_step


if __name__ == "__main__":
    holder_part = build_router_holder()
    fit_test_part = build_fit_test_piece()

    main_path, fit_path = export_models()
    print(f"本番モデルを出力しました: {main_path}")
    print(f"  外形寸法 (X×Y×Z): {holder_part.bounding_box().size}")
    print(f"  体積: {holder_part.volume / 1000.0:.2f} cm^3")
    print(f"嵌合テストモデルを出力しました: {fit_path}")
    print(f"  外形寸法 (X×Y×Z): {fit_test_part.bounding_box().size}")
    print(f"  体積: {fit_test_part.volume / 1000.0:.2f} cm^3")

    try:
        show_object(holder_part, name="speaker_stand_router_holder")
        show_object(
            Pos(0.0, 125.0, 0.0) * fit_test_part,
            name="speaker_stand_router_holder_fit_test",
        )
    except Exception as exc:  # pragma: no cover
        print(f"OCP CAD Viewer 未接続のためプレビュー送信をスキップしました: {exc}")
