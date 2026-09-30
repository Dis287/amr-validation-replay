#!/usr/bin/env python3
import argparse, collections, gzip, hashlib, json, pathlib, sys

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024), b""): h.update(b)
    return h.hexdigest()

def load_dsk(path):
    d={}; dup=0
    with open(path) as f:
        for line in f:
            k,a=line.split()
            if k in d: dup+=1
            d[k]=int(a)
    if dup: raise SystemExit(f"duplicate DSK rows in {path}: {dup}")
    return d

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--inputs",nargs="+",required=True); ap.add_argument("--combined",required=True); ap.add_argument("--out",required=True); a=ap.parse_args()
    occurrence={}
    input_rows={}; input_sha={}
    for spec in a.inputs:
        name,path=spec.split("=",1); d=load_dsk(path); input_rows[name]=len(d); input_sha[name]=sha256(path)
        for k,v in d.items(): occurrence.setdefault(k,[]).append((name,v))
    expected={k:v for k,v in occurrence.items() if len(v)>=2}
    seen=set(); errors=collections.Counter(); examples=[]
    with gzip.open(a.combined,"rt") as f:
        for line in f:
            k,*tags=line.split()
            if tags and tags[0]=="|": tags=tags[1:]
            if k in seen: errors["duplicate_output_row"]+=1
            seen.add(k)
            if k not in expected:
                errors["extra_or_below_minimum"]+=1
                if len(examples)<10: examples.append({"kmer":k,"error":"extra_or_below_minimum","tags":tags})
                continue
            want=sorted(f"{n}:{v}" for n,v in expected[k])
            if sorted(tags)!=want:
                errors["sample_or_abundance_mismatch"]+=1
                if len(examples)<10: examples.append({"kmer":k,"error":"sample_or_abundance_mismatch","tags":tags,"expected":want})
    errors["missing_expected"]=len(set(expected)-seen)
    result={"schema":"amr-resource-panel-n8-verification-v1","input_rows":input_rows,"input_sha256":input_sha,
      "independent_union":len(occurrence),"independent_present_in_at_least_two":len(expected),
      "seer_output_rows":len(seen),"seer_unique_output":len(seen),"seer_errors":dict(errors),
      "first_errors":examples,"combined_sha256":sha256(a.combined),"combined_bytes":pathlib.Path(a.combined).stat().st_size}
    pathlib.Path(a.out).write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    if any(errors.values()) or len(seen)!=len(expected): raise SystemExit(2)
if __name__=="__main__": main()
