@echo off
rem Salva e desliga jogo, login, banco e painel.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\parar.ps1"
