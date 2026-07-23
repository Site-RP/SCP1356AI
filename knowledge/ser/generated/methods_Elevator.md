# SER Methoden — Elevator

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## LockElevator
- Beschreibung: Locks elevators.
- Argumente: elevators: Elevators, lockReason: Enum<DoorLockReason>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ElevatorMethods/LockElevatorMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SendElevator
- Beschreibung: Sends elevators to the next floor.
- Argumente: elevators: Elevators
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ElevatorMethods/SendElevatorMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetElevatorText
- Beschreibung: Changes the text on the elevator panels between LCZ and HCZ.
- Argumente: text: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ElevatorMethods/SetElevatorTextMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## UnlockElevator
- Beschreibung: Unlocks elevators.
- Argumente: elevators: Elevators
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ElevatorMethods/UnlockElevatorMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
