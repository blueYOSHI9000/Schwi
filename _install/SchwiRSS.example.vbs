'replace the path on the 5th line so it points to the 'windows_run_on_startup.bat' script
'open the "README.md" file in a text editor to see more detailed instructions
'
Set WshShell = CreateObject("WScript.Shell") 
WshShell.Run chr(34) & "C:\REPLACE_THIS_PATH\SchwiRSS\run_on_startup\windows_run_on_startup.bat" & Chr(34), 0
Set WshShell = Nothing