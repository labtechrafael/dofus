@echo off
rem Instala tudo: Java, MariaDB, Gradle, JPEXS, servidor StarLoco, banco, painel e o Mundo LabTech.
rem Antes, coloque o cliente Dofus Retro 1.39.8 em server\client-starloco (veja o README).
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\instalar.ps1"
pause
