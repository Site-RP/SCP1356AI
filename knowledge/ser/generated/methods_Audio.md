# SER Methoden — Audio

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## Audio.IsLoaded
- Beschreibung: Returns true if a given audio clip has been loaded
- Argumente: clip name: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AudioMethods/Audio_IsLoadedMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Audio.IsPlaying
- Beschreibung: Checks if the audio player is playing anything.
- Argumente: speaker name: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AudioMethods/Audio_IsPlayingMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Audio.Load
- Beschreibung: Loads an audio file into the audio player.
- Argumente: file path: Text, clip name: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AudioMethods/Audio_LoadMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Audio.Play
- Beschreibung: Plays a loaded audio clip from a created speaker.
- Argumente: speaker name: Text, audio clip name: Text, loop?: Bool
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AudioMethods/Audio_PlayMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Audio.Stop
- Beschreibung: Plays a loaded audio clip from a created speaker.
- Argumente: speaker name: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AudioMethods/Audio_StopMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Speaker.CreateGlobal
- Beschreibung: Creates a speaker to play audio through.
- Argumente: speaker name: Text, volume: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AudioMethods/Speaker_CreateGlobalMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Speaker.CreateOnPosition
- Beschreibung: Creates a speaker in a specified XYZ position.
- Argumente: speaker name: Text, x: Float, y: Float, z: Float, volume: Float, min distance: Float, max distance: Float, is stereo: Bool
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AudioMethods/Speaker_CreateOnPositionMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Speaker.CreatePlayerAttached
- Beschreibung: Creates a speaker attached to a player to play audio through.
- Argumente: player to attach: Player, speaker name: Text, volume: Float, min distance: Float, max distance: Float, is stereo: Bool
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AudioMethods/Speaker_CreatePlayerAttachedMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Speaker.Destroy
- Beschreibung: Destroys a speaker.
- Argumente: speaker name: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AudioMethods/Speaker_DestroyMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Speaker.Exists
- Beschreibung: Returns true or false indicating if a speaker with the provided name exists.
- Argumente: speaker name: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AudioMethods/Speaker_ExistsMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
