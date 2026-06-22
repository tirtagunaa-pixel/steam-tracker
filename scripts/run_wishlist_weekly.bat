@echo off
cd /d "C:\Users\IDG2601\Documents\Claude Agents"
echo [%date% %time%] Running Wishlist weekly report... >> output\wishlist_tracker_log.txt
python scripts\steam_wishlist_tracker.py --mode weekly >> output\wishlist_tracker_log.txt 2>&1
echo [%date% %time%] Weekly report done. >> output\wishlist_tracker_log.txt
