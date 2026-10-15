#!/bin/bash
# build_mod.sh -- reconstroi o APK modado do GOF2 HD a partir de stock/ + scripts/
#
# Requer: unzip, zip, zipalign, apksigner (Android SDK build-tools), python3.
# Uso:  ./scripts/build_mod.sh [saida.apk]
#
# Pipeline do .so (rode antes se precisar regerar):
#   stock/libgof2hdaa_stock.so -> (+ unlock) -> stock/libgof2hdaa_allunlock.so
#   -> apply_cheats.py -> mod/libgof2hdaa_mod_v31.so
# Aqui usamos diretamente o .so final ja pronto.
set -euo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$HERE/build/GOF2FHD_MOD.apk}"
SO="$HERE/mod/libgof2hdaa_mod_v31.so"
APK="$HERE/stock/net.fishlabs.gof2hdallandroid2012.apk"
WORK="$HERE/.build-tmp"

rm -rf "$WORK"
mkdir -p "$WORK/apk" "$(dirname "$OUT")"

# 1. dados modados (copia e patcheia)
cp "$HERE/stock/items.bin" "$WORK/items.bin"
cp "$HERE/stock/ships.bin" "$WORK/ships.bin"
python3 "$HERE/scripts/patch_data.py" "$WORK/items.bin" "$WORK/ships.bin"

# 2. descompacta o APK original e substitui .so + dados
unzip -q "$APK" -d "$WORK/apk"
cp "$SO"   "$WORK/apk/lib/armeabi-v7a/libgof2hdaa.so"
cp "$WORK/items.bin" "$WORK/apk/assets/data/bin/items.bin"
cp "$WORK/ships.bin" "$WORK/apk/assets/data/bin/ships.bin"

# 3. re-zipa sem as assinaturas antigas
( cd "$WORK/apk" && rm -f META-INF/*.SF META-INF/*.RSA META-INF/*.MF 2>/dev/null || true
  zip -qr "$WORK/unsigned.apk" . )

# 4. zipalign + assina
zipalign -f -p 4 "$WORK/unsigned.apk" "$WORK/aligned.apk"
apksigner sign --out "$OUT" "$WORK/aligned.apk"

echo "OK -> $OUT"
