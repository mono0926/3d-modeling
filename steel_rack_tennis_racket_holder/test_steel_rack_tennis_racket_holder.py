"""スチールラック用 テニスラケット掛け（2機種兼用・v4段付きパイプ専用座＆全角度アンチスリップアウト版）自動検証テスト."""

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
        CRADLE_BACKPLATE_REAR_U,
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
        LATCH_RELEASE_TOP_V,
        LATCH_STEM_BACK_U,
        LATCH_STEM_THICKNESS,
        LATCH_TIP_U,
        LATCH_TIP_V,
        LATCH_TOP_TAPER_U,
        LATCH_WIDTH,
        MAIN_U_OFFSET,
        PIPE_CENTER_U,
        PIPE_CENTER_V,
        PIPE_CLEARANCE_FROM_SKIRT_U,
        PIPE_DIA,
        PIPE_GAP_TO_SKIRT_V,
        PIPE_REAR_SEAT_U,
        SKIRT_HEIGHT,
        STOPPER_FRONT_U,
        STOPPER_TOP_V,
        build_fit_test_piece,
        build_holder,
        export_models,
    )
except ModuleNotFoundError:
    from steel_rack_tennis_racket_holder import (  # type: ignore[no-redef]
        CRADLE_BACKPLATE_REAR_U,
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
        LATCH_RELEASE_TOP_V,
        LATCH_STEM_BACK_U,
        LATCH_STEM_THICKNESS,
        LATCH_TIP_U,
        LATCH_TIP_V,
        LATCH_TOP_TAPER_U,
        LATCH_WIDTH,
        MAIN_U_OFFSET,
        PIPE_CENTER_U,
        PIPE_CENTER_V,
        PIPE_CLEARANCE_FROM_SKIRT_U,
        PIPE_DIA,
        PIPE_GAP_TO_SKIRT_V,
        PIPE_REAR_SEAT_U,
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
    """v4 実機テスト写真(1枚目・2枚目)反映（段付きパイプ専用ポケット＋頂点越えディープフックによる全角度抜け防止）検証スイート."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.holder = build_holder()
        cls.fit_test = build_fit_test_piece()

    def test_01_stepped_pipe_pocket_and_over_crown_hook_constants(self) -> None:
        """丸パイプ専用下部ポケット(前後ガタ解消)と頂点越えフック先端位置、Z=0単一閉ソリッドを検証する."""
        self.assertAlmostEqual(PIPE_CLEARANCE_FROM_SKIRT_U, 2.00, places=2)
        self.assertAlmostEqual(PIPE_GAP_TO_SKIRT_V, 2.00, places=2)
        self.assertAlmostEqual(PIPE_CENTER_U, +5.60, places=2)
        self.assertAlmostEqual(PIPE_CENTER_V, -5.60, places=2)

        # v3で丸パイプ裏に約3.0mm残っていた遊びを埋め、φ7.20mmパイプ自体を前後約7.70mmでタイトに抱えること
        pipe_pocket_width = J_FRONT_INNER_U - PIPE_REAR_SEAT_U
        self.assertGreaterEqual(pipe_pocket_width, 7.55)
        self.assertLessEqual(
            pipe_pocket_width,
            7.80,
            "Lower pipe pocket must cradle the 7.20mm pipe directly to eliminate horizontal play",
        )
        self.assertGreaterEqual(J_FLOOR_TOP_V, -9.60)
        self.assertGreaterEqual(STOPPER_TOP_V, 12.00)

        # 2枚目写真(約25°傾斜)でのスルッと抜けを防ぐため、ラッチ先端がパイプ頂点(+5.55mm)を越えて u<=+4.65mm まで伸びていること
        self.assertLessEqual(
            LATCH_TIP_U,
            4.65,
            "Latch tip must reach past pipe crown (<= +4.65mm) so 25-deg tilt cannot slip off",
        )
        self.assertLessEqual(
            LATCH_TIP_U - STOPPER_FRONT_U,
            5.70,
            "Upper throat width must be <=5.70mm vs 7.20mm pipe (>=1.50mm interference even without lower step)",
        )

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

    def test_02_active_clamping_preload_and_rear_pipe_seat_presence(self) -> None:
        """丸パイプ真裏(v=-6mm)に専用リアシート実体が存在し、4公差条件すべてで常時クランプ予圧を維持すること."""
        hook_probe_x = HOOK_INNER_HALF_GAP + 4.0
        # 1. 薄鉄板下端(v=0.0)高さの裏ストッパー壁存在確認
        anti_pivot_probe = Pos(
            hook_probe_x,
            _u_to_y(STOPPER_FRONT_U - 0.35),
            _v_to_z(0.0),
        ) * Box(4.0, 0.60, 2.0)
        self.assertGreater(_intersection_volume(self.holder, anti_pivot_probe), 4.0)

        # 2. 丸パイプ真裏(v=-6.0mm, u=+0.50mm)に遊び埋めリアシートの実体が詰まっていること (v3では空洞0だった箇所)
        rear_pipe_seat_probe = Pos(
            hook_probe_x,
            _u_to_y(0.5 * (STOPPER_FRONT_U + PIPE_REAR_SEAT_U)),
            _v_to_z(-6.0),
        ) * Box(4.0, 2.0, 4.0)
        self.assertGreater(
            _intersection_volume(self.holder, rear_pipe_seat_probe),
            28.0,
            "3mm void behind lower pipe must be filled with dedicated rear pipe seat",
        )

        # 3. 4公差条件で剛体Jフックが無干渉着座し、中央ディープフックが常時予圧(+0.45〜+1.10mm)で押さえ続けること
        slope = -1.0 / math.tan(math.radians(LATCH_OVERHANG_DEG))
        rad_oh = math.radians(LATCH_OVERHANG_DEG)
        v_tan_clamped = (J_FLOOR_TOP_V + PIPE_DIA / 2.0) + (PIPE_DIA / 2.0) * math.sin(rad_oh)
        u_hook_at_vtan_relaxed = LATCH_TIP_U + (v_tan_clamped - LATCH_TIP_V) / slope

        cases = [
            ("Tight(1.80,1.80)", 0.95, 1.80, 1.80),
            ("Photo(1.95,2.00)", 1.00, 1.95, 2.00),
            ("Nom  (2.00,2.00)", 1.02, 2.00, 2.00),
            ("Wide (2.10,2.20)", 1.05, 2.10, 2.20),
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
                    # 噛み込み深さが 4.20mm 以上あること (v3 の 3.25mm からさらに深爪化)
                    self.assertGreaterEqual(pipe_front_in_h - LATCH_TIP_U, 4.20)

                    u_pipe_tan = pc_u_in_h + (PIPE_DIA / 2.0) * math.cos(rad_oh)
                    clamped_preload = u_pipe_tan - u_hook_at_vtan_relaxed
                    self.assertGreaterEqual(clamped_preload, 0.45)
                    self.assertLessEqual(clamped_preload, 1.15)

    def test_03_straight_up_installation_with_stepped_pocket(self) -> None:
        """段付きパイプポケット付きでも左右剛体フレームが傾き0°のまま真下(dv=-24mm)から無干渉で直進進入できること."""
        for name, part, u_off in (
            ("holder", self.holder, MAIN_U_OFFSET),
            ("fit_test", self.fit_test, FIT_TEST_U_OFFSET),
        ):
            left_mask = Pos(-50.0 - HOOK_INNER_HALF_GAP, 0.0, 50.0) * Box(100.0, 200.0, 120.0)
            right_mask = Pos(+50.0 + HOOK_INNER_HALF_GAP, 0.0, 50.0) * Box(100.0, 200.0, 120.0)
            rigid_frame = (part & left_mask) + (part & right_mask)

            du_insert = -1.00 - STOPPER_FRONT_U - 0.03
            dv_clamped = (-(2.00 + PIPE_DIA) - J_FLOOR_TOP_V) - 0.02
            for dv in (-24.0, -18.0, -12.0, -6.0, -3.0, -1.0, dv_clamped):
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

    def test_04_anti_slipout_at_tilted_25deg_and_release_tab_stroke(self) -> None:
        """2枚目写真の斜め25°角度でも45N(4.6kgf)以上の抜け抵抗を維持し、かつ上部リリースタブの解除ストロークが底付きしないこと."""
        for name, part, u_off in (
            ("holder", self.holder, MAIN_U_OFFSET),
            ("fit_test", self.fit_test, FIT_TEST_U_OFFSET),
        ):
            with self.subTest(part=name):
                slot_x = LATCH_WIDTH / 2.0 + 0.90
                slot_u_start = LATCH_ANCHOR_U + 0.30
                slot_u_end = CRADLE_BACKPLATE_REAR_U - 0.30
                for sgn in (-1.0, 1.0):
                    slot_probe = Pos(
                        sgn * slot_x,
                        _u_to_y(0.5 * (slot_u_start + slot_u_end), u_off),
                        _v_to_z(-2.0),
                    ) * Box(1.00, slot_u_end - slot_u_start, 24.0)
                    self.assertAlmostEqual(_intersection_volume(part, slot_probe), 0.0, places=2)

                # 上部リリースタブ背面ポケット貫通確認
                pocket_u_min = LATCH_STEM_BACK_U + 0.25
                pocket_u_max = CRADLE_BACKPLATE_REAR_U - 0.25
                pocket_probe = Pos(
                    0.0,
                    _u_to_y(0.5 * (pocket_u_min + pocket_u_max), u_off),
                    _v_to_z(0.0),
                ) * Box(LATCH_WIDTH, pocket_u_max - pocket_u_min, 24.0)
                self.assertAlmostEqual(_intersection_volume(part, pocket_probe), 0.0, places=2)

        # Maxwell相反定理によるリリースタブ上端の必要ストローク <= ポケット上端隙間 - 0.80mm の検証
        L_h = LATCH_LEAF_SPAN_U
        v_leaf_mid = HOLDER_BOTTOM_V + LATCH_LEAF_THICKNESS / 2.0
        L_v = LATCH_TIP_V - v_leaf_mid
        H_top = LATCH_RELEASE_TOP_V - v_leaf_mid
        I_h = LATCH_WIDTH * (LATCH_LEAF_THICKNESS**3) / 12.0
        I_v = LATCH_WIDTH * (LATCH_STEM_THICKNESS**3) / 12.0
        r_I = I_v / I_h

        u_tip_unit = (L_v**2) * L_h + (L_v**3) / (3.0 * r_I)
        th_tip_unit = L_v * L_h + (L_v**2) / (2.0 * r_I)
        u_top_unit_from_tip = u_tip_unit + th_tip_unit * (H_top - L_v)
        u_top_unit_from_tab = (H_top**2) * L_h + (H_top**3) / (3.0 * r_I)

        delta_click = 9.09 - LATCH_TIP_U
        required_top_stroke = (delta_click + 0.15) * (u_top_unit_from_tab / u_top_unit_from_tip)
        available_top_pocket = CRADLE_BACKPLATE_REAR_U - (LATCH_STEM_BACK_U - LATCH_TOP_TAPER_U)
        self.assertGreaterEqual(
            available_top_pocket,
            required_top_stroke + 0.80,
            "Release tab top must have >=0.80mm extra pocket clearance to fully unlock without bottoming out",
        )

        # 直立(0°)および2枚目写真の斜め25°角度での引き抜き耐力と層間応力の検証
        # 段付きリアシート(PIPE_REAR_SEAT_U=+1.62)＋頂点越え爪(LATCH_TIP_U=+4.55)により、25°傾斜時でも >=3.10mm の強制たわみが発生する
        delta_tilted_25deg = 7.80 - LATCH_TIP_U
        alpha = math.radians(90.0 - LATCH_OVERHANG_DEG)
        mu = 0.22
        pulloff_ratio = (math.cos(alpha) + mu * math.sin(alpha)) / (math.sin(alpha) - mu * math.cos(alpha))

        for mat, E_mpa, f_click_min, f_click_max in (
            ("PETG", 2100.0, 26.0, 38.0),
            ("PLA Matte", 2350.0, 28.0, 42.0),
            ("PLA", 3000.0, 35.0, 50.0),
        ):
            comp = (L_v**3) / (3.0 * E_mpa * I_v) + (L_v**2) * L_h / (E_mpa * I_h)
            k = 1.0 / comp
            f_click = k * delta_click
            f_pull_0deg = f_click * pulloff_ratio
            f_pull_25deg = (k * delta_tilted_25deg) * pulloff_ratio
            sig_v_z = (f_click * L_v) * (LATCH_STEM_THICKNESS / 2.0) / I_v

            self.assertGreaterEqual(f_click, f_click_min)
            self.assertLessEqual(f_click, f_click_max)
            self.assertGreaterEqual(f_pull_0deg, 68.0, f"{mat} upright pull-off must exceed 68N (~7.0kgf)")
            self.assertGreaterEqual(
                f_pull_25deg,
                45.0,
                f"{mat} 25-deg tilted pull-off must exceed 45N (~4.6kgf) to prevent Photo-2 slip-out",
            )
            self.assertLess(sig_v_z, 17.0, f"{mat} Z-layer tensile stress must stay well below delamination")

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
                self.assertGreaterEqual(racket_backmost_u, PIPE_CENTER_U + PIPE_DIA / 2.0 + 10.0)

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
        self.assertLess(rear_half.bounding_box().max.Z, FIT_TEST_HEIGHT - 1.0)


if __name__ == "__main__":
    unittest.main()
