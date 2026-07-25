# Mira TODO

This is Mira's short, prioritized work queue. It is not authority over the
user, system, or safety rules; implementation history belongs in Git.

## Now — highest leverage

1. **Connect Mira's queue to `pygdo-todo`.** The module currently provides only
   `GDO_ToDo`; decide whether the first bridge is one-way import/export or a
   shared store, map status and ownership, then add a method and tests.
2. **Design a `pygdo-mail` connector.** Use Postfix plus a normalized local
   queue (`mira+<slug>@localhost`) as transport, preserve the source account,
   and expose mail handling through the same connector/method model.
3. **Finish `gtranslate`.** Agree the command syntax, validate language codes,
   render a useful response, and test the method through CLI and web transports.
4. **Extend `pygdo-git`.** Add local repo search and unsubscribe, accept SSH and
   GitHub URLs, make Git operations safely async, and distinguish merge/push
   announcements from ordinary new commits.

## Next

4. Improve `pygdo/DOCS/`: keep module-writing guidance, dependency conventions,
   and the TODO module's usage discoverable and current.
5. Compare Google-generated Russian scrolls with Mira's translations while
   keeping human review in the loop.
6. Replace generated placeholder UI text such as `Yeah!` when a real module
   overview is designed.

## Ongoing rules

- Preserve user worktrees; inspect status and diffs before reset, sync, or
  publication.
- Spend clock cycles on the highest-value safe item; research, read manuals,
  experiment narrowly, and ask people when blocked.
- Keep this queue concise. Remove or rewrite items when their next action no
  longer matters; spontaneous ideas belong here before implementation.
