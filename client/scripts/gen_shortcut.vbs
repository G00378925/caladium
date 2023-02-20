Set WShell = WScript.CreateObject("WScript.Shell")
Set shortcut = WShell.CreateShortcut(WShell.SpecialFolders("Desktop") & "\Caladium.lnk")

shortcut.TargetPath = WShell.ExpandEnvironmentStrings("%ProgramFiles%") & "\Caladium\caladium.exe"
shortcut.Save()