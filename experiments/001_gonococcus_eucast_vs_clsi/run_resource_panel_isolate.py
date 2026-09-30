#!/usr/bin/env python3
import argparse, hashlib, json, os, pathlib, subprocess, sys, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024), b""): h.update(b)
    return h.hexdigest()

def md5(path):
    h=hashlib.md5()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024), b""): h.update(b)
    return h.hexdigest()

def run(cmd, **kw):
    print("+", " ".join(map(str,cmd)), flush=True)
    subprocess.run(list(map(str,cmd)), check=True, **kw)

def download(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists(): dest.unlink()
    req=urllib.request.Request(url, headers={"User-Agent":"amr-validation-replay/experiment001"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest,"wb") as w:
        while True:
            b=r.read(1024*1024)
            if not b: break
            w.write(b)

def verify_dsk(fasta, ascii_path, out_json):
    ORDER=str.maketrans({"A":"0","C":"1","T":"2","G":"3"})
    COMP=str.maketrans("ACGT","TGCA")
    def canonical(w):
        rc=w.translate(COMP)[::-1]
        return min((w,rc), key=lambda x:x.translate(ORDER))
    independent={}
    seq=[]
    with open(fasta) as fh:
        def consume():
            if not seq: return
            s="".join(seq).upper()
            for i in range(len(s)-30):
                w=s[i:i+31]
                if all(c in "ACGT" for c in w):
                    k=canonical(w); independent[k]=independent.get(k,0)+1
        for line in fh:
            if line.startswith(">"):
                consume(); seq=[]
            else: seq.append(line.strip())
        consume()
    observed={}
    dup=0
    with open(ascii_path) as fh:
        for line in fh:
            k,a=line.split()
            if k in observed: dup+=1
            observed[k]=int(a)
    missing=set(independent)-set(observed)
    extra=set(observed)-set(independent)
    wrong=sum(independent[k]!=v for k,v in observed.items() if k in independent)
    result={
      "independent_canonical_31mers":len(independent),"dsk_rows":len(observed),
      "duplicate_rows":dup,"missing":len(missing),"extra":len(extra),
      "abundance_mismatches":wrong,"filtered_fasta_sha256":sha256(fasta),
      "dsk_ascii_sha256":sha256(ascii_path),"dsk_ascii_bytes":os.path.getsize(ascii_path)
    }
    pathlib.Path(out_json).write_text(json.dumps(result,indent=2)+"\n")
    if dup or missing or extra or wrong or len(independent)!=len(observed): raise SystemExit(2)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--label",required=True)
    ap.add_argument("--work",required=True)
    ap.add_argument("--tools",required=True)
    a=ap.parse_args()
    work=pathlib.Path(a.work).resolve(); tools=pathlib.Path(a.tools).resolve()
    sel=json.loads((ROOT/"resource_panel_selection.json").read_text())
    row=next(x for x in sel if x["label"]==a.label)
    runid=row["run_accession"]
    stage=work/runid; stage.mkdir(parents=True,exist_ok=True)
    urls=row["fastq_ftp"].split(";"); sizes=list(map(int,row["fastq_bytes"].split(";"))); md5s=row["fastq_md5"].split(";")
    inputs=[]
    for i,(u,size,want) in enumerate(zip(urls,sizes,md5s),1):
        p=stage/f"{runid}_{i}.fastq.gz"
        download("https://"+u,p)
        got_size=p.stat().st_size; got_md5=md5(p)
        if got_size!=size or got_md5!=want: raise SystemExit(f"input integrity failure {p}: size {got_size}/{size} md5 {got_md5}/{want}")
        inputs.append({"path":str(p),"expected_size":size,"actual_size":got_size,"expected_md5":want,"actual_md5":got_md5,"pass":True})
    spades_out=stage/"spades"; spades_out.mkdir(exist_ok=True)
    run([sys.executable,ROOT/"bounded_stage.py","--name",f"{runid}_spades","--cwd",str(work),"--watch-dir",str(spades_out),"--evidence",str(stage/"spades.json"),"--timeout","2700","--",
         tools/"SPAdes-4.3.0-Linux/bin/spades.py","-1",stage/f"{runid}_1.fastq.gz","-2",stage/f"{runid}_2.fastq.gz","-o",spades_out,"-t","2","-m","8"])
    filtered=stage/"filtered.fasta"; filter_metrics=stage/"filter.json"
    run([sys.executable,ROOT/"filter_contigs.py",spades_out/"contigs.fasta",filtered,filter_metrics])
    quast_out=stage/"quast"; quast_out.mkdir(exist_ok=True)
    run([sys.executable,ROOT/"bounded_stage.py","--name",f"{runid}_quast","--cwd",str(work),"--watch-dir",str(quast_out),"--evidence",str(stage/"quast.json"),"--timeout","300","--",
         sys.executable,tools/"quast-5.2.0/quast.py","--min-contig","200","--no-plots","--no-html","--no-icarus","-t","2","-l","raw,filtered","-o",quast_out,spades_out/"contigs.fasta",filtered])
    tmp=stage/"dsk_tmp"; tmp.mkdir(exist_ok=True)
    run([sys.executable,ROOT/"bounded_stage.py","--name",f"{runid}_dsk","--cwd",str(work),"--watch-dir",str(tmp),"--evidence",str(stage/"dsk.json"),"--timeout","900","--",
         tools/"dsk-v2.3.3-bin-Linux/bin/dsk","-file",filtered,"-kmer-size","31","-abundance-min","1","-out",stage/"kmers","-out-tmp",tmp,"-max-memory","8000"])
    run([sys.executable,ROOT/"bounded_stage.py","--name",f"{runid}_dsk2ascii","--cwd",str(work),"--watch-dir",str(stage),"--evidence",str(stage/"dsk2ascii.json"),"--timeout","300","--",
         tools/"dsk-v2.3.3-bin-Linux/bin/dsk2ascii","-file",stage/"kmers.h5","-out",stage/"kmers.txt"])
    verify_dsk(filtered,stage/"kmers.txt",stage/"verification.json")
    result={
      "schema":"amr-resource-panel-isolate-v1","label":a.label,"selection":row,"inputs":inputs,
      "spades":json.loads((stage/"spades.json").read_text()),"filter":json.loads(filter_metrics.read_text()),
      "quast":json.loads((stage/"quast.json").read_text()),"dsk":json.loads((stage/"dsk.json").read_text()),
      "dsk2ascii":json.loads((stage/"dsk2ascii.json").read_text()),"verification":json.loads((stage/"verification.json").read_text())
    }
    (stage/"isolate_result.json").write_text(json.dumps(result,indent=2)+"\n")
    # raw reads and bulky SPAdes intermediates are not evidence artifacts
    for p in stage.glob("*.fastq.gz"): p.unlink()
    import shutil
    shutil.rmtree(spades_out,ignore_errors=True); shutil.rmtree(quast_out,ignore_errors=True); shutil.rmtree(tmp,ignore_errors=True)
    (stage/"kmers.h5").unlink(missing_ok=True)
    print(json.dumps({"status":"PASS","label":a.label,"run_accession":runid,"kmers":result["verification"]["dsk_rows"]}))

if __name__=="__main__": main()
