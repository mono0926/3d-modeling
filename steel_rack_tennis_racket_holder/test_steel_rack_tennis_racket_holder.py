"""スチールラック用 テニスラケット掛け（2機種兼用）の自動幾何・干渉・運動学・STEP出力検証テスト."""

from collections import deque
import math
from pathlib import Path
import tempfile
import unittest
import numpy as np
from build123d import (
    Align,
    Box,
    BuildPart,
    Cylinder,
    Plane,
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
        HOOK_OUTER_HALF_SPAN,
        HOOK_WIDTH,
        MAIN_U_OFFSET,
        PIPE_CENTER_U,
        PIPE_CENTER_V,
        PIPE_DIA,
        SKIRT_HEIGHT,
        SKIRT_THICKNESS_MAX,
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
        HOOK_OUTER_HALF_SPAN,
        HOOK_WIDTH,
        MAIN_U_OFFSET,
        PIPE_CENTER_U,
        PIPE_CENTER_V,
        PIPE_DIA,
        SKIRT_HEIGHT,
        SKIRT_THICKNESS_MAX,
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
    """設計座標 u (手前 +u) を造形座標 Y へ変換する."""
    return u + u_offset


def _v_to_z(v: float) -> float:
    """設計座標 v (棚板下端 v=0) を造形座標 Z (Z=0 接地) へ変換する."""
    return v - HOLDER_BOTTOM_V


class TestSteelRackTennisRacketHolder(unittest.TestCase):
    """設計仕様書 Section 6 に基づく自動幾何・力学・運動学検証スイート."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.holder = build_holder()
        cls.fit_test = build_fit_test_piece()

    def test_01_solids_valid_and_build_plate_grounded(self) -> None:
        """本番モデルとテストピースが単一有効ソリッドで Z=0 接地・原点中心であること."""
        for name, part in (("holder", self.holder), ("fit_test", self.fit_test)):
            with self.subTest(part=name):
                self.assertTrue(part.is_valid, f"{name} must be valid")
                self.assertEqual(len(part.solids()), 1, f"{name} must be 1 single solid")
                self.assertGreater(part.volume, 1000.0)

                bb = part.bounding_box()
                self.assertAlmostEqual(bb.min.Z, 0.0, places=2)
                self.assertAlmostEqual((bb.min.X + bb.max.X) / 2.0, 0.0, places=2)
                self.assertAlmostEqual((bb.min.Y + bb.max.Y) / 2.0, 0.0, places=2)

        bb_main = self.holder.bounding_box()
        self.assertGreaterEqual(bb_main.size.X, 112.0)
        self.assertLessEqual(bb_main.size.X, 124.0)
        self.assertAlmostEqual(bb_main.size.Z, CRADLE_TOTAL_HEIGHT, places=2)
        # 0.20mm / 0.30mm 両対応 (0.60mm 整数倍)
        self.assertAlmostEqual(bb_main.size.Z % 0.60, 0.0, places=2)

        bb_fit = self.fit_test.bounding_box()
        self.assertAlmostEqual(bb_fit.size.X, FIT_TEST_WIDTH, places=2)
        self.assertAlmostEqual(bb_fit.size.Z, FIT_TEST_HEIGHT, places=2)

    def test_02_rack_non_interference_and_gap_tolerance(self) -> None:
        """棚板(隙間変動1.4〜3.5mm含む)と非干渉であり、φ7.2mmパイプに微小Cスナップすること."""
        span_x = 140.0
        # 隙間が 1.4mm (dv=-0.6mm) 〜 3.5mm (dv=+1.5mm) に変動しても棚板と完全非干渉であること
        for dv in (-0.60, 0.00, +1.50):
            skirt = Pos(
                0.0,
                _u_to_y(-SKIRT_THICKNESS_MAX / 2.0),
                _v_to_z(dv + SKIRT_HEIGHT / 2.0),
            ) * Box(span_x, SKIRT_THICKNESS_MAX, SKIRT_HEIGHT)
            shelf_top = Pos(
                0.0,
                _u_to_y(-25.0),
                _v_to_z(dv + SKIRT_HEIGHT - 0.55),
            ) * Box(span_x, 50.0, 1.10)
            shelf = skirt + shelf_top
            vol_shelf = _intersection_volume(self.holder, shelf)
            self.assertAlmostEqual(
                vol_shelf,
                0.0,
                places=3,
                msg=f"Holder must not collide with steel shelf at dv={dv}mm",
            )

        # 着座位置では φ7.40mm サドル内に φ7.20mm パイプがクリアランス収容され常時クリープ応力ゼロであること
        pipe_seated = (
            Pos(0.0, _u_to_y(PIPE_CENTER_U), _v_to_z(PIPE_CENTER_V))
            * Rot(0, 90, 0)
            * Cylinder(PIPE_DIA / 2.0, span_x)
        )
        self.assertAlmostEqual(
            _intersection_volume(self.holder, pipe_seated),
            0.0,
            places=3,
            msg="Seated 7.20mm pipe should rest inside 7.40mm saddle without constant creep interference",
        )

        # Cスナップ開口喉部 (上奥+135° と 下前-14° の中点) を φ7.20mm パイプが通過する際は
        # 開口弦長 約6.87mm (< 7.20mm) により確実に弾性スナップ干渉が発生すること
        a_top = math.radians(135.0)
        a_jaw = math.radians(-14.0)
        u_throat = PIPE_CENTER_U + 3.70 * 0.5 * (math.cos(a_top) + math.cos(a_jaw))
        v_throat = PIPE_CENTER_V + 3.70 * 0.5 * (math.sin(a_top) + math.sin(a_jaw))
        pipe_at_throat = (
            Pos(0.0, _u_to_y(u_throat), _v_to_z(v_throat))
            * Rot(0, 90, 0)
            * Cylinder(PIPE_DIA / 2.0, span_x)
        )
        vol_throat = _intersection_volume(self.holder, pipe_at_throat)
        self.assertGreater(vol_throat, 3.0, "C-snap throat must positively retain 7.20mm pipe")
        self.assertLess(vol_throat, 45.0, "C-snap throat interference must remain gentle")

        # φ6.50mm 以下の細い円柱なら喉部も無干渉で通過できること (過大な干渉でないことの証明)
        pipe_small_at_throat = (
            Pos(0.0, _u_to_y(u_throat), _v_to_z(v_throat))
            * Rot(0, 90, 0)
            * Cylinder(6.50 / 2.0, span_x)
        )
        self.assertAlmostEqual(_intersection_volume(self.holder, pipe_small_at_throat), 0.0, places=3)

        # 嵌合テストピースも同様に棚板非干渉・パイプ微小スナップであること
        skirt_fit = Pos(
            0.0,
            -SKIRT_THICKNESS_MAX / 2.0 + FIT_TEST_U_OFFSET,
            _v_to_z(SKIRT_HEIGHT / 2.0),
        ) * Box(40.0, SKIRT_THICKNESS_MAX, SKIRT_HEIGHT)
        self.assertAlmostEqual(_intersection_volume(self.fit_test, skirt_fit), 0.0, places=3)

    def test_03_three_point_self_lock_features_exist(self) -> None:
        """左右Jフックに①フチ裏ストッパー爪・②パイプ上奥座・③下前スナップ爪と十分な肉厚があること."""
        hook_mid_x = HOOK_OUTER_HALF_SPAN - HOOK_WIDTH / 2.0
        for sign in (-1.0, 1.0):
            cx = sign * hook_mid_x
            # ① 棚板フチ裏ストッパー爪 (u=-1.6, v=+5.5 付近にソリッドが存在)
            probe_stopper = Pos(cx, _u_to_y(-1.80), _v_to_z(5.50)) * Box(4.0, 0.8, 2.0)
            self.assertGreater(
                _intersection_volume(self.holder, probe_stopper),
                6.0,
                "Skirt-back stopper finger must be solid on both J-hooks",
            )
            # ② パイプ上奥 (+118 deg) サドル肉厚確認
            a_top = math.radians(118.0)
            u_top = PIPE_CENTER_U + 4.60 * math.cos(a_top)
            v_top = PIPE_CENTER_V + 4.60 * math.sin(a_top)
            probe_top = Pos(cx, _u_to_y(u_top), _v_to_z(v_top)) * Box(4.0, 1.0, 1.0)
            self.assertGreater(_intersection_volume(self.holder, probe_top), 3.5)

            # ③ パイプ真下のUアーム弾性部に十分な肉厚 (>=3.4mm) があること
            probe_u_arm = Pos(cx, _u_to_y(PIPE_CENTER_U), _v_to_z(PIPE_CENTER_V - 5.55)) * Box(
                10.0, 2.0, 3.2
            )
            self.assertGreater(_intersection_volume(self.holder, probe_u_arm), 55.0)

    def test_04_kinematic_insertion_path_from_front(self) -> None:
        """本番モデルの全幅3D投影断面(スナップ爪先端を除く)がラック手前下方から無干渉で進入できること."""
        hook_mid_x = HOOK_OUTER_HALF_SPAN - HOOK_WIDTH / 2.0
        bb = self.holder.bounding_box()

        # 全幅にわたる代表Xスライス (センター・Jフック中央・V字ウイング中腹〜上端) の和集合で 2D シルエットを構築
        us = np.linspace(bb.min.Y - MAIN_U_OFFSET, bb.max.Y - MAIN_U_OFFSET, 130)
        vs = np.linspace(bb.min.Z + HOLDER_BOTTOM_V, bb.max.Z + HOLDER_BOTTOM_V, 130)
        from OCP.BRepClass import BRepClass_FaceClassifier
        from OCP.gp import gp_Pnt
        from OCP.TopAbs import TopAbs_IN, TopAbs_ON

        classifier = BRepClass_FaceClassifier()
        pts_set: set[tuple[float, float]] = set()
        for x_slice in (0.0, hook_mid_x, 30.0, 40.0, 50.0):
            sec_faces = (Plane.YZ.offset(x_slice) & self.holder).faces()
            for u in us:
                y = _u_to_y(float(u))
                for v in vs:
                    # Cスナップ干渉領域 (パイプ下前 -55〜+10 deg かつ r < 4.15mm) のみ弾性変形分として除外
                    rp = math.hypot(u - PIPE_CENTER_U, v - PIPE_CENTER_V)
                    ang = math.degrees(math.atan2(v - PIPE_CENTER_V, u - PIPE_CENTER_U))
                    if rp < 4.15 and -55.0 <= ang <= 10.0:
                        continue
                    z = _v_to_z(float(v))
                    p3 = gp_Pnt(x_slice, y, z)
                    for sf in sec_faces:
                        classifier.Perform(sf.wrapped, p3, 1e-4)
                        if classifier.State() in (TopAbs_IN, TopAbs_ON):
                            pts_set.add((round(float(u), 3), round(float(v), 3)))
                            break

        pts = np.array(sorted(pts_set), dtype=float)
        self.assertGreater(len(pts), 2000)

        def collides_with_rack(p: np.ndarray) -> bool:
            u_arr, v_arr = p[:, 0], p[:, 1]
            hit_pipe = ((u_arr - PIPE_CENTER_U) ** 2 + (v_arr - PIPE_CENTER_V) ** 2) < (
                PIPE_DIA / 2.0 - 0.03
            ) ** 2
            hit_skirt = (
                (u_arr > -SKIRT_THICKNESS_MAX)
                & (u_arr < 0.0)
                & (v_arr > 0.0)
                & (v_arr < SKIRT_HEIGHT)
            )
            hit_ceil = (
                (u_arr > -80.0)
                & (u_arr < 0.0)
                & (v_arr >= SKIRT_HEIGHT - 1.1)
                & (v_arr <= SKIRT_HEIGHT + 2.0)
            )
            return bool(np.any(hit_pipe | hit_skirt | hit_ceil))

        self.assertFalse(collides_with_rack(pts), "Installed pose (minus snap lip) must be clear")

        ry = pts[:, 0] - PIPE_CENTER_U
        rz = pts[:, 1] - PIPE_CENTER_V
        visited = {(0, 0, 0)}
        queue = deque([(0, 0, 0)])
        escaped = False
        while queue:
            iu, iv, ith = queue.popleft()
            th = math.radians(ith * 4.0)
            c, s = math.cos(th), math.sin(th)
            cur = np.column_stack(
                [PIPE_CENTER_U + c * ry - s * rz + iu, PIPE_CENTER_V + s * ry + c * rz + iv]
            )
            if float(cur[:, 0].min()) > 2.5:
                escaped = True
                break
            for du in (-1, 0, 1):
                for dv in (-1, 0, 1):
                    for dth in (-1, 0, 1):
                        if du == 0 and dv == 0 and dth == 0:
                            continue
                        nxt = (iu + du, iv + dv, ith + dth)
                        if (
                            nxt not in visited
                            and -18 <= nxt[0] <= 24
                            and -34 <= nxt[1] <= 8
                            and -16 <= nxt[2] <= 16
                        ):
                            visited.add(nxt)
                            th2 = math.radians(nxt[2] * 4.0)
                            c2, s2 = math.cos(th2), math.sin(th2)
                            cand = np.column_stack(
                                [
                                    PIPE_CENTER_U + c2 * ry - s2 * rz + nxt[0],
                                    PIPE_CENTER_V + s2 * ry + c2 * rz + nxt[1],
                                ]
                            )
                            if not collides_with_rack(cand):
                                queue.append(nxt)

        self.assertTrue(escaped, "Must have a continuous collision-free SE(2) installation path")

    def test_05_both_rackets_fit_in_cradle_and_clear_shelf(self) -> None:
        """CLASH 26 V3.0 と HEAD EXTREME MP 2026 の双方がV字溝に安定着座し棚板とも干渉しないこと."""
        rackets = [
            # (name, w_bot, w_top, tri_h, throat_thick, max_shoulder_thick)
            ("Wilson CLASH 26 V3.0", 35.0, 121.0, 99.0, 24.0, 24.0),
            ("HEAD EXTREME MP 2026", 41.0, 130.0, 99.0, 21.5, 26.0),
        ]
        u_mid = CRADLE_INNER_BACK_U + CRADLE_GROOVE_DEPTH / 2.0

        for name, w_bot, w_top, tri_h, t_throat, t_max in rackets:
            with self.subTest(racket=name):
                half_slope = (w_top - w_bot) / (2.0 * tri_h)
                half_angle_deg = math.degrees(math.atan(half_slope))

                def make_racket_at(v_tri_bot: float):
                    # 左右のスロートシャフト + ブリッジ横棒 + 下グリップシャフト
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
                    # ブリッジ横棒 (v = v_tri_bot + tri_h .. + 12mm)
                    bridge = Pos(
                        0.0,
                        _u_to_y(u_mid),
                        _v_to_z(v_tri_bot + tri_h + 6.0),
                    ) * Box(w_top - 10.0, t_max, 12.0)
                    # 下部グリップシャフト
                    handle = Pos(
                        0.0,
                        _u_to_y(u_mid),
                        _v_to_z(v_tri_bot - 45.0),
                    ) * Box(29.0, t_throat, 90.0)
                    res = parts[0] + parts[1] + bridge + handle
                    return res

                # 上方 (v_tri_bot = +10mm) では干渉ゼロ (スッと入る入口開口)
                self.assertAlmostEqual(
                    _intersection_volume(self.holder, make_racket_at(10.0)),
                    0.0,
                    places=2,
                    msg=f"{name} must enter openly from above",
                )

                # 下へ降ろしていき、着座高さ v_seat を二分探索で特定
                v_hi, v_lo = 10.0, -45.0
                self.assertGreater(
                    _intersection_volume(self.holder, make_racket_at(v_lo)),
                    5.0,
                    f"{name} must be caught by V-cradle before passing through",
                )
                for _ in range(18):
                    v_m = 0.5 * (v_hi + v_lo)
                    if _intersection_volume(self.holder, make_racket_at(v_m)) > 0.05:
                        v_lo = v_m
                    else:
                        v_hi = v_m

                v_seat = v_hi
                # 三角穴上端ブリッジがクレードル上端より十分上 (>15mm余裕) にあること
                self.assertGreater(
                    v_seat + tri_h,
                    HOLDER_TOP_V + 15.0,
                    f"{name} throat bridge must stay well above cradle top",
                )
                # 最大フレーム厚部でも棚板前面 (u <= 0) とのクリアランスが 7.0mm 以上あること
                racket_backmost_u = u_mid - t_max / 2.0
                self.assertGreaterEqual(
                    racket_backmost_u,
                    7.0,
                    f"{name} max beam must clear shelf edge by >= 7.0mm",
                )
                # 前後とも溝内に確実に収まっていること (手前リップ内面 u=CRADLE_INNER_BACK_U+CRADLE_GROOVE_DEPTH)
                self.assertLessEqual(
                    u_mid + t_throat / 2.0,
                    CRADLE_INNER_BACK_U + CRADLE_GROOVE_DEPTH - 1.0,
                )

    def test_06_support_free_overhangs_and_step_export_roundtrip(self) -> None:
        """Z>0.1mm にサポート必須の急な下向き平面が存在せず、STEP出力が正常に行えること."""
        for name, part in (("holder", self.holder), ("fit_test", self.fit_test)):
            for face in part.faces():
                cz = face.center().Z
                if cz <= 0.15:
                    continue
                n = face.normal_at(face.center())
                # ビルドプレート向きのほぼ水平な天井面 (normal.Z < -0.75 => オーバーハング角 > 48.6°) が大きな面積を持たないこと
                if n.Z < -0.75:
                    self.assertLess(
                        face.area,
                        8.0,
                        f"{name} has unsupported downward overhang face at Z={cz:.2f}mm (area={face.area:.1f}mm^2, nZ={n.Z:.2f})",
                    )

        with tempfile.TemporaryDirectory() as tmpdir:
            main_path, fit_path = export_models(Path(tmpdir))
            self.assertTrue(main_path.exists())
            self.assertTrue(fit_path.exists())
            self.assertGreater(main_path.stat().st_size, 5000)
            self.assertGreater(fit_path.stat().st_size, 2000)

            imported_main = import_step(str(main_path))
            imported_fit = import_step(str(fit_path))
            self.assertEqual(len(imported_main.solids()), 1)
            self.assertEqual(len(imported_fit.solids()), 1)

    def test_07_racket_contact_and_outer_edges_filleted(self) -> None:
        """ラケット接触部およびクレードル外周の長尺エッジに保護Rフィレットが施されていること."""
        from build123d import GeomType

        # クレードル長手方向(約55〜62mm)に伸びる円筒/トーラス状のフィレット面が少なくとも12面以上存在すること
        curved_long_faces = [
            f
            for f in self.holder.faces()
            if f.geom_type in (GeomType.CYLINDER, GeomType.TORUS, GeomType.BSPLINE)
            and f.bounding_box().size.Z > 45.0
        ]
        self.assertGreaterEqual(
            len(curved_long_faces),
            12,
            "V-cradle inner/outer sloped rails must be filleted to protect racket paint and hands",
        )


if __name__ == "__main__":
    unittest.main()
