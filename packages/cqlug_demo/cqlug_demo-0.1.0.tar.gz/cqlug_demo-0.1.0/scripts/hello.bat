ECHO OFF

REM Used to help execute because windows is trivially fixated 
REM on extensions.
REM
REM An alternative way is described on the python windows faq
REM but I have not tested yet.
REM 
REM - Create xxx.cmd
REM - Insert the following line at the top
REM
REM @setlocal enableextensions & python -x %~f0 %* & goto :EOF

set DIR=%~dp0
python %DIR%\hello %*
