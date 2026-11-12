"""スチールラック用テニスボールスタンド (steel_rack_tennis_ball_holder) 印刷中断リカバリー用パーツ生成スクリプト.

0.6mmノズル・0.30mmレイヤー高さにおいて、789/820層目で印刷中断・ベッド剥がれが発生した際に、
未印刷の残り部分（最上段C字リング皿の頂部）のみをZ=0接地で切り出してSTEP出力します。
"""

from pathlib import Path
from build123d import *

try:
    from ocp_vscode import show_object
except ImportError:  # pragma: no cover

    def show_object(*_args, **_kwargs) -> None:
        pass

from steel_rack_tennis_ball_holder import build_holder


def generate_recovery_parts() -> tuple[Path, Path]:
    target_dir = Path(__file__).resolve().parent
    holder = build_holder()

    # 1. 第788層完了直後（Z = 236.40mm）で水平切断した残余パーツ（推奨: 789層目開始前）
    # 本体側の中断面をカッターやヤスリで平らに均して788層天面に合わせた場合に最適
    cut_z_788 = 788 * 0.30  # 236.40mm
    top_788 = (Pos(0, 0, -cut_z_788) * holder.split(Plane.XY.offset(cut_z_788), keep=Keep.TOP)).solids()[0]
    out_788 = target_dir / "steel_rack_tennis_ball_holder_recovery_from_layer789.step"
    export_step(top_788, str(out_788))

    # 2. 第789層完了直後（Z = 236.70mm）で水平切断した残余パーツ
    # もし789層目が完全に塗り終わっていた場合に最適
    cut_z_789 = 789 * 0.30  # 236.70mm
    top_789 = (Pos(0, 0, -cut_z_789) * holder.split(Plane.XY.offset(cut_z_789), keep=Keep.TOP)).solids()[0]
    out_789 = target_dir / "steel_rack_tennis_ball_holder_recovery_from_layer790.step"
    export_step(top_789, str(out_789))

    return out_788, out_789


if __name__ == "__main__":
    p788, p789 = generate_recovery_parts()
    print(f"Generated recovery STEP (from Layer 789 / Z=236.40mm): {p788}")
    print(f"Generated recovery STEP (from Layer 790 / Z=236.70mm): {p789}")
