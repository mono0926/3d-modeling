"""
設計要件:
    - マットブラックのスチールラック（天板端部が下に18.1mm折り曲げられた約1.0mm厚の薄鉄板フチ ＋
      その板の垂直面から手前へ2.0mmクリアランスを空け、下端から2.0mm下に通る φ7.2mm 水平丸パイプ）に
      前後上下のガタつきゼロ・斜め抜けゼロでワンタッチ固定できる共通ベースフックモジュール。
    - 実機4世代（v1〜v4）のテストプリントにより確立した「段付き丸パイプ専用ポケット（幅7.70mm・底R0.80mm）＋
      頂点越え常時予圧35°ディープフック板バネ（u=+4.55mm・予圧+0.75mm）＋ 指掛けリリースタブ（v=+9.60mm）」を
      Single Source of Truth として一元管理し、ラケット掛け・ボールスタンド・今後のラック用アクセサリーから
      共通インポートして再利用できる構造とする。
    - アタッチメントごとに異なる外幅（outer_half_span）やフロント背板肉厚（spine_thickness）・高さ（spine_height）のみを
      パラメトリックに指定可能とし、ラック接触部・板バネ部の最適寸法は厳密に保護する。
    - 最新の3Dプリンター（Bambu Lab P2S Combo 等）での出力を想定し、Z=0 連続繊維ベタ置きの完全サポートフリー設計とする。
    - 単体実行時には事前嵌合確認用の基準テストピース（steel_rack_base_hook.step）を同ディレクトリへ出力する。

推奨フィラメント:
    - PETG（Bambu PETG HF / PETG Matte ブラック推奨 — 常時クランプ予圧に対する長期耐クリープ性と靭性のため）
    - PLA Matte / PLA Tough でも使用可能（15.05mmロングリーフ＋根元C1.2mmガセットにより層間応力を抑制済み）。

推奨スライサー設定:
    - レイヤー高さ (Layer height): 0.20mm (0.4mmノズル時) または 0.30mm (0.6mmノズル時) — 全高28.80mm / リーフ厚1.80mm 整数倍
    - 壁ループ (Wall loops): 3〜4
    - インフィル (Sparse infill): 20〜25% (Gyroid または Cross Hatch)
    - サポート (Supports): なし (None — 全オーバーハング55.0°以下のサポートフリー設計)
    - ブリム (Brim): 不要

印刷統計（予想）:
    - steel_rack_base_hook.step: 印刷時間 約18〜22分、フィラメント使用量 約13〜16g（ソリッド体積 16.60cm³）

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

import math
from pathlib import Path
from build123d import *

try:
    from ocp_vscode import show_object
except ImportError:  # pragma: no cover

    def show_object(*_args, **_kwargs) -> None:
        pass


# ==============================================================================
# スチールラック実機検証済み 共通ロック定数 (単位: mm / 角度: deg)
# 内部設計座標 (x, u, v):
#   x: ラック左右方向 (中央 x = 0.00)
#   u: 前後方向 (棚板の垂直面[前面] u = 0.00, 室内手前 +u, 棚奥側 -u)
#   v: 上下方向 (棚板前垂れ下端 v = 0.00, 上方 +v, 下方 -v, ビルドプレート接地 v = -15.00)
# ==============================================================================

# --- スチールラック実測基準寸法 ---
PIPE_DIA = 7.20  # 水平丸パイプ外径
PIPE_RADIUS = PIPE_DIA / 2.0  # 3.60mm
PIPE_CLEARANCE_FROM_SKIRT_U = 2.00  # 棚板垂直面(u=0.0)から丸パイプ奥面(u=+2.0)までの前後クリアランス
PIPE_GAP_TO_SKIRT_V = 2.00  # 棚板下端(v=0.0)から丸パイプ上端(v=-2.0)までの上下クリアランス
PIPE_CENTER_U = PIPE_CLEARANCE_FROM_SKIRT_U + PIPE_RADIUS  # +5.60mm (丸パイプ u = +2.00 〜 +9.20mm)
PIPE_CENTER_V = -(PIPE_GAP_TO_SKIRT_V + PIPE_RADIUS)  # -5.60mm (丸パイプ v = -9.20 〜 -2.00mm)

SKIRT_HEIGHT = 18.10  # 棚板垂直面の縦高さ (v = 0.00 〜 +18.10mm)
SKIRT_THICKNESS_MAX = 1.05  # 約1.0mm薄鉄板の実測基準板厚

# --- ベース高さ・事前嵌合テストピース基準寸法 (0.60mm 整数倍) ---
HOLDER_BOTTOM_V = -15.00  # ビルドプレート接地面 (Z = 0.00mm)
FIT_TEST_TOP_V = 13.80  # テストピースおよび下部フロントスパイン基準上端
FIT_TEST_HEIGHT = FIT_TEST_TOP_V - HOLDER_BOTTOM_V  # 28.80mm (= 0.60mm * 48)
DEFAULT_SPINE_THICKNESS = 4.80  # 標準フロントスパイン肉厚

# --- デュアル剛体Jフック ＆ 段付き丸パイプ専用ポケット寸法 ---
LATCH_WIDTH = 16.00  # 中央独立ロング板バネラッチ幅 (x = -8.00 〜 +8.00mm)
LATCH_SIDE_GAP = 1.80  # 板バネ左右の完全分離スリット幅 (スライサー融着ゼロ保証)
HOOK_INNER_HALF_GAP = LATCH_WIDTH / 2.0 + LATCH_SIDE_GAP  # 9.80mm (中央19.60mmベイ)

FIT_TEST_SIDE_HOOK_WIDTH = 8.70  # テストピースの左右対称Jフック幅 (各8.70mm)
FIT_TEST_WIDTH = 2.0 * (HOOK_INNER_HALF_GAP + FIT_TEST_SIDE_HOOK_WIDTH)  # 37.00mm

HOOK_REAR_BACK_U = -6.80  # 背面Uステム外側面
STOPPER_FRONT_U = -1.06  # 上部薄鉄板裏ストッパー壁 (v=-0.80〜+11.80mm まで全面フラット密着)
STOPPER_LEADIN_CHAMFER = 0.80  # 上端先端のみの導入45°テーパー量
STOPPER_TOP_V = 12.60  # ストッパー上端 (フロントスパインより1.2mm低く前後識別可能)

SKIRT_STEP_TOP_V = -0.80  # 薄鉄板下端(v=0.0)と干渉しない段差開始高さ
PIPE_REAR_SEAT_U = 1.62  # 丸パイプ下半分専用の背面受け座 (前後ガタ完全解消)
PIPE_STEP_BOTTOM_V = SKIRT_STEP_TOP_V - (PIPE_REAR_SEAT_U - STOPPER_FRONT_U)  # -3.48mm (上向き45°スロープ)
J_FLOOR_TOP_V = -9.55  # 丸パイプ底面受け座 (底肉厚 5.45mm)
J_FRONT_INNER_U = 9.32  # Jフック前側ガイド内壁 (下部パイプポケット幅 7.70mm)
J_FRONT_FUNNEL = 1.15  # 前側上端入口の45°導入ファンネル量
J_DECK_TOP_V = 8.40  # Jフック前側デッキ上面
J_REAR_OUTER_CHAMFER = 1.60  # 背面外上角の面取り量

# --- 中央 Z=0 連続繊維・頂点越え35°ディープフック板バネラッチ寸法 ---
LATCH_ANCHOR_U = -4.30  # 背面下部クロスバーへの固定根元位置
LATCH_LEAF_THICKNESS = 1.80  # Z=0 水平リーフ板厚 (0.60mm * 3)
LATCH_STEM_FRONT_U = 8.95  # 垂直ステム前面
LATCH_STEM_THICKNESS = 3.60  # 垂直ステム前後厚
LATCH_STEM_BACK_U = LATCH_STEM_FRONT_U + LATCH_STEM_THICKNESS  # +12.55mm
LATCH_LEAF_SPAN_U = 0.5 * (LATCH_STEM_FRONT_U + LATCH_STEM_BACK_U) - LATCH_ANCHOR_U  # 15.05mm

LATCH_OVERHANG_DEG = 55.0  # ディープフック下面の造形オーバーハング角 (水平から35.0°)
LATCH_TIP_U = 4.55  # 丸パイプ頂点(+5.60mm)を越える深爪先端位置
LATCH_TIP_V = -1.42  # 着座完了時にも常時クランプ予圧を残す高さ設定
LATCH_NOSE_BLUNT_H = 0.45  # ノズル造形安定化のための先端垂直フラット高さ
LATCH_RELEASE_TOP_V = 9.60  # 指先が掛かりやすいリリースタブ上端
LATCH_TOP_TAPER_U = 0.80  # リリースタブ上端背面のテーパー逃げ量
LATCH_POCKET_GAP = 9.35  # ステム背面のたわみ逃げポケット基準幅 (上端10.15mm)
LATCH_POCKET_REAR_U = LATCH_STEM_BACK_U + LATCH_POCKET_GAP  # +21.90mm


def build_j_hook_2d_face(
    spine_thickness: float = DEFAULT_SPINE_THICKNESS,
    spine_height: float = FIT_TEST_HEIGHT,
) -> Face:
    """(u, v) 平面における段付きパイプ専用ポケット付き剛体Jフック断面 Face を生成する."""
    spine_front_u = LATCH_POCKET_REAR_U + spine_thickness
    spine_top_v = HOLDER_BOTTOM_V + spine_height

    pts = [
        (HOOK_REAR_BACK_U, HOLDER_BOTTOM_V),
        (spine_front_u, HOLDER_BOTTOM_V),
        (spine_front_u, spine_top_v),
        (LATCH_POCKET_REAR_U, spine_top_v),
        (LATCH_POCKET_REAR_U, J_DECK_TOP_V),
        (J_FRONT_INNER_U + J_FRONT_FUNNEL, J_DECK_TOP_V),
        (J_FRONT_INNER_U, J_DECK_TOP_V - J_FRONT_FUNNEL),
        (J_FRONT_INNER_U, J_FLOOR_TOP_V),
        (PIPE_REAR_SEAT_U, J_FLOOR_TOP_V),
        (PIPE_REAR_SEAT_U, PIPE_STEP_BOTTOM_V),
        (STOPPER_FRONT_U, SKIRT_STEP_TOP_V),
        (STOPPER_FRONT_U, STOPPER_TOP_V - STOPPER_LEADIN_CHAMFER),
        (STOPPER_FRONT_U - STOPPER_LEADIN_CHAMFER, STOPPER_TOP_V),
        (HOOK_REAR_BACK_U + J_REAR_OUTER_CHAMFER, STOPPER_TOP_V),
        (HOOK_REAR_BACK_U, STOPPER_TOP_V - J_REAR_OUTER_CHAMFER),
        (HOOK_REAR_BACK_U, HOLDER_BOTTOM_V),
    ]

    with BuildSketch(Plane.YZ) as sk:
        with BuildLine():
            Polyline(*pts)
        make_face()
        floor_corners = [
            vtx
            for vtx in sk.vertices()
            if abs(vtx.Y - J_FLOOR_TOP_V) < 0.05
            and (abs(vtx.X - PIPE_REAR_SEAT_U) < 0.05 or abs(vtx.X - J_FRONT_INNER_U) < 0.05)
        ]
        if floor_corners:
            fillet(floor_corners, 0.80)
    return sk.sketch.faces()[0]


def build_center_latch_2d_face() -> Face:
    """(u, v) 平面における頂点越え常時予圧35°ディープフック板バネラッチ断面 Face を生成する."""
    v_leaf_top = HOLDER_BOTTOM_V + LATCH_LEAF_THICKNESS  # -13.20mm
    u_overlap_back = LATCH_ANCHOR_U - 1.00

    du_nose = LATCH_STEM_FRONT_U - LATCH_TIP_U  # 4.40mm
    hook_slope = -1.0 / math.tan(math.radians(LATCH_OVERHANG_DEG))  # -0.7002075
    v_lock_root = LATCH_TIP_V + hook_slope * du_nose  # -4.50mm

    v_tip_top = LATCH_TIP_V + LATCH_NOSE_BLUNT_H  # -0.97mm
    v_bevel_top = v_tip_top + du_nose  # +3.43mm

    gusset_front = 1.20
    taper_start_v = 2.00

    pts = [
        (u_overlap_back, HOLDER_BOTTOM_V),
        (LATCH_STEM_BACK_U, HOLDER_BOTTOM_V),
        (LATCH_STEM_BACK_U, taper_start_v),
        (LATCH_STEM_BACK_U - LATCH_TOP_TAPER_U, LATCH_RELEASE_TOP_V),
        (LATCH_STEM_FRONT_U, LATCH_RELEASE_TOP_V),
        (LATCH_STEM_FRONT_U, v_bevel_top),
        (LATCH_TIP_U, v_tip_top),
        (LATCH_TIP_U, LATCH_TIP_V),
        (LATCH_STEM_FRONT_U, v_lock_root),
        (LATCH_STEM_FRONT_U, v_leaf_top + gusset_front),
        (LATCH_STEM_FRONT_U - gusset_front, v_leaf_top),
        (u_overlap_back, v_leaf_top),
        (u_overlap_back, HOLDER_BOTTOM_V),
    ]

    with BuildSketch(Plane.YZ) as sk:
        with BuildLine():
            Polyline(*pts)
        make_face()
    return sk.sketch.faces()[0]


def build_steel_rack_mounting_core(
    outer_half_span: float,
    spine_thickness: float = DEFAULT_SPINE_THICKNESS,
    spine_height: float = FIT_TEST_HEIGHT,
    add_front_notch: bool = False,
    align_bottom_to_z0: bool = False,
) -> Part:
    """実機検証済みのスチールラック用デュアルJフック＋中央ディープフック板バネのマウントコアを生成する."""
    if outer_half_span <= HOOK_INNER_HALF_GAP + 2.0:
        raise ValueError(
            f"outer_half_span ({outer_half_span}) must exceed HOOK_INNER_HALF_GAP + 2.0 ({HOOK_INNER_HALF_GAP + 2.0})"
        )

    side_hook_w = outer_half_span - HOOK_INNER_HALF_GAP
    j_face = build_j_hook_2d_face(spine_thickness=spine_thickness, spine_height=spine_height)

    hook_right = extrude(
        Pos(HOOK_INNER_HALF_GAP, 0.0, 0.0) * j_face,
        amount=side_hook_w,
        dir=(1, 0, 0),
    )
    hook_left = extrude(
        Pos(-outer_half_span, 0.0, 0.0) * j_face,
        amount=side_hook_w,
        dir=(1, 0, 0),
    )

    rear_bar_u_len = LATCH_ANCHOR_U - HOOK_REAR_BACK_U  # 2.50mm
    rear_bar_h = J_FLOOR_TOP_V - HOLDER_BOTTOM_V  # 5.45mm
    rear_crossbar = Pos(
        0.0,
        0.5 * (HOOK_REAR_BACK_U + LATCH_ANCHOR_U),
        HOLDER_BOTTOM_V + 0.5 * rear_bar_h,
    ) * Box(2.0 * outer_half_span, rear_bar_u_len, rear_bar_h)

    spine_front_u = LATCH_POCKET_REAR_U + spine_thickness
    front_spine = Pos(
        0.0,
        0.5 * (LATCH_POCKET_REAR_U + spine_front_u),
        HOLDER_BOTTOM_V + 0.5 * spine_height,
    ) * Box(2.0 * outer_half_span, spine_thickness, spine_height)

    latch_face = build_center_latch_2d_face()
    center_latch = extrude(
        Pos(-LATCH_WIDTH / 2.0, 0.0, 0.0) * latch_face,
        amount=LATCH_WIDTH,
        dir=(1, 0, 0),
    )

    core = hook_right + hook_left + rear_crossbar + front_spine + center_latch

    if add_front_notch:
        spine_top_v = HOLDER_BOTTOM_V + spine_height
        notch = (
            Pos(0.0, 0.5 * (LATCH_POCKET_REAR_U + spine_front_u), spine_top_v)
            * Rot(0, 45, 0)
            * Box(2.40, spine_thickness + 2.0, 2.40)
        )
        core = core - notch

    cleaned = core.clean()
    if align_bottom_to_z0:
        cleaned = Pos(0.0, 0.0, -HOLDER_BOTTOM_V) * cleaned
    return cleaned.solids()[0]


def build_steel_rack_fit_test_piece(spine_thickness: float = DEFAULT_SPINE_THICKNESS) -> Part:
    """XY原点中央・Z=0接地に整列済みのスチールラック事前嵌合テストピースを生成する."""
    core = build_steel_rack_mounting_core(
        outer_half_span=FIT_TEST_WIDTH / 2.0,
        spine_thickness=spine_thickness,
        spine_height=FIT_TEST_HEIGHT,
        add_front_notch=True,
        align_bottom_to_z0=True,
    )
    bb = core.bounding_box()
    cx = 0.5 * (bb.min.X + bb.max.X)
    cy = 0.5 * (bb.min.Y + bb.max.Y)
    return (Pos(-cx, -cy, -bb.min.Z) * core).solids()[0]


def export_models(output_dir: Path | None = None) -> Path:
    """単体嵌合確認用STEPファイル (steel_rack_base_hook.step) を出力する."""
    target_dir = Path(__file__).resolve().parent if output_dir is None else Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    step_path = target_dir / "steel_rack_base_hook.step"
    export_step(build_steel_rack_fit_test_piece(), str(step_path))
    return step_path


if __name__ == "__main__":
    fit_part = build_steel_rack_fit_test_piece()
    out = export_models()
    print(f"Exported steel rack base hook STEP: {out}")
    show_object(fit_part, name="steel_rack_base_hook")
