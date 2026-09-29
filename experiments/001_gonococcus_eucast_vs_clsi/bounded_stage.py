#!/usr/bin/env python3
import argparse, hashlib, json, os, pathlib, signal, subprocess, time

def status_rows():
    rows={}
    for p in pathlib.Path('/proc').glob('[0-9]*/status'):
        try:
            d=dict(line.split(':',1) for line in p.read_text().splitlines() if ':' in line)
            rows[int(p.parent.name)]={'ppid':int(d['PPid']),'rss_kib':int(d.get('VmRSS','0 kB').split()[0]),'nspid':int(d.get('NSpid','0').split()[-1])}
        except (OSError,ValueError,KeyError): pass
    return rows

def descendants(rows,root):
    out={root}
    while True:
        new={pid for pid,v in rows.items() if v['ppid'] in out}
        if new <= out:return out
        out |= new

def size_tree(path):
    total=0
    for p in pathlib.Path(path).rglob('*'):
        try:
            if p.is_file():total += p.stat().st_size
        except OSError: pass
    return total

def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        while b:=f.read(1024*1024):h.update(b)
    return h.hexdigest()

ap=argparse.ArgumentParser();ap.add_argument('--name',required=True);ap.add_argument('--cwd',required=True);ap.add_argument('--watch-dir',required=True);ap.add_argument('--evidence',required=True);ap.add_argument('--timeout',type=int,default=2700);ap.add_argument('command',nargs=argparse.REMAINDER);a=ap.parse_args()
if a.command and a.command[0]=='--':a.command=a.command[1:]
if not a.command:raise SystemExit('missing command')
ev=pathlib.Path(a.evidence);ev.parent.mkdir(parents=True,exist_ok=True);log=ev.with_suffix('.log')
host_self=int(pathlib.Path('/proc/self/status').read_text().split('NSpid:')[1].splitlines()[0].split()[0])
start=time.monotonic();peak_rss=0;peak_disk=size_tree(a.watch_dir);timed_out=False
with log.open('w') as out:
 p=subprocess.Popen(a.command,cwd=a.cwd,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
 while p.poll() is None:
  rows=status_rows();roots=[pid for pid,v in rows.items() if v['ppid']==host_self and v['nspid']==p.pid]
  live=set()
  for root in roots:live |= descendants(rows,root)
  peak_rss=max(peak_rss,sum(rows[x]['rss_kib'] for x in live if x in rows));peak_disk=max(peak_disk,size_tree(a.watch_dir))
  if time.monotonic()-start>a.timeout:
   timed_out=True;os.killpg(p.pid,signal.SIGTERM);time.sleep(2)
   if p.poll() is None:os.killpg(p.pid,signal.SIGKILL)
   break
  time.sleep(.5)
rc=p.wait();elapsed=time.monotonic()-start
record={'schema':'amr-resource-stage-v1','name':a.name,'command':a.command,'cwd':str(pathlib.Path(a.cwd).resolve()),'timeout_seconds':a.timeout,'timed_out':timed_out,'exit_code':rc,'wall_seconds':round(elapsed,3),'sample_interval_seconds':0.5,'sampled_peak_process_tree_rss_kib':peak_rss,'sampled_peak_watch_dir_bytes':peak_disk,'final_watch_dir_bytes':size_tree(a.watch_dir),'log_sha256':digest(log)}
ev.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
raise SystemExit(124 if timed_out else rc)
