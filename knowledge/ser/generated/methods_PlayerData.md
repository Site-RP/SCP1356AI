# SER Methoden — PlayerData

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## ClearPlayerData
- Beschreibung: Clears data associated with specified players
- Argumente: players: Players, key to clear: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerDataMethods/ClearPlayerDataMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## GetPlayerData
- Beschreibung: Gets player data from the key.
- Argumente: player: Player, key: Text, default value: AnyValue
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerDataMethods/GetPlayerDataMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## HasPlayerData
- Beschreibung: Checks if a given key has an associated value for a given player.
- Argumente: player: Player, key: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerDataMethods/HasPlayerDataMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetPlayerData
- Beschreibung: Associates a custom key with a value for a given player.
- Argumente: player: Player, key: Text, value to set: AnyValue
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerDataMethods/SetPlayerDataMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
