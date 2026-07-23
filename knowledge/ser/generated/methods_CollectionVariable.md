# SER Methoden — CollectionVariable

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## Coll.Contains
- Beschreibung: Returns true if the value exists in the collection
- Argumente: collection: Collection, value to check: AnyValue
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CollectionVariableMethods/Coll_ContainsMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Coll.Create
- Beschreibung: Returns an empty collection.
- Argumente: keine
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CollectionVariableMethods/Coll_CreateMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Coll.Fetch
- Beschreibung: Returns a value from a collection variable at a given position.
- Argumente: collection: Collection, index: Int
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CollectionVariableMethods/Coll_FetchMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Coll.Insert
- Beschreibung: Adds a value to a collection variable
- Argumente: collection variable: CollectionVariable, value: AnyValue
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CollectionVariableMethods/Coll_InsertMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Coll.Join
- Beschreibung: Returns a collection that has the combined values of all the given collections
- Argumente: collections: Collection
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CollectionVariableMethods/Coll_JoinMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Coll.Remove
- Beschreibung: Removes a matching value from a collection variable
- Argumente: collection variable: CollectionVariable, value to remove: AnyValue, amount of matches to remove: Int
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CollectionVariableMethods/Coll_RemoveMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Coll.RemoveAt
- Beschreibung: Removes a value at the provided index from a collection variable
- Argumente: collection variable: CollectionVariable, index: Int
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CollectionVariableMethods/Coll_RemoveAtMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Coll.Subtract
- Beschreibung: Returns a collection that has the values of the first collection without the values of the latter
- Argumente: original collection: Collection, collections to remove values from: Collection
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CollectionVariableMethods/Coll_SubtractMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
