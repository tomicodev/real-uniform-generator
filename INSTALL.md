# Blender 5.2へのインストールと確認

## 推奨: GitHub Actionsの配布ZIP

1. リポジトリの `Actions` を開きます。
2. 最新の `Validate and Package Blender Add-on` を選択します。
3. 画面下部のArtifactsから `real_uniform_generator-v0.2.0` をダウンロードします。
4. Blender 5.2のPreferencesから `Install from Disk` を選択します。
5. ダウンロードしたZIPを指定します。
6. 3Dビューで `N` キーを押し、`Uniform` タブを開きます。

## WindowsでZIP作成と実動確認を一括実行

リポジトリ直下でPowerShellを開き、次を実行します。

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\build_and_test.ps1
```

既定のBlenderパスは以下です。

```text
C:\Program Files\Blender Foundation\Blender 5.2\blender.exe
```

異なる場所にインストールしている場合は次のように指定します。

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\build_and_test.ps1 `
  -BlenderExe "D:\Apps\Blender\blender.exe"
```

このスクリプトは次の順序で検証します。

1. BlenderのExtension BuildでZIPを作成
2. BlenderのExtension ValidateでZIPを検証
3. ソースツリーから生成・書き出しテスト
4. 一時的なBlenderユーザー環境とローカルExtension Repositoryを作成
5. 配布ZIPを実際にインストールして有効化
6. インストール済みアドオンから生成、プレビュー、全形式書き出しを実行
7. 一時環境を削除

成功すると、コンソールに以下が表示されます。

```text
RUG_SMOKE_TEST_OK
RUG_INSTALLED_EXTENSION_TEST_OK
```

次のZIPが作成されます。

```text
dist\real_uniform_generator-v0.2.0.zip
```

スモークテストは以下を確認します。

- 外布、ウエストベルト、裏地、縫製、ファスナー、ホックの生成
- 外布の頂点数、UV、プリーツのシャープエッジ
- Base Color、Roughness、Normal画像の生成とパック
- プレビューPNG
- GLB、FBX、OBJ、MTL、外部PNG、BLENDの作成

## リポジトリZIPから手動導入する場合

1. `Code > Download ZIP` でリポジトリをダウンロードして展開します。
2. `real_uniform_generator` フォルダを開き、その**中身**をZIP圧縮します。
3. ZIPを開いた直下に以下があることを確認します。
   - `__init__.py`
   - `blender_manifest.toml`
   - `LICENSE.txt`
   - `geometry.py`
   - `finishing.py`
   - `materials.py`
   - `textures.py`
4. Blenderの `Install from Disk` からZIPを指定します。

## 初回確認

1. `Uniform` タブで既定値のまま `制服スカートを生成` を押します。
2. Outlinerに `RUG_UniformSkirt` コレクションが生成されることを確認します。
3. `確認用スタジオを作成` を押します。
4. ビューポートをマテリアルプレビューまたはレンダー表示にします。
5. 必要に応じて `プレビュー画像を書き出す` を押します。

PBRテクスチャはスカート生成時にBlender内で作成され、画像としてBlendファイルへパックされます。1024 pxが標準です。高精細な確認では2048 px、動作確認を優先する場合は512 pxを選択してください。

## 保存・書き出し

- `BLENDコピーを保存`: 現在開いている作業ファイルを変更せず、別名の `.blend` コピーを保存します。
- GLB: Base Color、Roughness、Normal画像を単一ファイルへ内包します。
- FBX: 画像を外部保存したうえでテクスチャ埋め込みを試行します。
- OBJ: `.obj`、`.mtl` と、`<ファイル名>_textures` フォルダ内のPNGを出力します。

書き出し処理は生成物を一時複製してからモディファイアを適用するため、Blender内の元モデルは変更しません。

## アンインストール

1. BlenderのPreferencesでExtensionsまたはAdd-onsを開きます。
2. `Real Uniform Generator` を検索します。
3. メニューから削除します。

## エラーが出た場合

Blenderの `Window > Toggle System Console` またはScripting画面のConsoleで、`Python: Traceback` から末尾までをコピーしてください。エラー行だけでなくTraceback全文が必要です。
