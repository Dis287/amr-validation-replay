#!/usr/bin/env python3
import argparse,hashlib,json,pathlib
ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('output');ap.add_argument('metrics');a=ap.parse_args()
rows=[];h=None;seq=[]
def add():
 if h is not None:rows.append((h,''.join(seq)))
for line in open(a.input):
 if line.startswith('>'):add();h=line.strip();seq=[]
 else:seq.append(line.strip())
add();kept=[]
for h,s in rows:
 cov=float(h.rsplit('_cov_',1)[1])
 if len(s)>=200 and cov>=10:kept.append((h,s))
with open(a.output,'w') as f:
 for h,s in kept:f.write(h+'\n'+s+'\n')
def n50(items):
 lens=sorted((len(s) for _,s in items),reverse=True);half=sum(lens)/2;c=0
 for n in lens:
  c+=n
  if c>=half:return n
m={'raw_contigs':len(rows),'raw_bases':sum(len(s) for _,s in rows),'raw_n50_all_lengths':n50(rows),'filtered_contigs':len(kept),'filtered_bases':sum(len(s) for _,s in kept),'filtered_n50_all_lengths':n50(kept),'filter':'length>=200 and SPAdes header _cov_>=10'}
pathlib.Path(a.metrics).write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m))
