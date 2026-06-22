@echo off
cd /d "C:\Users\IDG2601\Documents\Claude Agents"
echo [%date% %time%] Running Steam Watch update... >> output\steam_watch_log.txt
python scripts\update_steam_watch.py >> output\steam_watch_log.txt 2>&1
echo [%date% %time%] Done. >> output\steam_watch_log.txt
