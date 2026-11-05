# Phase 1 - literature review

Goal: map the literature the paper must sit in, for the target venue's readership, and find the gaps the claim can
fill. Use the paper search tools available (Consensus search, web search, OpenAlex/Crossref pages) and read
abstracts; do not cite from memory.

Write `<project>/lit/refs.yaml`: a list of entries
`{key, doi, title, first_author, year, venue, shows, relevance, cluster}` where `shows` is one sentence on what the
paper actually finds or does (from its abstract or text), `relevance` how it bears on our claim, `cluster` one of
the clusters below. DOI is required unless the work has none (then `url`). 30-60 entries; quality over count.

Write `<project>/lit/review.md`:

1. **Clusters.** 4-7 strands relevant to the claim and the venue (method, application, policy question, the venue's
   own debates). For each: 3-6 sentences with keys, what is established, what is contested.
2. **Where the claim sits.** What is new relative to each strand; what a referee from each strand will ask.
3. **Gaps the claim could fill**, ranked by how well the material can fill them.
4. **The venue's literature.** Papers published in the target journal (and special issue, if any) in the last
   three years on related topics: who publishes there, which methods, which framing. Name them with keys.
5. **Must-cite list.** The 10-15 references a referee would expect to see, with why.

Check that the draft's existing bibliography covers the must-cite list; list what is missing.
