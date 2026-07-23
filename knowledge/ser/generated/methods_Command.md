# SER Methoden — Command

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## Command
- Beschreibung: Runs a server command with full permission.
- Argumente: command: Text, sender: Player
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CommandMethods/CommandMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## ResetGlobalCommandCooldown
- Beschreibung: Resets the global command cooldown for the 'CustomCommand' flag.
- Argumente: command: Reference<CustomCommandFlag.CustomCommand>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CommandMethods/ResetGlobalCommandCooldownMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## ResetPlayerCommandCooldown
- Beschreibung: Resets a player's command cooldown from the 'CustomCommand' flag.
- Argumente: command: Reference<CustomCommandFlag.CustomCommand>, players: Players
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CommandMethods/ResetPlayerCommandCooldownMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
