@echo off
cd /d "%~dp0"

where py
where python

echo.
echo Tentando iniciar a Nora...
echo.

py nora.pyw

echo.
echo Se apareceu algum erro, mande ele aqui.
pause