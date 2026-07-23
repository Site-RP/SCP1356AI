# SER Methoden — TeslaRule

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## AddTeslaIgnoreRule
- Beschreibung: Sets the players that will be ignored by a tesla.
- Argumente: players: Players, remove id: Text, update: Bool
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/TeslaRuleMethods/AddTeslaIgnoreRuleMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## RemoveTeslaIgnoreRule
- Beschreibung: Resets the list of players ignored by a tesla.
- Argumente: id to remove: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/TeslaRuleMethods/RemoveTeslaIgnoreRuleMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
