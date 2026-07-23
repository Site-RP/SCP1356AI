# SER Methoden — Script

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## IsRunning
- Beschreibung: Returns true if given script is running
- Argumente: script name: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ScriptMethods/IsRunningMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## RunFunc
- Beschreibung: Runs a function script with arguments.
- Argumente: script to run: CreatedScript, values to pass: AnyValue
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ScriptMethods/RunFuncMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## RunScript
- Beschreibung: Runs a script.
- Argumente: script to create: CreatedScript, variables to pass: Variable
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ScriptMethods/RunScriptMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## RunScriptAndWait
- Beschreibung: Runs a script and waits until the ran script has finished.
- Argumente: script to create: CreatedScript, variables to pass: Variable
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ScriptMethods/RunScriptAndWaitMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## ScriptExists
- Beschreibung: Returns true or false indicating if a script with the provided name exists.
- Argumente: script name: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ScriptMethods/ScriptExistsMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## StopScript
- Beschreibung: Stops a given script.
- Argumente: running script: RunningScript
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ScriptMethods/StopScriptMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## ThisInfo
- Beschreibung: Returns info about the current script
- Argumente: info to receive: Options
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ScriptMethods/ThisInfoMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## TransferVariables
- Beschreibung: Makes a copy of the given local variable(s) in a different script.
- Argumente: target script: RunningScript, variables: Variable
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ScriptMethods/TransferVariablesMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Trigger
- Beschreibung: Fires a given trigger, executing scripts which are attached to it.
- Argumente: trigger name: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ScriptMethods/TriggerMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
