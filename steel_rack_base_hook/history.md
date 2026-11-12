# 履歴とプロンプト経緯 (`steel_rack_base_hook`)

## 2026-11-12 — スチールラック共通ベースフックモジュールとして切り出し（Issue `#38` / PR `#39`）

### 経緯・目的
- `steel_rack_tennis_racket_holder`（v1〜v4 実機装着テスト）で確立したマットブラックスチールラック（18.1mm薄鉄板フチ ＋ 前方2.0mmクリアランス・下2.0mmの φ7.2mm 水平丸パイプ）向けの高保持ワンタッチロック機構を、`steel_rack_tennis_ball_holder` および今後の同ラック用アクセサリー群と安全に共有するため、独立した共通モジュール `steel_rack_base_hook` として抽出した。

### 主な仕様
- **固定保護パラメーター（Single Source of Truth）**:
  - 段付き丸パイプ専用ポケット（`PIPE_REAR_SEAT_U = +1.62mm`, `J_FRONT_INNER_U = +9.32mm`, 底角 `R0.80mm` フィレット）
  - 上部薄鉄板裏ストッパー（`STOPPER_FRONT_U = -1.06mm`）
  - 中央 Z=0 連続繊維ロングリーフ（厚 `1.80mm`, 長 `15.05mm`, 根元 `1.20mm` ガセット）＋ 頂点越え35°ディープフック（`LATCH_TIP_U = +4.55mm`, `LATCH_TIP_V = -1.42mm`）＋ 指掛けリリースタブ（`v = +9.60mm`）
- **可変インターフェース（`build_steel_rack_mounting_core`）**:
  - `outer_half_span`: アタッチメントの全幅に応じた左右Jフック外端位置
  - `spine_thickness` / `spine_height`: 前面構造体（クレードル背板や縦タワー等）と直結するフロントスパインの肉厚・高さ
  - `align_bottom_to_z0`: 内部設計座標（`v >= -15.00mm`）とビルドプレート座標（`Z >= 0.00mm`）の両対応
- **インポート環境**:
  - ルート `pyproject.toml` による `cq-conda-env` への editable 登録および `pyrightconfig.json` 設定により、`sys.path` ワークアラウンドなしで全ディレクトリから直接インポート可能とした。
