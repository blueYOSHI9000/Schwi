# Install SchwiRSS
## easy method
- download the source code (either via git or just the .zip)
- [Install python](https://www.python.org/downloads/)
	- Should already be installed by default on linux
- open `windows_install.bat` or `linux_install.sh` inside the `_install` folder
- done! you can now open `_windows_start.bat` or `_linux_start.sh` to start the bot
	- if this didn't work, use the commandline method below

## Commandline method
- download the source code (either via git or just the .zip)
- [Install python](https://www.python.org/downloads/)
	- Should already be installed by default on linux
- open commandline terminal
	- Windows: Press Win+R and enter `cmd`
	- Linux: Press Ctrl+Alt+T
- move to the folder SchwiRSS is in
	- copy the path SchwiRSS is in (something like `C:\Users\blueYOSHI\Documents\GitHub\SchwiRSS`)
	- Windows/Linux: type `cd ` and insert the path (note: some Linux terminals use Ctrl+Shift+V to paste)
		- final command should look something like this: `cd C:\Users\blueYOSHI\Documents\GitHub\SchwiRSS`
- type `py -V` - if it outputs something like `Python 3.8.3` it's good (try installing python again if your version is lower - though it'll likely still work anyway)
	- if it output nothing, something else or `Python 2.x.x` then try using a different command like `python -V` or `python3 -V`
		- if none of these work then try installing python again
	- Windows: if the command that worked is not `py` then `_windows_start.bat` has to be edited - simply open it in a text editor and replace `py` with whatever worked
	- Linux: if the command that worked is not `python3` then `_linux_start.sh` has to be edited - simply open it in a text editor and replace `python3` with whatever worked
- all subsequent mentions of `py` should be replaced with whatever worked for you (like `python` or `python3`)
- enter `py -m pip install -r requirements.txt` to install all required libraries SchwiRSS needs

This has only been tested on Windows, though it *should* work on other platforms as well.

# Run SchwiRSS on startup
## Windows
- open commandline (press Win+R, then enter `cmd`)
- enter `py -V` - if it outputs something like `Python 3.8.3` it's good
	- if that didn't work try entering `python -V` or `python3 -V`
- go to the "run_on_startup" folder
- rename `windows_run_on_startup.example.bat` to `windows_run_on_startup.bat` (it's suggested to duplicate the file first to keep the original)
- open `windows_run_on_startup.bat` and fill in the path on the 6th line (it should point to the folder 'main.py' and this readme is in - note: the folder, NOT the file)
	- the finished line would look something like this: `cd C:\Users\blueYOSHI\Documents\GitHub\SchwiRSS`
	- if the command that worked earlier was not `py -V` then it has to be replaced on the 8th line with whatever worked
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