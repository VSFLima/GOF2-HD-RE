#!/usr/bin/env python3
# Patch in-place do ships.bin dentro do OBB do GOF2.
# Gera um stream deflate com tamanho EXATO igual ao csize original (valido do inicio ao fim),
# troca o stream + os dois CRCs (header local e diretorio central). Nada de offsets se move.
# Uso:  python3 patch_obb_ships.py            (dry-run)
#       python3 patch_obb_ships.py --write    (aplica)
#       python3 patch_obb_ships.py --restore  (volta do backup)
import zipfile, zlib, struct, os, sys

OBB = '/storage/emulated/0/Android/obb/net.fishlabs.gof2hdallandroid2012/main.47947006.net.fishlabs.gof2hdallandroid2012.obb'
TGT = '47947_GOF2CONTENT_ETC/assets/data/bin/ships.bin'
NEW = '/data/data/com.termux/files/home/gof2-re/mod/ships_mod_all.bin'
BACKUP = '/data/data/com.termux/files/usr/tmp/opencode/obb_ships_backup.bin'


def make_exact_deflate(data, target):
    """Stream deflate (raw) de tamanho EXATO = target que descomprime para data.
    Compressao Huffman do inicio + bloco 'stored' final com os ultimos k bytes (granularidade 1B)."""
    n = len(data)
    for k in range(0, n + 1):
        co = zlib.compressobj(9, zlib.DEFLATED, -15)
        s1 = co.compress(data[:n - k]) + co.flush(zlib.Z_SYNC_FLUSH)
        total = len(s1) + 5 + k
        if total == target:
            stored = b'\x01' + struct.pack('<H', k) + struct.pack('<H', (~k) & 0xffff) + data[n - k:]
            out = s1 + stored
            return out
        if total > target:
            return None
    return None


def restore():
    with open(BACKUP, 'rb') as b:
        lh, cco, rlen = struct.unpack('<IIQ', b.read(16))
        region = b.read(rlen)
        cdb = b.read(4)
    with open(OBB, 'r+b') as f:
        f.seek(lh); f.write(region)
        f.seek(cco); f.write(cdb)
        f.flush(); os.fsync(f.fileno())
    print('restaurado de', BACKUP)
    got = zipfile.ZipFile(OBB).read(TGT)
    print('restore verify: len', len(got), 'crc %08x' % (zlib.crc32(got) & 0xffffffff))


def main():
    newdata = open(NEW, 'rb').read()
    z = zipfile.ZipFile(OBB)
    i = z.getinfo(TGT)
    fn = i.filename.encode()
    lh = i.header_offset
    with open(OBB, 'rb') as f:
        f.seek(lh); lhdr = f.read(30)
    (_s, _v, flag, _m, _t, _d, _c, _cs, _us, lfnl, lexl) = struct.unpack('<IHHHHHIIIHH', lhdr)
    data_off = lh + 30 + lfnl + lexl
    loc_len = 30 + lfnl + lexl + i.compress_size
    csize, usize = i.compress_size, i.file_size
    print('lh_off    =', lh, ' data_off =', data_off, ' (local fnl=%d exl=%d)' % (lfnl, lexl))
    print('csize     =', csize, ' usize =', usize, ' flag = 0x%04x' % flag)
    print('newdata   =', len(newdata), 'B  tamanho-igual:', len(newdata) == usize)
    assert len(newdata) == usize
    assert not (flag & 0x8), 'data descriptor presente'

    stream = make_exact_deflate(newdata, csize)
    assert stream is not None, 'nao consegui deflate de tamanho exato'
    assert len(stream) == csize, (len(stream), csize)
    assert zlib.decompress(stream, -15) == newdata, 'roundtrip falhou'
    new_crc = zlib.crc32(newdata) & 0xffffffff
    print('stream    =', len(stream), 'B exatos; roundtrip OK; crc novo %08x (antigo %08x)' % (new_crc, i.CRC))

    sz = os.path.getsize(OBB)
    with open(OBB, 'rb') as f:
        f.seek(max(0, sz - 66000)); tail = f.read()
    k = tail.rfind(b'PK\x05\x06'); assert k >= 0
    eocd = tail[k:]
    cdoff, = struct.unpack_from('<I', eocd, 16)
    cdsize, = struct.unpack_from('<I', eocd, 12)
    central_crc_off = None
    with open(OBB, 'rb') as f:
        f.seek(cdoff); cd = f.read(cdsize)
    pos = 0
    while pos + 46 <= len(cd) and cd[pos:pos+4] == b'PK\x01\x02':
        fields = struct.unpack_from('<HHHHHHIIIHHHHHII', cd, pos + 4)
        fnl, exl, cml = fields[9], fields[10], fields[11]
        if cd[pos+46:pos+46+fnl].decode('latin1') == TGT:
            central_crc_off = cdoff + pos + 16
        pos += 46 + fnl + exl + cml
    assert central_crc_off is not None
    print('central crc off', central_crc_off)

    if '--write' not in sys.argv:
        print('DRY-RUN ok. use --write para aplicar.')
        return

    if not os.path.exists(BACKUP):
        os.makedirs(os.path.dirname(BACKUP), exist_ok=True)
        with open(OBB, 'rb') as f:
            f.seek(lh); region = f.read(loc_len)
            f.seek(central_crc_off); cdb = f.read(4)
        with open(BACKUP, 'wb') as b:
            b.write(struct.pack('<IIQ', lh, central_crc_off, len(region)))
            b.write(region); b.write(cdb)
        print('backup ->', BACKUP)
    else:
        print('backup ja existe ->', BACKUP)

    with open(OBB, 'r+b') as f:
        f.seek(data_off); f.write(stream)
        f.seek(lh + 14); f.write(struct.pack('<I', new_crc))
        f.seek(central_crc_off); f.write(struct.pack('<I', new_crc))
        f.flush(); os.fsync(f.fileno())
    print('escrito.')

    got = zipfile.ZipFile(OBB).read(TGT)
    print('verify: len', len(got), ' igual ao novo:', got == newdata)


if __name__ == '__main__':
    if '--restore' in sys.argv:
        restore()
    else:
        main()
