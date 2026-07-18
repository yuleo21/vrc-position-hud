# PositionHUD

VRChat用シェーダー(`PositionHUD.shader`)と、そこに焼き込まれた座標データを画面キャプチャ経由で読み取るPythonデコーダ(`decoder/`)のセット。

## 導入

### 必要なもの

- Unity: [ModularAvatar](https://modular-avatar.nadena.dev/)
- Python: [uv](https://docs.astral.sh/uv/)(`decoder/`側で使用。詳細は [decoder/README.md](decoder/README.md))

### Unity側

1. `PositionHUD_vX.Y.Z.unitypackage` をUnityプロジェクトにインポート
2. `Assets/njm2360/PositionHUD/Prefab/PositionHUD.prefab` をアバター配下に置く

| プロパティ                 | 意味                                     | デフォルト |
| -------------------------- | ---------------------------------------- | ---------- |
| `_BlockPx`                 | グリッド1ビットの一辺(px)                | 1          |
| `_OffsetX` / `_OffsetY`    | グリッド左上の画面端からのオフセット(px) | 0 / 0      |
| `_TextPx`                  | テキストHUDの1ドットの大きさ(px)         | 2          |
| `_ShowPixel` / `_ShowText` | 各HUDの表示切り替え                      | 0 / 0      |

### VRChat側

ExpressionMenuから"Pixel-HUD"をONにする。Pythonのデコーダが読むのはこのグリッドだけなので、これだけで動きます。"Text-HUD"は目視確認用のおまけです。

### Python側

`decoder/`が独立したuvプロジェクトです。使い方は [decoder/README.md](decoder/README.md) を参照。`_BlockPx` / `_OffsetX` / `_OffsetY` を変更した場合は、`decoder/src/posehud/spec.py` の同名定数も必ず合わせること。1pxでもズレるとマジックナンバー不一致で読めなくなります。

## ライセンス

BSD 2-Clause [LICENSE](LICENSE)
