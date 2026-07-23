# SER Methoden — Discord

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## Discord.CreateMessage
- Beschreibung: Creates a discord message object.
- Argumente: message content: Text, sender name: Text, sender avatar url: Text, embeds: Reference<Embed_CreateMethod.DEmbed>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DiscordMethods/Discord_CreateMessageMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Discord.DeleteMessage
- Beschreibung: Deletes a message sent by a discord webhook (with that same webhook).
- Argumente: webhook url: Text, message id: Text, thread id: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DiscordMethods/Discord_DeleteMessageMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Discord.EditMessage
- Beschreibung: Edits a message sent by a discord webhook (with that same webhook).
- Argumente: webhook url: Text, message id: Text, message object: Reference<Discord_CreateMessageMethod.DMessage>, thread id: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DiscordMethods/Discord_EditMessageMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Discord.SendMessage
- Beschreibung: Sends a message using a discord webhook.
- Argumente: webhook url: Text, message object: Reference<Discord_CreateMessageMethod.DMessage>, thread id: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DiscordMethods/Discord_SendMessageMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Discord.SendMessageAndWait
- Beschreibung: Sends a message using a discord webhook and waits until it is completed. Returns the message id.
- Argumente: webhook url: Text, message object: Reference<Discord_CreateMessageMethod.DMessage>, thread id: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DiscordMethods/Discord_SendMessageAndWaitMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Embed.Create
- Beschreibung: Creates an embed which can later be sent to discord via webhook.
- Argumente: title: Text, description: Text, color: Color, author: Reference<Embed_CreateAuthorMethod.DEmbedAuthor>, footer: Reference<Embed_CreateFooterMethod.DEmbedFooter>, thumbnail url: Text, image url: Text, clickable url: Text, fields: Reference<Embed_CreateFieldMethod.DEmbedField>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DiscordMethods/Embed_CreateMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Embed.CreateAuthor
- Beschreibung: Creates an author object that can be used in discord embeds.
- Argumente: name: Text, icon url: Text, clickable url: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DiscordMethods/Embed_CreateAuthorMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Embed.CreateField
- Beschreibung: Creates a field object that can be used in discord embeds.
- Argumente: name: Text, value: Text, inline: Bool
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DiscordMethods/Embed_CreateFieldMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Embed.CreateFooter
- Beschreibung: Creates a footer that can be used in discord embeds.
- Argumente: content: Text, icon url: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DiscordMethods/Embed_CreateFooterMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
