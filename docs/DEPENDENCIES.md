# Сторонние зависимости

Не входят в дистрибутив BLACK SIGNAL. В GAMMA большинство уже установлено. Проверяйте список именно выбранного модуля; xlibs и полный набор мебели не требуются каждому моду.

Референсные версии — снимок локального профиля, а не утверждение о самой новой версии.

| Зависимость | Автор | Ссылка | Примечание |
|---|---|---|---|
| G.A.M.M.A. / Anomaly 1.5.3 | Grokitach and the Anomaly team | [Страница автора](https://github.com/Grokitach/Stalker_GAMMA) | Целевая среда всех модулей — установленная GAMMA 0.9.5 из авторского профиля; отдельный ZIP означает независимую установку модуля, а не совместимость с чистой Anomaly. |
| Modded Exes / DLTX | themrdemonized and contributors | [Страница автора](https://github.com/themrdemonized/xray-monolith/releases) | Используйте совместимый движок из своей GAMMA. Не заменяйте EXE только ради этого пака. |
| Mod Configuration Menu (MCM) | RavenAscendant and contributors | [Страница автора](https://www.moddb.com/mods/stalker-anomaly/addons/anomaly-mod-configuration-menu) | В GAMMA уже установлен. Конфигурационное меню также требуется ряду базовых модов. |
| Grok’s Body Health System Redux | Grokitach | [Страница автора](https://www.moddb.com/mods/stalker-anomaly/addons/100-groks-body-health-system-redux-for-151) | Использовать с GAMMA Medications Balance своего профиля. |
| Anomaly Skill System | HarukaSai | [Страница автора](https://www.moddb.com/mods/stalker-anomaly/addons/anomaly-skill-system) | Нужны Skill System и баланс навыков GAMMA. Skills Expansion необязателен. |
| Quick Action Wheel | HarukaSai | [Страница автора](https://www.moddb.com/mods/stalker-anomaly/addons/quick-action-wheel) | Также требует свои исходные зависимости; отключить GAMMA Quick Action Wheel Balance при использовании FLX QAW. |
| Hideout Furniture | Aoldri | [Страница автора](https://www.moddb.com/mods/stalker-anomaly/addons/hideout-furniture-hf) | Базовая система мебели для зависимых дополнений. |
| Hideout Furniture Expansion | maidresidence, HarukaSai, Frogs, Raven | [Страница автора](https://www.moddb.com/mods/stalker-anomaly/addons/hideout-furniture-expansion) | Модели и секции декора, используемые сценами новых NPC. |
| Even More Hideout Furniture | facelessez | [Страница автора](https://www.moddb.com/mods/stalker-anomaly/addons/even-more-hideout-furniture) | Дополнительный декор сцен Янтаря; установить также базовую мебель. |
| Dux’s Innumerable Character Kit | DuxFortis | [Страница автора](https://www.moddb.com/mods/stalker-anomaly/addons/dick) | Нужен для используемых моделей персонажей Арены. |
| Screen Space Shaders | Ascii1457 | [Страница автора](https://www.moddb.com/mods/stalker-anomaly/addons/screen-space-shaders) | Референс — ScreenSpaceShaders_Update из текущей GAMMA. Графические правки рассчитаны на DX11/r3; произвольная версия с ModDB не считается проверенной. |
| 3D Shader Scopes for GAMMA | Redotix99, Andtheherois, party50 and contributors | [Страница автора](https://www.moddb.com/mods/stalker-anomaly/addons/3d-shader-scopes-for-gamma) | Базовые прицелы для патча сеток. |
| Mark Switch (GAMMA version) | party50, meowie, Andtheherois | [Страница автора](https://github.com/andtheherois/Mark-Switch-10-GAMMA-version) | Компонент текущей GAMMA; правка числа сеток относится к Ракурсу и 1П76. |
| Laser Settings | Borksy | [Страница автора](https://www.moddb.com/mods/stalker-anomaly/addons/laser-settings-v2-7) | База управления яркостью лазеров. |
| LNCT Campfire Healing (Vanilla & BHS) | lnct | [Страница автора](https://www.moddb.com/mods/stalker-anomaly/addons/lnct-campfire-healing) | Отдых у костра включает исправленный скрипт лечения, но требует настройки и прочие файлы LNCT. |
| G.A.M.M.A. Enhanced Recoil | Grokitach and contributors | [Страница автора](https://github.com/Grokitach/Stalker_GAMMA) | Внутренний компонент GAMMA; отдельная библиотека для скачивания не нужна. |
| G.A.M.M.A. Footsteps | GAMMA contributors; see installed addon credits | [Страница автора](https://github.com/Grokitach/Stalker_GAMMA) | Штатные default-сэмплы, используемые Audible NPC Footsteps Plus. |
| PDA Radio Extended | Starcry_; original player by Tronex | [Страница автора](https://www.moddb.com/mods/stalker-anomaly/addons/pda-radio-extended) | Не требуется для BLACK SIGNAL Personal Radio; справочная ссылка на исходный музыкальный аддон. Автор запрещает включение аддона в модпаки, его файлы и музыка не включены. |
| xlibs | damiansirbu-stalker and contributors | [Страница автора](https://www.moddb.com/mods/stalker-anomaly/addons/xlibs-1001) | Справочная ссылка для сторонних модов. Прямой обязательной зависимости доступных модулей BLACK SIGNAL от xlibs не выявлено; автоматически не устанавливается. |
| Python 3.10+ for Windows (with Tk) | Python Software Foundation and contributors | [Страница автора](https://www.python.org/downloads/windows/) | Только для исходного FLX Radio Importer.py и инструментов сборки, не для игровых скриптов. |
| FFmpeg | FFmpeg developers | [Страница автора](https://ffmpeg.org/download.html) | Только для конвертации своей музыки импортёром. Положить ffmpeg.exe рядом с импортёром или добавить в PATH. В пак не включён. |
| .NET 8 SDK | Microsoft and contributors | [Страница автора](https://dotnet.microsoft.com/download/dotnet/8.0) | Только для сборки SaveReset из исходников. Готовый self-contained SaveReset.exe отдельного .NET Runtime не требует. |
