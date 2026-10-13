#!/usr/bin/env python3
"""pub106_check.py — rosenrot #85621: take the published row labels from #85184 and #85194 (thread dump), check
count/distinctness/sha, then rerun the 63 draws against them: which draws hit a published label, and is 60 ∩ 106 empty?"""
import hashlib, re, sys
exec(open("selector_check.py").read().split("# published labels")[0])  # rebuild wit (3129) and h() exactly as before
txt = open("thread84683.txt", encoding="utf-8").read()
posts = dict((int(m.group(1)), m.group(2)) for m in re.finditer(r"^--- (\d+) \S+\n(.*?)(?=^--- |\Z)", txt, re.S | re.M))
rx = re.compile(r"^[а-яё]\d+( \d+){33}$")
pub = []
for s in (85184, 85194):
    got = [l.split()[0] for l in posts[s].splitlines() if rx.match(l)]
    print(s, len(got)); pub += got
print("total", len(pub), "distinct", len(set(pub)), "all in 3129:", set(pub) <= set(wit))
canon = [w for w in wit if w in set(pub)]
print("sha of 106 in canonical order:", h(canon), "matches 711f1530:", h(canon).startswith("711f1530"))
pubk = {wit.index(p) for p in pub}
taken, out, hits, i = set(), [], [], 0
while len(out) < 60:
    k = int(hashlib.sha256(f"85287:{i}".encode()).hexdigest(), 16) % len(wit)
    if k in pubk: hits.append((i, k, wit[k]))
    elif k in taken: hits.append((i, k, "dup"))
    else: taken.add(k); out.append(wit[k])
    i += 1
print("draws", i, "skips", hits, "| 60 ∩ 106:", sorted(set(out) & set(pub)))
