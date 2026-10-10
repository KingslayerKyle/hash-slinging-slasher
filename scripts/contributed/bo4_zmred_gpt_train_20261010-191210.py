"""Token-level GPT-2 on known BO4 names: tokens are the pieces between '_' and '/', and the separators.
docker run --rm --gpus all -v /root/gloss:/w -e PYTHONPATH=/w/pylib pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime \
    python /w/gpt_train.py [--epochs 4] [--focus p8_zm_red --focus-epochs 3]"""
import argparse, json, math, os, random, re, time
from collections import Counter
import torch
from transformers import GPT2Config, GPT2LMHeadModel

ap = argparse.ArgumentParser()
ap.add_argument('--names', default='/w/names_train.txt')
ap.add_argument('--out', default='/w/gpt')
ap.add_argument('--epochs', type=int, default=4)
ap.add_argument('--focus', default='p8_zm_red')
ap.add_argument('--focus-epochs', type=int, default=3)
ap.add_argument('--layers', type=int, default=8)
ap.add_argument('--dim', type=int, default=512)
a = ap.parse_args()
SPLIT = re.compile(r'[^_/]+|[_/]')
MAXLEN = 48

names = [l.strip() for l in open(a.names) if l.strip()]
toks = [SPLIT.findall(n) for n in names]
freq = Counter(t for ts in toks for t in ts)
vocab = ['<pad>', '<bos>', '<eos>', '<unk>'] + sorted(t for t, c in freq.items() if c >= 2)
idx = {t: i for i, t in enumerate(vocab)}
os.makedirs(a.out, exist_ok=True)
json.dump(vocab, open(os.path.join(a.out, 'vocab.json'), 'w'))


def enc(ts):
    return [1] + [idx.get(t, 3) for t in ts][:MAXLEN - 2] + [2]


data = [enc(ts) for ts in toks if len(ts) <= MAXLEN - 2]
focus = [enc(ts) for n, ts in zip(names, toks) if n.startswith(a.focus) and len(ts) <= MAXLEN - 2]
print('names', len(data), 'focus', len(focus), 'vocab', len(vocab), flush=True)

cfg = GPT2Config(vocab_size=len(vocab), n_positions=MAXLEN, n_embd=a.dim, n_layer=a.layers, n_head=8,
                 bos_token_id=1, eos_token_id=2, pad_token_id=0)
model = GPT2LMHeadModel(cfg).cuda()
print('params', sum(p.numel() for p in model.parameters()) // 10**6, 'M', flush=True)


def batches(rows, bs):
    random.shuffle(rows)
    for i in range(0, len(rows), bs):
        b = rows[i:i + bs]
        L = max(len(r) for r in b)
        x = torch.zeros(len(b), L, dtype=torch.long)
        for j, r in enumerate(b):
            x[j, :len(r)] = torch.tensor(r)
        yield x.cuda()


def train(rows, epochs, lr, bs=512):
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    steps = epochs * math.ceil(len(rows) / bs)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=lr, total_steps=steps, pct_start=0.05)
    model.train()
    t, s = time.time(), 0
    for e in range(epochs):
        tot, n = 0.0, 0
        for x in batches(rows, bs):
            labels = x.masked_fill(x == 0, -100)
            with torch.autocast('cuda', dtype=torch.bfloat16):
                loss = model(input_ids=x, attention_mask=(x != 0).long(), labels=labels).loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(); sched.step(); opt.zero_grad(set_to_none=True)
            tot += loss.item(); n += 1; s += 1
        print('epoch', e, 'loss %.3f' % (tot / n), '%ds' % (time.time() - t), flush=True)


train(data, a.epochs, 1e-3)
model.save_pretrained(os.path.join(a.out, 'base'))
if focus and a.focus_epochs:
    train(focus + random.sample(data, min(len(data), 4 * len(focus))), a.focus_epochs, 2e-4, bs=256)
model.save_pretrained(os.path.join(a.out, 'focus'))
print('saved', a.out)
