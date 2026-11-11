"""スチールラック用 テニスラケット掛け（2機種兼用・v3高保持タイトロック版）の自動幾何・予圧・ばね力学・運動学検証テスト."""

import math
from pathlib import Path
import tempfile
import unittest
from build123d import (
    Box,
    Cylinder,
    GeomType,
    Pos,
    Rot,
    import_step,
)

try:
    from steel_rack_tennis_racket_holder.steel_rack_tennis_racket_holder import (
        CRADLE_GROOVE_DEPTH,
        CRADLE_INNER_BACK_U,
        CRADLE_TOTAL_HEIGHT,
        FIT_TEST_HEIGHT,
        FIT_TEST_U_OFFSET,
        FIT_TEST_WIDTH,
        HOLDER_BOTTOM_V,
        HOLDER_TOP_V,
        HOOK_INNER_HALF_GAP,
        J_FLOOR_TOP_V,
        J_FRONT_INNER_U,
        LATCH_ANCHOR_U,
        LATCH_LEAF_SPAN_U,
        LATCH_LEAF_THICKNESS,
        LATCH_OVERHANG_DEG,
        LATCH_POCKET_REAR_U,
        LATCH_STEM_BACK_U,
        LATCH_STEM_THICKNESS,
        LATCH_TIP_U,
        LATCH_TIP_V,
        LATCH_WIDTH,
        MAIN_U_OFFSET,
        PIPE_CENTER_U,
        PIPE_CENTER_V,
        PIPE_CLEARANCE_FROM_SKIRT_U,
        PIPE_DIA,
        PIPE_GAP_TO_SKIRT_V,
        SKIRT_HEIGHT,
        STOPPER_FRONT_U,
        STOPPER_TOP_V,
        build_fit_test_piece,
        build_holder,
        export_models,
    )
except ModuleNotFoundError:
    from steel_rack_tennis_racket_holder import (  # type: ignore[no-redef]
        CRADLE_GROOVE_DEPTH,
        CRADLE_INNER_BACK_U,
        CRADLE_TOTAL_HEIGHT,
        FIT_TEST_HEIGHT,
        FIT_TEST_U_OFFSET,
        FIT_TEST_WIDTH,
        HOLDER_BOTTOM_V,
        HOLDER_TOP_V,
        HOOK_INNER_HALF_GAP,
        J_FLOOR_TOP_V,
        J_FRONT_INNER_U,
        LATCH_ANCHOR_U,
        LATCH_LEAF_SPAN_U,
        LATCH_LEAF_THICKNESS,
        LATCH_OVERHANG_DEG,
        LATCH_POCKET_REAR_U,
        LATCH_STEM_BACK_U,
        LATCH_STEM_THICKNESS,
        LATCH_TIP_U,
        LATCH_TIP_V,
        LATCH_WIDTH,
        MAIN_U_OFFSET,
        PIPE_CENTER_U,
        PIPE_CENTER_V,
        PIPE_CLEARANCE_FROM_SKIRT_U,
        PIPE_DIA,
        PIPE_GAP_TO_SKIRT_V,
        SKIRT_HEIGHT,
        STOPPER_FRONT_U,
        STOPPER_TOP_V,
        build_fit_test_piece,
        build_holder,
        export_models,
    )


def _intersection_volume(shape_a, shape_b) -> float:
    """2つの3D形状のブーリアン積体積 (mm^3) を安全に算出する."""
    common = shape_a & shape_b
    if common is None:
        return 0.0
    solids = common.solids()
    return float(sum(s.volume for s in solids)) if solids else 0.0


def _u_to_y(u: float, u_offset: float = MAIN_U_OFFSET) -> float:
    """設計座標 u (棚板垂直面 u=0, 手前 +u) を造形座標 Y へ変換する."""
    return u + u_offset


def _v_to_z(v: float) -> float:
    """設計座標 v (棚板下端 v=0) を造形座標 Z (Z=0 接地) へ変換する."""
    return v - HOLDER_BOTTOM_V


def _make_rack_3d(
    u_offset: float,
    skirt_t: float = 1.00,
    gap_u: float = 1.95,
    gap_v: float = 2.00,
    du_holder: float = 0.0,
    dv_holder: float = 0.0,
    span_x: float = 140.0,
):
    """ホルダー座標系に対する実機スチールラック（薄鉄板フチ＋前方φ7.2mm丸パイプ）3D形状を生成する."""
    u_shift = -du_holder
    v_shift = -dv_holder

    skirt = Pos(
        0.0,
        _u_to_y(-skirt_t / 2.0 + u_shift, u_offset),
        _v_to_z(SKIRT_HEIGHT / 2.0 + v_shift),
    ) * Box(span_x, skirt_t, SKIRT_HEIGHT)

    shelf_top = Pos(
        0.0,
        _u_to_y(-25.0 + u_shift, u_offset),
        _v_to_z(SKIRT_HEIGHT - 0.50 + v_shift),
    ) * Box(span_x, 50.0, 1.00)

    pc_u = gap_u + PIPE_DIA / 2.0 + u_shift
    pc_v = -(gap_v + PIPE_DIA / 2.0) + v_shift
    pipe = (
        Pos(0.0, _u_to_y(pc_u, u_offset), _v_to_z(pc_v))
        * Rot(0, 90, 0)
        * Cylinder(PIPE_DIA / 2.0, span_x)
    )
    return skirt + shelf_top, pipe


class TestSteelRackTennisRacketHolder(unittest.TestCase):
    """v3 実機装着写真フィードバック反映（ゼロガタ精密スロット＋常時予圧ディープフック＋高保持ばね）検証スイート."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.holder = build_holder()
        cls.fit_test = build_fit_test_piece()

    def test_01_true_rack_constants_and_tight_slot_geometry(self) -> None:
        """丸パイプ前方配置とタイト化された前後・上下寸法、単一有効ソリッドZ=0接地を検証する."""
        self.assertAlmostEqual(PIPE_CLEARANCE_FROM_SKIRT_U, 2.00, places=2)
        self.assertAlmostEqual(PIPE_GAP_TO_SKIRT_V, 2.00, places=2)
        self.assertAlmostEqual(PIPE_CENTER_U, +5.60, places=2)
        self.assertAlmostEqual(PIPE_CENTER_V, -5.60, places=2)

        # v2 で緩かった前後開口(11.25mm)および底面深さ(-11.00mm)が実機に合わせてタイト化されていること
        slot_width = J_FRONT_INNER_U - STOPPER_FRONT_U
        self.assertGreaterEqual(slot_width, 10.35)
        self.assertLessEqual(slot_width, 10.60, "J-slot width must be tightened to eliminate ~1.1mm play")
        self.assertGreaterEqual(J_FLOOR_TOP_V, -9.80, "J-floor must sit close under pipe to eliminate 1.8mm vertical rattle")
        self.assertGreaterEqual(STOPPER_TOP_V, 11.00, "Rear stopper must extend deeply behind steel skirt")

        for name, part in (("holder", self.holder), ("fit_test", self.fit_test)):
            with self.subTest(part=name):
                self.assertTrue(part.is_valid, f"{name} must be valid")
                self.assertEqual(len(part.solids()), 1, f"{name} must be 1 single watertight solid")
                bb = part.bounding_box()
                self.assertAlmostEqual(bb.min.Z, 0.0, places=2)
                self.assertAlmostEqual((bb.min.X + bb.max.X) / 2.0, 0.0, places=2)
                self.assertAlmostEqual((bb.min.Y + bb.max.Y) / 2.0, 0.0, places=2)
                self.assertAlmostEqual(bb.size.Z % 0.60, 0.0, places=2)

        self.assertAlmostEqual(self.holder.bounding_box().size.Z, CRADLE_TOTAL_HEIGHT, places=2)
        self.assertAlmostEqual(self.fit_test.bounding_box().size.X, FIT_TEST_WIDTH, places=2)
        self.assertAlmostEqual(self.fit_test.bounding_box().size.Z, FIT_TEST_HEIGHT, places=2)
        self.assertAlmostEqual(LATCH_LEAF_THICKNESS % 0.60, 0.0, places=2)

    def test_02_active_clamping_preload_and_anti_pivot_wall(self) -> None:
        """着座時に丸パイプ底面受けとディープフックで常時クランプ予圧が発生し、下部逃げガタがないこと."""
        # 1. 薄鉄板下端(v=0.0)高さでも裏ストッパー壁が u=STOPPER_FRONT_U まで詰まっており反時計回り抜けが起きないこと
        hook_probe_x = HOOK_INNER_HALF_GAP + 4.0
        anti_pivot_probe = Pos(
            hook_probe_x,
            _u_to_y(STOPPER_FRONT_U - 0.35),
            _v_to_z(0.0),
        ) * Box(4.0, 0.60, 3.0)
        self.assertGreater(
            _intersection_volume(self.holder, anti_pivot_probe),
            6.5,
            "Rear J-hook must stay flush behind skirt all the way across v=0mm (no lower relief gap)",
        )

        # 2. 実機近傍の公差範囲で、底面着座時に剛体Jフックが無干渉かつ中央フックが常時予圧(>0.20mm)を維持すること
        slope = -1.0 / math.tan(math.radians(LATCH_OVERHANG_DEG))
        rad_oh = math.radians(LATCH_OVERHANG_DEG)
        v_tan_clamped = (J_FLOOR_TOP_V + PIPE_DIA / 2.0) + (PIPE_DIA / 2.0) * math.sin(rad_oh)
        u_hook_at_vtan_relaxed = LATCH_TIP_U + (v_tan_clamped - LATCH_TIP_V) / slope

        cases = [
            ("Tight(1.75,1.75)", 0.95, 1.75, 1.75),
            ("Photo(1.95,2.00)", 1.00, 1.95, 2.00),
            ("Nom  (2.00,2.00)", 1.03, 2.00, 2.00),
            ("Wide (2.15,2.25)", 1.05, 2.15, 2.25),
        ]
        for name, part, u_off in (
            ("holder", self.holder, MAIN_U_OFFSET),
            ("fit_test", self.fit_test, FIT_TEST_U_OFFSET),
        ):
            left_mask = Pos(-50.0 - HOOK_INNER_HALF_GAP, 0.0, 50.0) * Box(100.0, 200.0, 120.0)
            right_mask = Pos(+50.0 + HOOK_INNER_HALF_GAP, 0.0, 50.0) * Box(100.0, 200.0, 120.0)
            rigid_hooks = (part & left_mask) + (part & right_mask)

            for case_label, skirt_t, gap_u, gap_v in cases:
                with self.subTest(part=name, case=case_label):
                    du_seat = -skirt_t - STOPPER_FRONT_U - 0.02
                    # パイプ下端が J_FLOOR_TOP_V の 0.02mm 上に接するクランプ着座位置
                    dv_seat = (-(gap_v + PIPE_DIA) - J_FLOOR_TOP_V) - 0.02
                    shelf, pipe = _make_rack_3d(
                        u_off,
                        skirt_t=skirt_t,
                        gap_u=gap_u,
                        gap_v=gap_v,
                        du_holder=du_seat,
                        dv_holder=dv_seat,
                    )
                    self.assertAlmostEqual(_intersection_volume(rigid_hooks, shelf), 0.0, places=2)
                    self.assertAlmostEqual(_intersection_volume(rigid_hooks, pipe), 0.0, places=2)

                    pc_u_in_h = (gap_u + PIPE_DIA / 2.0) - du_seat
                    pipe_front_in_h = pc_u_in_h + PIPE_DIA / 2.0
                    # ディープフックの噛み込み量が 3.00mm 以上あること (v2 の ~2.1mm から大幅拡大)
                    self.assertGreaterEqual(pipe_front_in_h - LATCH_TIP_U, 3.00)

                    # 着座完了時点でもフックが弛まず +0.20〜+1.00mm の常時クランプ予圧で丸パイプを押さえ続けること
                    u_pipe_tan = pc_u_in_h + (PIPE_DIA / 2.0) * math.cos(rad_oh)
                    clamped_preload = u_pipe_tan - u_hook_at_vtan_relaxed
                    self.assertGreaterEqual(clamped_preload, 0.20, "Must actively clamp pipe with zero vertical rattle")
                    self.assertLessEqual(clamped_preload, 1.00)

    def test_03_straight_up_installation_without_excluded_points(self) -> None:
        """左右の剛体フレーム全体が傾き0°のまま真下(dv=-24mm)から着座位置まで無干渉で直進進入できること."""
        for name, part, u_off in (
            ("holder", self.holder, MAIN_U_OFFSET),
            ("fit_test", self.fit_test, FIT_TEST_U_OFFSET),
        ):
            left_mask = Pos(-50.0 - HOOK_INNER_HALF_GAP, 0.0, 50.0) * Box(100.0, 200.0, 120.0)
            right_mask = Pos(+50.0 + HOOK_INNER_HALF_GAP, 0.0, 50.0) * Box(100.0, 200.0, 120.0)
            rigid_frame = (part & left_mask) + (part & right_mask)

            du_insert = -1.00 - STOPPER_FRONT_U - 0.04  # 実機薄鉄板裏に 0.04mm 沿わせた直進ライン
            dv_clamped = (-(2.00 + PIPE_DIA) - J_FLOOR_TOP_V) - 0.02
            for dv in (-24.0, -18.0, -12.0, -6.0, -2.0, dv_clamped):
                shelf, pipe = _make_rack_3d(
                    u_off,
                    skirt_t=1.00,
                    gap_u=1.95,
                    gap_v=2.00,
                    du_holder=du_insert,
                    dv_holder=dv,
                )
                self.assertAlmostEqual(
                    _intersection_volume(rigid_frame, shelf + pipe),
                    0.0,
                    places=2,
                    msg=f"{name} rigid frame must slide straight up at dv={dv:.2f}mm with zero collision",
                )

    def test_04_isolated_deep_latch_pocket_and_high_retention_force(self) -> None:
        """中央板バネが完全分離され、引き抜き耐力が 6.0kgf (60N) 以上の強力な脱落防止力を持つこと."""
        for name, part, u_off in (
            ("holder", self.holder, MAIN_U_OFFSET),
            ("fit_test", self.fit_test, FIT_TEST_U_OFFSET),
        ):
            with self.subTest(part=name):
                slot_x = LATCH_WIDTH / 2.0 + 0.90
                slot_u_start = LATCH_ANCHOR_U + 0.30
                slot_u_end = LATCH_POCKET_REAR_U - 0.30
                for sgn in (-1.0, 1.0):
                    slot_probe = Pos(
                        sgn * slot_x,
                        _u_to_y(0.5 * (slot_u_start + slot_u_end), u_off),
                        _v_to_z(-2.0),
                    ) * Box(1.00, slot_u_end - slot_u_start, 24.0)
                    self.assertAlmostEqual(_intersection_volume(part, slot_probe), 0.0, places=2)

                self.assertGreaterEqual(LATCH_POCKET_REAR_U - LATCH_STEM_BACK_U, 5.50)
                pocket_probe = Pos(
                    0.0,
                    _u_to_y(0.5 * (LATCH_STEM_BACK_U + LATCH_POCKET_REAR_U), u_off),
                    _v_to_z(-3.0),
                ) * Box(LATCH_WIDTH, (LATCH_POCKET_REAR_U - LATCH_STEM_BACK_U) - 0.40, 22.0)
                self.assertAlmostEqual(_intersection_volume(part, pocket_probe), 0.0, places=2)

        # Castigliano エネルギー法による押し込みクリック力・引き抜き耐力・層間応力の検証
        L_h = LATCH_LEAF_SPAN_U
        L_v = LATCH_TIP_V - (HOLDER_BOTTOM_V + LATCH_LEAF_THICKNESS / 2.0)
        I_h = LATCH_WIDTH * (LATCH_LEAF_THICKNESS**3) / 12.0
        I_v = LATCH_WIDTH * (LATCH_STEM_THICKNESS**3) / 12.0
        delta_click = 9.05 - LATCH_TIP_U  # 実機パイプ手前端(+9.05mm)通過時の押し込み量 (~3.25mm)

        alpha = math.radians(90.0 - LATCH_OVERHANG_DEG)  # 水平からのフック角 (35.0°)
        mu = 0.22
        pulloff_ratio = (math.cos(alpha) + mu * math.sin(alpha)) / (math.sin(alpha) - mu * math.cos(alpha))

        for mat, E_mpa, f_click_min, f_click_max in (
            ("PETG", 2100.0, 24.0, 38.0),
            ("PLA Matte", 2350.0, 26.0, 42.0),
            ("PLA", 3000.0, 32.0, 50.0),
        ):
            comp = (L_v**3) / (3.0 * E_mpa * I_v) + (L_v**2) * L_h / (E_mpa * I_h)
            k = 1.0 / comp
            f_click = k * delta_click
            f_pulloff = f_click * pulloff_ratio
            sig_v_z = (f_click * L_v) * (LATCH_STEM_THICKNESS / 2.0) / I_v

            self.assertGreaterEqual(f_click, f_click_min, f"{mat} click force must feel firm and solid")
            self.assertLessEqual(f_click, f_click_max, f"{mat} click force must remain hand-installable")
            self.assertGreaterEqual(
                f_pulloff,
                60.0,
                f"{mat} downward pull-off resistance must exceed 60N (>6.1kgf) so it never falls off",
            )
            self.assertLess(sig_v_z, 17.5, f"{mat} Z-layer tensile stress must stay well below delamination")

    def test_05_both_rackets_fit_in_cradle_and_clear_shelf(self) -> None:
        """CLASH 26 V3.0 と HEAD EXTREME MP 2026 の双方がV字溝に安定着座し棚板・パイプと十分離れること."""
        rackets = [
            ("Wilson CLASH 26 V3.0", 35.0, 121.0, 99.0, 24.0, 24.0),
            ("HEAD EXTREME MP 2026", 41.0, 130.0, 99.0, 21.5, 26.0),
        ]
        u_mid = CRADLE_INNER_BACK_U + CRADLE_GROOVE_DEPTH / 2.0

        for name, w_bot, w_top, tri_h, t_throat, t_max in rackets:
            with self.subTest(racket=name):
                half_slope = (w_top - w_bot) / (2.0 * tri_h)
                half_angle_deg = math.degrees(math.atan(half_slope))

                def make_racket_at(v_tri_bot: float):
                    shaft_len = 110.0
                    shaft_w = 13.5
                    parts = []
                    for sgn in (-1.0, 1.0):
                        x_mid = sgn * (w_bot / 2.0 + half_slope * (tri_h / 2.0) - shaft_w / 2.0)
                        v_mid = v_tri_bot + tri_h / 2.0
                        arm = (
                            Pos(x_mid, _u_to_y(u_mid), _v_to_z(v_mid))
                            * Rot(0, sgn * half_angle_deg, 0)
                            * Box(shaft_w, t_throat, shaft_len)
                        )
                        parts.append(arm)
                    bridge = Pos(
                        0.0,
                        _u_to_y(u_mid),
                        _v_to_z(v_tri_bot + tri_h + 6.0),
                    ) * Box(w_top - 10.0, t_max, 12.0)
                    handle = Pos(
                        0.0,
                        _u_to_y(u_mid),
                        _v_to_z(v_tri_bot - 45.0),
                    ) * Box(29.0, t_throat, 90.0)
                    return parts[0] + parts[1] + bridge + handle

                self.assertAlmostEqual(_intersection_volume(self.holder, make_racket_at(10.0)), 0.0, places=2)
                v_hi, v_lo = 10.0, -45.0
                self.assertGreater(_intersection_volume(self.holder, make_racket_at(v_lo)), 5.0)
                for _ in range(18):
                    v_m = 0.5 * (v_hi + v_lo)
                    if _intersection_volume(self.holder, make_racket_at(v_m)) > 0.05:
                        v_lo = v_m
                    else:
                        v_hi = v_m

                v_seat = v_hi
                self.assertGreater(v_seat + tri_h, HOLDER_TOP_V + 15.0)
                racket_backmost_u = u_mid - t_max / 2.0
                self.assertGreaterEqual(racket_backmost_u, PIPE_CENTER_U + PIPE_DIA / 2.0 + 8.0)

    def test_06_support_free_overhangs_and_step_export_roundtrip(self) -> None:
        """Z>0.15mm の全面がサポート不要範囲(<=55.0°: n.Z >= -0.825)に収まり、STEP往復が正常であること."""
        for name, part in (("holder", self.holder), ("fit_test", self.fit_test)):
            for face in part.faces():
                cz = face.center().Z
                if cz <= 0.15:
                    continue
                n = face.normal_at(face.center())
                if n.Z < -0.825:
                    self.assertLess(
                        face.area,
                        2.0,
                        f"{name} exceeds 55-deg support-free overhang at Z={cz:.2f}mm (area={face.area:.1f}mm^2, nZ={n.Z:.3f})",
                    )

        with tempfile.TemporaryDirectory() as tmpdir:
            main_path, fit_path = export_models(Path(tmpdir))
            self.assertTrue(main_path.exists())
            self.assertTrue(fit_path.exists())
            self.assertEqual(len(import_step(str(main_path)).solids()), 1)
            self.assertEqual(len(import_step(str(fit_path)).solids()), 1)

    def test_07_racket_contact_fillets_and_fit_test_orientation_cue(self) -> None:
        """クレードル長尺エッジに保護Rがあり、テストピース前後の高さ差で向きが即判別できること."""
        curved_long_faces = [
            f
            for f in self.holder.faces()
            if f.geom_type in (GeomType.CYLINDER, GeomType.TORUS, GeomType.BSPLINE)
            and f.bounding_box().size.Z > 45.0
        ]
        self.assertGreaterEqual(len(curved_long_faces), 12)

        front_half = self.fit_test & (Pos(0.0, 20.0, 50.0) * Box(80.0, 40.0, 100.0))
        rear_half = self.fit_test & (Pos(0.0, -25.0, 50.0) * Box(80.0, 40.0, 100.0))
        self.assertAlmostEqual(front_half.bounding_box().max.Z, FIT_TEST_HEIGHT, places=2)
        self.assertLess(rear_half.bounding_box().max.Z, FIT_TEST_HEIGHT - 2.0)


if __name__ == "__main__":
    unittest.main()
