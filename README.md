# GOF2 HD — Engenharia Reversa / Código-fonte do Mod

Acervo completo do processo de engenharia reversa e construção do mod para
**Galaxy on Fire 2 HD** (Android, pacote `net.fishlabs.gof2hdallandroid2012`).

O mod pronto (APK + OBB) está em outro repositório: **GOF2-HD-Mod**.
Este aqui guarda o **processo**: scripts, offsets, formatos e binários de
referência — tudo o que é necessário para reconstruir o mod do zero.

---

## Estrutura

```
gof2-re/
├── README.md            este índice
├── NOTES.md             notas técnicas (offsets, formatos, técnicas) — LEIA PRIMEIRO
├── scripts/
│   ├── apply_cheats.py  patcheia o .so (lista completa de offsets)
│   ├── mkvariant.py     gera variantes ligando/desligando grupos de patch
│   ├── patch_data.py    patcheia items.bin / ships.bin (recriado)
│   └── build_mod.sh     pipeline completo: .so + dados + zip + align + sign (recriado)
├── symbols/
│   ├── syms.txt         símbolos dinâmicos (llvm-nm -D, formato GNU)
│   ├── mangled.txt      nomes C++ mangled
│   └── demangled.txt    nomes C++ demangled
├── disasm/
│   └── dis.txt          disassembly completo Thumb (llvm-objdump)
├── patches/             patches JSON de outro ferramental (texto)
├── stock/               material ORIGINAL (não modificar)
│   ├── libgof2hdaa_stock.so       .so original limpo (md5 6cfdff8d…)
│   ├── libgof2hdaa_allunlock.so   .so com patches de "destrancar tudo"
│   ├── net.fishlabs.gof2hdallandroid2012.apk  APK original
│   ├── items.bin  ships.bin  ships_mod.bin  systems.bin
└── mod/
    └── libgof2hdaa_mod_v31.so     .so final usado no APK v31 (md5 ac9f4141…)
```

## md5 de referência

| arquivo | md5 |
|---|---|
| stock/libgof2hdaa_stock.so | `6cfdff8d604f11b61a44b5e10e810bb1` |
| stock/libgof2hdaa_allunlock.so | `d34def298aadf4b9cd8461c5ac79e333` |
| mod/libgof2hdaa_mod_v31.so | `ac9f4141a21876554c667e7094fdc9f0` |

## Ferramentas usadas (repos públicos, não re-hospedados aqui)

- gof2edit  — https://github.com/Ravernstal/gof2edit
- KaamoClubModApi — https://github.com/1337Skid/KaamoClubModApi
- GOF2Haxx — https://github.com/R00tFS/GOF2Haxx
- Galaxy-on-Fire-2-FULL-HD-Android — https://github.com/KiritoJPK/Galaxy-on-Fire-2-FULL-HD-Android

Toolchain: `llvm-objdump`/`llvm-nm` (Thumb, armv7), `capstone`, `python3`,
`zipalign`, `apksigner`, `apktool`, `jadx`.

> Tudo o que não está aqui e era grande/redundante (arquivos `.xapk`, `.7z`,
> APKs intermediários v1–v30, saídas do jadx/apktool) pode ser regenerado a
> partir do `stock/` + `scripts/`, conforme `NOTES.md`.
