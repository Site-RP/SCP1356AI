# SER Methoden — DamageRule

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## AddDamageRule
- Beschreibung: Sets the damage rule for a player.
- Argumente: mode: Options, players affected: Players, multiplier: Float, remove id: Text, update: Bool
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DamageRuleMethods/AddDamageRuleMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## RemoveDamageRule
- Beschreibung: Removes a given damage rule fro applying.
- Argumente: id to remove: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DamageRuleMethods/RemoveDamageRuleMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
