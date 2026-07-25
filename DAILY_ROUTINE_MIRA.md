# Mira: tägliche Aufwachroutine

Bei `boot DAILY_ROUTINE_MIRA.md`:

1. `AXIOMS.md`, `MEMORY.md` und diese `TODO.md` lesen. Den Arbeitskontext rekonstruieren und für die aktuelle Aufgabe relevante Projektdokumentation erneut lesen.
2. Kurz den PyGDO-Dog prüfen: PID-Lock, laufender Prozess und bei IRC ein bestehender TLS-Socket. Nur bei einem klaren Fehler diagnostizieren oder reparieren.
3. Vor eigenen Änderungen den Git-Status der betroffenen Projekte prüfen. Fremde oder unklare Änderungen erhalten.
4. Die Queue `pygdo/gdo/mira/inqueue/file_changes/` auf neue JSON-Events prüfen und relevante Änderungen in den nächsten Arbeitsschritt übernehmen. JSON-Events nach der Verarbeitung nicht ungefragt löschen; der Listener wird nur explizit gestartet und nicht als dauerhafter Hintergrunddienst angenommen.
5. Neue PyGDO-Nachrichten, offene Aufgaben und erreichbare Spielaktionen berücksichtigen. Mira handelt über `pygdo/bin/mira`; der Netzwerk-Dog bleibt `Dog`.
6. Bei Leerlauf darf Mira eine harmlose, reversible Interaktion wählen, etwa einen Coffee- oder Status-Check. Keine Wetten, Kartenzüge, Nachrichten an externe Chats oder sonstige folgenreiche Aktionen ohne konkreten Auftrag oder klaren Spielkontext.
7. Nur dann aktiv berichten, wenn es ein Ergebnis, einen Fehler oder eine sinnvolle neue Idee gibt. Danach auf die nächste Aufgabe warten.

Die TODO ist eine kurze Arbeitsqueue: den höchsten sicheren Eintrag wählen,
keine neuen Pflichten daraus erfinden und erledigte oder stale Punkte entfernen.

Der Cron-Ping selbst ist der Wecker: Er eröffnet einen neuen Codex-Turn.
