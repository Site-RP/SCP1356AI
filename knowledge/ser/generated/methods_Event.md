# SER Methoden — Event

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## AddEventHandler
- Beschreibung: Adds an event handler to the provided event.
- Argumente: event name: Event, callback: Callback
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/EventMethods/AddEventHandlerMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## DisableEvent
- Beschreibung: Disables the provided event from running.
- Argumente: eventName: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/EventMethods/DisableEventMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## EnableEvent
- Beschreibung: Enables the provided event to run after being disabled.
- Argumente: eventName: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/EventMethods/EnableEventMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## IsAllowed
- Beschreibung: Sets whether or not the event is allowed to run.
- Argumente: isAllowed: Bool
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/EventMethods/IsAllowedMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
