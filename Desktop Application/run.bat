@ECHO OFF

Rem THIS IS A COMMENT

Rem Below VBS code gives this script admin privilege on Windows
>NUL 2>&1 REG.exe query "HKU\S-1-5-19" || (
    ECHO SET UAC = CreateObject^("Shell.Application"^) > "%TEMP%\Getadmin.vbs"
    ECHO UAC.ShellExecute "%~f0", "%1", "", "runas", 1 >> "%TEMP%\Getadmin.vbs"
    "%TEMP%\Getadmin.vbs"
    DEL /f /q "%TEMP%\Getadmin.vbs" 2>NUL
    Exit /b
)

Rem cd to current directory
cd /d %~dp0

Rem Run the MQTT server.
start "" python mqtt_client_read.py

Rem Run the GUI
start "" python gui3.py
