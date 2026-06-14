# Site Module Template

Copy this file to `references/<site>-docs-map.md`, fill every section, then register the module in `SKILL.md` → Site Modules and in the Reference Files list. The mentor core (Mentorship Mode M1–M7, teaching beats, guardrails, evidence/honesty rules) is reused unchanged — a module only supplies what is site-specific.

This template works for **any** webapp, not just options-data sites. For a domain unrelated to options (e.g. a data dashboard, a design tool, a SaaS app), keep sections 1–7 and 9, and replace section 8 (Coverage Ledger mapping, which is options-specific) with that domain's own "what must I check before concluding" checklist — or omit it if the task is pure tutoring with no analytical conclusion. If the new domain needs concept primers of its own, add a `references/<domain>-concept-primers.md` alongside this map and point the teaching loop at it instead of `options-concept-primers.md`.

> Always verify against the live site before relying on detail; sites change. Date your findings.

---

## 1. Access boundaries (fill first)
- What is public / no-login?
- What requires an account or paid plan, and where does it live (which domain/subpath)?
- Does the user have an account? If not, default to the public surface and teach gated tools from docs, demonstrating live on an accessible site (M5). **Never bypass logins, paywalls, or bot checks.**
- Plan tiers and what each unlocks (context only — never a recommendation to buy).

## 2. Core URLs
- Home / marketing, docs/support, pricing, app/dashboard, and any deep-linkable views.
- Note the URL pattern for per-entity pages (e.g. per-ticker, per-project) and whether filter/view state is encoded in the URL (enables M6/M7 deep links). Copy site-generated URLs rather than hand-building them.

## 3. Tool / feature inventory
Table: Tool | Access (public/gated + plan) | What it shows | Teaching use. One row per feature the mentor might drive or reference.

## 4. Domain concepts & proprietary terms
Definitions of the site's named concepts, **verified from its own docs**. Anchor each to the shared mental model where one exists. Flag anything proprietary/fitted (vs. standard theory) so the apprentice knows what's house methodology.

## 5. Vocabulary bridge
Table mapping this site's terms to the shared primer concepts (or to another module's terms). Call out same-idea-different-name pairs explicitly so the apprentice's model transfers across tools instead of fragmenting.

## 6. Data semantics & freshness
- Where does the data come from; what are its known assumptions/conventions (carry caveats forward)?
- Update cadence per tool; real-time vs. delayed vs. snapshot.
- Market-closed / off-hours / weekend behavior and how to label it (structure-only, etc.).

## 7. Deep-link & synchronization notes (M6/M7)
- How to produce a reproducible link to the exact view being taught.
- Zoom/filter controls and any gotchas (e.g. silent fallback on bad parameters, defaults that skip the lens you want).

## 8. Analytical coverage mapping (options modules only)
Map the Coverage Ledger lenses (OI, volume, max pain, skew/IV, Greeks, GEX, DEX, unusual options, P&L) to this site's surface. Mark lenses with no equivalent `unavailable (site)`; complement with another module or label `PARTIAL ANALYSIS` per SKILL.md rule 15. **For non-options domains, replace this section with the domain's own pre-conclusion checklist, or delete it for pure-tutoring modules.**

## 9. Teaching path (especially when access is limited)
A concrete default walkthrough: which public pages/docs to open, how to teach each concept from them, how to bridge vocabulary, and where to run a live demonstration if the richest tool is gated. Keep the M2 loop intact: frame → prime → show live → interpret → check → bridge.

---

### Registration checklist (do after filling the module)
- [ ] `SKILL.md` → Site Modules: add the site, its docs-map path, a one-line scope, and any access caveat.
- [ ] `SKILL.md` → Reference Files: list the new module under "Site modules."
- [ ] If the domain is non-options: add/point to a domain concept-primers file and note it in the module.
- [ ] Validate: frontmatter description still < 1024 chars; all referenced files exist; live-test one walkthrough on the new site.
