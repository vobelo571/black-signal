@echo off
chcp 65001 >nul
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Custom-Mods.ps1" -Action Save
if errorlevel 1 pause
