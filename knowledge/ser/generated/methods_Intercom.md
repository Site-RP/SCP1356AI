# SER Methoden — Intercom

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## IntercomInfo
- Beschreibung: Returns info about the Intercom.
- Argumente: mode: Options
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/IntercomMethods/IntercomInfoMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetIntercomState
- Beschreibung: Sets the state of usage of the intercom.
- Argumente: state: Enum<IntercomState>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/IntercomMethods/SetIntercomStateMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetIntercomText
- Beschreibung: Sets the text on the Intercom.
- Argumente: text: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/IntercomMethods/SetIntercomTextMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
