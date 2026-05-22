Set fso = CreateObject("Scripting.FileSystemObject")
Set WshShell = CreateObject("WScript.Shell")

' Lay duong dan thu muc hien tai cua file script
strPath = fso.GetParentFolderName(WScript.ScriptFullName)

' Thiet lap thu muc lam viec de dam bao duong dan tuong doi chinh xac
WshShell.CurrentDirectory = strPath

' Chay file RUN_APP.bat voi che do an hoan toan (0)
WshShell.Run chr(34) & strPath & "\RUN_APP.bat" & chr(34), 0

Set WshShell = Nothing
