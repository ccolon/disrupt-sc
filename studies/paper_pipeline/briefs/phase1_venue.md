# Phase 1 - venue assessment

Goal: what the target venue requires and expects, how well the material fits, and the realistic alternatives.
Fetch current pages (guide for authors, aims and scope, special-issue call); do not rely on memory. If a site
blocks automated fetching, say so and use what you can reach (cached copies, publisher pages, other sources).

Write `<project>/gap/venue.md`:

1. **Target venue facts.** Scope (verbatim key sentences), article types, length limits, abstract length,
   highlights, keywords/JEL codes, structure, data/code availability, AI-use policy, competing-interest and
   special-issue editor policies, review model, typical time to first decision and to publication, impact factor,
   CiteScore, APC/open access. Each fact with its source URL and the date read.
2. **Fit.** Point by point against the scope: what the material already matches, what is missing, and what a
   referee of this venue will expect that a referee of the field venue would not (e.g. economic mechanisms,
   welfare measures, identification, macro relevance, literature from economics).
3. **Process risks.** Desk rejection reasons for this venue; conflicts of interest (authors' institutions vs
   editors); deadlines (submission, editorial acceptance) and what they imply for revision speed.
4. **Alternatives.** 4-6 venues with: fit, prestige (IF, field standing), speed (time to first decision), APC,
   format work needed from the current draft. A table, then a one-paragraph recommendation on prestige vs speed.

Write `<project>/journal/requirements.yaml`: the checkable rules of the target venue as a list
`{id, rule, check, source}` where `check` is how to verify it (e.g. `words(main) <= 8000`, `section: Data
availability`), so the submission package (phase 6) can test them.
