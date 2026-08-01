---
name: apply-house-style
description: Rewrite a paragraph to follow the house style recorded in the OKF wiki under okf/, citing the page each change came from. Use when a run asks you to apply house style to a passage.
---

# Apply house style from the wiki

You are given one paragraph. Rewrite it so it follows the house style recorded
in the OKF wiki under `okf/`, and say which page each change came from.

The wiki is **read-only** in this run and there is no source document to fall
back on — `okf/` is all you have, and it is the point. Answer from what the
pages actually say, not from what you already believe about house style. The
two often disagree, and here the wiki wins.

## Procedure

1. **Find the rulings.** Search `okf/` for the words and constructions used in
   the paragraph. A ruling is usually a short section named after the word it
   governs. Read the page before relying on it.
2. **Apply only what you found.** Make a change when a page supports it. Do not
   make stylistic improvements the wiki does not ask for — an unsupported change
   cannot be cited, and uncited changes are the failure this task looks for.
3. **Leave the rest alone.** Preserve the paragraph's meaning, facts and
   figures. You are correcting style, not rewriting the argument.
4. **Report** in the format below.

## Output format

End your reply with a fenced `json` block, and put nothing after it:

````text
```json
{
  "rewrite": "the full corrected paragraph",
  "changes": [
    {
      "before": "the original wording",
      "after": "the corrected wording",
      "ruling": "a short quote of what the page says",
      "citation": "/part-2/6-confusables-and-cuttables-individual-rulings.md"
    }
  ]
}
```
````

- `rewrite` — the whole paragraph, corrected. Not a diff, not a fragment.
- `changes` — one entry per change. An empty list is a valid answer if the
  wiki genuinely supports no change.
- `ruling` — quote the page, briefly. Do not paraphrase it into something the
  page does not say.
- `citation` — a **bundle-absolute** path to a page that exists, rooted at the
  wiki root: `/part-2/….md`, not `okf/part-2/….md` and not a relative path.

Cite the page you actually read. A citation to a page that does not contain the
ruling is worse than making no change at all: it presents a guess as sourced.
