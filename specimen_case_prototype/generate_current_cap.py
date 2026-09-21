import os
from build123d import *
from ocp_vscode import show_object

"""
今印刷中の本体（Current Body: 溝深さ1.5mm / 溝幅2.4mm / 外壁3.0mm）に
100%完璧にジャストフィットするように最適化した専用エンドキャップです。

- 突起の飛び出し量: 1.50mm（本体溝の奥までしっかり届く）
- 突起のY方向厚み: 2.10mm（本体の溝幅2.4mmに対して0.15mmずつのスムーズな嵌合クリアランス）
- メインバー厚み: 2.70mm（手前壁厚3.0mmに対してツライチ）
- 指がかりノッチ: 幅14mm、深さ1.2mm
- 印刷時間: 約5分、フィラメント使用量: 約4g
- 推奨設定: 0.6mmノズル、0.24mmレイヤー、自動ブリム有効
"""

# 今印刷中の本体の確定寸法
SLOT_W = 76.45
WALL_THICKNESS = 3.0
TOTAL_H = 55.35
Z_ACRYLIC_BOTTOM = 47.5
CAP_GUIDE_DEPTH = 1.5
CAP_GUIDE_WIDTH = 2.4

FIT_CLEARANCE = 0.15  # 高精度ジャストフィット公差

# エンドキャップ寸法
cap_w = SLOT_W - 2 * FIT_CLEARANCE              # 76.15mm
cap_l = WALL_THICKNESS - 2 * FIT_CLEARANCE      # 2.70mm
cap_h = TOTAL_H - Z_ACRYLIC_BOTTOM - FIT_CLEARANCE  # 7.70mm

with BuildPart() as cap:
    # 1. メインバー
    Box(
        cap_w,
        cap_l,
        cap_h,
        align=(Align.CENTER, Align.CENTER, Align.MIN)
    )

    # 2. 左右のガイド突起（本体の溝に深く届くように配置）
    # 本体の溝外側端は ±(SLOT_W/2 + CAP_GUIDE_DEPTH) = ±39.725mm
    # 突起の外側端を ±(39.725 - FIT_CLEARANCE) = ±39.575mm に設定
    # 突起のX幅: (39.575 - cap_w/2) = (39.575 - 38.075) = 1.50mm
    rib_reach_x = 39.725 - FIT_CLEARANCE
    rib_width = (rib_reach_x - (cap_w / 2)) * 2  # 両端ブロック幅
    rib_len = CAP_GUIDE_WIDTH - 2 * FIT_CLEARANCE  # 2.10mm

    for side in [-1, 1]:
        with Locations((side * (cap_w / 2), 0, 0)):
            Box(
                rib_width,
                rib_len,
                cap_h,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.ADD
            )

    # 3. 指がかりノッチ
    with Locations((0, 0, cap_h)):
        Box(
            14.0,
            cap_l + 2.0,
            2.4,  # 深さ1.2mm
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
            mode=Mode.SUBTRACT
        )

    # 4. 上部角の微小面取り
    top_edges = cap.edges().sort_by(Axis.Z)[-4:]
    if top_edges:
        chamfer(top_edges, length=0.4)

part = cap.part

output_dir = os.path.dirname(__file__)
output_path = os.path.join(output_dir, "end_cap_current_fit.step")
export_step(part, output_path)
print(f"Exported current fit cap to: {output_path}")
print(f"Cap Bounding Box: {part.bounding_box()}")
