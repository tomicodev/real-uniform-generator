# Changelog

## 0.6.0 — 2026-07-25

### Rebuilt

- Base64 runtime payloadを廃止し、通常の複数Pythonモジュール構成へ移行
- Blender 5.2の登録・解除・再登録を検証
- 一枚の連続布としてプリーツと裾折り返しを生成
- 急角度プリーツでSolidifyが破綻しない法線方向厚みへ変更
- 表ベルト、上端折り、内側見返し、接着芯を持つベルト構造へ変更
- 左脇コンシールファスナーを内側縫製構造として再実装

### Added

- 正面・側面・背面・内側・ファスナーの検証ビュー
- OpenGL / DirectX Normalの自動認識とDirectX Y反転
- Eevee / Cycles検証
- GLB / BLEND出力スモークテスト
- 通常モジュール構成を検証するGitHub Actions

### Verified

- 20本プリーツ、ウエスト68cm、ヒップ92cm、丈48cm
- 外布は1連結メッシュ
- 表地厚1.25mm、裾折り返し4cm、実寸UV
- 独立した裾リング、トーラス、巨大な外部ファスナー金具なし

## 0.5.0 — 2026-07-25

### Rebuilt

- 放射状の波形スカートを廃止し、連続したナイフプリーツ型紙エンジンへ移行
- ウエスト・ヒップ周長から楕円断面を算出
- 縫い止まり、解放区間、自由部分を分離
- 外部裾リングを廃止し、内側裾見返しへ変更
- ウエストベルトを中空・開き付き構造へ変更

### Added

- 実寸入力
- 左脇／右脇／後ろ中心の開き位置
- 縫い代、左右テープ、ナイロンコイル、小型スライダー、上下止め、ホック
- 内側構造の表示切替
- まつり縫い／ミシン縫い
- 物理スケールUV
- Adobe Substance / Envato等の外部PBRフォルダ読込
- BaseColor、Roughness、NormalGL、NormalDX、Height、AOの自動判定
- DirectX NormalのY反転
- 4096px内蔵PBR
- Adobe/Envato素材制作ガイド
- 型紙数理テスト

### Material changes

- 内蔵生地の色むらと凹凸を大幅に弱め、樹脂的な見え方を抑制
- Roughnessを高め、Sheenを抑制
- HeightをNormalとは別チャンネルで生成

### Known limitations

- 自動Cloth緩和はまだ既定生成へ組み込んでいません
- 実物生地を用いない内蔵PBRは、近接Heroショット用の最終素材ではありません
- 人物へのフィッティングは対象ボディごとの調整が必要です
