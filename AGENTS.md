# YGO Deck Studio - Read First

## Current baseline

The current development baseline is 3.0.0-alpha.221-duelcore.1-rc254.

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

Publishing: either push the version tag, or use the publish button (GitHub -> Actions -> Build and Release -> Run workflow on main, type "publish"). The button builds main and creates the tag and prerelease named by launcher/version.go; it refuses if that tag already exists. Both paths refuse a release whose built manifest does not match the tag, so a tag placed on the wrong commit cannot publish a mislabeled release. Claude cloud sessions cannot push tags or create releases through their git proxy; the button is how to publish without a local git client.

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
- Embedded-slot size cap: tools/patch_embedded_web.py can only write each browser asset into the slot the rc189 executable allocated for it (web/js/duel-core.js: 798,551 bytes, web/js/app.js: 463,846, web/styles.css: 586,884, web/index.html: 97,860) after processing. Since rc244 the JavaScript is minified with terser (pinned in tools/patch_embedded_web.py, run through npx; local names only, class and property names kept), which leaves roughly 140 KB of room in each JavaScript slot; without npx the patcher falls back to whitespace compaction and the files may not fit. web/duel-core.css (slot 361,955) is patched since rc244 too; before that, edits to it never shipped. CI fails at "Prepare verified recovered source" when a file no longer fits. Measure before committing JavaScript changes: `python -c "import sys;sys.path.insert(0,'tools');import patch_embedded_web as pw;from pathlib import Path;print(len(pw.replacement_bytes(Path('web/js/duel-core.js'),'web/js/duel-core.js')))"`. rc242 freed room by deleting methods nothing referenced; comments are free, code is not. tests/test_rc243_duel_review.py asserts both JavaScript files still fit.
- Duel sounds are recorded clips since rc251: about 40 short Ogg Opus clips (mono, 20 kbit/s, at most 1.8 s), base64, split between globalThis.YGO_DUEL_SFX at the end of web/js/app.js and DUEL_SFX_LONG at the end of web/js/duel-core.js so both embedded slots keep headroom (about 97 KB left in app.js and 68 KB in duel-core.js; measure before adding clips) and decoded once by preloadSoundSamples in duel-core.js. playSound and the attack sound play the clip for a kind when it is decoded and otherwise fall back to the synthesized recipe, so every clip key must also be a recipe kind, an attack clip (attack, atkbeast, atkmagic, atkfire) or shuffle (rc253: playDeckShuffleSound waits for that clip because the shuffle is often the first sound of a duel; the older data-URI shuffle is only the fallback). Card-handling and a few remaining clips are mixed with ffmpeg from CC0 recordings (sources credited in docs/LEGAL_NOTICE.txt); the owner rejected two synthesized sets as too basic, so do not go back to tones, and send the owner an audio preview before changing the set. Use only CC0 or similarly unrestricted recordings and credit them. tests/test_rc251_recorded_sfx.py decodes every clip in a real browser. The fallback recipes: sounds are synthesized from the recipe table in soundRecipes() (tones and filtered noise bursts, rendered by renderSoundRecipe through a shared compressor and generated reverb; gains are absolute, roughly 0.1 to 0.7 per layer, because the rc247 set at 0.03 to 0.06 was close to inaudible). Judge loudness and length by rendering recipes through an OfflineAudioContext, and effects by capturing frames from the live app, before shipping; the owner cannot be the first to find out. Two older data-URI clips (deck shuffle, default attack) remain in duel-core.css. Add a sound by adding a recipe, a category in soundCategoryForKind and, for a new category, a row in soundEffectDefinitions; tests/test_rc247_battle_fx_sound.py fails if a recipe is silent or uncategorized. Board effects that must overlay the field are appended to document.body with position:fixed (the duel root is a fixed layer, not a top-layer dialog).
- Card-action effects (rc252) are drawn by playFx(name,x,y,options) in web/js/duel-core.js on one fixed full-window canvas (.duel-fx-canvas) with additive blending; the canvas exists only while particles are alive. Effects: summon, special, fusion, synchro, xyz, link, ritual, activate (colour by card type), negated, disabled, destroyed, togy, banished, tohand, todeck, targeted, statup, statdown, unaffected, impact. They are triggered from playSummonRing, playActivationPulse, playBattleDestruction, playAttackLunge, playMoveAnimation (through fxForMove: a card leaving for the Graveyard, banished pile, hand or Deck) and the affected-card outcome popup. They are original designs in the style players expect from current card-game simulators, not copies of another game's assets. Sizes scale with the card rectangle and counts with the battle effect intensity; nothing plays with animations off, during replay seek, or under prefers-reduced-motion. Render a frame-by-frame preview (stub requestAnimationFrame, step fxTick, screenshot) and send it to the owner before changing the look. Owner-chosen sounds (rc254): the owner uploaded 31 Pixabay sound effects they like (magical whooshes, spell casts and impacts, sword slices and clashes, explosions) and most battle, summon and effect clips are now 2-second excerpts of those files, one recording per action rather than layered mixes; the mapping is in docs/releases/CHANGELOG_rc254.txt. They are under the Pixabay Content License (use inside the app is allowed, standalone redistribution is not), so do not commit the source files; pixabay.com is behind a bot check this environment cannot pass, so new ones must be uploaded by the owner. Clips are 18 kbit/s and split by size between the two tables (largest into DUEL_SFX_LONG up to about 49 KB of base64) to keep more than 50 KB free in each JavaScript slot. Owner sound preferences (rc252): no bells, chimes, dings or gongs anywhere; dramatic and realistic sounds that fit warrior, magic and dragon battles (magical blasts, explosions, thunder, roars, blades) and match the action; phase change is a plain whoosh; card moves (draw, set, Normal Summon, to Graveyard, return, discard, material) use only card-handling recordings; activation of a Spell, Trap or effect is a clearly magical whoosh, not a blast and with no wobbling or warbling tone (the owner disliked a "woowoowoo" opening), and the Deck shuffle is a fast riffle of real cards (rc253); magic recordings are for effects (activation, chain, targeting, negation, stat changes, Special and Extra Deck Summons). tests/test_rc252_particle_fx.py runs every effect.
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
