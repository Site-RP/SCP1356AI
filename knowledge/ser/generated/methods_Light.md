# SER Methoden — Light

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## DisableLights
- Beschreibung: Turns off lights for rooms.
- Argumente: rooms: Rooms, duration: Duration
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/LightMethods/DisableLightsMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## ResetLightColor
- Beschreibung: Resets the light color for rooms.
- Argumente: rooms: Rooms
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/LightMethods/ResetLightColorMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetLightColor
- Beschreibung: Sets the light color for rooms.
- Argumente: rooms: Rooms, color: Color, intensity: Float, transition duration: Duration
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/LightMethods/SetLightColorMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
