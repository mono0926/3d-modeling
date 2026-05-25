"""
設計要件:
    - エアダスター（Ciniffo製電動ブロワー）とPTFEチューブ（外径4mm、内径2.5mm）を中継するノズル。
    - エアダスター側の外径は、サイズ検証テストの結果に基づき 29.55mm に決定。
    - 差し込み深さは実測の 4.4mm。これ以上深く刺さらないように、外径 34.0mm のフランジ（出っ張り）を配置。
    - フランジ部分は、底面（Z=0）を下にして印刷する際にサポート不要（45度傾斜）で綺麗に出力できるよう、45度のなだらかな広がりテーパーとして設計。
    - PTFEチューブ側は「深さ15mm」の「テーパー付き圧入ソケット（入口φ4.25mm → 奥φ3.95mm、テスト穴3の結果）」とし、クサビ効果で固定。
    - 内部流路は25.35mmから2.5mmへと滑らかにすぼまるテーパーロフトとし、風圧ロスと内部オーバーハングを低減（サポート不要）。

推奨フィラメント:
    - PETG (耐熱性と靭性、PTFEチューブホールド力向上のため強く推奨)

推奨スライサー設定:
    - レイヤー高さ (Layer height): 0.2mm
    - 壁ループ数 (Wall loops): 4 (エア漏れ防止および強度の確保)
    - インフィル密度 (Infill density): 30% 以上 (強度重視、ジャイロイド推奨)
    - サポート (Support): 不要 (内部・外部ともに45度以下の傾斜で設計されているため、サポートなしで印刷可能)
    - シーム位置 (Seam position): 整列 (Aligned) または 背面 (Back)

印刷統計（予想）:
    - air_duster_nozzle: 印刷時間 約20〜25分、フィラメント使用量 約7g

履歴とプロンプト経緯:
    - 詳細は同ディレクトリ the history.md を参照。
"""

import cadquery as cq
import os

# ==================== パラメータ定義 ====================
# エアダスター側（ソケット部）
SOCKET_DIAMETER = 29.55   # テスト結果に基づき決定した差し込み外径
INSERT_DEPTH = 4.4       # 差し込み口の深さ (実測)
SOCKET_WALL = 2.1         # ソケット部の肉厚 (内径は SOCKET_DIAMETER - 2*SOCKET_WALL)

# フランジ部（これ以上深く刺さらないようにする出っ張り）
FLANGE_OD = SOCKET_DIAMETER + 2.0  # フランジの外径（片側1.0mmの段差で十分なストッパーとして機能）
# 3Dプリント時にサポートなしで印刷できるよう、広がり角度を45度に設計。
# 半径の広がり分（1.0mm）と同じ高さを確保することで、傾斜角45度を実現
FLANGE_HEIGHT = (FLANGE_OD - SOCKET_DIAMETER) / 2.0  # 1.0mm

# 中間部（絞り部）
TRANSITION_HEIGHT = 12.0  # フランジ上端からPTFEソケットへ絞り込む高さ

# PTFEチューブ側（圧入ソケット部）
PTFE_INSERT_DEPTH = 15.0  # PTFEチューブを差し込む深さ
PTFE_OD = 8.0             # PTFEソケットの外径
PTFE_HOLE_IN = 4.25       # チューブ差込口の入口直径 (テスト結果: 穴3)
PTFE_HOLE_OUT = 3.95      # チューブ差込口の奥の直径 (テスト結果: 穴3)

# 流路・共通
AIR_HOLE = 2.5            # 中心の空気穴の直径 (PTFEチューブの内径に合わせる)
TOTAL_HEIGHT = INSERT_DEPTH + FLANGE_HEIGHT + TRANSITION_HEIGHT + PTFE_INSERT_DEPTH

# Z座標の区切り（相対移動の設計用）
z0 = 0
z1 = INSERT_DEPTH
z2 = INSERT_DEPTH + FLANGE_HEIGHT
z3 = INSERT_DEPTH + FLANGE_HEIGHT + TRANSITION_HEIGHT
z4 = TOTAL_HEIGHT

# ==================== モデリング ====================
# 1. 外側ソリッドの作成 (ロフト接続)
# エアダスター側(Z=0)からフランジ(Z=z2)で広がり、そこからPTFE側へ向けて滑らかに絞り込む
outer_solid = (cq.Workplane("XY")
               .circle(SOCKET_DIAMETER / 2.0)
               .workplane(offset=z1)
               .circle(SOCKET_DIAMETER / 2.0)
               .workplane(offset=FLANGE_HEIGHT)
               .circle(FLANGE_OD / 2.0)
               .workplane(offset=TRANSITION_HEIGHT)
               .circle(PTFE_OD / 2.0)
               .workplane(offset=PTFE_INSERT_DEPTH)
               .circle(PTFE_OD / 2.0)
               .loft(ruled=True)
              )

# 2. 内側空気流路（中空部）の作成
# 差し込み奥(Z=z1)から中間接続部(Z=z3)にかけて、ロート状に空気を絞る
r_in_duster = (SOCKET_DIAMETER - 2.0 * SOCKET_WALL) / 2.0
inner_air = (cq.Workplane("XY")
             .circle(r_in_duster)
             .workplane(offset=z1)
             .circle(r_in_duster)
             .workplane(offset=FLANGE_HEIGHT + TRANSITION_HEIGHT)
             .circle(AIR_HOLE / 2.0)
             .workplane(offset=PTFE_INSERT_DEPTH)
             .circle(AIR_HOLE / 2.0)
             .loft(ruled=True)
            )

# 3. PTFEチューブ差し込み用穴（テーパーポケット）の作成
# Z=z3 から Z=z4 までテーパー穴を開ける
ptfe_hole = (cq.Workplane("XY")
             .workplane(offset=z3)
             .circle(PTFE_HOLE_OUT / 2.0)
             .workplane(offset=PTFE_INSERT_DEPTH)
             .circle(PTFE_HOLE_IN / 2.0)
             .loft(ruled=True)
            )

# 4. 本体から空気流路とPTFE穴を引く
result = outer_solid.cut(inner_air).cut(ptfe_hole)

# 5. エッジの面取り (差し込みやすさの向上)
# エアダスター差込口の先端（Z=0）外側を差し込みやすく0.5mm面取り
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
