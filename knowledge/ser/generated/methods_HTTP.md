# SER Methoden — HTTP

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## HTTP.Get
- Beschreibung: Sends a GET request to a provided URL and returns the response as a JSON object.
- Argumente: address: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/HTTPMethods/HTTP_GetMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## HTTP.Patch
- Beschreibung: Sends a PATCH request to a provided URL.
- Argumente: address: Text, json data to patch: Reference<JObject>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/HTTPMethods/HTTP_PatchMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## HTTP.Post
- Beschreibung: Sends a POST request to a provided URL.
- Argumente: address: Text, json data to post: Reference<JObject>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/HTTPMethods/HTTP_PostMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## JSON.Add
- Beschreibung: Adds a key-value pair to a JSON object.
- Argumente: JSON to add value to: Reference<JObject>, key: Text, value: Value<LiteralValue>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/HTTPMethods/JSON_AddMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## JSON.Create
- Beschreibung: Returns an empty JSON object.
- Argumente: keine
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/HTTPMethods/JSON_CreateMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## JSON.FormatToReadable
- Beschreibung: Returns the JSON object in a readable format.
- Argumente: JSON object: Reference<JObject>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/HTTPMethods/JSON_FormatToReadableMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## JSON.Parse
- Beschreibung: Parses a provided value into a JSON object.
- Argumente: string representation of JSON object: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/HTTPMethods/JSON_ParseMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
