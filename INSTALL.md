# Blender 5.2へのインストール

## 配布ZIPを使う

1. `real_uniform_generator-v0.5.0.zip` を用意します。
2. Blender 5.2を開きます。
3. `編集 > プリファレンス > エクステンション` または `アドオン` を開きます。
4. 右上メニューから `ディスクからインストール` を選びます。
5. ZIPを解凍せず選択します。
6. 3Dビューで `N` キーを押し、右側の **制服** タブを開きます。

## 旧版から更新する

1. Blenderを閉じます。
2. 旧 `Real Uniform Generator` をアンインストールします。
3. Blenderを再起動します。
4. v0.5.0 ZIPをインストールします。

同名モジュールを読み込んだまま上書きすると、旧Pythonコードがメモリーへ残る場合があります。再起動を挟んでください。

## 最初の確認

1. 既定値のまま `制服スカートを生成` を押します。
2. Outlinerに `RUG_UniformSkirt` が作られることを確認します。
3. 外側に独立した裾リングが存在しないことを確認します。
4. `内部構造を表示` をオンにして再生成すると、縫い代、テープ、コイル、金具を確認できます。
5. `確認用スタジオを作成` を押し、マテリアルプレビューまたはレンダー表示にします。

## 外部PBRを使う

1. BaseColor / Roughness / NormalGL / Heightなどの画像を一つのフォルダへ入れます。
2. `生地ソース` を `外部PBRフォルダ` にします。
3. フォルダを指定します。
4. `PBRフォルダを検査` を押します。
5. 認識結果をSystem Consoleで確認し、`制服スカートを生成` を押します。

認識しやすいファイル名:

```text
NavyUniform_BaseColor.png
NavyUniform_Roughness.png
NavyUniform_NormalGL.png
NavyUniform_Height.png
NavyUniform_AO.png
```
