# Changelog

## 0.2.0 — 2026-07-25

### Added

- Blender 4.3以降／Blender 5.2向けのモジュール構成
- ウエスト側で縫い止まり、裾へ向けて開くナイフプリーツ
- 外布、ウエストベルト、重なり、裾芯、裏地
- ウエスト、裾、プリーツ、脇接ぎのステッチ
- ファスナーテープ、ファスナー歯、引き手、ホック・アイ
- 外布と裏地のUV
- 冬服濃紺、夏服濃紺、チャコール、ブラックの生地プリセット
- Blender内で生成・パックするBase Color、Roughness、Normal画像
- 512 / 1024 / 2048 pxのPBRテクスチャ設定
- 確認用スタジオ、カメラ、照明、PNGプレビュー
- 元モデルを変更しないGLB / FBX / OBJ書き出し
- BLENDコピー保存
- Windows用のパッケージ作成・Blenderスモークテストスクリプト
- GitHub Actionsによる構文、構成、マニフェスト、配布ZIP検証

### Changed

- v0.1の単一ファイル実装を複数モジュールへ分割
- プリーツ形状を単純な周期形状から縫製構造を考慮した折り面へ変更
- GLBで生地情報を保持しやすい画像ベースPBR材質へ変更
- FBXではテクスチャ埋め込み、OBJでは外部PNG書き出しに対応

### Verification

- `tests/blender_smoke_test.py` は生成、UV、PBR画像、GLB、FBX、OBJ、MTL、PNG、BLENDを検査します。
- `tools/build_and_test.ps1` はWindows上のBlender 5.2をバックグラウンド起動してスモークテストを実行します。
