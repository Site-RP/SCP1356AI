# SER Methoden — PlayerValue

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## AmountOf
- Beschreibung: Returns the amount of players in a given player variable.
- Argumente: variable: Players
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerValueMethods/AmountOfMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Contains
- Beschreibung: Returns a true/false value indicating if the provided player is in the list.
- Argumente: player list: Players, searched player: Player
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerValueMethods/ContainsMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Except
- Beschreibung: Returns players from the original variable EXCEPT those that were present in other variables.
- Argumente: original players: Players, players to except: Players
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerValueMethods/ExceptMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Filter
- Beschreibung: Returns players which match the value for a given property.
- Argumente: players to filter: Players, player property to filter by: Enum<PlayerValue.PlayerProperty>, desired value of property: AnyValue
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerValueMethods/FilterMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Join
- Beschreibung: Returns all players that were provided from multiple player variables.
- Argumente: players: Players
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerValueMethods/JoinMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Overlapping
- Beschreibung: Checks if provided player variables have the exact same players.
- Argumente: first value: Players, other values: Players
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerValueMethods/OverlappingMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## ParsePlayers
- Beschreibung: Tries to parse the provided value to a player value.
- Argumente: input: AnyValue
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerValueMethods/ParsePlayersMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Take
- Beschreibung: Takes a specified amount of players from a player variable, lower or equal to the limit.
- Argumente: players: Players, limit: Int
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerValueMethods/TakeMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
