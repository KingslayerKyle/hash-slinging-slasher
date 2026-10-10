"""Samples names from the GPT-2 of gpt_train.py; unique names on stdout.
One prefix (--prefix) or a budget per prefix (--prefix-file, lines "prefix budget"): D&C-GEN-style split by prefix,
plus prefixes anchored on hits. --known drops names already known before they count against a budget."""
import argparse, json, os, re, sys, time
import torch
from transformers import GPT2LMHeadModel

ap = argparse.ArgumentParser()
ap.add_argument('--model', default='/w/gpt/focus')
ap.add_argument('--prefix', default='p8_zm_red_')
ap.add_argument('--prefix-file')
ap.add_argument('--known')
ap.add_argument('-n', type=int, default=5_000_000)
ap.add_argument('--batch', type=int, default=8192)
ap.add_argument('--temp', type=float, default=1.0)
ap.add_argument('--top-p', type=float, default=0.98)
a = ap.parse_args()
vocab = json.load(open(os.path.join(os.path.dirname(a.model), 'vocab.json')))
idx = {t: i for i, t in enumerate(vocab)}
model = GPT2LMHeadModel.from_pretrained(a.model).cuda().eval().to(torch.bfloat16)
known = set(l.strip().split(',')[-1] for l in open(a.known)) if a.known else set()
jobs = [(l.split()[0], int(l.split()[1])) for l in open(a.prefix_file) if l.strip()] if a.prefix_file else [(a.prefix, a.n)]
seen, t, out = set(), time.time(), sys.stdout
with torch.no_grad():
    for j, (prefix, budget) in enumerate(jobs):
        pre = [1] + [idx.get(tok, 3) for tok in re.findall(r'[^_/]+|[_/]', prefix)]
        if 3 in pre[1:] or len(pre) > 40:
            continue
        got, stale, bs = 0, 0, min(a.batch, max(64, budget))
        while got < budget and stale < 5:
            x = torch.tensor([pre] * bs).cuda()
            g = model.generate(x, attention_mask=torch.ones_like(x), do_sample=True, temperature=a.temp, top_p=a.top_p,
                               top_k=0, max_length=48, eos_token_id=2, pad_token_id=0, bad_words_ids=[[3]])
            before = got
            for row in g.tolist():
                s = ''.join(vocab[i] for i in row[1:] if i > 3)
                if s not in seen and s not in known:
                    seen.add(s)
                    out.write(s + '\n')
                    got += 1
            stale = stale + 1 if got - before < bs // 100 else 0
        print('job', j, len(jobs), prefix, got, 'unique', len(seen), '%ds' % (time.time() - t), file=sys.stderr, flush=True)
