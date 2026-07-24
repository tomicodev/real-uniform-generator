# Blender 5.2へのインストール

## 推奨: GitHub Actionsの配布ZIP

1. リポジトリの `Actions` を開きます。
2. 最新の `Validate and Package Blender Add-on` を選択します。
3. 画面下部のArtifactsから `real_uniform_generator-v0.2.0` をダウンロードします。
4. Blender 5.2で `Edit > Preferences > Add-ons` を開きます。
5. 右上メニューから `Install from Disk` を選択します。
6. ダウンロードしたZIPを指定します。
7. 3Dビューで `N` キーを押し、`Uniform` タブを開きます。

## リポジトリZIPから導入する場合

1. `Code > Download ZIP` でリポジトリをダウンロードして展開します。
2. 展開した中の `real_uniform_generator` フォルダだけをZIP圧縮します。
3. ZIPを開いた直下に以下があることを確認します。
   - `__init__.py`
   - `blender_manifest.toml`
   - `geometry.py`
   - `materials.py`
4. Blenderの `Install from Disk` からZIPを指定します。

## 初回確認

1. `Uniform` タブで既定値のまま `制服スカートを生成` を押します。
2. Outlinerに `RUG_UniformSkirt` コレクションが生成されることを確認します。
3. `確認用スタジオを作成` を押します。
4. ビューポートをマテリアルプレビューまたはレンダー表示にします。
5. 必要に応じて `プレビュー画像を書き出す` を押します。

## 保存・書き出し

- `BLENDコピーを保存`: 現在開いている作業ファイルを変更せず、別名の `.blend` コピーを保存します。
- GLB: マテリアルを含めた受け渡し向けです。
- FBX: DCCやゲームエンジン向けです。
- OBJ: 汎用メッシュ形式です。Blender固有のノード材質は完全には再現されません。

書き出し処理は生成物を一時複製してからモディファイアを適用するため、Blender内の元モデルは変更しません。

## アンインストール

1. Blenderで `Edit > Preferences > Add-ons` を開きます。
2. `Real Uniform Generator` を検索します。
3. メニューから削除します。

## エラーが出た場合

Blenderの `Window > Toggle System Console` またはScripting画面のConsoleで、`Python: Traceback` から末尾までをコピーしてください。エラー行だけでなくTraceback全文が必要です。
