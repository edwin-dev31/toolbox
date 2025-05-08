@echo off
setlocal EnableDelayedExpansion

:: Ask for subject name
set /p subject=Enter the subject name:

:: Ask for number of weeks
set /p weeks=Enter the number of weeks:

:: Create subject folder
mkdir "%subject%"

:: Create week folders inside the subject folder
for /L %%i in (1,1,%weeks%) do (
    set "num=0%%i"
    set "num=!num:~-2!"
    mkdir "%subject%\!num!_WEEK"
)

echo Folders created successfully.
pause
