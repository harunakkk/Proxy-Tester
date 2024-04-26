@echo off
:loop
python Proxy_Searcher.py
timeout /t 3600 > nul
goto :loop
PAUSE