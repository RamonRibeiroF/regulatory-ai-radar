Option Explicit

Dim fileSystem
Dim shell
Dim scriptDirectory
Dim powershellScript
Dim command
Dim exitCode

' Step 1: create the required Windows automation objects.
Set fileSystem = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

' Step 2: locate the PowerShell script from this file.
scriptDirectory = fileSystem.GetParentFolderName( _
    WScript.ScriptFullName _
)

powershellScript = fileSystem.BuildPath( _
    scriptDirectory, _
    "run_scheduled_pipeline.ps1" _
)

' Step 3: build the hidden PowerShell execution command.
command = _
    "powershell.exe " & _
    "-NoProfile " & _
    "-ExecutionPolicy Bypass " & _
    "-File " & _
    Chr(34) & powershellScript & Chr(34)

' Step 4: run the pipeline invisibly and wait for completion.
exitCode = shell.Run( _
    command, _
    0, _
    True _
)

' Step 5: return the pipeline exit code to Task Scheduler.
WScript.Quit exitCode