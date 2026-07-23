# SER Methoden — Callvote

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## Vote.CreateOption
- Beschreibung: Creates a vote option, which can be used in a vote.
- Argumente: option: Text, display text: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CallvoteMethods/Vote_CreateOptionMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Vote.Start
- Beschreibung: Starts a vote.
- Argumente: question: Text, player asking: Player, options: Reference<Vote_CreateOptionMethod.VoteOption>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CallvoteMethods/Vote_StartMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Vote.StartAndWait
- Beschreibung: Starts a vote and waits until it is completed.
- Argumente: question: Text, player asking: Player, options: Reference<Vote_CreateOptionMethod.VoteOption>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CallvoteMethods/Vote_StartAndWaitMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
