# SER Methoden — Health

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## AddHume
- Beschreibung: Adds hume shield to players. Do not confuse this method with {nameof(SetHumeShieldMethod)}
- Argumente: players: Players, amount: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/HealthMethods/AddHumeMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Damage
- Beschreibung: Damages players.
- Argumente: players: Players, amount: Float, reason: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/HealthMethods/DamageMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Heal
- Beschreibung: Heals players. Doesn't exceed their max health.
- Argumente: players to heal: Players, amount: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/HealthMethods/HealMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Kill
- Beschreibung: Kills players.
- Argumente: players: Players, reason: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/HealthMethods/KillMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetAHP
- Beschreibung: Sets the amount of AHP for players.
- Argumente: players: Players, amount: Float, limit: Float, decay: Float, efficacy: Float, sustain: Duration, isPersistent: Bool
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/HealthMethods/SetAHPMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetHealth
- Beschreibung: Sets health for players.
- Argumente: players: Players, health: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/HealthMethods/SetHealthMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetHumeShield
- Beschreibung: Sets hume shield for players.
- Argumente: players: Players, amount: Float, limit: Float, regen rate: Float, regen cooldown: Duration
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/HealthMethods/SetHumeShieldMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetMaxHealth
- Beschreibung: Sets the max health of players.
- Argumente: players: Players, maxHealth: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/HealthMethods/SetMaxHealthMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetRegeneration
- Beschreibung: Adds health regeneration to players.
- Argumente: players: Players, regeneration rate: Float, regeneration duration: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/HealthMethods/SetRegenerationMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
