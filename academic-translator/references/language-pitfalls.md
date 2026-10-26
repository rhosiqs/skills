# Language-pair and field pitfalls

Load the sections that match the job. Each entry is a failure that survives a fluency check — the output reads fine and is still wrong.

## Contents
- Chinese ↔ English
- Japanese ↔ English
- Korean ↔ English
- German ↔ English
- French / Spanish / Portuguese ↔ English
- Russian ↔ English
- Arabic ↔ English
- Terms that shift meaning by field
- Structural conventions by section

---

## Chinese ↔ English

**Into English**
- Topic-comment structure has no English equivalent. Rebuild with an explicit grammatical subject rather than a dangling participle. A sentence beginning "通过分析…" becomes "Analysis of X shows…" or "We analyzed X and found…", not "By analyzing X, the result is…".
- Sentence length. One Chinese sentence with three or four commas usually becomes two or three English sentences. Comma splices are the most visible marker of unedited Chinese-to-English translation.
- Zero anaphora. Chinese drops subjects freely; English requires them. Recover the referent from context and, if it is genuinely ambiguous, flag it rather than guess.
- Aspect, not tense. 了 marks completion, not past tense. Decide tense from the rhetorical role of the sentence (what we did = past, what is known = present).
- 研究 covers study, research, investigation, and work. Pick by role: "this study" for the present work, "research" for the field, "studies" for prior work.
- Intensifier inflation. 非常, 极大地, 十分, 充分 usually drop entirely in English. "Greatly improves" and "fully validates" read as overclaiming to English reviewers.
- 我国 is "China", not "our country", in an international journal.
- 等 at the end of a list is "etc." only sometimes — often it should become "and others" or be dropped.
- Formulaic closings ("希望本研究能为…提供参考") have no English equivalent and are usually cut or replaced with a concrete statement of contribution.

**Into Chinese**
- English passive voice should mostly become active or 被-free constructions; heavy 被 use reads as translationese.
- Keep the English acronym after the Chinese expansion on first use; do not invent a Chinese acronym.
- Long English noun stacks ("deep learning based image segmentation framework") need unpacking with 的 and reordering, not a token-by-token chain.

---

## Japanese ↔ English

- Subject omission is even more pervasive than in Chinese. Determine whether the agent is the authors, prior researchers, or the general community before choosing "we", "prior work", or a passive.
- The topic marker は versus subject marker が can encode contrast and given/new status that English carries by article choice and word order. Getting this wrong shifts emphasis silently.
- Politeness and humility formulas (謙譲語, ～と考えられる, ～と思われる) are conventional register, not hedges of the author's confidence. Translating every ～と考えられる as "it is thought that" produces an unreadably tentative English paper. Judge from context whether it is a real hedge or a register marker.
- ～における, ～に関する, ～に対する chains need restructuring, not a preposition each.
- Katakana loanwords are not always their English source. Check field usage before assuming.

---

## Korean ↔ English

- Same subject-omission and honorific-register issues as Japanese; apply the same judgment about ～것으로 보인다 as convention versus hedge.
- Sino-Korean technical vocabulary often has a well-established English equivalent that is not the literal gloss. Check the field's English literature.
- Korean academic prose uses longer coordinate chains than English. Break them.

---

## German ↔ English

- Nested subordinate clauses and end-position verbs must be unwound; a faithful English mirror produces a sentence the reader cannot parse.
- Nominalization density is higher in German. English tolerates some but converting every -ung noun to an English -tion noun yields the classic opaque translationese paragraph. Convert some to verbs.
- Modal particles (ja, doch, eben, zwar) mostly disappear in English.
- False friends that survive fluency checks: aktuell (current, not actual), eventuell (possibly, not eventually), sensibel (sensitive, not sensible), Kontrolle (often monitoring, not control), Bilanz (balance sheet or assessment, context-dependent).

**Into German**: restore compound nouns rather than stringing genitives; English "we" often becomes an impersonal construction in traditional German academic prose, though this convention is weakening in the sciences.

---

## French / Spanish / Portuguese ↔ English

- Higher rhetorical elaboration. French academic prose in particular builds an argument before stating the conclusion; English states it first. Reordering is legitimate in publication-ready mode, not in faithful mode.
- French false friends: actuellement (currently), éventuellement (possibly), important (large), sensible (noticeable), contrôler (to check), formation (training), expérience (experiment or experience — disambiguate from context).
- Spanish/Portuguese: pretender (to intend), realizar (to carry out), asistir (to attend), notorio (well known). "Realizar un experimento" is "conduct an experiment", not "realize" it.
- The impersonal on / se construction usually becomes an English passive or "we", depending on whether the authors did the thing.
- Romance sentence length again exceeds English norms. Split.

---

## Russian ↔ English

- Articles do not exist in Russian and must be reconstructed; article errors are the most common giveaway and they can change meaning (a result versus the result).
- Aspect pairs carry completion information that English encodes with tense and adverbs.
- Heavy nominal constructions and instrumental chains need verb-based rebuilding in English.
- Russian academic prose uses the authorial plural and impersonal constructions where English now prefers "we".

---

## Arabic ↔ English

- Coordination with و where English wants subordination or a sentence break. Chains of "and" read as unstructured in English.
- Verb-initial word order and dual number have no English equivalents; restructure rather than mirror.
- Established English transliterations of names and terms vary; pick one system, state it, and use it throughout.

---

## Terms that shift meaning by field

Resolve these from the discipline before translating, not after.

| Term | Diverging senses |
|---|---|
| significant | statistical (p-value) vs. substantive importance — never blur these in either direction |
| bias | statistical estimator bias / cognitive bias / sampling bias / electrical bias / editorial slant |
| model | mathematical model / statistical model / trained ML artifact / animal model / theoretical framework |
| control | experimental control group / statistical adjustment / control system / access control |
| domain | mathematical domain / application area / protein domain / DNS domain |
| subject | research participant / topic / grammatical subject / legal subject |
| power | statistical power / physical power / political power |
| validity | measurement validity / logical validity / legal validity |
| resolution | image resolution / dispute resolution / a formal decision |
| stress | mechanical stress / psychological stress / linguistic stress |
| sample | statistical sample / physical specimen / audio sample |
| population | statistical population / biological population / demographic population |
| network | neural network / social network / computer network |
| regression | statistical regression / developmental regression |
| discrimination | statistical/perceptual discrimination / unfair treatment — this one is a genuine hazard, since the wrong choice can reverse the sense of a sentence |

---

## Structural conventions by section

Knowing what a section is doing helps decide tense, hedging, and how much reordering is defensible.

- **Abstract** — usually mirrors the paper's structure in miniature. Word limits are strict; if the translation overshoots a stated limit, tighten and say what you cut. Past tense for what was done, present for what is claimed.
- **Introduction** — present tense for established knowledge, present perfect for the state of the field, past for specific prior studies. Citation integration conventions differ by language; convert to the target field's style but never change which work is cited.
- **Methods** — the highest-fidelity section. Past tense, no smoothing, no consolidation of steps, every parameter and unit verified digit by digit. An omitted concentration or duration makes the study unreproducible.
- **Results** — past tense for findings, present for what figures and tables show. Do not import interpretation from the discussion.
- **Discussion** — hedging density peaks here and matters most. Preserve every limitation and every qualifier.
- **Reference list** — not translated. Reformat only if the user asks for a specific citation style, and then reformat mechanically without altering content.
