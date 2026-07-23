# SER Methoden — Dictionary

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## Dict.Add
- Beschreibung: Adds a key-value pair to a dictionary.
- Argumente: dictionary: Reference<Dict>, key: AnyValue, value: AnyValue
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DictionaryMethods/Dict_AddMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Dict.Contains
- Beschreibung: Returns true if the dictionary contains the provided key
- Argumente: dictionary: Reference<Dict>, key: AnyValue
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DictionaryMethods/Dict_ContainsMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Dict.Create
- Beschreibung: Creates an empty dictionary.
- Argumente: keine
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DictionaryMethods/Dict_CreateMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Dict.Get
- Beschreibung: Gets a value associated with a key from a dictionary.
- Argumente: dictionary: Reference<Dict>, key: AnyValue
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DictionaryMethods/Dict_GetMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Dict.Remove
- Beschreibung: Removes a key-value pair from a dictionary.
- Argumente: dictionary: Reference<Dict>, key to remove: AnyValue
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DictionaryMethods/Dict_RemoveMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
