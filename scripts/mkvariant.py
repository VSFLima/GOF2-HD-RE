import sys
stock=open('gamedata/libgof2hdaa.so','rb').read()
v19=open('gamedata/libgof2hdaa_cheats_v19.so','rb').read()
base=bytearray(open('gamedata/libgof2hdaa_stockgod.so','rb').read())
d=[i for i in range(len(stock)) if stock[i]!=v19[i]]
runs=[]
s=d[0];p=d[0]
for i in d[1:]:
    if i==p+1:p=i
    else:runs.append((s,p));s=i;p=i
runs.append((s,p))
def run_of(off):
    for s,e in runs:
        if s<=off<=e: return (s,e)
    raise SystemExit(f"offset {off:#x} not in any run")
GROUPS={
 'cloak1':[0x0965c9],'readyCloak':[0x096f6b,0x096f80],'boost':[0x0993d7],
 'cloak2':[0x0998c0],'credits':[0x0a9930],'levelTime':[0x0c434a],
 'transaction':[0x0e40be],'miningLost':[0x133dc0],'menuState':[0x142f2d],
 'valkyrie':[0x143dc6],'supernova':[0x1440ac],'scanner':[0x148d4c],
 'gunAmmo':[0x16dc24,0x16dc32,0x16dc4a],'changeLoad':[0x193a78],
}
keys=sys.argv[1].split(',')
out=sys.argv[2]
for k in keys:
    for off in GROUPS[k]:
        s,e=run_of(off)
        base[s:e+1]=v19[s:e+1]
open(out,'wb').write(base)
print("wrote",out,"groups=",keys)
