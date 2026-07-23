# SER Methoden — Config

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## Config.GetOption
- Beschreibung: Tries to get a value from a config.
- Argumente: config: Reference<CustomConfig>, keys: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ConfigMethods/Config_GetOptionMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Config.Read
- Beschreibung: Reads and returns a config.
- Argumente: config name: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ConfigMethods/Config_ReadMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
