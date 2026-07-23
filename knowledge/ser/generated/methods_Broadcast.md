# SER Methoden — Broadcast

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## AnimatedBroadcast
- Beschreibung: Sends an animated broadcast to specified players.
- Argumente: players: Players, duration: Duration, content: Text, line break length: Int
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/BroadcastMethods/AnimatedBroadcastMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Broadcast
- Beschreibung: Sends a broadcast to players.
- Argumente: players: Players, duration: Duration, message: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/BroadcastMethods/BroadcastMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## ClearBroadcasts
- Beschreibung: Clears broadcasts for players.
- Argumente: players: Players
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/BroadcastMethods/ClearBroadcastsMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## ClearCountdown
- Beschreibung: Removes an active countdown for players if one is active.
- Argumente: players: Players
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/BroadcastMethods/ClearCountdownMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Countdown
- Beschreibung: Creates a countdown using broadcasts.
- Argumente: players: Players, duration: Duration, title: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/BroadcastMethods/CountdownMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Hint
- Beschreibung: Sends a hint to players.
- Argumente: players: Players, duration: Duration, message: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/BroadcastMethods/HintMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
