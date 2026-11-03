"""Build deterministic standalone addons and a FOMOD archive; Python stdlib only."""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
STAMP=(2026,11,4,0,0,0)

def load():
    return (json.loads((ROOT/'pack.json').read_text(encoding='utf-8')),
            json.loads((ROOT/'dependencies.json').read_text(encoding='utf-8'))['dependencies'])

def filename(module):
    return f'BLACK-SIGNAL-{module["id"]}-{module["version"]}.zip'

def module_readme(m,deps):
    lines=[f'# BLACK SIGNAL — {m["title"]}', '', '**by @Flixmo**', '',
           f'Модуль `{m["id"]}` · версия **{m["version"]}**.', '', m['description'], '',
           '## Обязательные зависимости', '']
    for key in m['requires']:
        d=deps[key]
        version=f' Референс: {d["reference_version"]}.' if d.get('reference_version') else ''
        lines.append(f'- [{d["name"]}]({d["url"]}) — {d["author"]}.{version} {d["note"]}')
    opt=m.get('optional',[])
    if opt:
        lines += ['', '## Необязательные инструменты и зависимости', '']
        for key in opt:
            d=deps[key]; lines.append(f'- [{d["name"]}]({d["url"]}) — {d["note"]}')
    lines += ['', '## Установка', '',
       '1. Закройте игру и сделайте резервную копию сохранений.',
       '2. Установите этот ZIP через Mod Organizer 2 как отдельный мод.',
       '3. Включите зависимости, затем этот модуль. В левой панели поставьте его ниже базовых модов, чтобы его файлы имели больший числовой приоритет.',
       '4. Отключите старую отдельную копию этого же модуля, если она уже установлена.',
       '5. Полностью перезапустите игру через MO2.', '', m['notes'], '',
       'Устанавливайте либо отдельный ZIP, либо тот же компонент общего пака: не включайте две копии одновременно.', '',
       'Сторонние библиотеки не включены; ссылки выше ведут на страницы авторов. Не обновляйте библиотеки внутри GAMMA без проверки совместимости.', '',
       '## Авторство и проверка', '',
       'Пак и доработки — @Flixmo. Оригинальные авторы базовых модов, моделей, текстур и звуков сохраняют авторство. См. CREDITS.md и upstream-docs/.', '',
       'Это компонент первого интеграционного кандидата 0.1.0-rc.1. Проверки упаковки не заменяют тестирование в игровом движке. Работа на чистой Anomaly и произвольных версиях GAMMA не заявлена.', '']
    if m['id']=='personal-radio':
        lines += ['## Личная музыка', '',
          'Музыкальных треков в ZIP нет. В папке установленного модуля запустите `FLX Radio Importer.py` с Python 3.10+ и Tk; для конвертации нужен FFmpeg. Импортёр кладёт свои OGG в `gamedata/sounds/radio/_playlist_5`. Перезапустите игру после импорта.', '',
          'Без импортированной музыки плеер использует штатный беззвучный ресурс. Файл `.keep` сохраняет пустую папку и не считается треком. PDA Radio Extended не нужен; его музыка и ресурсы Starcry_ не включены.', '']
    return '\n'.join(lines)

def generate_docs(pack,deps):
    table=['# Отдельные загрузки BLACK SIGNAL', '',
       'Каждый модуль устанавливается отдельно без общего пака. Скачайте нужный ZIP из GitHub Releases и установите через MO2. Обязательные библиотеки перечислены на странице каждого модуля.', '',
       '| Модуль | Версия | Скачать ZIP | Описание и зависимости |', '|---|---|---|---|']
    for m in pack['modules']:
        folder=ROOT/'modules'/m['id']
        (folder/'README.md').write_text(module_readme(m,deps),encoding='utf-8')
        (folder/'module.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (folder/'meta.ini').write_text(f'[General]\ngameName=stalkeranomaly\nversion={m["version"]}\nmodid=0\nnotes=BLACK SIGNAL by @Flixmo - {m["id"]}\n',encoding='utf-8')
        link=f'https://github.com/vobelo571/black-signal/releases/download/v{pack["version"]}/{filename(m)}'
        table.append(f'| {m["title"]} | {m["version"]} | [Скачать]({link}) | [Открыть](../modules/{m["id"]}/README.md) |')
    (ROOT/'docs'/'DOWNLOADS.md').write_text('\n'.join(table)+'\n',encoding='utf-8')
    lines=['# Сторонние зависимости', '',
       'Не входят в дистрибутив BLACK SIGNAL. В GAMMA большинство уже установлено. Проверяйте список именно выбранного модуля; xlibs и полный набор мебели не требуются каждому моду.', '',
       'Референсные версии — снимок локального профиля, а не утверждение о самой новой версии.', '',
       '| Зависимость | Автор | Ссылка | Примечание |', '|---|---|---|---|']
    for d in deps.values(): lines.append(f'| {d["name"]} | {d["author"]} | [Страница автора]({d["url"]}) | {d["note"]} |')
    (ROOT/'docs'/'DEPENDENCIES.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    inv=['# Исходный состав', '', 'Захват доступных файлов: 04.11.2026. Игровые файлы оригинальной установки не изменялись.', '',
         '| ID | Исходная папка | Файлов gamedata |', '|---|---|---|']
    for m in pack['modules']:
        n=sum(f.is_file() for f in (ROOT/'modules'/m['id']/'gamedata').rglob('*'))
        inv.append(f'| {m["id"]} | {m["source_folder"]} | {n} |')
    inv += ['', 'Взята установленная копия Merramun, а не вторая копия одноимённого Git-репозитория.',
            'Исходные контрольные суммы до изменений упаковки: `source-manifest.json`. Контрольные суммы готовых архивов: `dist/SHA256SUMS.txt`.', '']
    (ROOT/'docs'/'SOURCE_INVENTORY.md').write_text('\n'.join(inv),encoding='utf-8')

def fomod(pack,deps):
    xsi='http://www.w3.org/2001/XMLSchema-instance'
    ET.register_namespace('xsi',xsi)
    root=ET.Element('config',{f'{{{xsi}}}noNamespaceSchemaLocation':'http://qconsulting.ca/fo3/ModConfig5.0.xsd'})
    ET.SubElement(root,'moduleName').text=f'BLACK SIGNAL {pack["version"]} — by @Flixmo'
    required=ET.SubElement(root,'requiredInstallFiles')
    ET.SubElement(required,'folder',source='docs',destination='BLACK-SIGNAL-docs',priority='0')
    for name in ['README.md','CREDITS.md','RIGHTS.md']:
        ET.SubElement(required,'file',source=name,destination='BLACK-SIGNAL-docs/'+name,priority='0')
    steps=ET.SubElement(root,'installSteps',order='Explicit')
    groups=collections.defaultdict(list)
    for m in pack['modules']: groups[m['group']].append(m)
    for group,mods in groups.items():
        step=ET.SubElement(steps,'installStep',name=group)
        optional=ET.SubElement(step,'optionalFileGroups',order='Explicit')
        grp=ET.SubElement(optional,'group',name='Выберите нужные компоненты',type='SelectAny')
        plugins=ET.SubElement(grp,'plugins',order='Explicit')
        for m in mods:
            plugin=ET.SubElement(plugins,'plugin',name=m['title'])
            req='; '.join(deps[k]['name'] for k in m['requires'])
            ET.SubElement(plugin,'description').text=f'{m["description"]}\n\nТребуется: {req}.\n\n{m["notes"]}'
            files=ET.SubElement(plugin,'files')
            ET.SubElement(files,'folder',source=f'modules/{m["id"]}/gamedata',destination='gamedata',priority='10')
            ET.SubElement(files,'file',source=f'modules/{m["id"]}/README.md',destination=f'BLACK-SIGNAL-docs/modules/{m["id"]}.md',priority='10')
            ET.SubElement(files,'file',source=f'modules/{m["id"]}/module.json',destination=f'BLACK-SIGNAL-docs/selected/{m["id"]}.json',priority='10')
            if m['id']=='personal-radio':
                ET.SubElement(files,'file',source='modules/personal-radio/FLX Radio Importer.py',destination='FLX Radio Importer.py',priority='10')
            desc=ET.SubElement(plugin,'typeDescriptor')
            ET.SubElement(desc,'type',name='Optional')
    ET.indent(root,space='  ')
    return ET.tostring(root,encoding='utf-8',xml_declaration=True)

def zip_entries(path,entries):
    path.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for arc,data in sorted(entries.items()):
            info=zipfile.ZipInfo(arc,STAMP); info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644 << 16
            z.writestr(info,data.read_bytes() if isinstance(data,Path) else data)

def tree(folder,prefix=''):
    return {prefix+f.relative_to(folder).as_posix():f for f in folder.rglob('*') if f.is_file() and '__pycache__' not in f.parts}

def build(out):
    pack,deps=load(); generate_docs(pack,deps)
    out.mkdir(parents=True,exist_ok=True)
    for m in pack['modules']:
        entries=tree(ROOT/'modules'/m['id'])
        for name in ['CREDITS.md','RIGHTS.md']: entries[name]=ROOT/name
        # Include the actual referenced dependency records in each separate download.
        relevant=set(m['requires']+m.get('optional',[]))
        entries['dependencies.json']=(json.dumps({k:deps[k] for k in sorted(relevant)},ensure_ascii=False,indent=2)+'\n').encode('utf-8')
        zip_entries(out/filename(m),entries)
    entries=tree(ROOT/'modules','modules/')
    entries.update(tree(ROOT/'docs','docs/'))
    for name in ['README.md','CREDITS.md','RIGHTS.md','pack.json','dependencies.json']: entries[name]=ROOT/name
    entries['fomod/ModuleConfig.xml']=fomod(pack,deps)
    info=ET.Element('fomod')
    for key,value in [('Name','BLACK SIGNAL'),('Author','@Flixmo'),('Version',pack['version']),('Description','Modular addons for G.A.M.M.A. by @Flixmo')]: ET.SubElement(info,key).text=value
    entries['fomod/info.xml']=ET.tostring(info,encoding='utf-8',xml_declaration=True)
    zip_entries(out/f'BLACK-SIGNAL-{pack["version"]}-MO2.zip',entries)
    for utility in ['CustomMods','SaveReset']:
        entries={k:v for k,v in tree(ROOT/'utilities'/utility).items() if not ({'bin','obj','backups'} & set(Path(k).parts))}
        entries['CREDITS.md']=ROOT/'CREDITS.md'; entries['RIGHTS.md']=ROOT/'RIGHTS.md'
        zip_entries(out/f'BLACK-SIGNAL-{utility}-source.zip',entries)
    executable=ROOT/'utilities/SaveReset/bin/SaveReset.exe'
    if executable.is_file():
        entries={'SaveReset.exe':executable,'README.md':ROOT/'utilities/SaveReset/README.md',
            'README-original.txt':ROOT/'utilities/SaveReset/README-original.txt',
            'CREDITS.md':ROOT/'CREDITS.md','RIGHTS.md':ROOT/'RIGHTS.md'}
        zip_entries(out/'BLACK-SIGNAL-SaveReset-win-x64.zip',entries)
    files=sorted(out.glob('*.zip'))
    (out/'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.name}\n' for f in files),encoding='ascii')
    print(f'Built {len(files)} archives: {len(pack["modules"])} addons, FOMOD, utility sources and optional SaveReset binary in {out}')

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,default=ROOT/'dist'); ap.add_argument('--docs-only',action='store_true')
    args=ap.parse_args()
    if args.docs_only: generate_docs(*load())
    else: build(args.out.resolve())
