"""カーテンレール上用 HomePod mini 2 機械ロック式スタンドの自動幾何・干渉・STEP出力検証テスト."""

from pathlib import Path
import math
import tempfile
import unittest
from build123d import (
    Align,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    Cylinder,
    Plane,
    Polygon,
    Polyline,
    Pos,
    Rot,
    extrude,
    fillet,
    import_step,
    make_face,
    vertices,
)

try:
    from curtain_rail_homepod_mini_stand.curtain_rail_homepod_mini_stand import (
        CABLE_CLIP_BORE_DIA,
        CABLE_CLIP_CENTER_U,
        CABLE_CLIP_CENTER_V,
        CABLE_CLIP_PROTRUSION,
        CABLE_CLIP_SLIT_GAP,
        DECK_TOP_HEIGHT,
        FIT_TEST_WIDTH,
        FIT_U_OFFSET,
        FLEX_OUTER_GAP,
        FRONT_FLEX_REST_U,
        FRONT_HOOK_LIP_DEPTH,
        HOOK_LIP_THICKNESS,
        HOMEPOD_FOOT_DIA,
        M3_AXIS_V,
        M3_NUT_SLOT_U_START,
        MAIN_BODY_DEPTH,
        MAIN_U_OFFSET,
        NOMINAL_RAIL_SPAN,
        OUTER_FRAME_FRONT_U,
        OUTER_FRAME_INNER_U,
        POCKET_CENTER_U,
        POCKET_DEPTH,
        RAIL_CORNER_RADIUS,
        RAIL_RUNNER_SLOT_WIDTH,
        RAIL_SLOT_HEIGHT,
        RAIL_THICKNESS,
        RAIL_WIDTH,
        REAR_HOOK_LIP_DEPTH,
        STAND_WIDTH,
        TOTAL_DEPTH_WITH_CLIP,
        TOTAL_HEIGHT,
        V_OFFSET,
        build_fit_test_piece,
        build_stand,
        export_models,
    )
except ModuleNotFoundError:
    from curtain_rail_homepod_mini_stand import (  # type: ignore[no-redef]
        CABLE_CLIP_BORE_DIA,
        CABLE_CLIP_CENTER_U,
        CABLE_CLIP_CENTER_V,
        CABLE_CLIP_PROTRUSION,
        CABLE_CLIP_SLIT_GAP,
        DECK_TOP_HEIGHT,
        FIT_TEST_WIDTH,
        FIT_U_OFFSET,
        FLEX_OUTER_GAP,
        FRONT_FLEX_REST_U,
        FRONT_HOOK_LIP_DEPTH,
        HOOK_LIP_THICKNESS,
        HOMEPOD_FOOT_DIA,
        M3_AXIS_V,
        M3_NUT_SLOT_U_START,
        MAIN_BODY_DEPTH,
        MAIN_U_OFFSET,
        NOMINAL_RAIL_SPAN,
        OUTER_FRAME_FRONT_U,
        OUTER_FRAME_INNER_U,
        POCKET_CENTER_U,
        POCKET_DEPTH,
        RAIL_CORNER_RADIUS,
        RAIL_RUNNER_SLOT_WIDTH,
        RAIL_SLOT_HEIGHT,
        RAIL_THICKNESS,
        RAIL_WIDTH,
        REAR_HOOK_LIP_DEPTH,
        STAND_WIDTH,
        TOTAL_DEPTH_WITH_CLIP,
        TOTAL_HEIGHT,
        V_OFFSET,
        build_fit_test_piece,
        build_stand,
        export_models,
    )


def _intersection_volume(part_a, part_b) -> float:
    """2つの形状の共通部分体積を返す（非干渉なら 0.0）."""
    inter = part_a & part_b
    if inter is None:
        return 0.0
    solids = inter.solids()
    return sum(s.volume for s in solids)


def _box_uvz(
    u_min: float,
    u_max: float,
    v_min: float,
    v_max: float,
    z_min: float,
    z_max: float,
    u_offset: float = MAIN_U_OFFSET,
):
    """内部設計座標 (u, v, z) の範囲からモデル座標系 (X, Y, Z) の Box を生成する."""
    cx = (u_min + u_max) / 2.0 + u_offset
    cy = (v_min + v_max) / 2.0 + V_OFFSET
    cz = (z_min + z_max) / 2.0
    return Pos(cx, cy, cz) * Box(u_max - u_min, v_max - v_min, z_max - z_min)


def _rounded_rail_uvz(
    u_min: float,
    u_max: float,
    v_min: float,
    v_max: float,
    corner_r: float,
    z_min: float,
    z_max: float,
    u_offset: float = MAIN_U_OFFSET,
):
    """楕円(角丸R)断面を持つC型カーテンレール外形ソリッドを生成する."""
    x0, x1 = u_min + u_offset, u_max + u_offset
    y0, y1 = v_min + V_OFFSET, v_max + V_OFFSET
    with BuildPart() as rail_bp:
        with BuildSketch(Plane.XY.offset(z_min)):
            with BuildLine():
                Polyline((x0, y0), (x1, y0), (x1, y1), (x0, y1), close=True)
            make_face()
            fillet(vertices(), radius=corner_r)
        extrude(amount=z_max - z_min)
    return rail_bp.part


class TestCurtainRailHomePodMiniStand(unittest.TestCase):
    """本番モデルおよび事前嵌合テストピースの仕様適合テスト (v2 実測楕円レール最適化版)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.stand = build_stand()
        cls.fit_test = build_fit_test_piece()

    def test_stand_is_single_valid_closed_solid(self) -> None:
        solids = self.stand.solids()
        self.assertEqual(len(solids), 1, "本番モデルは単一閉ソリッドである必要があります")
        self.assertTrue(solids[0].is_valid, "本番モデルソリッドが invalid です")
        self.assertGreater(solids[0].volume, 25_000.0, "体積が想定より小さすぎます")

    def test_print_orientation_and_bounding_box(self) -> None:
        bb = self.stand.bounding_box()
        # Z=0 ビルドプレート接地 & Z=66.00mm (0.30mm * 220層)
        self.assertAlmostEqual(bb.min.Z, 0.0, places=3)
        self.assertAlmostEqual(bb.max.Z, STAND_WIDTH, places=2)
        self.assertAlmostEqual(bb.size.Z, 66.0, places=2)

        # XY外寸: 95.0mm (本体87.8mm + クリップ7.2mm) x 21.4mm、中心(0,0)、P2S造形範囲内
        self.assertAlmostEqual(MAIN_BODY_DEPTH, 87.8, places=2)
        self.assertAlmostEqual(CABLE_CLIP_PROTRUSION, 7.2, places=2)
        self.assertAlmostEqual(TOTAL_DEPTH_WITH_CLIP, 95.0, places=2)
        self.assertAlmostEqual(TOTAL_HEIGHT, 21.4, places=2)
        self.assertAlmostEqual(bb.size.X, TOTAL_DEPTH_WITH_CLIP, delta=0.05)
        self.assertAlmostEqual(bb.size.Y, TOTAL_HEIGHT, delta=0.05)
        self.assertAlmostEqual((bb.min.X + bb.max.X) / 2.0, 0.0, delta=0.05)
        self.assertAlmostEqual((bb.min.Y + bb.max.Y) / 2.0, 0.0, delta=0.05)
        self.assertLess(bb.size.X, 250.0)
        self.assertLess(bb.size.Y, 250.0)
        self.assertLess(bb.size.Z, 250.0)

    def test_curtain_rails_and_runner_slots_clearance_and_claws(self) -> None:
        # 1. 実測合わせ済みの楕円断面ダブルC型レール (幅17.5 x 厚さ9.5mm、角丸R3.2mm、外寸スパン66.8mm) と自由状態で非干渉
        self.assertAlmostEqual(RAIL_THICKNESS, 9.5, places=2)
        self.assertAlmostEqual(RAIL_SLOT_HEIGHT, 9.8, places=2)
        self.assertAlmostEqual(RAIL_WIDTH, 17.5, places=2)
        self.assertAlmostEqual(RAIL_CORNER_RADIUS, 3.2, places=2)
        self.assertAlmostEqual(NOMINAL_RAIL_SPAN, 66.8, places=2)

        rear_rail = _rounded_rail_uvz(
            0.0,
            RAIL_WIDTH,
            -RAIL_THICKNESS,
            0.0,
            RAIL_CORNER_RADIUS,
            -5.0,
            STAND_WIDTH + 5.0,
        )
        front_rail_start = NOMINAL_RAIL_SPAN - RAIL_WIDTH
        front_rail = _rounded_rail_uvz(
            front_rail_start,
            NOMINAL_RAIL_SPAN,
            -RAIL_THICKNESS,
            0.0,
            RAIL_CORNER_RADIUS,
            -5.0,
            STAND_WIDTH + 5.0,
        )
        self.assertAlmostEqual(_intersection_volume(self.stand, rear_rail), 0.0, places=2)
        self.assertAlmostEqual(_intersection_volume(self.stand, front_rail), 0.0, places=2)

        # 2. 前後両レール底面中央のランナー走行空間 (中央幅6.0mm + 左右余裕1.0mmずつ = 幅8.0mm × 下方全域) と完全非干渉
        self.assertAlmostEqual(RAIL_RUNNER_SLOT_WIDTH, 6.0, places=2)
        runner_margin = 1.0
        rear_slot_center = RAIL_WIDTH / 2.0
        front_slot_center = front_rail_start + RAIL_WIDTH / 2.0
        half_check_w = RAIL_RUNNER_SLOT_WIDTH / 2.0 + runner_margin

        rear_runner_zone = _box_uvz(
            rear_slot_center - half_check_w,
            rear_slot_center + half_check_w,
            -40.0,
            -RAIL_THICKNESS,
            -5.0,
            STAND_WIDTH + 5.0,
        )
        front_runner_zone = _box_uvz(
            front_slot_center - half_check_w,
            front_slot_center + half_check_w,
            -40.0,
            -RAIL_THICKNESS,
            -5.0,
            STAND_WIDTH + 5.0,
        )
        self.assertAlmostEqual(_intersection_volume(self.stand, rear_runner_zone), 0.0, places=2)
        self.assertAlmostEqual(_intersection_volume(self.stand, front_runner_zone), 0.0, places=2)

        # 3. 楕円丸みを越えて底面フラット部を捉える深め下ツメ (奥4.3mm、手前3.6mm) かつ ロック時しなり約0.8mm (自由位置67.6mm)
        self.assertAlmostEqual(REAR_HOOK_LIP_DEPTH, 4.3, places=2)
        self.assertAlmostEqual(FRONT_FLEX_REST_U, 67.6, places=2)
        self.assertAlmostEqual(FRONT_HOOK_LIP_DEPTH, 3.6, places=2)
        self.assertAlmostEqual(HOOK_LIP_THICKNESS, 3.2, places=2)
        self.assertAlmostEqual(FLEX_OUTER_GAP, 3.4, places=2)

        # 手前ツメ先端 (67.6 - 3.6 = 64.0mm) がレール外寸 (66.8mm) より2.8mm内側へ入り込み、片手スナップ仮固定が効くこと
        front_lip_tip_u = FRONT_FLEX_REST_U - FRONT_HOOK_LIP_DEPTH
        self.assertAlmostEqual(front_lip_tip_u, 64.0, places=2)
        self.assertGreater(NOMINAL_RAIL_SPAN - front_lip_tip_u, 2.5)

        rear_claw_probe = _box_uvz(0.5, 3.9, -12.6, -10.2, 10.0, 56.0)
        front_claw_probe = _box_uvz(64.4, 67.3, -12.6, -10.2, 10.0, 56.0)
        self.assertGreater(_intersection_volume(self.stand, rear_claw_probe), 250.0)
        self.assertGreater(_intersection_volume(self.stand, front_claw_probe), 200.0)

        # 4. 手前バネ爪の背面に2.8mmスナップ変形を余裕で逃がす3.4mmの逃げ空間 (u=69.4〜72.8mm) が開いていること
        flex_gap_probe = _box_uvz(70.1, 72.5, -9.0, 3.5, 8.0, 22.0)
        self.assertAlmostEqual(_intersection_volume(self.stand, flex_gap_probe), 0.0, places=2)

    def test_m3_deadlock_bolt_hole_and_hex_nut_slot(self) -> None:
        z_mid = STAND_WIDTH / 2.0
        # 1. M3ボルト軸 (v = M3_AXIS_V = -4.9mm, z = 33.0mm) が外枠 (u=72.8〜82.8mm) を貫通していること
        self.assertAlmostEqual(OUTER_FRAME_INNER_U, 72.8, places=2)
        self.assertAlmostEqual(OUTER_FRAME_FRONT_U, 82.8, places=2)
        self.assertAlmostEqual(M3_AXIS_V, -4.9, places=2)
        bolt_ray = _box_uvz(
            OUTER_FRAME_INNER_U - 0.5,
            OUTER_FRAME_FRONT_U + 0.5,
            M3_AXIS_V - 1.0,
            M3_AXIS_V + 1.0,
            z_mid - 1.0,
            z_mid + 1.0,
        )
        self.assertAlmostEqual(_intersection_volume(self.stand, bolt_ray), 0.0, places=2)

        # 2. 前面ボルト頭ザグリ (u=78.4〜82.8mm, M3×12mm頭ツライチ対応) が開口していること
        cbore_probe = _box_uvz(78.7, 82.8, M3_AXIS_V - 2.0, M3_AXIS_V + 2.0, z_mid - 2.0, z_mid + 2.0)
        self.assertAlmostEqual(_intersection_volume(self.stand, cbore_probe), 0.0, places=2)

        # 3. M3六角ナット下差し込みスロット (u=74.15〜76.80mm) が下端面からナット中心まで開口し、
        #    実寸 M3 六角ナット (二面幅5.50mm × 厚み2.40mm) が非干渉で収まり回転止めされること
        self.assertAlmostEqual(M3_NUT_SLOT_U_START, 74.15, places=2)
        nut_chute_probe = _box_uvz(
            M3_NUT_SLOT_U_START + 0.25,
            M3_NUT_SLOT_U_START + 2.40,
            -13.2,
            M3_AXIS_V + 1.5,
            z_mid - 2.6,
            z_mid + 2.6,
        )
        self.assertAlmostEqual(_intersection_volume(self.stand, nut_chute_probe), 0.0, places=2)

        nut_u = M3_NUT_SLOT_U_START + 0.125
        hf = 5.50 / 2.0
        cr = 5.50 / math.sqrt(3.0)
        hs = cr / 2.0
        nut_plane = Plane(
            origin=(nut_u + MAIN_U_OFFSET, M3_AXIS_V + V_OFFSET, z_mid),
            x_dir=(0, 1, 0),
            z_dir=(1, 0, 0),
        )
        with BuildPart() as real_m3_nut_bp:
            with BuildSketch(nut_plane):
                Polygon(
                    (-hs, -hf),
                    (hs, -hf),
                    (cr, 0.0),
                    (hs, hf),
                    (-hs, hf),
                    (-cr, 0.0),
                    align=None,
                )
            extrude(amount=2.40)
        self.assertAlmostEqual(
            _intersection_volume(self.stand, real_m3_nut_bp.part), 0.0, places=2
        )

        # 30度回転させた場合は60°六角壁と干渉し、空回り防止(アンチスピン)が機能すること
        rotated_nut = (
            Pos(nut_u + MAIN_U_OFFSET, M3_AXIS_V + V_OFFSET, z_mid)
            * Rot(30, 0, 0)
            * Pos(-(nut_u + MAIN_U_OFFSET), -(M3_AXIS_V + V_OFFSET), -z_mid)
            * real_m3_nut_bp.part
        )
        self.assertGreater(_intersection_volume(self.stand, rotated_nut), 1.0)

    def test_acoustic_top_pocket_and_cable_strain_relief_clip(self) -> None:
        z_mid = STAND_WIDTH / 2.0
        pocket_floor_v = DECK_TOP_HEIGHT - POCKET_DEPTH
        self.assertAlmostEqual(DECK_TOP_HEIGHT, 8.4, places=2)
        self.assertAlmostEqual(POCKET_DEPTH, 1.5, places=2)
        self.assertAlmostEqual(POCKET_CENTER_U, 36.5, places=2)
        self.assertAlmostEqual(HOMEPOD_FOOT_DIA, 48.0, places=2)

        # 1. HomePod mini 2 底面シリコン足 (φ48.0mm) が浅溝底面 (v=+6.9mm) 上に非干渉で収まること
        sim_foot = (
            Pos(POCKET_CENTER_U + MAIN_U_OFFSET, pocket_floor_v + 0.05 + V_OFFSET, z_mid)
            * Rot(90, 0, 0)
            * Cylinder(
                radius=HOMEPOD_FOOT_DIA / 2.0,
                height=12.0,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
            )
        )
        self.assertAlmostEqual(_intersection_volume(self.stand, sim_foot), 0.0, places=2)

        # 2. 浅溝外周の天板リム (v=+7.2〜+8.2mm) が存在し、かつ浅溝直下 (v=+0.5〜+6.7mm) が100%ソリッド反射床であること
        rim_probe = _box_uvz(2.0, 8.0, 7.2, 8.2, z_mid - 2.0, z_mid + 2.0)
        solid_floor_probe = _box_uvz(23.5, 49.5, 0.5, 6.7, z_mid - 5.0, z_mid + 5.0)
        self.assertGreater(_intersection_volume(self.stand, rim_probe), 20.0)
        self.assertAlmostEqual(
            _intersection_volume(self.stand, solid_floor_probe),
            solid_floor_probe.volume,
            delta=0.5,
        )

        # 3. 左側面下部の電源コード抜け止めクリップ (z=56.5〜65.5mm) の内径ボアと背面導入スリットが開口していること
        self.assertAlmostEqual(CABLE_CLIP_BORE_DIA, 4.5, places=2)
        self.assertAlmostEqual(CABLE_CLIP_SLIT_GAP, 2.9, places=2)
        sim_cord = Pos(
            CABLE_CLIP_CENTER_U + MAIN_U_OFFSET,
            CABLE_CLIP_CENTER_V + V_OFFSET,
            61.0,
        ) * Cylinder(radius=1.85, height=8.0)
        self.assertAlmostEqual(_intersection_volume(self.stand, sim_cord), 0.0, places=2)

        slit_probe = _box_uvz(
            -12.5,
            CABLE_CLIP_CENTER_U,
            CABLE_CLIP_CENTER_V - 1.1,
            CABLE_CLIP_CENTER_V + 1.1,
            57.0,
            65.0,
        )
        self.assertAlmostEqual(_intersection_volume(self.stand, slit_probe), 0.0, places=2)

        clip_upper_jaw_probe = _box_uvz(
            CABLE_CLIP_CENTER_U - 1.5,
            CABLE_CLIP_CENTER_U + 1.5,
            CABLE_CLIP_CENTER_V + 2.5,
            CABLE_CLIP_CENTER_V + 3.8,
            57.0,
            65.0,
        )
        self.assertGreater(_intersection_volume(self.stand, clip_upper_jaw_probe), 15.0)

    def test_fit_test_piece_and_step_export_roundtrip(self) -> None:
        solids = self.fit_test.solids()
        self.assertEqual(len(solids), 1)
        self.assertTrue(solids[0].is_valid)
        bb = self.fit_test.bounding_box()
        self.assertAlmostEqual(bb.min.Z, 0.0, places=3)
        self.assertAlmostEqual(bb.max.Z, FIT_TEST_WIDTH, places=2)
        self.assertAlmostEqual(bb.size.X, MAIN_BODY_DEPTH, delta=0.05)
        self.assertAlmostEqual(bb.size.Y, TOTAL_HEIGHT, delta=0.05)

        # テストピース中央 (z = 6.0mm) でも M3 ボルト穴およびナットスロットが貫通していること
        z_fit_mid = FIT_TEST_WIDTH / 2.0
        fit_bolt_ray = _box_uvz(
            OUTER_FRAME_INNER_U - 0.5,
            OUTER_FRAME_FRONT_U + 0.5,
            M3_AXIS_V - 1.0,
            M3_AXIS_V + 1.0,
            z_fit_mid - 1.0,
            z_fit_mid + 1.0,
            u_offset=FIT_U_OFFSET,
        )
        self.assertAlmostEqual(_intersection_volume(self.fit_test, fit_bolt_ray), 0.0, places=2)

        with tempfile.TemporaryDirectory() as tmpdir:
            main_path, fit_path = export_models(Path(tmpdir))
            self.assertTrue(main_path.exists())
            self.assertTrue(fit_path.exists())
            reloaded_main = import_step(str(main_path))
            reloaded_fit = import_step(str(fit_path))
            self.assertAlmostEqual(
                reloaded_main.volume,
                self.stand.volume,
                delta=self.stand.volume * 0.002,
            )
            self.assertAlmostEqual(
                reloaded_fit.volume,
                self.fit_test.volume,
                delta=self.fit_test.volume * 0.002,
            )


if __name__ == "__main__":
    unittest.main()
