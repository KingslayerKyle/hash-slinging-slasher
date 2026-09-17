"""BO4 xanim names read out of the Wraith package index shipped in the game folder.

E:\\...\\Call of Duty Black Ops 4\\PackageIndex\\bo4_xanim.wni is a Wraith .wni name index (2019,
LZ4 block after an 18-byte header, then 8-byte hash + NUL-terminated name per entry). Its 3,411
entries were checked against the real pocket ids; almost all are already known, these are not.
The companion bo4_sab.wni and bo4_ximage.wni gave nothing new.
"""

NAMES = r"""
vm_blundergat_fire_rechamber_ads
vm_bowie_knife_69
vm_bowie_knife_71
""".strip().splitlines()

for n in NAMES:
    n = n.strip()
    if n:
        print(n)
