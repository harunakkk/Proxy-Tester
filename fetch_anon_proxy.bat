@echo off
:loop
echo Proxy Searching
python Proxy_Searcher.py
timeout /t 3600 > nul
goto :loop
PAUSE