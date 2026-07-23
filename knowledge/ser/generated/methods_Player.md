# SER Methoden — Player

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## Ban
- Beschreibung: Bans players from the server.
- Argumente: players: Players, duration: Duration, reason: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/BanMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Explode
- Beschreibung: Explodes players.
- Argumente: players: Players
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/ExplodeMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## GetAmmoLimit
- Beschreibung: Gets the player's limit on a certain ammunition type
- Argumente: player to get the limit from: Player, ammo type: Enum<AmmoType>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/GetAmmoLimitMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## GetIPInfo
- Beschreibung: Fetches information about a provided player IP address using ProxyCheck.io.
- Argumente: player: Player, apiKey: Text
- Aliases: Fetches information about a provided player IP address using ProxyCheck.io.
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/GetIPInfoMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## HasPermission
- Beschreibung: Checks if a player has a specific permission.
- Argumente: player: Player, permissions: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/HasPermissionMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Jump
- Beschreibung: Makes players jump (with modifiable jump strength).
- Argumente: players: Players, jump strength: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/JumpMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Kick
- Beschreibung: Kicks players from the server.
- Argumente: players: Players, reason: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/KickMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Mute
- Beschreibung: Mutes specified players.
- Argumente: players: Players, is temporary: Bool
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/MuteMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## ResetMute
- Beschreibung: Resets mute status for specified players.
- Argumente: players: Players, revoke permament: Bool
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/ResetMuteMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetAmmoLimit
- Beschreibung: Sets the players' limit on a certain ammunition type
- Argumente: players to set the limit to: Players, ammo type: Enum<AmmoType>, limit: Int
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/SetAmmoLimitMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetAppearance
- Beschreibung: Changes the appearance of a player (or reskins)
- Argumente: players whose appearance will be changed: Players, role to change appearance to: Enum<RoleTypeId>, players who will see the change: Players
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/SetAppearanceMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetBypass
- Beschreibung: Grants or removes bypass mode for players.
- Argumente: players: Players, mode: Bool
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/SetBypassMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetCustomInfo
- Beschreibung: Sets custom info (overhead text) for specific players.
- Argumente: playersToAffect: Players, customInfoText: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/SetCustomInfoMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetDisplayName
- Beschreibung: Sets display name for specified players
- Argumente: players: Players, display name: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/SetDisplayNameMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetEmote
- Beschreibung: Sets emotion for specified players
- Argumente: players: Players, emotion: Enum<EmotionPresetType>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/SetEmoteMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetGodMode
- Beschreibung: Enables or disables godmode for specified players.
- Argumente: players: Players, mode: Bool
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/SetGodModeMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetGravity
- Beschreibung: Changes player gravity.
- Argumente: players: Players, gravity: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/SetGravityMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetGroup
- Beschreibung: Sets or removes group from specified players
- Argumente: players: Players, group: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/SetGroupMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetNoclip
- Beschreibung: Enables or disables access to noclip for specified players.
- Argumente: players: Players, isAllowed: Bool
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/SetNoclipMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetRole
- Beschreibung: Sets a role for players.
- Argumente: players: Players, newRole: Enum<RoleTypeId>, spawnFlags: Enum<RoleSpawnFlags>, reason: Enum<RoleChangeReason>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/SetRoleMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetShownPlayerInfo
- Beschreibung: Sets what information about the player is shown.
- Argumente: players: Players, info to show: Enum<PlayerInfoArea>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/SetShownPlayerInfoMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetSize
- Beschreibung: Sets the size of players.
- Argumente: players: Players, x size: Float, y size: Float, z size: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/SetSizeMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetSpectatability
- Beschreibung: Allows or disallows a player to be spectated.
- Argumente: players: Players, new state: Bool
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/SetSpectatabilityMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Show
- Beschreibung: Formats provided players into a nice text representation.
- Argumente: players: Players, property: Enum<PlayerValue.PlayerProperty>, separator: Text, separator on beginning: Bool
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/ShowMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## ShowHitMarker
- Beschreibung: Shows a hit marker to players.
- Argumente: players: Players, hitmarker size: Float, should play audio: Bool, hitmarker type: Enum<HitmarkerType>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/ShowHitMarkerMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Stamina
- Beschreibung: Control the stamina of players.
- Argumente: options: Options, players: Players, stamina value: Float, delay stamina regen: Bool
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PlayerMethods/StaminaMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
