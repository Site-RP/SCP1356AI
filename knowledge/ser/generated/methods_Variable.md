# SER Methoden — Variable

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## GetVariableByName
- Beschreibung: Returns the value of a variable with the given name and prefix.
- Argumente: variable name: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/VariableMethods/GetVariableByNameMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## GlobalVariables
- Beschreibung: Returns a collection containing all the global variable names
- Argumente: keine
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/VariableMethods/GlobalVariablesMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## LogVar
- Beschreibung: Returns a formatted version of the variable for logging purposes.
- Argumente: variable: Variable
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/VariableMethods/LogVarMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## VarExists
- Beschreibung: Returns a bool value indicating if the provided variable exists.
- Argumente: variable: Token<VariableToken>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/VariableMethods/VarExistsMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
