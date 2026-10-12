"""Direct list pass: each BO7 model name, and the name with its last one or two segments trimmed,
behind every prefix modern materials carry (`m/`, `tm/`, `~tm/`, `mtl_`, ...). The plan version is
contrib/model_log_stems.py; this one keeps the raw `tm/<name>` spellings the model list carries.

    python contrib/model_log_direct.py ..\\assets.log | confirm_list - --script contrib/model_log_direct.py
"""
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else r"..\assets.log"
names = set()
for line in open(path, encoding="utf-8", errors="replace"):
    n = line.split(",", 1)[-1].strip()
    if "::" in n:
        n = n.split("::")[-1]
    n = re.sub(r"^\(\w+\)", "", n)
    if n:
        names.add(n)

stems = set(names)
for n in names:
    p = n.split("_")
    for k in range(1, 3):
        if len(p) > k + 1:
            stems.add("_".join(p[:-k]))

pre = ["", "m/", "tm/", "#tm7/", "mc/", "i/", "mtl_", "m/mtl_", "tm/mtl_", "tml8/", "m8/", "~tm/",
       "tm78/", "mh/", "tmr/", "tm9/", "wc/", "tw/", "elc/", "elcq/"]
out = sys.stdout
for s in stems:
    for p in pre:
        out.write(p + s + "\n")
