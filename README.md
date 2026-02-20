## AI活用の3Dモデリング

- [CadQuery](https://github.com/CadQuery/cadquery)を利用前提

### 環境構築

特にApple Silicon Macでpipを使ったCadQueryインストールは失敗しがちなので、condaを使うことを推奨。

Miniforgeインストール

```sh
brew install miniforge
```

初期設定

```sh
conda init zsh
source ~/.zshrc # 再起動でもOK
```

Python 3.11で専用環境を作成

```sh
conda create -n cq-conda-env python=3.11 -c conda-forge
```

CadQueryをインストール

```sh
# 環境に入る
conda activate cq-conda-env
# conda-forge経由でCadQueryをインストール
conda install -c conda-forge cadquery
```

#### 3Dプレビュー

本プロジェクトでは、CadQueryのモデルをエディタ上でリアルタイムプレビューするために **OCP CAD Viewer** を使用します。

##### エディタ拡張機能のインストール

**■ 標準のVS Codeを使用している場合**
拡張機能マーケットプレイスから `OCP CAD Viewer` (Bernhard Walter作) を検索してインストールしてください。

**■ Cursor / VSCodiumを使用している場合**
この拡張機能はOpen VSXには登録されていないため、[OCP CAD Viewer Releases](https://github.com/bernhard-42/vscode-ocp-cad-viewer/releases) から最新の `.vsix` ファイルをダウンロード・インストールします。

無事にプレビュー環境が構築できてよかったです！✨ コードを書きながらリアルタイムで形状が確認できると、開発体験が段違いに良くなりますよね。

今後の環境構築や、他のマシンでセットアップする際にも迷わないよう、READMEにそのままコピペして使えるMarkdown形式のテキストを作成しました。先ほど話題に出たCursor等向けのVSIXインストールの手順や、`cq-conda-env` 環境へのパッケージ導入も網羅しています。

以下を `README.md` に追記して活用してください！

---

````markdown
## 開発環境のセットアップ (3Dプレビュー)

本プロジェクトでは、CadQueryのモデルをエディタ上でリアルタイムプレビューするために **OCP CAD Viewer** を使用します。

### 1. エディタ拡張機能のインストール

**■ 標準のVS Codeを使用している場合**
拡張機能マーケットプレイスから `OCP CAD Viewer` (Bernhard Walter作) を検索してインストールしてください。

**■ Cursor / VSCodiumを使用している場合**
この拡張機能はOpen VSXには登録されていないため、GitHubの公式リリースページからVSIXファイルをダウンロードして手動インストールする必要があります。

1. [OCP CAD Viewer Releases](https://github.com/bernhard-42/vscode-ocp-cad-viewer/releases) から最新の `.vsix` ファイルをダウンロードします。
2. ターミナルから以下のコマンドでインストールします。

```bash
# Cursorの場合
cursor --install-extension ocp-cad-viewer-*.vsix

# VSCodiumの場合
codium --install-extension ocp-cad-viewer-*.vsix
```
````

##### 2. Pythonパッケージのインストール

プレビュー機能（エディタとの通信）を有効にするため、CadQueryを実行しているconda環境に専用パッケージをインストールします。

```bash
conda activate cq-conda-env
pip install ocp-vscode

```

_(※初回スクリプト実行時に右下に表示される `OCP VS Code not found...` のダイアログで「yes」を選択することでも自動インストール可能です。)_

##### 3. プレビューの実行手順

1. コマンドパレット（`Cmd + Shift + P`）を開き、`OCP CAD Viewer: Start Server` を実行します（右側にビューワーペインが開きます）。
2. プレビューしたいPythonスクリプト（例: `cube.py`）を実行します。
3. ビューワーペインに3Dモデルがレンダリングされます。

**コード内の記述要件:**
スクリプト内でモデルを表示するには、以下のインポートと関数呼び出しが必要です。

```python
import cadquery as cq
from ocp_vscode import show_object

# ... (モデルの定義) ...

# プレビューの実行
show_object(stand)

```

### 使い方

環境に入る(プレーンな環境では毎回初めに実行必要)。
(`.envrc`が設定済みなので、direnv導入済みなら自動実行される。)

```sh
conda activate cq-conda-env
```

以下など任意のスクリプトを実行すると、stepファイルが出力される。

```
python cap.py
```

VS Code系エディタの場合、Python: Select Interpreterから、`Python 3.11.x ('cq-conda-env': conda)`を選択して実行ボタン押すだけで良い。

### stapファイルの扱い

stepファイルは、Bambu Studioなどでそのまま開けるが、Autodesk Fusionを経由したい場合は以下。

1. Autodesk Fusionで開く
2. 3Dプリントのエクスポートで3MFファイルとして出力
3. Bambu Studioで開く
