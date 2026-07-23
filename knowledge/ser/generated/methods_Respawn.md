# SER Methoden — Respawn

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## GetWaveTimer
- Beschreibung: Returns the duration of a given spawn wave.
- Argumente: wave type: Wave
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/RespawnMethods/GetWaveTimerMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## PlayWaveEffect
- Beschreibung: Plays a Respawn Wave effect (the NTF helicopter/CI van arrival animation)
- Argumente: wave type: Wave
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/RespawnMethods/PlayWaveEffectMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SpawnWave
- Beschreibung: Forces a wave to start.
- Argumente: wave type: Wave, mode: Options
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/RespawnMethods/SpawnWaveMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## WaveInfluence
- Beschreibung: Changes influence of a wave.
- Argumente: wave type: Wave, mode: Options, influence: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/RespawnMethods/WaveInfluenceMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## WaveRespawnTime
- Beschreibung: Changes the time left to spawn a wave.
- Argumente: wave type: Wave, mode: Options, time: Duration
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/RespawnMethods/WaveRespawnTimeMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## WaveRespawnTokens
- Beschreibung: Changes respawn tokens of a wave.
- Argumente: wave type: Wave, mode: Options, respawn tokens: Int
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/RespawnMethods/WaveRespawnTokensMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
