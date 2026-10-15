# NOTES — GOF2 HD (Android) — Engenharia Reversa

Pacote: `net.fishlabs.gof2hdallandroid2012`
Alvo principal: `lib/armeabi-v7a/libgof2hdaa.so` (2 469 656 bytes, ARM Thumb).
Dados do jogo: `assets/data/bin/{items,ships,systems,stations,wanted}.bin`.

> **Fora deste doc:** o mod pronto (APK/OBB) está no repositório `GOF2-HD-Mod`.

---

## 1. Convenções / quirks da toolchain

- **File offset == VA** dentro de `.text` (o segmento começa em 0).
- `llvm-objdump` mostra a **coluna hex = valor da meia-palavra**; os **bytes no
  arquivo são little-endian**. Ex.: `dd20` ⇒ bytes `20 dd`; `3801` ⇒ `01 38`.
- **Pipe quebra a saída** do `llvm-objdump` — rode sem pipe ou redirecione p/ arquivo.
- `objdump` GNU imprime offsets de struct em **decimal**; `llvm-objdump` em **hex**.
- Sem `xxd` (use `od`). Sem `keystone` (encode Thumb na mão).
- Sem `/tmp` — usar `/data/data/com.termux/files/usr/tmp/opencode/`.

---

## 2. Formato dos arquivos de dados

### items.bin (27532 B no APK, BE)
- 233 itens. Cada item = **3 arrays** concatenados: `[count u32 BE][count × i32 BE]`.
- Os pares **(chave, valor)** ficam no **3º array**: `arrays[3*idx + 2]`.
- Leitura no binário: `Item::getAttribute(int)` @ `0xe403c`.

**Chaves de atributo:**
| chave | significado |
|---|---|
| 1 | tipo (0=primary, 1=secondary, 2=turret, 3=equipment, 4=commodity) |
| 2 | ordenação (sort) |
| 3 | nível tec (tecLevel) |
| 7 | preço compra (buy) |
| 8 | preço venda (sell) |
| 9 | dano (damage) |
| 11 | recarga (recarga) |
| 12 | velocidade do projétil |
| 13 | rotação |
| 16 | automático (Automatic) |
| 17 | alcance (range) |

Contagens por tipo: primary 40, secondary 30, turret 10, equipment 66, commodity 87.

### ships.bin (2304 B)
- 64 registros × **36 bytes**, `>9I` (**big-endian**).
- Campos: `(id, preco, preco2, casco?, f4, f5, f6, f8, f9)`.
- **Manejo (handling) = campo8/100** (+0.2 se for equipamento tipo 3).
- Spectre = **registro 44**.
- Campo 8 no v31 = **300**.

Referências de Spectre (fins de comparação):
| origem | valores |
|---|---|
| APK base | `(44, 800, 65, 30000000, 4, 2, 0, 16, 138)` |
| APK v31 (nosso) | `(44, 99999999, 999999, 12000000, 10, 20, 0, 20, 300)` |
| OBB instalado | `(44, 99999999, 999999, 12000000, 10, 5, 1, 50, 500)` ← já vinha modificado |
| gamedata/ships.bin | `(44, 800, 65, 12000000, 4, 2, 0, 16, 138)` |
| gamedata/ships_mod.bin | `(44, 800, 999999, 12000000, 4, 2, 0, 16, 138)` |

### .lang
- Formato: `[u16 BE len][utf8]`, 3401 entradas.
- Nome de item: id = `itemId + 1274`. Descrição: id = `itemId + 1041`.

---

## 3. Funções-chave (endereço = file offset)

| função | endereço | observação |
|---|---|---|
| `Item::getAttribute(int)` | `0xe403c` | lê par chave/valor |
| `Globals::init` | `0xe7b80` | chama os loaders UMA vez |
| `FileRead::loadItemsBinary` (plt) | `0x5e588` | abre `data/bin/items.bin` |
| `FileRead::loadShipsBinary` (plt) | `0x5e594` | abre `data/bin/ships.bin` |
| `FileRead::loadSystemsBinary` (plt) | `0x5c0b0` | abre `data/bin/systems.bin` |
| `Gun::shootAt` | `0x16d518` | +0x74 = munição; Player::shoot @0xa04b4 exige ret==1 |
| `Gun::update` | `~0x16e940` | |
| `Gun::calcCharacterCollision` | `0x16e928` | |
| `Ship::getFreeSpace` | `0x193a78` | |
| `Level::getTimeLimit` | `0xc434a` | |
| `SolarSystem::isVisible` | `0x170cb4` | |
| `Station::isDiscovered` | `0xa3a50` | |
| `SolarSystem::isFullyDiscovered` | `0x170c30` | |
| `Status::isBlueprintUnlocked(int)` | `0xa9ab6` | |
| `BluePrint::isUnlocked` | `0x196532` | |
| `Station::stationHasHiddenBlueprint` | `0xa3ec8` | |
| `SolarSystem::hasNoOwner` | `0x170cc0` | |

---

## 4. Pipeline do .so

```
stock/libgof2hdaa_stock.so
      │  (+ patches de "destrancar tudo")
      ▼
stock/libgof2hdaa_allunlock.so
      │  apply_cheats.py
      ▼
mod/libgof2hdaa_mod_v31.so   (usado no APK v31)
```

`apply_cheats.py` lê `libgof2hdaa_allunlock.so` e escreve `libgof2hdaa_cheats.so`.
Ajuste os paths no topo do script conforme a pasta local.

### Lista de patches do .so (file offset → bytes)

| offset | original | patchado | o que faz |
|---|---|---|---|
| `0x9fa70` | | `7047` | `Player::damage` → `bx lr` (god) |
| `0x9f7f0` | | `7047` | `Player::damageGamma` → `bx lr` |
| `0x9f834` | | `7047` | `Player::damageEmp` → `bx lr` |
| `0x16dc24` | `0138` | `00bf` | munição da arma site A: `subs`→nop |
| `0x16dc30` | `4ff0ff31` | `4ff00001` | arg `changeAmount` → 0 (A) |
| `0x16dc48` | `4ff0ff31` | `4ff00001` | arg `changeAmount` → 0 (B) |
| `0x16dc4c` | `0138` | `00bf` | munição da arma site B: `subs`→nop |
| `0x193a78` | | `4ff6ff70c7f6ff70704700bf` | `Ship::getFreeSpace` → 0x7FFFFFFF |
| `0xe40be` | | `6430` | incremento de compra do item → +100 |
| `0xc434a` | | `4ff6ff707047` | `Level::getTimeLimit` → 65535 |
| `0x993d6` | `20 dd` | `20 e0` | boost nunca auto-encerra (`b.n +0x20`) |
| `0x96f6a` | `0146002091f8ad2132b1d1f8` | `01207047` + `00bf`×11 | `PlayerEgo::readyForCloak` → 1 |
| `0x998c0` | `40f39080` | `90e000bf` | cloaking nunca auto-encerra |
| `0x965c8` | `23da` | `23e0` | gate de ativação do cloak → sempre |
| `0x148d4c` | | `0120704700bf` | `Radar::hasScanner` → 1 |
| `0x133dc0` | | `0020704700bf` | `MiningGame::gameLost` → 0 (nunca perde) |

`RET1 = 01 20 70 47` = `movs r0,#1; bx lr` (usado nos patches “→1”).
Para reverter qualquer patch, reescreva os bytes originais da tabela.

### Grupos do mkvariant.py (patch seletivo por recurso)

`mkvariant.py` computa os "runs" do diff entre `stock` e a variante `v19` e
copia grupos escolhidos da v19 para dentro de uma base (`stockgod`).
Grupos e offsets:

| grupo | offsets |
|---|---|
| cloak1 | 0x0965c9 |
| readyCloak | 0x096f6b, 0x096f80 |
| boost | 0x0993d7 |
| cloak2 | 0x0998c0 |
| credits | 0x0a9930 |
| levelTime | 0x0c434a |
| transaction | 0x0e40be |
| miningLost | 0x133dc0 |
| menuState | 0x142f2d |
| **valkyrie** | 0x143dc6 |
| **supernova** | 0x1440ac |
| scanner | 0x148d4c |
| gunAmmo | 0x16dc24, 0x16dc32, 0x16dc4a |
| changeLoad | 0x193a78 |

Uso: `python3 scripts/mkvariant.py boost,cloak1,gunAmmo out.so`

> **Atenção (bug aberto):** os grupos `valkyrie`/`supernova` e os endereços de
> menu (~0x142f2d) sugerem que há lógica **por campanha**. Isso é a pista para
> o problema "mods só se aplicam na DLC Supernova, não na Valkyrie nem no base".

---

## 5. Patches de dados (items.bin / ships.bin)

- **Primárias:** em todo item tipo 0, setar chave `9` (dano) = **10000**.
  Recarga/velocidade/rotação permanecem originais.
- **Liberator** (id **179**, dano base 850): dano = **999999**.
- **ships.bin registro 44 (Spectre):**
  `(44, 99999999, 999999, 12000000, 10, 20, 0, 20, 300)`.
- **Todos os itens em todas as estações / compra ilimitada:** stock de compra
  ajustado via `0xe40be` (+100) e nops em `0xe4082`/`0xe40b8`.

> Os binários de dados ficam em duas cópias: dentro do APK
> (`assets/data/bin/`) e dentro do OBB (`47947_GOF2CONTENT_ETC/assets/data/bin/`).
> **Ainda não confirmado** de qual das duas o jogo lê. O `ships.bin` do OBB já
> veio com o registro 44 modificado, o que sugere **OBB**.

---

## 6. Bug conhecido / em aberto

- **Mods só aplicam no modo Supernova (DLC).** Na Valkyrie e no jogo base os
  mods não aparecem. Investigar os patches de menu/estado em `~0x142f2d` e os
  grupos `valkyrie`/`supernova`. Verificar se os dados vêm do OBB.
- **Weapon fire-then-stop:** primárias disparam uma vez e param. O patch de
  cloaking revertido na v31 pode ter corrigido — não confirmado em jogo.

---

## 7. Reconstruir o APK (pipeline)

1. Descompactar o APK original (`stock/net.fishlabs.gof2hdallandroid2012.apk`).
2. Substituir `lib/armeabi-v7a/libgof2hdaa.so` pelo `.so` modado.
3. Substituir `assets/data/bin/items.bin` e `ships.bin` pelos modados.
4. Re-zipar, `zipalign -p 4`, `apksigner sign`.
5. Se os dados vierem do OBB, aplicar os mesmos `.bin` no OBB
   (`…/Android/obb/net.fishlabs.gof2hdallandroid2012/main.47947006…obb`,
   entradas em DEFLATE).

Os scripts `patch_data.py` e `build_mod.sh` neste diretório automatizam
3–4 (recriados — valide o parser de items antes de confiar).
