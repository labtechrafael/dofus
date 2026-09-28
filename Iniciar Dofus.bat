@echo off
rem Liga o painel (se preciso), o banco, o login e o jogo, e abre o painel no navegador.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\iniciar.ps1"
