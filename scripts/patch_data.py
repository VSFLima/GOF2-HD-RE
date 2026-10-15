#!/usr/bin/env python3
# patch_data.py -- patcheia items.bin e ships.bin do GOF2 HD (Android).
#
# ATENCAO: script RECRIADO a partir das notas; valide antes de confiar.
# Uso:  python3 scripts/patch_data.py [items.bin] [ships.bin]
#       (defaults: stock/items.bin  stock/ships.bin  -- edita no lugar)
#
# Mods aplicados:
#   items.bin  -> toda primary (tipo 0): dano (chave 9) = 10000
#                 Liberator (id 179): dano (chave 9) = 999999
#   ships.bin  -> registro 44 (Spectre) =
#                 (44, 99999999, 999999, 12000000, 10, 20, 0, 20, 300)

import struct
import sys
import os

ITEM_COUNT = 233      # itens em items.bin
SHIP_COUNT = 64       # registros em ships.bin
SHIP_FIELDS = 9       # >9I  (big-endian)
PRIMARY_DAMAGE = 10000
LIBERATOR_ID = 179
LIBERATOR_DAMAGE = 999999
SPECTRE_IDX = 44
SPECTRE = (44, 99999999, 999999, 12000000, 10, 20, 0, 20, 300)


# --------------------------- items.bin ---------------------------
def parse_items(data):
    """Cada item = 3 arrays [count u32 BE][count x i32 BE] em sequencia.
    Os pares (chave,valor) ficam no 3o array."""
    off = 0
    items = []
    for i in range(ITEM_COUNT):
        arrs = []
        for a in range(3):
            if off + 4 > len(data):
                raise SystemExit("EOF inesperado em items.bin @item %d arr %d" % (i, a))
            (cnt,) = struct.unpack_from(">I", data, off)
            off += 4
            if cnt > 100000:
                raise SystemExit("count suspeito=%d @item %d arr %d" % (cnt, i, a))
            vals = list(struct.unpack_from(">%di" % cnt, data, off))
            off += 4 * cnt
            arrs.append(vals)
        items.append(arrs)
    if off != len(data):
        raise SystemExit("parse de items.bin nao consumiu o arquivo todo "
                         "(%d de %d) -- formato assumido errado" % (off, len(data)))
    return items


def kv_get(arr, key):
    for i in range(0, len(arr) - 1, 2):
        if arr[i] == key:
            return i
    return None


def kv_set(arr, key, value):
    i = kv_get(arr, key)
    if i is None:
        arr.extend([key, value])
    else:
        arr[i + 1] = value


def write_items(path, items):
    out = bytearray()
    for arrs in items:
        for a in arrs:
            out += struct.pack(">I", len(a))
            out += struct.pack(">%di" % len(a), *a)
    with open(path, "wb") as f:
        f.write(out)


def patch_items(path):
    items = parse_items(open(path, "rb").read())
    np, nl = 0, 0
    for idx, arrs in enumerate(items):
        pairs = arrs[2]
        ti = kv_get(pairs, 1)
        if ti is None:
            continue
        if pairs[ti + 1] == 0:                       # primary
            kv_set(pairs, 9, PRIMARY_DAMAGE)
            np += 1
        if idx == LIBERATOR_ID:
            kv_set(pairs, 9, LIBERATOR_DAMAGE)
            nl += 1
    write_items(path, items)
    print("items.bin: %d primaries -> dano %d | Liberator(%d) -> %d"
          % (np, PRIMARY_DAMAGE, LIBERATOR_ID, LIBERATOR_DAMAGE))
    return np, nl


# --------------------------- ships.bin ---------------------------
def patch_ships(path):
    data = bytearray(open(path, "rb").read())
    rec = struct.calcsize(">%dI" % SHIP_FIELDS)      # 36
    if len(data) != SHIP_COUNT * rec:
        raise SystemExit("ships.bin com tamanho inesperado: %d (esperado %d)"
                         % (len(data), SHIP_COUNT * rec))
    off = SPECTRE_IDX * rec
    struct.pack_into(">%dI" % SHIP_FIELDS, data, off, *SPECTRE)
    with open(path, "wb") as f:
        f.write(data)
    print("ships.bin: registro %d (Spectre) -> %s" % (SPECTRE_IDX, SPECTRE))


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    items = sys.argv[1] if len(sys.argv) > 1 else os.path.join(root, "stock", "items.bin")
    ships = sys.argv[2] if len(sys.argv) > 2 else os.path.join(root, "stock", "ships.bin")
    patch_items(items)
    patch_ships(ships)


if __name__ == "__main__":
    main()
