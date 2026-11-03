"""Capture existing Flixmo addons without changing the installed game.

Only used on the author's machine. Published builds read modules/, not GAMMA.
"""
from __future__ import annotations
import argparse
import configparser
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# id, installed folder, title, group, description, required dependencies, notes
CATALOG = [
 ('repeat-loot','1004- FLX Repeat Loot','Повторный обыск','Мир и баланс','Небольшие дополнительные находки каждые 24 игровых часа на поддерживаемых локациях.',[], 'Прототип 0.2.0. Меняет доступность ресурсов. More Dynamic Items поддерживается, но не обязателен.'),
 ('pda-trader-restock','1005- FLX PDA Trader Restock','Пополнение торговцев из КПК','Интерфейс и удобство','Кнопка платного пополнения ассортимента: 25 000 RU за подтверждённый заказ.',[], 'Не открывает закрытые уровни ассортимента.'),
 ('bhs-fixes','1006- BHS Fixes by flx','BHS Fixes','Исправления','Сохранение состояния конечностей, лечение у врачей и восстановление BHS при загрузке.',['bhs'], 'Совместим с отдыхом и лечением у костра.'),
 ('delete-all-saves','1007- FLX Delete All Saves','Удалить все сохранения','Интерфейс и удобство','Кнопка массового удаления сохранений в меню загрузки.',[], 'Удаляет сохранения после подтверждения. Выбирать осознанно; заранее сделать копию savedgames.'),
 ('arena-mutant-trader','1008- FLX Arena Mutant Trader','Жила: торговец Арены','Персонажи и снаряжение','Торговец частями мутантов, мастерская и контракты.',['dux','hf','hf-expansion'], 'Нужен доступ в помещения Арены. Внешний Taskboard необязателен.'),
 ('stash-network','1008- FLX Stash Network','Сеть тайников','Интерфейс и удобство','Управление сетью хранилищ и распределением предметов.',[], 'Настройки и подробности в исходном README. Проверить на копии сохранения.'),
 ('belt-presets','1009- FLX Belt Presets','Пресеты пояса','Интерфейс и удобство','Три пресета артефактов пояса в инвентаре.',[], 'Использует уже имеющиеся предметы.'),
 ('mutant-magnetism-fix','1009- FLX Mutants No Attack Magnetism','Без притягивания к мутантам','Исправления','DLTX-правка притягивания игрока при атаках мутантов.',['dltx'], 'Не заменяет модели мутантов.'),
 ('zone-field-gear','1010- FLX Zone Field Gear','Снаряжение Зоны','Персонажи и снаряжение','32 фракционных костюма: восемь семейств, модели, руки, иконки и баланс.',['dltx'], 'При удалении сначала убрать добавленные предметы или вернуться к сохранению до установки. Основы: Anomaly, Blackgrowl, IENCE, LASS; см. CREDITS.'),
 ('soft-rays-weather','1011- FLX Soft Rays HD and Gentle Weather','Мягкие лучи и спокойная погода','Графика и звук','Мягкие лучи, сокращённые выборки шейдеров, ослабление дождя и отключение Airborne Pulse.',['sss'], 'Патч текущих DX11/r3-шейдеров. Не устанавливает 4K-паки и не меняет user.ltx или MCM. Результат на других версиях SSS не проверен.'),
 ('yantar-hunter','1012- FLX Yantar Hunter Trader','Калибр: снабженец Янтаря','Персонажи и снаряжение','Торговец противомутантными боеприпасами с пятью ступенями репутации.',['dltx','hf','hf-expansion','hf-more'], 'Ассортимент рассчитан на текущую баллистику GAMMA; для чистой Anomaly не заявлен.'),
 ('artefact-weight-fix','1013- FLX Artefact Weight Fix','Фикс веса артефактов','Исправления','Выравнивает заданный вес секций артефактов через DLTX.',['dltx'], 'Установить после модов артефактов.'),
 ('yantar-guide','1014- FLX Yantar Guide','Ориентир: проводник Янтаря','Персонажи и снаряжение','Постоянный проводник с восемью платными маршрутами и подтверждением оплаты.',['dltx','hf','hf-expansion','hf-more'], 'Поддержка существующих сохранений предусмотрена модулем.'),
 ('npc-arsenal','1015- FLX NPC Arsenal','Арсенал NPC','Мир и баланс','Вооружение NPC по рангу, броне и фракции; миграция подходящих существующих NPC.',[], 'Меняет оружие обычных NPC с сохранением результата. Резервная копия сейва обязательна для отката изменений.'),
 ('qaw-food-meds','999- FLX QAW Auto Food Meds','Колесо еды и медикаментов','Интерфейс и удобство','Автозаполнение QAW едой и медициной.',['qaw'], 'Отключить G.A.M.M.A. Quick Action Wheel Balance; базовый Quick Action Wheel оставить включённым.'),
 ('career-ranks','Duty and Military Career Ranks - FLX','Звания и научные должности','Мир и баланс','Карьерные приставки для Долга, военных и учёных.',[], 'RU/EN. Сохраняет отдельные шкалы фракций.'),
 ('scrounger-perk','FLX Scrounger Perk','Навык «Падальщик»','Мир и баланс','Пятый навык Haruka: опыт за находки и улучшение состояния отдельных деталей.',['skills'], 'FLX Skill Perks необязателен. Не улучшает оружие целиком.'),
 ('skill-perks','FLX Skill Perks','Полезные эффекты навыков','Мир и баланс','Пассивные эффекты и множители опыта по уровням навыков.',['skills','mcm','gamma-recoil'], 'Первая тестовая версия. Содержит override Enhanced Recoil текущей GAMMA.'),
 ('footsteps-config','NPC Audible Footsteps - Flixmo','Шаги NPC: конфигурация Oleh','Графика и звук','Выделенная настройка step_params исходного конфига Oleh.',[], 'Исходный автор oleh5230. Старый вариант; не является восстановленной звуковой частью Fireteam.'),
 ('taskboard','Taskbord edt by flx','Taskboard: редакция FLX','Интерфейс и удобство','Группировка заданий, накопительные бонусы, метки и настраиваемая сдача.',['mcm'], 'Основа — iTheon PDA Taskboard. Установить после оригинального Taskboard и его патчей.'),
 ('campfire-rest','Chiki-Briki Campfire Rest','Отдых у костра','Мир и баланс','Посадка у костра, плавная камера и интеграция лечения.',['lnct'], 'Ctrl+V; MCM для настроек необязателен. Включает override LNCT Campfire Healing.'),
 ('rf-frequency-plus','RF-Частота+','RF-Частота+','Интерфейс и удобство','Активные частоты заданий и районы поиска в подсказке ресивера.',[], 'RF-задания берутся из установленной GAMMA; собственных заданий не создаёт.'),
 ('audible-footsteps','Audible NPC Footsteps Plus','Слышимые шаги врагов','Графика и звук','Пространственный звук движущихся врагов из звуковой части Fireteam.',['gamma-footsteps'], 'Не включать вместе с полным Fireteam AI; дополнительные шаги могут суммироваться с обычными.'),
 ('merramun-casino','1001- WTTG3 Merramun PDA Slots','Merramun: ноутбук-казино','Персонажи и снаряжение','Каскадный слот на ноутбуке в бункере учёных.',['dltx'], 'Взята установленная версия. Использует изображения и звуки Welcome to the Game III; авторы оригинала сохраняются.'),
 ('nasoska-photo','Ycatan_ - Nasoska Photo','Ycatan_: фотография','Персонажи и снаряжение','Отдельная замена фотографии и её иконки.',['dltx'], 'Персональный мод для Ycatan_; материал пользователя. Необязательный компонент.'),
 ('personal-radio','1000- FLX Personal PDA Radio','Личное радио КПК','Графика и звук','Личный плейлист, сохранение трека и состояния, импортёр музыки.',[], 'Музыка и FFmpeg не включены. Импортёр: Python 3.10+ с Tk и FFmpeg. Импортировать свои треки до запуска игры. PDA Radio Extended не требуется: звуки интерфейса берутся из Anomaly.'),
]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def run(gamma):
    mods=gamma/'mods'
    if (ROOT/'modules').exists():
        raise SystemExit('modules/ already exists; use a fresh checkout for capture (never overwrites).')
    captured=[]; audit=[]
    for mid, folder, title, group, description, requires, notes in CATALOG:
        source=mods/folder
        if not (source/'gamedata').is_dir():
            raise FileNotFoundError(source)
        dest=ROOT/'modules'/mid
        version='1.0.0'
        if (source/'meta.ini').is_file():
            cfg=configparser.ConfigParser(interpolation=None,strict=False)
            cfg.read(source/'meta.ini',encoding='utf-8-sig')
            version=cfg.get('General','version',fallback=version)
        if mid=='npc-arsenal': version='1.1.1'
        if mid=='zone-field-gear': version='0.7.1'
        if mid=='taskboard': version='2026.10.25'
        if mid=='scrounger-perk': version='0.1.0'
        for f in sorted((source/'gamedata').rglob('*')):
            if not f.is_file() or f.suffix=='.disabled': continue
            if mid=='personal-radio' and 'sounds' in f.relative_to(source).parts: continue
            target=dest/f.relative_to(source)
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(f,target)
            audit.append({'module':mid,'source_folder':folder,'path':f.relative_to(source).as_posix(),'sha256':digest(target),'bytes':target.stat().st_size})
        for f in source.iterdir():
            if f.is_file() and (f.name.lower().startswith(('readme','license','copying','lore_sources'))):
                target=dest/'upstream-docs'/f.name
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(f,target)
        if mid=='personal-radio':
            shutil.copyfile(source/'FLX Radio Importer.py',dest/'FLX Radio Importer.py')
        captured.append(dict(id=mid,title=title,group=group,version=version,description=description,requires=['gamma']+requires,notes=notes,default=False,author='@Flixmo',source_folder=folder))
    # Recover proven fixes made in existing addon folders / MO2 overwrite.
    scopes=mods/'410- 3DSS for GAMMA - Redotix99 & Andtheherois & party50'
    fixes=[('laser-fix','Лазеры: исправление шейдеров',['laser-settings','sss'],gamma/'overwrite',
        [f'gamedata/shaders/r3/models_laserbeam{x}' for x in ['.ps','.vs','.s','_dot.ps','_dot.vs']]),
       ('reticle-fix','Ракурс и 1П76: исправление сеток',['3dss','mark-switch'],scopes,
        ['gamedata/shaders/r3/models_reflex_reticle.vs','gamedata/shaders/r3/models_reflex_reticle_3db.vs','gamedata/configs/mod_system_z_markswitch_sights.ltx'])]
    for mid,title,requires,source,files in fixes:
        for rel in files:
            f=source/rel; target=ROOT/'modules'/mid/rel
            target.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(f,target)
            audit.append({'module':mid,'source_folder':source.name,'path':rel,'sha256':digest(target),'bytes':target.stat().st_size})
        captured.append(dict(id=mid,title=title,group='Исправления',version='1.0.0',description=title+'. Совместимые файлы из исправленной локальной установки.',requires=['gamma']+requires,notes='DX11/r3. Проверять с той же версией базовых шейдеров. Диагностические скрипты и кэш не включены.',default=False,author='@Flixmo',source_folder=source.name))
    # Preserve inactive/superseded work without enabling it as a functioning addon.
    for folder in ['1001- FLX Relations Reset','ocrea_']:
        source=mods/folder
        for f in (source/'gamedata').rglob('*'):
            if f.is_file() and 'sounds' not in f.relative_to(source).parts:
                target=ROOT/'archive'/folder/f.relative_to(source)
                target.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(f,target)
    # Portable sources only. Never copy saved mod lists, logs, backups, PDBs or obj/bin.
    for name in ['Custom-Mods.ps1','1_SAVE_before_GAMMA_update.cmd','2_RESTORE_after_GAMMA_update.cmd','README_RU.txt']:
        target=ROOT/'utilities'/'CustomMods'/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(gamma/'_tools'/'CustomMods'/name,target)
    for name in ['Program.cs','SaveReset.csproj','global.json']:
        target=ROOT/'utilities'/'SaveReset'/'src'/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(gamma/'_tools'/'SaveReset'/'src'/name,target)
    shutil.copyfile(gamma/'_tools'/'SaveReset'/'README.txt',ROOT/'utilities'/'SaveReset'/'README-original.txt')
    write_json(ROOT/'pack.json',{'name':'BLACK SIGNAL','author':'@Flixmo','version':'0.1.0-rc.1','target':'S.T.A.L.K.E.R. Anomaly 1.5.3 / G.A.M.M.A. 0.9.5','modules':captured})
    write_json(ROOT/'docs'/'source-manifest.json',audit)
    print(f'Captured {len(captured)} modules, {len(audit)} game files, {sum(x["bytes"] for x in audit)/1048576:.1f} MiB')

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--gamma',type=Path,required=True)
    run(ap.parse_args().gamma.resolve())
