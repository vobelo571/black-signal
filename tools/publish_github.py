"""Publish authorized BLACK SIGNAL releases using the user's Git credential helper.

Credentials stay in process memory and are never written to files or printed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPO='vobelo571/black-signal'

def credentials():
    token=os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if not token:
        env=dict(os.environ,GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='Never')
        result=subprocess.run(['git','credential','fill'],input='protocol=https\nhost=github.com\n\n',capture_output=True,text=True,env=env,timeout=30,cwd=ROOT)
        values=dict(line.split('=',1) for line in result.stdout.splitlines() if '=' in line)
        token=values.get('password')
    if not token: raise RuntimeError('GitHub login required through Git Credential Manager or GH_TOKEN.')
    return token

class GitHub:
    def __init__(self): self.token=credentials()
    def request(self,path,method='GET',data=None,raw=None):
        url=path if path.startswith('https://') else 'https://api.github.com'+path
        if not (url.startswith('https://api.github.com/') or url.startswith('https://uploads.github.com/')):
            raise ValueError('Unexpected API host')
        headers={'Authorization':'Bearer '+self.token,'Accept':'application/vnd.github+json','User-Agent':'BLACK-SIGNAL-Publisher','X-GitHub-Api-Version':'2022-11-28'}
        if raw is not None:
            headers['Content-Type']='application/octet-stream'; body=raw
        elif data is not None:
            headers['Content-Type']='application/json'; body=json.dumps(data).encode('utf-8')
        else: body=None
        req=urllib.request.Request(url,headers=headers,data=body,method=method)
        with urllib.request.urlopen(req,timeout=300) as response:
            b=response.read()
            return json.loads(b) if b else None
    def maybe(self,path):
        try: return self.request(path)
        except urllib.error.HTTPError as exc:
            if exc.code==404: return None
            raise

def ensure_repo(api):
    user=api.request('/user')
    if user['login'].lower()!=REPO.split('/')[0].lower(): raise RuntimeError('Authenticated account is not the expected owner.')
    repo=api.maybe('/repos/'+REPO)
    if repo is None:
        repo=api.request('/user/repos','POST',{'name':'black-signal','description':'BLACK SIGNAL — by @Flixmo. Modular addons for S.T.A.L.K.E.R. G.A.M.M.A.; full pack and standalone downloads.','private':False,'has_issues':True,'has_wiki':False,'auto_init':False})
        print('Created public repository: '+repo['html_url'],flush=True)
    if repo['private']: raise RuntimeError('Existing repository is private; refusing to change its visibility implicitly.')
    remotes=subprocess.run(['git','remote','get-url','origin'],cwd=ROOT,capture_output=True,text=True)
    if remotes.returncode:
        subprocess.run(['git','remote','add','origin',repo['clone_url']],cwd=ROOT,check=True)
    elif remotes.stdout.strip().removesuffix('.git').lower()!=repo['clone_url'].removesuffix('.git').lower():
        raise RuntimeError('Existing origin points to another repository.')
    print('Pushing main branch',flush=True)
    subprocess.run(['git','push','-u','origin','main'],cwd=ROOT,check=True,env=dict(os.environ,GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='Never'))
    return repo

def publish(api):
    pack=json.loads((ROOT/'pack.json').read_text(encoding='utf-8'))
    report=json.loads((ROOT/'dist/validation.json').read_text(encoding='utf-8'))
    if report['errors'] or report['archives_verified']<31: raise RuntimeError('Archive validation has not passed.')
    paths=[]
    for line in (ROOT/'dist/SHA256SUMS.txt').read_text(encoding='ascii').splitlines():
        expected,name=line.split('  ',1)
        if Path(name).name!=name: raise RuntimeError('Invalid asset name')
        path=ROOT/'dist'/name
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected: raise RuntimeError('Checksum mismatch: '+name)
        paths.append(path)
    paths += [ROOT/'dist/SHA256SUMS.txt',ROOT/'dist/validation.json']
    tag='v'+pack['version']
    release=api.maybe('/repos/'+REPO+'/releases/tags/'+tag)
    if release and not release['draft']: raise RuntimeError('Release already published; refusing to replace its assets.')
    if not release:
        release=api.request('/repos/'+REPO+'/releases','POST',{'tag_name':tag,'target_commitish':'main','name':'BLACK SIGNAL '+pack['version']+' — by @Flixmo','body':(ROOT/'docs/RELEASE_NOTES.md').read_text(encoding='utf-8'),'draft':True,'prerelease':True})
    print('Draft release: '+str(release['id']),flush=True)
    existing={a['name']:a for a in api.request('/repos/'+REPO+'/releases/'+str(release['id'])+'/assets?per_page=100')}
    upload=release['upload_url'].split('{',1)[0]
    for n,path in enumerate(paths,1):
        payload=path.read_bytes(); digest='sha256:'+hashlib.sha256(payload).hexdigest()
        old=existing.get(path.name)
        if old and old.get('digest')==digest and old['size']==len(payload):
            print(f'[{n}/{len(paths)}] Already uploaded: {path.name}',flush=True); continue
        if old: raise RuntimeError('Existing asset differs: '+path.name)
        print(f'[{n}/{len(paths)}] Uploading {path.name} ({len(payload)} bytes)',flush=True)
        asset=api.request(upload+'?name='+urllib.parse.quote(path.name),method='POST',raw=payload)
        if asset['size']!=len(payload) or asset.get('digest',digest)!=digest: raise RuntimeError('Uploaded asset failed verification: '+path.name)
    current=api.request('/repos/'+REPO+'/releases/'+str(release['id'])+'/assets?per_page=100')
    if {p.name for p in paths}!={a['name'] for a in current}: raise RuntimeError('Remote asset list mismatch.')
    release=api.request('/repos/'+REPO+'/releases/'+str(release['id']),'PATCH',{'draft':False,'prerelease':True})
    (ROOT/'_local').mkdir(exist_ok=True)
    (ROOT/'_local/published-release.json').write_text(json.dumps(release,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Published: '+release['html_url'],flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('action',choices=['repo','release'])
    args=ap.parse_args(); api=GitHub()
    if args.action=='repo': ensure_repo(api)
    else: publish(api)
