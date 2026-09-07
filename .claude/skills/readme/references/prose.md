# Prose and voice

Structure decides whether a README is usable. Prose decides whether it is
trusted. Read this before drafting sentences; skip it for a purely structural
edit.

One idea underpins the rest: clear writing follows from clear thinking, and
the reverse holds too. In plain words it is far harder to hide that you are
unsure what you mean. Jargon is where unverified claims hide, so plain
language is a verification technique rather than a decoration.

The failure this guards against is writing on automatic pilot — assembling
the phrases that usually appear around this kind of subject, rather than
working out what is true of this one. Such prose reads fluently sentence by
sentence and falls apart the moment somebody checks it. That is the exact
failure mode of a generated README.

## The register

Aim for prose that reads less like a lecture and more like a colleague who
knows the system explaining it. Direct, unhurried, never selling.

That register governs the prose — the description, the context paragraph, how
it works, the limitations. It does not govern reference material. Config
tables, flag lists and API entries should be terse, uniform and scannable. A
conversational config table is worse than a dry one, because the reader is
looking something up rather than reading along.

## One term per concept

A README reader arrives in the middle: from a search result, an outline click,
a link someone pasted. They have not read the section above.

So name each thing once, then use that exact name every time. Never reach for
a synonym to avoid repetition. If the thing is a kit, it is a kit on every
mention — not a bundle, not a package, not a spec. Repetition that would be
dull in an essay is what makes a README searchable, and a reader who lands
mid-document has nothing to refer back to.

Acronyms follow the same rule. Expand one on first use in each section that
uses it, rather than once at the top of the file — a reader who arrives at
section 8 never saw the expansion in section 1.

Two carve-outs. Leave an acronym alone when it is more familiar than what it
stands for: *API*, *HTTP*, *JSON*, *CLI*, *URL*. And introduce no acronym you
use only once — spell the thing out and move on. An initialism used a single
time clutters the page and the reader's memory for nothing.

## Plain words

Prefer the short, everyday word. It is not only shorter, it is clearer:

- *use*, not *utilise*
- *build*, not *facilitate the construction of*
- *before*, not *prior to*
- *about*, not *approximately*
- *enough*, not *sufficient*
- *show*, not *demonstrate*
- *set up*, not *establish*

Three questions settle most choices. Is the word short? Would you use it
talking to a colleague? Does nearly everyone know it? A word that fails all
three is usually reaching for status: *leverage*, *utilise*, *holistic*,
*actionable*, *address* (as a verb for *fix*, *answer* or *handle*).

One exception matters. Where a long word is the project's real vocabulary — an
actual function name, a spec term, a protocol — use it exactly. Precision
outranks brevity when the word is an identifier.

## Jargon

Jargon has a job. It also has three failure modes:

- **Pomposity** — a longer word that adds nothing. A *meeting* becomes a
  *summit*, *ideas* become *learnings*, a *fix* becomes a *remediation*.
- **Verbing** — nouns pressed into service as verbs. Prefer *have an impact
  on* to *impact* and *give access to* to *access*.
- **Misdirection** — a word chosen to obscure. *Non-trivial* usually means
  *hard*; *known issue* usually means *bug*. Call things what they are.

Define only the terms you will use repeatedly, and rephrase the rest. An
acronym costs the reader more than it saves the writer, because they carry the
expansion while reading.

Calibrate against your reader: explaining the obvious insults them, assuming
too much abandons them. The prerequisite too boring to state is the one that
blocks somebody for an hour.

Use a technical term only in its exact sense. Your readers know these words,
so a loose one costs credibility on the spot. *Exponential* describes a rate
that compounds, not merely a fast one. *Atomic* means indivisible, not quick.
*Idempotent*, *race condition*, *deadlock* and *linear* all have precise
meanings somebody will check. Where you mean *fast*, write *fast*.

## Verbs and agents

Move the action into the verb. Abstract nouns made from verbs — *validation*,
*configuration*, *initialisation* — attract empty verbs, so finding one is the
fastest way to find the other.

- Not: *Validation of the input is performed by the parser.*
- But: *The parser validates the input.*

A precise verb also saves an adverb, because it carries the how as well as the
what. *The daemon retries* beats *the daemon tries again automatically*, and
*truncates* beats *shortens by cutting off the end*.

Prefer the active voice for the same reason. The passive earns its place in
three cases: the agent is unknown, the agent is genuinely uninteresting (*the
cache is invalidated on write*), or it keeps the subject consistent across
consecutive sentences.

Watch for the passive that hides *which component* acts. *The config is
loaded* leaves the reader asking by what, and when. Name it.

Vagueness is not the same fault. *Something went wrong* is active and still
tells the reader nothing.

## Cut

Most first drafts lose a fifth of their words with nothing lost.

- **Hedges** — *arguably*, *somewhat*, *fairly*, *rather*, *possibly*,
  *actually*, *really*. If you believe the claim, make it.
- **Intensifiers** — *very* weakens what it modifies. *A fast parser* is
  categorical; *a very fast parser* puts it on a scale with room above.
- **`there is` / `there are`** — *There are three ways to configure it*
  becomes *It can be configured three ways*.
- **Negatives** — *it is not uncommon* becomes *it happens often*. Stacked
  negatives invert your meaning without warning.
- **Pleonasms** — *end result*, *past experience*, *pre-planned*, *CLI
  interface*, *the fact that*, *in close proximity to*.
- **Padding prepositions** — *freed up*, *headed up by*, *split out into*.
- **Words the present tense implies** — *currently*, *at present*, *ongoing*.
  Keep one only when contrasting with another time.
- **`the case that`** — *in cases where this is unnecessary* becomes *where
  this is unnecessary*; *if it is the case that* becomes *if*.
- **`process`** — *the build process* is usually *the build*, and *the
  installation process* is *installation*.
- **`the former` / `the latter`** — these force the reader to stop and
  backtrack. Repeat the name instead.

Then ask whether each surviving adjective and adverb earns its keep. The aim
is not to remove all of them.

## Clichés

A dead metaphor is harmless. Nobody picturing an *iron will* thinks of metal,
and *under the hood* and *out of the box* pass unnoticed in technical writing.

The problem is the phrase with just enough life left to look vivid while doing
no work. It lets the writer skip the step of deciding what to say:

- *X does the heavy lifting* — say what X does.
- *getting started is a breeze* — show the command.
- *first-class support for Y* — say what is supported, and what is not.
- *a game-changer* — say what changed.

The test is whether the phrase carries information a reader could act on. If
cutting it loses nothing, it was filler. If replacing it forces you to work
out the specifics, it was hiding that you had not.

## Superlatives and buzzwords

The ten commonest words in press releases are *leader*, *leading*, *best*,
*top*, *unique*, *great*, *solution*, *largest*, *innovative* and *innovator*.
Everybody claims all ten, so none of them carries information. Their software
equivalents are *blazingly fast*, *robust*, *seamless*, *powerful*,
*production-ready*, *enterprise-grade* and *battle-tested*.

Cut them and let the facts do the work. *Handles 40,000 requests per second on
one core* says what *blazingly fast* gestures at, and a reader can check it.

A test for any vogue word: was it used this way twenty years ago, and will it
be in twenty more? If not, find a plainer one.

## Numbers and claims

A number in a README is a promise a reader may check.

- Give the **baseline**. *Twice as fast* means nothing without the thing it
  beats and the workload measured.
- Compare **like with like** — startup time against startup time, on stated
  hardware and stated versions.
- Do not overstate precision. *156,000* is honest where *156,231* implies a
  measurement nobody made.
- Round fractions beat percentages: *half the memory*, not *50.0% less*.
- *Increased by 100%* means *doubled*. Avoid *-fold*, which readers split on.
- Give changes old first, then new: *from 3.0s to 2.2s*.

## Sentences and paragraphs

Short sentences by default. Every full stop lets the reader clear their
working memory and start fresh, and long sentences are where syntax goes
wrong. Vary the length enough to avoid a staccato rhythm.

Avoid deep nesting. A subject separated from its verb by a long clause holds
the reader in suspense. Break it in two.

A sentence that has to be read twice is a failure. Trim the words you can, but
not the small functional words that carry structure — the *that* in *the file
that the parser writes* earns its place. Hyphenate compound modifiers for the
same reason: *read-only file*, *command-line tool*, *high-level API*.

Keep list items grammatically parallel. A README is mostly lists, and a list
that mixes forms reads as careless: *installs the binary, configuration of the
daemon, and to start the service* should be *installs the binary, configures
the daemon, and starts the service*. The same applies to section headings.

Check that an opening clause attaches to the subject that follows it. *Once
installed, you can run the tests* says that you were installed; write *once
the package is installed, run the tests*.

Watch the noun and verb forms of the same compound. *Setup* is a noun and *set
up* is a verb, so a heading reads **Setup** while an instruction reads *set up
the database*. The same split governs *login* and *log in*, *backup* and *back
up*, *checkout* and *check out*.

One idea per paragraph — a paragraph is a unit of thought, not of length. And
every section must make sense read alone, by somebody who arrived from a
search result.

## Hedging is not flagging

Cutting hedges does not mean overstating confidence. In practice the two pull
in opposite directions.

- **Hedging** softens a claim you believe: *this should probably work on
  Linux*. Cut it, or go and find out.
- **Flagging** records what you did not check: *this snippet is not covered by
  CI*. Keep it, and make it plain.

Write *the Windows path is untested* rather than *this may possibly work on
Windows*. The first states a fact about your knowledge. The second is a hedge
wearing a fact's clothes.

## The last pass

- Read the prose aloud. A stumble marks an awkward transition, a missing
  signpost, or a word repeated without noticing.
- Cut your own tics. Read the whole file at once to catch the word you reached
  for six times.
- Prefer a full stop to a semicolon, colon or dash. Reserve the colon for a
  genuine promise and delivery, most often the line introducing a code block.
  Keep dashes to one pair per paragraph.
- Murder your darlings. The effort a sentence cost you is no reason to keep
  it, and length is not an achievement.
- When editing somebody else's README, the aim is not to turn it into what you
  would have written. Fix what is unclear or untrue; leave what is merely
  different.

Finally: break any rule here sooner than write something clumsy. These are
aids to clear prose, not a compliance checklist. A sentence twisted to satisfy
a rule is worse than the plain sentence the rule was meant to prevent.
