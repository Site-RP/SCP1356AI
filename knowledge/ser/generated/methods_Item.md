# SER Methoden — Item

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## AdvDestroyItem
- Beschreibung: Destroys items on the ground and in inventories.
- Argumente: items: Items
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ItemMethods/AdvDestroyItemMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## AdvDropItem
- Beschreibung: Drops an item from player inventory and returns a reference to the pickup object of that item.
- Argumente: item: Reference<Item>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ItemMethods/AdvDropItemMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## AdvGiveItem
- Beschreibung: Gives a player a single item, and returns a reference to the item.
- Argumente: player to give item: Player, item type to add: Enum<ItemType>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ItemMethods/AdvGiveItemMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## ClearInventory
- Beschreibung: Clears player inventory.
- Argumente: players: Players, mode: Options
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ItemMethods/ClearInventoryMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## DestroyItem
- Beschreibung: Destroys an item in players' inventory.
- Argumente: players: Players, item: Enum<ItemType>, amount: Int
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ItemMethods/DestroyItemMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## DropItem
- Beschreibung: Drops items from players' inventories.
- Argumente: players: Players, itemTypeToDrop: Enum<ItemType>, amountToDrop: Int
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ItemMethods/DropItemMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## FirearmItemInfo
- Beschreibung: Returns info about provided firearm
- Argumente: firearm: Reference<FirearmItem>, property: Options
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ItemMethods/FirearmItemInfoMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## ForceEquip
- Beschreibung: Forces players to equip a provided item.
- Argumente: players: Players, item type: Enum<ItemType>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ItemMethods/ForceEquipMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## GiveCandy
- Beschreibung: Gives candy to players.
- Argumente: players: Players, candyType: Enum<CandyKindID>, amount: Int
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ItemMethods/GiveCandyMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## GiveItem
- Beschreibung: Gives an item to players.
- Argumente: players: Players, item: Enum<ItemType>, amount: Int
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ItemMethods/GiveItemMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## GrantLoadout
- Beschreibung: Grants players a class loadout.
- Argumente: players: Players, roleLoadout: Enum<RoleTypeId>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ItemMethods/GrantLoadoutMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetRadioRange
- Beschreibung: Sets the radio range of a specified radio item.
- Argumente: radio: Reference<RadioItem>, new radio range: Enum<RadioMessages.RadioRangeLevel>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ItemMethods/SetRadioRangeMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## UsableItemInfo
- Beschreibung: Returns information about provided usable item, like Painkillers, Medkit, etc.
- Argumente: usable: Reference<UsableItem>, property: Options
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/ItemMethods/UsableItemInfoMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
