import sys
src = "gamedata/libgof2hdaa_allunlock.so"
dst = "gamedata/libgof2hdaa_cheats.so"
d = bytearray(open(src,'rb').read())

def chk(off, exp, name):
    got = bytes(d[off:off+len(exp)])
    ok = got == exp
    print(f"[{'OK' if ok else 'FAIL'}] {name} @0x{off:x}: got {got.hex()} exp {exp.hex()}")
    return ok

print("== base sanity (phase 1) ==")
chk(0x43c0c, bytes.fromhex("00008040"), "speed 4.0f")
chk(0x9faec, bytes.fromhex("e000"), "god(phase1)")
chk(0x921c6, bytes.fromhex("264600bf"), "kaamo br")
chk(0x9220c, bytes.fromhex("402c"), "kaamo cmp")

patches = [
 (0x9fa70, "7047", "Player::damage -> bx lr"),
 (0x9f7f0, "7047", "Player::damageGamma -> bx lr"),
 (0x9f834, "7047", "Player::damageEmp -> bx lr"),
 (0x16dc24, "00bf", "gun ammo site A subs->nop"),
 (0x16dc30, "4ff00001", "gun ammo site A changeAmount arg -> 0"),
 (0x16dc48, "4ff00001", "gun ammo site B changeAmount arg -> 0"),
 (0x16dc4c, "00bf", "gun ammo site B subs->nop"),
 (0x193a78, "4ff6ff70c7f6ff70704700bf", "Ship::getFreeSpace -> 0x7FFFFFFF"),
 (0xe40be, "6430", "Item::transaction buy increment -> +100"),
 (0xc434a, "4ff6ff707047", "Level::getTimeLimit -> 65535"),
 # phase 3
 (0x993d6, "20e0", "boost never auto-end (b.n +0x20)"),
 (0x96f6a, "01207047" + "00bf"*11, "PlayerEgo::readyForCloak -> 1"),
 (0x998c0, "90e000bf", "cloak never auto-end (b.n +0x90, nop)"),
 (0x965c8, "23e0", "cloak activation gate -> always"),
 (0x148d4c, "0120704700bf", "Radar::hasScanner -> 1"),
 (0x133dc0, "0020704700bf", "MiningGame::gameLost -> 0"),
]

print("== pre-verify targets ==")
for off, hx, name in patches:
    b = bytes.fromhex(hx)
    print(f"  before 0x{off:06x} ({name}): {bytes(d[off:off+len(b)]).hex()}")

print("== applying ==")
for off, hx, name in patches:
    b = bytes.fromhex(hx)
    d[off:off+len(b)] = b

open(dst,'wb').write(d)

# verify
d2 = open(dst,'rb').read()
print("== post-verify ==")
for off, hx, name in patches:
    b = bytes.fromhex(hx)
    got = bytes(d2[off:off+len(b)])
    print(f"[{'OK' if got==b else 'FAIL'}] 0x{off:06x} {name}: {got.hex()}")
print("size:", len(d), "==", len(d))
