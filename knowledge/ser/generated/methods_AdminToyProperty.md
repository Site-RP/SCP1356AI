# SER Methoden — AdminToyProperty

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## SetCameraProperties
- Beschreibung: Sets the properties of a {nameof(CameraToy)}.
- Argumente: camera reference: Reference<CameraToy>, label: Text, up constraint: Float, down constraint: Float, left constraint: Float, right constraint: Float, minimal zoom: Float, maximal zoom: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AdminToyPropertyMethods/SetCameraPropertiesMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetInteractableProperties
- Beschreibung: Sets properties of an Interactable Toy.
- Argumente: toy: Reference<InteractableToy>, shape: Enum<InvisibleInteractableToy.ColliderShape>, interaction duration: Duration, is locked: Bool
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AdminToyPropertyMethods/SetInteractablePropertiesMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetLightSourceProperties
- Beschreibung: Sets the properties of a {nameof(LightSourceToy)}.
- Argumente: light reference: Reference<LightSourceToy>, intensity: Float, range: Float, color: Color, shadow type: Enum<LightShadows>, shadow strength: Float, light type: Enum<LightType>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AdminToyPropertyMethods/SetLightSourcePropertiesMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetPrimitiveObjectProperties
- Beschreibung: Sets properties of a {nameof(PrimitiveObjectToy)}.
- Argumente: toy reference: Reference<PrimitiveObjectToy>, type: Enum<PrimitiveType>, color: Color, flags: Enum<PrimitiveFlags>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AdminToyPropertyMethods/SetPrimitiveObjectPropertiesMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetShootingTargetProperties
- Beschreibung: Sets the properties of a {nameof(ShootingTargetToy)}.
- Argumente: target reference: Reference<ShootingTargetToy>, max hp: Int, auto reset time: Int, synchronize damage?: Bool
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AdminToyPropertyMethods/SetShootingTargetPropertiesMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetTextProperties
- Beschreibung: Sets the properties of a {nameof(TextToy)}.
- Argumente: text toy reference: Reference<TextToy>, label: Text, display width: Float, display height: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/AdminToyPropertyMethods/SetTextPropertiesMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
