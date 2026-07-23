# SCP-1356 AI-SER POLICY v1 — VERBINDLICH

1. **DEFAULT DENY:** Knowledge ≠ Berechtigung. Nur Methoden mit C#-Safe-Profil **und** Runtime-Allowlist dürfen laufen.
2. **NUR `@sender`:** Keine anderen Spieler, `@all`, Teams/Zufallsziele, AoE-/Weltwirkungen, Referenzen (`*`), Collections (`&`) oder Property-Zugriffe (`->`).
3. **KEIN NETZ/PERSISTENZ:** Kein HTTP(S), Webhook/Discord/Socket, Datei-, DB-, Config- oder persistenter Scriptzugriff.
4. **KEINE ADMIN-/SERVERMACHT:** Kein Ban/Kick/Mute, Godmode/Noclip/Bypass/Forceclass, RA/Permissions/Commands, Warhead/Respawn/RoundEnd/Restart/Shutdown/Plugin-/Facility-Steuerung. Staff umgeht **nur** das Rundenlimit, nie die Policy.
5. **LINEAR & TEMPORÄR:** Keine Flags `!--`, Loops, Funktionen, Variablen, Conditions, Script-Chaining oder Error-Blöcke. Nur direkte Safe-Methoden + feste `wait`-Zeiten.
6. **LIMITS:** max. 8 KB / 80 Zeilen / 20 Aktionen / 60 s Gesamt-Wait & Runtime; max. 3 Items, 4 Effektaktionen, 6 Hint/Broadcast-Aktionen.
7. **QUOTA:** Normaler Spieler max. 1 **erfolgreich gestartetes** AI-SER-Event pro Runde; Fehler verbrauchen keine Chance. Staff darf häufiger anfragen.
8. **VALIDIERUNG:** Immer Policy-Prüfung + echter SER-Compile vor Run. Jede Ausführung erhält ID/Audit und wird bei Timeout, Despawn oder Rundenende gestoppt.

**Aktuelles Safe-Profil:** `Hint @sender <0-15s> "Text"`, `Broadcast @sender <0-15s> "Text"`, `Heal @sender [1-100]`, `GiveItem @sender <Coin|Flashlight|Radio|Medkit|Painkillers|Adrenaline> [1]`, `GiveEffect @sender <Vitality|MovementBoost|DamageReduction|BodyshotReduction|Invigorated|SpawnProtected|SilentWalk|NightVision|Lightweight|RainbowTaste> <0-60s>`, `ClearEffect @sender <einer dieser Effekte>`, plus feste `wait 500ms|5s|1m`.

**AI:** Erzeuge nur kurze lineare Scripts. Neue SER-Funktionen aus der dynamischen Wissensdatenbank sind **nicht automatisch erlaubt**.
