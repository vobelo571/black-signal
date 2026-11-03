"""Validate payloads and build artifacts, without loading or changing the game."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build import load, filename, fomod

def sha(data): return hashlib.sha256(data).hexdigest()

def validate(archives=False):
    pack,deps=load(); errors=[]; warnings=[]; paths=defaultdict(list)
    scripts=[]; xml_count=0; file_count=0
    ids=[m['id'] for m in pack['modules']]
    if len(ids)!=len(set(ids)): errors.append('Duplicate module IDs')
    for m in pack['modules']:
        base=ROOT/'modules'/m['id']
        if m.get('default') is not False: errors.append('Module must be opt-in: '+m['id'])
        for key in m['requires']+m.get('optional',[]):
            if key not in deps: errors.append('Unknown dependency '+key)
            elif not deps[key]['url'].startswith('https://'): errors.append('Missing dependency URL '+key)
        if not (base/'gamedata').is_dir(): errors.append('Missing gamedata: '+m['id'])
        for f in base.rglob('*'):
            if not f.is_file(): continue
            file_count+=1; rel=f.relative_to(base).as_posix()
            if f.stat().st_size>=100*1024*1024: errors.append('File exceeds 100 MiB: '+str(f.relative_to(ROOT)))
            if f.suffix.lower() in {'.scoc','.scop','.log','.exe','.pdb','.mp3','.flac','.m4a'}: errors.append('Excluded/private artifact '+rel)
            if m['id']=='personal-radio' and f.suffix.lower()=='.ogg': errors.append('Personal music must not be packaged: '+rel)
            if rel.startswith('gamedata/'):
                paths[rel.casefold()].append((m['id'],sha(f.read_bytes())))
            if f.suffix=='.script': scripts.append(f)
            if f.suffix=='.xml':
                raw=f.read_bytes(); enc=re.search(br'encoding=["\x27]([^"\x27]+)',raw[:200])
                codec=enc.group(1).decode('ascii') if enc else 'utf-8-sig'
                try:
                    text=raw.decode(codec)
                    # Include-only files are valid Anomaly XML entry points.
                    includes=re.findall(r'^\s*#include\s+"([^"]+)"',text,flags=re.M)
                    text=re.sub(r'^\s*#include[^\n]*','',text,flags=re.M)
                    if not text.strip() and includes:
                        for inc in includes:
                            included=base/'gamedata'/'configs'/inc.replace('\\','/')
                            if not included.is_file(): raise ValueError('Missing include '+inc)
                        xml_count+=1
                        continue
                    ET.fromstring(text); xml_count+=1
                except Exception as exc: errors.append(f'XML {m["id"]}/{rel}: {exc}')
    collisions=[]
    for path,owners in paths.items():
        if len(owners)>1:
            collisions.append({'path':path,'modules':[x[0] for x in owners],'identical':len({x[1] for x in owners})==1})
            if len({x[1] for x in owners})>1: errors.append('Conflicting module paths: '+path)
    config=ET.fromstring(fomod(pack,deps))
    plugins=config.findall('.//plugin')
    if len(plugins)!=len(ids): errors.append('FOMOD plugin count mismatch')
    for plugin in plugins:
        if plugin.find('typeDescriptor/type').get('name')!='Optional': errors.append('Non-optional FOMOD component')
    for node in config.findall('.//file')+config.findall('.//folder'):
        rel=node.get('source'); dest=node.get('destination')
        if not (ROOT/rel).exists(): errors.append('FOMOD missing source: '+rel)
        if '..' in PurePosixPath(dest).parts or PurePosixPath(dest).is_absolute(): errors.append('Unsafe destination '+dest)
    # Provenance: game files are byte-for-byte copies except the reviewed radio filter.
    original=json.loads((ROOT/'docs/source-manifest.json').read_text(encoding='utf-8'))
    allowed_changes={('personal-radio','gamedata/scripts/ui_pda_radio_tab.script')}
    for item in original:
        f=ROOT/'modules'/item['module']/item['path']
        if not f.is_file(): errors.append('Missing captured file: '+item['module']+'/'+item['path'])
        elif sha(f.read_bytes())!=item['sha256'] and (item['module'],item['path']) not in allowed_changes:
            errors.append('Unexpected source change: '+item['module']+'/'+item['path'])
    lua_result='not available'
    try:
        from lupa.luajit21 import LuaRuntime
        runtime=LuaRuntime(encoding=None,unpack_returned_tuples=True)
        check=runtime.eval(b'function(s,n) local f,e=loadstring(s,n); return f~=nil,e end')
        for f in scripts:
            ok,error=check(f.read_bytes(),str(f.relative_to(ROOT)).encode('utf-8'))
            if not ok: errors.append(f'Lua {f.relative_to(ROOT)}: {error!r}')
        from test_radio_playlist import run as radio_test
        radio_cases=radio_test()
        lua_result=f'LuaJIT 2.1 / Lua 5.1: {len(scripts)} scripts compiled'
    except ImportError:
        radio_cases=[]
        warnings.append('LuaJIT syntax check unavailable (optional lupa.luajit21 package).')
    archive_count=0
    if archives:
        dist=ROOT/'dist'
        expected={filename(m) for m in pack['modules']}
        expected|={f'BLACK-SIGNAL-{pack["version"]}-MO2.zip','BLACK-SIGNAL-CustomMods-source.zip','BLACK-SIGNAL-SaveReset-source.zip'}
        if (ROOT/'utilities/SaveReset/bin/SaveReset.exe').is_file(): expected.add('BLACK-SIGNAL-SaveReset-win-x64.zip')
        if not expected.issubset({f.name for f in dist.glob('*.zip')}): errors.append('Missing expected release ZIPs')
        unexpected={f.name for f in dist.glob('*.zip')}-expected
        if unexpected: errors.append('Stale/unexpected ZIPs: '+', '.join(sorted(unexpected)))
        sums={line.split('  ',1)[1]:line.split('  ',1)[0] for line in (dist/'SHA256SUMS.txt').read_text(encoding='ascii').splitlines()}
        for name in sorted(expected):
            f=dist/name
            if not f.is_file(): continue
            archive_count+=1
            if sums.get(name)!=sha(f.read_bytes()): errors.append('ZIP checksum mismatch: '+name)
            with zipfile.ZipFile(f) as z:
                bad=z.testzip()
                if bad: errors.append('ZIP CRC failure: '+name+'/'+bad)
                names=z.namelist()
                for n in names:
                    if '..' in PurePosixPath(n).parts or PurePosixPath(n).is_absolute(): errors.append('Unsafe archive path: '+n)
                    if {'obj','backups','SaveReset_Backups','My Tracks','Imported Tracks Archive','__pycache__'} & set(PurePosixPath(n).parts): errors.append('Build/private directory in archive: '+name+'/'+n)
                    if name.endswith('-source.zip') and ('bin' in PurePosixPath(n).parts or n.endswith(('.exe','.pdb'))): errors.append('Binary in source archive: '+name+'/'+n)
                m=next((m for m in pack['modules'] if filename(m)==name),None)
                if m:
                    for source in (ROOT/'modules'/m['id']).rglob('*'):
                        if source.is_file():
                            rel=source.relative_to(ROOT/'modules'/m['id']).as_posix()
                            if rel not in names or z.read(rel)!=source.read_bytes(): errors.append('Standalone payload mismatch: '+name+'/'+rel)
                if name.endswith('-MO2.zip'):
                    packed=ET.fromstring(z.read('fomod/ModuleConfig.xml'))
                    for entry in packed.findall('.//file')+packed.findall('.//folder'):
                        src=entry.get('source')
                        exists=src in names if entry.tag=='file' else any(n.startswith(src+'/') for n in names)
                        if not exists: errors.append('FOMOD archive missing '+src)
                    # Simulate installing every selectable game component on Windows paths.
                    installed={}
                    for entry in packed.findall('.//plugin/files/folder'):
                        prefix=entry.get('source')+'/'
                        for n in names:
                            if n.startswith(prefix):
                                path=(entry.get('destination')+'/'+n[len(prefix):]).casefold()
                                data=z.read(n)
                                if path in installed and installed[path]!=data: errors.append('FOMOD conflicting install: '+path)
                                installed[path]=data
    report={'pack':pack['name'],'version':pack['version'],'modules':len(ids),'files':file_count,
        'xml_parsed':xml_count,'lua':lua_result,'radio_cases':radio_cases,'cross_module_paths':collisions,
        'archives_verified':archive_count,'errors':errors,'warnings':warnings,
        'game_test':'Not performed for the integrated pack','mo2_ui_test':'Not performed; archive structure and all-component file installation simulated'}
    if (ROOT/'dist').is_dir(): (ROOT/'dist/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 1 if errors else 0

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--archives',action='store_true')
    raise SystemExit(validate(ap.parse_args().archives))
