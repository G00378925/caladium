Set WShell = WScript.CreateObject("WScript.Shell")

' This function creates a shortcut to caladium
Function CreateCaladiumShortcut(lnkLocation)
    Set shortcut = WShell.CreateShortcut(lnkLocation)
    ' Caladium is installed to "Program Files"
    shortcut.TargetPath = WShell.ExpandEnvironmentStrings("%ProgramFiles%") & "\Caladium\caladium.exe"
    shortcut.Save()
End Function

' Create shortcut on the public desktop
CreateCaladiumShortcut(WShell.ExpandEnvironmentStrings("%Public%") & "\Desktop\Caladium.lnk")
' Create shortcut in the startup folder, so it starts on boot
CreateCaladiumShortcut(WShell.ExpandEnvironmentStrings("%ProgramData%") & "\Microsoft\Windows\Start Menu\Programs\Startup\Caladium.lnk")
