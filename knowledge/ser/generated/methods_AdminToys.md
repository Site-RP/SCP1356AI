# SER Methoden — AdminToys

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## Toy.Create
- Beschreibung: Creates an Admin Toy
- Argumente: toy type: Options
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AdminToysMethods/Toy_CreateMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Toy.Destroy
- Beschreibung: Destroys an Admin Toy.
- Argumente: toy reference: Reference<AdminToy>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AdminToysMethods/Toy_DestroyMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Toy.Info
- Beschreibung: Returns information about an Admin Toy
- Argumente: toy reference: Reference<AdminToy>, property: Options
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AdminToysMethods/Toy_InfoMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Toy.Move
- Beschreibung: Moves an Admin Toy relative to its rotation.
- Argumente: toy reference: Reference<AdminToy>, x position: Float, y position: Float, z position: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AdminToysMethods/Toy_MoveMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Toy.SetParent
- Beschreibung: Sets the parent of a toy (So that the toy follows it).
- Argumente: toy reference: Reference<AdminToy>, parent type: Options, player parent: Player, toy parent: Reference<AdminToy>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AdminToysMethods/Toy_SetParentMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Toy.SetRotation
- Beschreibung: Sets the rotation of a toy.
- Argumente: toy reference: Reference<AdminToy>, rotation mode: Options, x rotation: Float, y rotation: Float, z rotation: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AdminToysMethods/Toy_SetRotationMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Toy.SetScale
- Beschreibung: Sets the scale of a toy.
- Argumente: toy reference: Reference<AdminToy>, scale mode: Options, x scale: Float, y scale: Float, z scale: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AdminToysMethods/Toy_SetScaleMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Toy.TPPlayer
- Beschreibung: Teleports an Admin Toy to a given player
- Argumente: toy reference: Reference<AdminToy>, player to teleport toy to: Player, align toy rotation to player?: Bool
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AdminToysMethods/Toy_TPPlayerMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Toy.TPPosition
- Beschreibung: Teleports an Admin Toy to the given absolute coordinates
- Argumente: toy reference: Reference<AdminToy>, mode: Options, x position: Float, y position: Float, z position: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AdminToysMethods/Toy_TPPositionMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Toy.TPRoom
- Beschreibung: Teleports an Admin Toy to the given room
- Argumente: toy reference: Reference<AdminToy>, room to teleport toy to: Room, relative x: Float, relative y: Float, relative z: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AdminToysMethods/Toy_TPRoomMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
