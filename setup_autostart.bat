@echo off
echo ���� BreakReminder ����������...

:: ��ȡ��ǰĿ¼
set "CURRENT_DIR=%~dp0"
set "EXE_PATH=%CURRENT_DIR%dist\BreakReminder\BreakReminder.exe"

:: ��������������ݷ�ʽ
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = oWS.SpecialFolders("Startup") ^& "\BreakReminder.lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "%EXE_PATH%" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%CURRENT_DIR%dist\BreakReminder" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"
cscript //nologo "%TEMP%\CreateShortcut.vbs"
del "%TEMP%\CreateShortcut.vbs"

echo ��ɣ�BreakReminder �����´�����ϵͳʱ�Զ����С�
pause
