# SER Methoden — Text

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## Text.Contains
- Beschreibung: Returns true or false indicating if the provided text contains a provided value.
- Argumente: text: Text, text to check for: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/TextMethods/Text_ContainsMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Text.Pad
- Beschreibung: Fills the text from the left or right with the given character until the specified length is met
- Argumente: text to pad: Text, pad direction: Options, length: Int, character: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/TextMethods/Text_PadMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Text.Replace
- Beschreibung: Replaces given values in a given text.
- Argumente: value to perform the replacement on: Text, text to replace: Text, replacement text: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/TextMethods/Text_ReplaceMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Text.Slice
- Beschreibung: Slices off characters from beginning and end of a text value.
- Argumente: text: Text, beginning amount: Int, end amount: Int
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/TextMethods/Text_SliceMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Text.Trim
- Beschreibung: Trims the text value from whitspaces at the beginning and end.
- Argumente: text: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/TextMethods/Text_TrimMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
