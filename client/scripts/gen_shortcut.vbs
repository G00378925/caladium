Set WShell = WScript.CreateObject("WScript.Shell")

' Function to create a short to caladium
Function CreateCaladiumShortcut(lnkLocation)
    Set shortcut = WShell.CreateShortcut(lnkLocation)
    shortcut.TargetPath = WShell.ExpandEnvironmentStrings("%ProgramFiles%") & "\Caladium\caladium.exe"
    shortcut.Save()
End Function

' Create shortcut on the users desktop
CreateCaladiumShortcut(WShell.SpecialFolders("Desktop") & "\Caladium.lnk")
' Create shortcut in the startup folder, so it starts on boot
CreateCaladiumShortcut(WShell.ExpandEnvironmentStrings("%ProgramData%") & "\Microsoft\Windows\Start Menu\Programs\Startup\Caladium.lnk")
