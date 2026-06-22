@echo off
cd /d "C:\Users\IDG2601\Documents\Claude Agents"
echo [%date% %time%] Running Wishlist daily capture... >> output\wishlist_tracker_log.txt
python scripts\steam_wishlist_tracker.py --mode daily >> output\wishlist_tracker_log.txt 2>&1
echo [%date% %time%] Daily capture done. >> output\wishlist_tracker_log.txt
