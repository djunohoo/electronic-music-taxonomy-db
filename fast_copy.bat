@echo off
REM Optimized Music Collection Copy Script
REM Replace SOURCE_PATH and DEST_PATH with your actual paths

echo Starting optimized music collection copy...
echo.

REM Create destination directory if needed
if not exist "DEST_PATH" mkdir "DEST_PATH"

REM Robocopy with optimal settings for music files
robocopy "SOURCE_PATH" "DEST_PATH" /E /COPYALL /MT:16 /R:2 /W:5 /TEE /LOG:music_copy.log

echo.
echo Copy complete! Check music_copy.log for details.
echo.
pause
