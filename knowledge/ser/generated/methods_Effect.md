# SER Methoden — Effect

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## ClearEffect
- Beschreibung: Removes the provided status effect from players.
- Argumente: players: Players, effect: EffectType
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/EffectMethods/ClearEffectMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## GiveEffect
- Beschreibung: Adds a provided effect for specified players.
- Argumente: players: Players, effect: EffectType, duration: Duration, intensity: Int, add duration if active: Bool
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/EffectMethods/GiveEffectMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## HasEffect
- Beschreibung: Returns true or false indicating if the player has the provided effect.
- Argumente: player: Player, effect: EffectType
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/EffectMethods/HasEffectMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
