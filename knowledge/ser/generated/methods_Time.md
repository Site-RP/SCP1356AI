# SER Methoden — Time

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## Date.Current
- Beschreibung: Returns the current date.
- Argumente: time zone: Options
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/TimeMethods/Date_CurrentMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Date.Offset
- Beschreibung: Adds an offset to a date.
- Argumente: date: Reference<DateTime>, mode: Options, offset: Duration
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/TimeMethods/Date_OffsetMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## FormatDuration
- Beschreibung: Formats a duration into a special format.
- Argumente: duration to format: Duration, format: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/TimeMethods/FormatDurationMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## TimeInfo
- Beschreibung: Returns information about current time.
- Argumente: options: Options
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/TimeMethods/TimeInfoMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## ToDuration
- Beschreibung: Creates a duration value from a number and a unit.
- Argumente: length: Float, unit: Enum<DurationUnit>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/TimeMethods/ToDurationMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
