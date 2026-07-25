# Blender 5.2へのインストール

## 配布ZIPを使う

1. `real_uniform_generator-v0.6.0.zip` を用意します。
2. Blender 5.2を開きます。
3. `編集 > プリファレンス > エクステンション` または `アドオン` を開きます。
4. 右上メニューから `ディスクからインストール` を選びます。
5. ZIPを解凍せず選択します。
6. 3Dビューで `N` キーを押し、右側の **制服** タブを開きます。

## 旧版から更新する

1. Blenderを閉じます。
2. 旧 `Real Uniform Generator` をアンインストールします。
3. Blenderを再起動します。
4. v0.6.0 ZIPをインストールします。

v0.5以前はBase64 runtime payload方式でした。旧Pythonモジュールがメモリーへ残らないよう、アンインストール後にBlenderを再起動してください。

## 最初の確認

1. 空の新規シーンを開きます。
2. 既定値のまま `制服スカートを生成` を押します。
3. Outlinerの `RUG_Generated` コレクション内に `RUG_UniformSkirt` と各縫製部品が作られることを確認します。
4. 外側に独立した裾リングや巨大なファスナー金具がないことを確認します。
5. `確認用スタジオを作成` を押し、`正面プレビューを書き出す` でレンダーを確認します。
6. GLBまたはBLENDコピーを書き出し、元の作業ファイルが上書きされていないことを確認します。

## 外部PBRを使う

1. BaseColor / Roughness / NormalGLまたはNormalDX / Height / AOを一つのフォルダへ入れます。
2. `外部PBRを使用` をオンにします。
3. PBRフォルダを指定します。
4. 必要に応じて法線形式をAUTO / OpenGL / DirectXから選びます。
5. `PBR画像を確認` を押します。
6. `制服スカートを生成` を押します。

認識しやすいファイル名:

```text
uniform_wool_basecolor.png
uniform_wool_roughness.png
uniform_wool_normal_opengl.png
uniform_wool_normal_directx.png
uniform_wool_height.png
uniform_wool_ao.png
```
