"""Build BLACK SIGNAL: main catalog, installation page, standalone ZIPs and FOMOD."""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
STAMP=(2026,11,4,0,0,0)
REPO='https://github.com/vobelo571/black-signal'

def load():
    return (json.loads((ROOT/'tools/pack.json').read_text(encoding='utf-8')),
            json.loads((ROOT/'tools/dependencies.json').read_text(encoding='utf-8'))['dependencies'])

def filename(m): return f'BLACK-SIGNAL-{m["id"]}-{m["version"]}.zip'
def download(pack,name): return f'{REPO}/releases/download/v{pack["version"]}/{name}'
def full_filename(pack): return f'BLACK-SIGNAL-{pack["version"]}-MO2.zip'

def module_readme(m,deps):
    lines=[f'# {m["title"]}', '', f'BLACK SIGNAL · by @Flixmo · {m["version"]}', '',
           m['description'], '', '**Установка:** ZIP → Mod Organizer 2 → включить ниже базовых модов → перезапустить игру.', '', '**Требуется:**']
    for key in m['requires']:
        d=deps[key]; lines.append(f'- [{d["name"]}]({d["url"]}) — {d["author"]}.')
    if m.get('optional'):
        lines += ['', '**Необязательно:** '+', '.join(f'[{deps[k]["name"]}]({deps[k]["url"]})' for k in m['optional'])+'.']
    lines += ['', m['notes'], '', '**Авторы:** '+m['credits'], '',
              'Исходные инструкции и уведомления сохранены в upstream-docs/.']
    if m['id']=='personal-radio':
        lines += ['', 'Для своей музыки запустите FLX Radio Importer.py в папке установленного мода (Python 3.10+ с Tk и FFmpeg). Треки добавляются в gamedata/sounds/radio/_playlist_5.']
    return '\n'.join(lines)+'\n'

def generate_docs(pack,deps):
    main=['# BLACK SIGNAL — by @Flixmo', '',
        '28 модов для **S.T.A.L.K.E.R. G.A.M.M.A.** Скачайте весь пак с выбором компонентов или любой мод отдельно.', '',
        f'**[Скачать весь пак {pack["version"]}]({download(pack,full_filename(pack))})** · [Установка и зависимости](INSTALL.md) · [Release]({REPO}/releases/tag/v{pack["version"]})', '',
        '| Мод | Что делает | Скачать |', '|---|---|---|']
    for m in pack['modules']:
        main.append(f'| [{m["title"]}](modules/{m["id"]}/README.md) | {m["description"]} | [ZIP]({download(pack,filename(m))}) |')
        folder=ROOT/'modules'/m['id']
        (folder/'README.md').write_text(module_readme(m,deps),encoding='utf-8')
        (folder/'module.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (folder/'meta.ini').write_text(f'[General]\ngameName=stalkeranomaly\nversion={m["version"]}\nmodid=0\nnotes=BLACK SIGNAL by @Flixmo - {m["id"]}\n',encoding='utf-8')
    main += ['', '**Как установить:** скачайте ZIP, установите через MO2 и включите ниже базовых модов. В общем паке отметьте нужные компоненты. Старую копию того же мода отключите.', '',
             'Основа — Anomaly / GAMMA и моды сообщества. Исходные авторы указаны в описаниях компонентов; библиотеки скачиваются по ссылкам на странице установки.']
    (ROOT/'README.md').write_text('\n'.join(main)+'\n',encoding='utf-8')
    install=['# Установка и зависимости', '', '[← Все моды и скачивание](README.md)', '',
        'База: **Anomaly 1.5.3 / GAMMA 0.9.5**, Mod Organizer 2. В GAMMA большинство зависимостей уже установлено.', '',
        '1. Сделайте копию сохранений и закройте игру.',
        '2. Установите общий ZIP или выбранные отдельные ZIP через MO2.',
        '3. Включите зависимости, затем BLACK SIGNAL ниже них в левой панели.',
        '4. Отключите старые копии этих же модов и перезапустите игру.', '',
        'При смене компонентов общего пака переустанавливайте его **с заменой**, а не объединением.', '',
        '## Какие зависимости нужны', '',
        'Помимо GAMMA, смотрите строку выбранного мода. Полный список всем устанавливать не нужно.', '',
        '| Мод | Зависимости |', '|---|---|']
    for m in pack['modules']:
        keys=[k for k in m['requires'] if k!='gamma']
        req=', '.join(f'[{deps[k]["name"]}]({deps[k]["url"]})' for k in keys) or 'Только GAMMA'
        if m.get('optional'):
            req += '; необязательно: '+', '.join(f'[{deps[k]["name"]}]({deps[k]["url"]})' for k in m['optional'])
        install.append(f'| {m["title"]} | {req} |')
    install += ['', '## Совместимость', '',
        '- Колесо еды и медикаментов: отключите **G.A.M.M.A. Quick Action Wheel Balance**, базовый QAW оставьте.',
        '- Слышимые шаги врагов: не включайте вместе с полным Fireteam AI.',
        '- Графические патчи: **DX11/r3** и совместимые версии шейдеров.',
        '- Радио поставляется без музыки; для импорта своих треков нужны Python с Tk и FFmpeg.',
        '- Новые предметы, NPC и замены оружия сохраняются в сейве. Для полного отката используйте сохранение до установки.',
        '- Проверены файлы, Lua, XML и архивы. Полный совместный прогон всех модулей в игре ещё не выполнен.', '',
        'Авторы и дополнительные замечания находятся в README выбранного компонента.']
    (ROOT/'INSTALL.md').write_text('\n'.join(install)+'\n',encoding='utf-8')
    notes=[f'# BLACK SIGNAL {pack["version"]} — by @Flixmo', '',
        f'**[Скачать весь пак]({download(pack,full_filename(pack))})** · [Все 28 модов отдельно]({REPO}#readme) · [Установка и библиотеки]({REPO}/blob/main/INSTALL.md)', '',
        '- Общий пак с выбором компонентов в MO2.',
        '- Каждый мод доступен отдельным ZIP.',
        '- Упрощены главная страница и инструкции.',
        '- Убраны SaveReset, CustomMods и лишняя служебная документация.', '',
        'Игровые файлы модулей не менялись. Установка: ZIP → MO2 → включить ниже базовых модов. Старые копии тех же модов отключить.', '',
        'Для Anomaly 1.5.3 / GAMMA 0.9.5. Сторонние библиотеки и личная музыка не включены.']
    (ROOT/'_local').mkdir(exist_ok=True)
    (ROOT/'_local/release-notes.md').write_text('\n'.join(notes)+'\n',encoding='utf-8')

def fomod(pack,deps):
    xsi='http://www.w3.org/2001/XMLSchema-instance'; ET.register_namespace('xsi',xsi)
    root=ET.Element('config',{f'{{{xsi}}}noNamespaceSchemaLocation':'http://qconsulting.ca/fo3/ModConfig5.0.xsd'})
    ET.SubElement(root,'moduleName').text=f'BLACK SIGNAL {pack["version"]} — by @Flixmo'
    required=ET.SubElement(root,'requiredInstallFiles')
    for name in ['README.md','INSTALL.md']:
        ET.SubElement(required,'file',source=name,destination='BLACK-SIGNAL/'+name,priority='0')
    steps=ET.SubElement(root,'installSteps',order='Explicit'); groups=collections.defaultdict(list)
    for m in pack['modules']: groups[m['group']].append(m)
    for group,mods in groups.items():
        step=ET.SubElement(steps,'installStep',name=group)
        optional=ET.SubElement(step,'optionalFileGroups',order='Explicit')
        grp=ET.SubElement(optional,'group',name='Выберите нужные компоненты',type='SelectAny')
        plugins=ET.SubElement(grp,'plugins',order='Explicit')
        for m in mods:
            plugin=ET.SubElement(plugins,'plugin',name=m['title'])
            req='; '.join(deps[k]['name'] for k in m['requires'])
            ET.SubElement(plugin,'description').text=f'{m["description"]}\n\nТребуется: {req}.\n\n{m["notes"]}\n\nАвторы: {m["credits"]}'
            files=ET.SubElement(plugin,'files')
            ET.SubElement(files,'folder',source=f'modules/{m["id"]}/gamedata',destination='gamedata',priority='10')
            ET.SubElement(files,'file',source=f'modules/{m["id"]}/README.md',destination=f'BLACK-SIGNAL/modules/{m["id"]}.md',priority='10')
            ET.SubElement(files,'file',source=f'modules/{m["id"]}/module.json',destination=f'BLACK-SIGNAL/selected/{m["id"]}.json',priority='10')
            if (ROOT/'modules'/m['id']/'upstream-docs').is_dir():
                ET.SubElement(files,'folder',source=f'modules/{m["id"]}/upstream-docs',destination=f'BLACK-SIGNAL/upstream/{m["id"]}',priority='10')
            if m['id']=='personal-radio':
                ET.SubElement(files,'file',source='modules/personal-radio/FLX Radio Importer.py',destination='FLX Radio Importer.py',priority='10')
            ET.SubElement(ET.SubElement(plugin,'typeDescriptor'),'type',name='Optional')
    ET.indent(root,space='  ')
    return ET.tostring(root,encoding='utf-8',xml_declaration=True)

def zip_entries(path,entries):
    path.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for arc,data in sorted(entries.items()):
            info=zipfile.ZipInfo(arc,STAMP); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o100644 << 16
            z.writestr(info,data.read_bytes() if isinstance(data,Path) else data)

def tree(folder,prefix=''):
    return {prefix+f.relative_to(folder).as_posix():f for f in folder.rglob('*') if f.is_file() and '__pycache__' not in f.parts}

def build(out):
    pack,deps=load(); generate_docs(pack,deps); out.mkdir(parents=True,exist_ok=True)
    for m in pack['modules']:
        entries=tree(ROOT/'modules'/m['id']); entries['INSTALL.md']=ROOT/'INSTALL.md'
        zip_entries(out/filename(m),entries)
    entries=tree(ROOT/'modules','modules/')
    for name in ['README.md','INSTALL.md']: entries[name]=ROOT/name
    entries['fomod/ModuleConfig.xml']=fomod(pack,deps)
    info=ET.Element('fomod')
    for key,value in [('Name','BLACK SIGNAL'),('Author','@Flixmo'),('Version',pack['version']),('Description','Modular addons for G.A.M.M.A. by @Flixmo')]: ET.SubElement(info,key).text=value
    entries['fomod/info.xml']=ET.tostring(info,encoding='utf-8',xml_declaration=True)
    zip_entries(out/full_filename(pack),entries)
    files=sorted(out.glob('*.zip'))
    (out/'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.name}\n' for f in files),encoding='ascii')
    print(f'Built {len(files)} ZIPs: {len(pack["modules"])} separate mods and one FOMOD.')

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,default=ROOT/'dist'); ap.add_argument('--docs-only',action='store_true'); args=ap.parse_args()
    if args.docs_only: generate_docs(*load())
    else: build(args.out.resolve())
