# Run SchwiRSS on startup
## Windows
- go to the "run_on_startup" folder
- rename `windows_run_on_startup.example.bat` to `windows_run_on_startup.bat` (it's suggested to duplicate the file first to keep the original)
- open `windows_run_on_startup.bat` and fill in the path on the 6th line (it should point to the folder 'main.py' and this readme is in - note: the folder, NOT the file)
	- the finished line would look something like this: `cd C:\Users\blueYOSHI\Documents\GitHub\SchwiRSS`
- rename `SchwiRSS.example.vbs` to `SchwiRSS.vbs` (it's suggested to duplicate the file first to keep the original)
- open `SchwiRSS.vbs` and edit the path on the 5th line so it points to the `windows_run_on_startup.bat` file we edited earlier
	- the finished line would look something like this: `WshShell.Run chr(34) & "C:\Users\blueYOSHI\Documents\GitHub\SchwiRSS\run_on_startup\windows_run_on_startup.bat" & Chr(34), 0`
- then move `SchwiRSS.vbs` to the windows startup directory - there are two of those, one which executes the script for every user and one that only executes it for the current user
	- to add it for all users, move it here: `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp`
	- to only add it for the current user, move it here: `C:\Users\[User Name]\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup` (don't forget to replace `[User Name]`)
- now SchwiRSS should run automatically on each startup

### Why do we need 2 files for this?/What exactly am I doing here?
The core file here is `SchwiRSS.vbs` which, if setup correctly, is found in Windows' startup directory. Windows always checks that startup directory and executes every program in it. I don't know the specifics of the file itself since I found it [here](https://www.winhelponline.com/blog/run-bat-files-invisibly-without-displaying-command-prompt/) but it basically executes a program/script (which is `windows_run_on_startup.bat`) in the background without a visible commandline window being opened. We can't run the bot in it directly since it's important that the bot is ran in the correct directory (which can't be done in `SchwiRSS.vbs`), that's why we use `windows_run_on_startup.bat` which simply changes the directory using `cd` and then starts the bot with `py main.py`.

## (somewhat) Important info
If the bot is run on startup with the instructions here then there won't be a visible window anywhere, so the only way to close it (without having to find the exact task) is via discord commands:
- Use `schwi.kill` to shut it down
- Use `schwi.restart` to restart it

Note: Only owners can do this so make sure the correct owner ID was entered in config.json.
Instead of using the `schwi.` prefix (or whatever prefix is used) it's also possible to simply @ the bot.

Also, if the bot suddenly stopped responding, chances are it silently crashed (which hopefully never happens).