# SER Methoden — Database

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## DB.Add
- Beschreibung: Adds or overwrites a key-value pair into the database.
- Argumente: database: Database, key: Text, value: AnyValue
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DatabaseMethods/DB_AddMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## DB.Contains
- Beschreibung: Returns true if the provided key exists in the database.
- Argumente: database: Database, key: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DatabaseMethods/DB_ContainsMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## DB.Create
- Beschreibung: Creates a new JSON file in the database folder.
- Argumente: name: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DatabaseMethods/DB_CreateMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## DB.Exists
- Beschreibung: Returns true if the provided database exists.
- Argumente: database name: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DatabaseMethods/DB_ExistsMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## DB.Get
- Beschreibung: Returns the value of a given key in the database.
- Argumente: database: Database, key: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DatabaseMethods/DB_GetMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## DB.Remove
- Beschreibung: Removes a key from a database.
- Argumente: database: Database, key: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DatabaseMethods/DB_RemoveMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
