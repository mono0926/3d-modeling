"""
設計要件:
    - エアダスター（Ciniffo製電動ブロワー、外径29.3mm実寸）とPTFEチューブ（外径4mm、内径2.5mm）を中継するノズル。
    - エアダスター側の仮の外径は、テスト用の29.2mm（テスト結果により調整可能）に設定。
    - 差し込み深さは実測の4.4mmとし、風圧で抜けないよう接触面積を最大化。
    - PTFEチューブ側は「深さ15mm」の「テーパー付き圧入ソケット（入口φ4.15mm → 奥φ3.85mm）」とし、クサビ効果で固定。
    - 内部流路は25.0mmから2.5mmへと滑らかにすぼまるテーパーロフトとし、風圧ロスと内部オーバーハングを低減（サポート不要）。

推奨フィラメント:
    - PETG (耐熱性と靭性、PTFEチューブホールド力向上のため強く推奨)

推奨スライサー設定:
    - レイヤー高さ (Layer height): 0.2mm
    - 壁ループ数 (Wall loops): 4 (エア漏れ防止および強度の確保)
    - インフィル密度 (Infill density): 30% 以上 (強度重視、ジャイロイド推奨)
    - サポート (Support): 不要 (内部・外部ともに45度未満の傾斜で設計されているため、サポートなしで印刷可能)
    - シーム位置 (Seam position): 整列 (Aligned) または 背面 (Back)

印刷統計（予想）:
    - air_duster_nozzle: 印刷時間 約15〜20分、フィラメント使用量 約6g

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

import cadquery as cq
import os

# ==================== パラメータ定義 ====================
# エアダスター側（ソケット部）
SOCKET_DIAMETER = 29.2    # 【要微調整】テスト後に確定する差し込み部外径の仮値 (実寸29.3)
INSERT_DEPTH = 4.4       # 差し込み口の深さ (実測)
SOCKET_WALL = 2.1         # ソケット部の肉厚 (内径は SOCKET_DIAMETER - 2*SOCKET_WALL)

# 中間部（絞り部）
TRANSITION_HEIGHT = 12.0  # 29.2mmから8.0mmへ絞り込むテーパー部の高さ

# PTFEチューブ側（圧入ソケット部）
PTFE_INSERT_DEPTH = 15.0  # PTFEチューブを差し込む深さ
PTFE_OD = 8.0             # PTFEソケットの外径
PTFE_HOLE_IN = 4.15       # チューブ差込口の入口直径 (少し入れやすく)
PTFE_HOLE_OUT = 3.85      # チューブ差込口の奥の直径 (クサビ効果でホールド)

# 流路・共通
AIR_HOLE = 2.5            # 中心の空気穴の直径 (PTFEチューブの内径に合わせる)
TOTAL_HEIGHT = INSERT_DEPTH + TRANSITION_HEIGHT + PTFE_INSERT_DEPTH

# ==================== モデリング ====================
# 1. 外側ソリッドの作成 (ロフト接続)
# エアダスター側からPTFE側に向けて滑らかに絞り込む
outer_solid = (cq.Workplane("XY")
               .circle(SOCKET_DIAMETER / 2.0)
               .workplane(offset=INSERT_DEPTH)
               .circle(SOCKET_DIAMETER / 2.0)
               .workplane(offset=TRANSITION_HEIGHT)
               .circle(PTFE_OD / 2.0)
               .workplane(offset=PTFE_INSERT_DEPTH)
               .circle(PTFE_OD / 2.0)
               .loft(ruled=True)
              )

# 2. 内側空気流路（中空部）の作成
# ロート状に空気を絞り、PTFE手前まで導く
r_in_duster = (SOCKET_DIAMETER - 2.0 * SOCKET_WALL) / 2.0
inner_air = (cq.Workplane("XY")
             .circle(r_in_duster)
             .workplane(offset=INSERT_DEPTH)
             .circle(r_in_duster)
             .workplane(offset=TRANSITION_HEIGHT)
             .circle(AIR_HOLE / 2.0)
             .workplane(offset=PTFE_INSERT_DEPTH)
             .circle(AIR_HOLE / 2.0)
             .loft(ruled=True)
            )

# 3. PTFEチューブ差し込み用穴（テーパーポケット）の作成
# 上端から深さ PTFE_INSERT_DEPTH まで掘る
z_ptfe_bottom = INSERT_DEPTH + TRANSITION_HEIGHT
ptfe_hole = (cq.Workplane("XY")
             .workplane(offset=z_ptfe_bottom)
             .circle(PTFE_HOLE_OUT / 2.0)
             .workplane(offset=PTFE_INSERT_DEPTH)
             .circle(PTFE_HOLE_IN / 2.0)
             .loft(ruled=True)
            )

# 4. 本体から空気流路とPTFE穴を引く
result = outer_solid.cut(inner_air).cut(ptfe_hole)

# 5. エッジの面取り・フィレット処理 (使いやすさと流体力学的最適化)
# エアダスター差込口の先端（Z=0）外側を差し込みやすく面取り
result = result.edges("<Z").chamfer(0.5)

# OCP CAD Viewerでプレビュー
try:
    from ocp_vscode import show_object
    show_object(result)
except ImportError:
    pass

# STEPファイルとして出力
output_dir = os.path.dirname(__file__)
output_path = os.path.join(output_dir, "air_duster_nozzle.step")
cq.exporters.export(result, output_path)
print(f"Exported STEP to {output_path}")
