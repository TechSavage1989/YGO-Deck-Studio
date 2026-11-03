# YGO Deck Studio - Read First

## Current baseline

The current development baseline is 3.0.0-alpha.221-duelcore.1-rc242.

This project is a recovered-source continuation. The original native Go source for the rc189 application shell was not available. The current browser entry points, launcher/updater, tests, and release handoff are maintained in Git. The complete recovered-source tree, including web dependencies, artwork, and the verified rc189 native baseline, is distributed in the versioned Source ZIP identified in docs/SOURCE_SNAPSHOT.md. Use that complete snapshot together with newer confirmed Git changes; do not reconstruct missing files from older revisions. tools/patch_embedded_web.py patches the maintained browser assets into the verified rc189 native baseline before the launcher embeds that core executable.

Do not replace the recovered native baseline or reconstruct duel-engine behavior unless the project owner explicitly requests it.

## Repository and release feed

Repository: https://github.com/TechSavage1989/YGO-Deck-Studio

Expected release feed: GitHub Releases from the same repository.

App identity: com.techsavage1989.ygo-deck-studio

Stable public executable filename: YGODeckStudio.exe

Do not change repository visibility, publish source, create credentials, embed tokens, overwrite a published release, or change release ownership without explicit owner approval.

## Versioning

Increment the release candidate consistently in:

- launcher/version.go
- tools/patch_embedded_web.py
- web/index.html
- web/js/app.js
- web/js/duel-core.js
- release changelog and validation filenames

Published tags use v followed by the complete application version. Never reuse an existing tag or overwrite its release assets.

## Build

Primary build command:

Windows:
py -3 scripts\build_release.py --out dist

Linux/macOS development environments with Go and Python:
python3 scripts/build_release.py --out dist

The build produces a standalone Windows executable named YGODeckStudio.exe, a portable ZIP containing the stable launch filename, source ZIP, update-manifest.json, validation report when present, and SHA-256 manifest.

The Windows launcher must link launcher/rsrc_windows_amd64.syso. The checked-in object contains the original application icon and is verified against web/assets/app_icon.ico in the finished executable during every release build. Run python tools/generate_windows_icon.py to regenerate it after an icon change. Never patch the completed launcher to add icons.

## Tests

Run at minimum:

- node --check web/js/app.js
- node --check web/js/duel-core.js
- go test ./launcher/updater
- python tests/test_rc236_update_client_timers.py
- python tests/test_rc238_update_banner_clicks.py (loads source and packaged stylesheets; real mouse clicks only)
- current targeted duel-selection, Xyz-material, shared-EMZ, visual-log, and named-identity regressions

The release builder runs the current focused set automatically.

## Update architecture

The stable launcher embeds the current recovered native core and starts it from per-user application storage. The browser UI discovers the launcher's loopback update service and performs scheduling/UI only. The launcher performs GitHub release queries, ETag/backoff handling, download validation, staging, replacement, health confirmation, and rollback.

Automatic checks occur at startup, every five minutes while active/online, and on focus/visibility return after two minutes. Automatic download/install/restart is prohibited.

Update release requirements:

- update-manifest.json asset
- YGODeckStudio.exe launcher asset named by update-manifest.json
- matching SHA-256 and file size in the manifest
- GitHub Release tag matching the manifest tag

A matching hash is integrity validation, not publisher code signing.

The public standalone asset, manifest asset_name, and portable EXE must all use YGODeckStudio.exe, without any release or version suffix. Versioned archive/tag names remain supported. The installer must continue replacing and restarting the actual running launcher path. Preserve existing custom or legacy executable paths so current shortcuts remain valid; never derive the installed target name from the release asset name.

## Data locations

Launcher/updater data on Windows:

%LOCALAPPDATA%\YGO Deck Studio 3\

Important subfolders:

- App - extracted current core payload
- Updater - ETag/cache state, downloads, helper, health markers, last result, and one rollback backup
- Logs - reserved launcher/update diagnostics

Do not persist updater downloads, caches, staging files, or settings beside the portable executable. Temporary same-volume replacement files may exist beside the executable only during an install and must be cleaned after the helper exits.

## Preservation rules

Preserve working deck editor, duel simulator, settings, visual design, rules integration, visual Duel Log, attack effects/audio, Direct Hand/Field selection, Xyz-material handling, shared Extra Monster Zone mapping, and existing user data unless a requested change requires otherwise.

OCGCore remains authoritative for duel legality. UI work must not silently override engine candidate lists or rules decisions.

Practice Dummy gotchas (rc242):

- Every player-bearing field in a core message must be mapped from core to logical numbering in mapCoreMessageValue; CHAINING.triggering_controller was missed until rc242 and silently flipped the Dummy's threat assessment whenever the Dummy went first.
- Do not request OcgQueryFlags.TYPE in card queries. No published ocgcore-wasm build parses it, and an unparsed entry desynchronizes every later field of that query. tests/test_rc242_practice_dummy_decisions.py guards the refresh flag set.
- Dummy decision rules live in the dummy* methods at the end of web/js/duel-core.js. Keep "trigger" (a card's own When/If-this-card effect) distinct from event-activated Traps; only the former skips the response assessment.
- A headless end-to-end Dummy duel can be driven with the real engine (ocgcore-wasm from npm, Project Ignis cards.cdb and CardScripts) by serving web/ plus the /api/duel-engine endpoints and calling the controller's start() with a fixedSetup; see docs/validation/DUELCORE_VALIDATION_alpha221_duelcore1_rc242.txt for the procedure used.

## Repository layout contract

Keep the root limited to the entries in `scripts/check_layout.py`. Put implementation in the existing source directories, tests in `tests/`, automation in `scripts/` or `tools/`, and longer documentation/evidence in `docs/`. Do not add generated builds, logs, dependency trees, or versioned notes to the root. Any deliberate layout change must update the guard, all build/test/package path consumers, and this handoff in the same change. Run `python scripts/check_layout.py` before committing; CI and packaging enforce it. Preserve public executable/DLL/archive names and update endpoints.

## Repository standards (all contributors and AI tools)

This repository follows the shared TechSavage1989 standard in [`docs/REPOSITORY_STANDARDS.md`](docs/REPOSITORY_STANDARDS.md), the same file in every app repository. Read it before changing anything. In short:

- **README:** centered header (real icon, one `<h1>`, tagline, quick links Download · Get started · Features · Screenshots · Updates · Development, hero image), then the standard section order. Update it in the same pull request as any user-visible change.
- **Screenshots:** real captures with fictional data in `docs/images/` (`hero.png` + kebab-case names). Recapture any screenshot a UI change makes stale, in the same pull request.
- **Layout:** compact root; respect the root allowlist and checks above. Never commit build output, binaries, archives, logs, caches or secrets.
- **Branches:** short-lived `feat/` `fix/` `docs/` `chore/` `release/` branches, one focused change per pull request, merge only on green checks, delete the branch after merging.
- **Instructions:** this file is the single source of project rules for every tool; `CLAUDE.md` imports it. Add new rules and gotchas here.

Where this file's project-specific rules differ from the shared standard, this file wins; an enforced check script wins over both.
