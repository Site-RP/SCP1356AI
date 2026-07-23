# SER Methoden — Output

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## Error
- Beschreibung: Sends an error message.
- Argumente: error: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/OutputMethods/ErrorMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Print
- Beschreibung: Prints the text provided to the server console.
- Argumente: text: Text, color: Enum<ConsoleColor>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/OutputMethods/PrintMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Reply
- Beschreibung: Sends a message to the place where the script was run from.
- Argumente: message: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/OutputMethods/ReplyMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
