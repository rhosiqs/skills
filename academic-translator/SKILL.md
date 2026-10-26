---
name: academic-translator
description: Translate scholarly text between English and Chinese (or any language pair) with terminology fidelity, correct academic register, a term glossary, and notes on judgment calls. Use whenever the user pastes or uploads a paper, abstract, thesis chapter, literature review, grant proposal, conference submission, peer review, or response letter and wants it in another language — including non-English academic writing rendered into publishable English for journal submission. Also use for bilingual side-by-side versions, terminology glossaries, and critiques of an existing academic translation, and on phrases like "academic English", "for submission", "polish my abstract", "翻譯這段摘要", "學術翻譯", "润色". Trigger on obviously scholarly text (citations, hedged claims, methods language) even when the request is only "translate this". Not for casual one-line conversational translation with no technical content.
---

# Academic Translator

Academic translation fails differently from ordinary translation. A tourist phrasebook translation that is 90% right is fine. A methods section that is 90% right may describe an experiment that was never run. The cost of error here sits in precision, not fluency, so this skill optimizes for a translation that a domain reviewer would accept as an accurate account of the same claims — not for a translation that reads smoothly to a non-specialist.

## Step 1: Establish the job before translating

Four things determine everything downstream. Infer what you can from the text and the conversation; ask only about what you genuinely cannot infer, and ask it in one short message rather than a questionnaire.

- **Direction.** Source language is usually obvious from the text. For the target: if the user wrote to you in language X and did not specify, X is the default target. If the source is already in X, they most likely want English for submission — say which assumption you made in one line rather than stalling.
- **Chinese variant, when Chinese is the target.** Traditional (Taiwan, Hong Kong) and Simplified (Mainland) differ in terminology, not only in characters: 資訊/信息, 軟體/软件, 迴歸分析/回归分析, 物件導向/面向对象, 最佳化/优化, 光碟/光盘. Match whichever variant the user writes in. With no signal at all, pick one, hold it consistently, and say which in the notes.
- **Discipline.** The expected fields are botany and plant physiology, biotechnology, bioinformatics, computer science, horticulture, and agriculture. Read `references/domain-terminology.md` before translating anything in these fields — that is most jobs, so treat loading it as the default, not the exception. It carries the nomenclature rules, the Taiwan/Mainland term splits, and the hazard list. Infer the specific subfield from the content and name your inference so the user can correct it, because renderings diverge inside this cluster too: 表現 is *expression* in a molecular paper and *performance* in a cultivar trial; 模式 is *model organism* in plant biology and *pattern* elsewhere.
- **Destination.** A translation for the user's own comprehension, a translation for journal submission, and a translation for a bilingual teaching handout have different tolerances for smoothing. Journal submission is the strictest.
- **Mode.** Pick from the four below.

## Step 2: Pick the mode

**A — Faithful translation (default).** Render the source into the target language with no content added, removed, reordered, or resolved. Ambiguity in the source stays ambiguous in the target, or gets flagged in a note. Use this unless the user asks for something else.

**B — Publication-ready English.** The user's source-language draft becomes English that a journal will accept. Sentence boundaries, connectives, and information order may be reworked to match English academic conventions, because the direct calque of a Chinese or Japanese paragraph is often ungrammatical-sounding in English even when every word is right. What still may not change: the claims, their strength, the numbers, the causal structure, or the citations. If the source makes a claim the evidence does not support, translate the claim as made and note the concern separately — do not quietly soften it.

**C — Bilingual.** Alternate source and target at paragraph or sentence granularity. Use paragraph granularity by default; sentence granularity when the user is studying the text or checking the translation. Never merge or split source units silently in this mode, since the alignment is the point.

**D — Translation review.** The user has a translation and wants it checked. Produce a table of specific problems — location, source text, current rendering, proposed rendering, and why it matters — ranked with meaning-changing errors first, terminology inconsistencies second, register and fluency last. Do not rewrite the whole thing unless asked.

## Fidelity rules

These are where academic translation is actually won or lost.

**Hedging is data, not decoration.** "The results suggest a possible association" is a different scientific claim from "the results show an association". Map hedges one-for-one: may/might/could, appears to, is consistent with, tends to, is likely, cannot be excluded. Strengthening a hedge is the single most common serious error in academic translation, and it is invisible to anyone reading only the target text. The same applies in reverse: do not add hedges the author did not use.

**Preserve negation scope and quantifier scope.** "Not all participants completed the task" and "all participants did not complete the task" are different findings. Rebuild the scope explicitly in the target language rather than mirroring word order.

**Numbers, units, and statistics pass through untouched.** No unit conversion, no rounding, no reformatting of p-values or confidence intervals, no changing 1,000 to 1.000 or vice versa unless the target-language convention requires it — and if it does, apply it consistently across the whole document. Verify every digit against the source before finishing.

**Tense and voice carry meaning in some fields.** In empirical papers, past tense typically marks what was done and found in this study, present tense marks established knowledge and what the paper argues. Mirror this distinction even when the target language handles tense differently.

**Do not resolve the author's ambiguity.** If a pronoun's referent is unclear in the source, guessing at it in the target inserts a claim the author did not make. Flag it in the notes instead.

## Do not translate these

Leave in the source form, and add a target-language gloss in parentheses on first mention only when the user is reading for comprehension:

- Personal names, unless a standard target-language form exists in the field's literature
- Institution names, unless the institution publishes an official target-language name — use the official one, never a homemade rendering
- Journal titles, conference names, and dataset names
- The reference list, including titles of cited works
- Variable names, code identifiers, chemical formulas, and equations
- Latin binomials and their authority citations, in italics — *Oryza sativa* L. Cultivar names keep single quotes and roman type: 'Tainung No. 1'. Convert Chinese corner brackets to quotes; never translate the cultivar itself.
- Gene and protein symbols, with their capitalisation and italics intact — *AP1* the gene, *ap1* the mutant allele, AP1 the protein. Case is data here, not style.
- Accessions and identifiers: GenBank numbers, AT3G54340, LOC_Os01g01010, plasmid and strain names, primer sequences
- Media, hormones, and reagents as the source wrote them: MS medium, ½MS, 2,4-D, BAP
- Software, databases, and file formats: BLAST, HISAT2, GATK, SAMtools, TAIR, KEGG, FASTQ, BAM, VCF, GFF3
- Anything inside a code fence, including comments unless the user asks for those specifically
- Established acronyms — introduce as `full target-language expansion (ORIGINAL ACRONYM)` on first use, then use the original acronym throughout
- Figure and table labels ("Figure 3", "Table 2"), and every cross-reference to them

## Terminology consistency

Inconsistent terminology is the strongest signal of machine translation and the fastest way for a reviewer to lose trust in a manuscript. One source term gets one target term for the entire document, even where a synonym would read better.

Before translating anything longer than a page, extract the recurring technical terms and fix their renderings. Where the field has an established convention, use it even if a more literal option exists — readers search on the conventional term. Where two conventions compete, pick one, use it throughout, and say which you picked and why in the notes.

Carry the glossary forward across the whole conversation. If the user later sends another section of the same paper, reuse the earlier renderings rather than re-deriving them.

For documents over roughly 2,000 words, present the glossary before the full translation and invite corrections — fixing a term choice at that point costs one line, fixing it afterward costs a full re-read.

## Register

Academic register is not just formality. It includes: nominalization density, impersonal constructions, citation integration, connective inventory, and how strongly authors are permitted to assert. These differ by language and by field, and matching them is most of what makes a translation read as native.

Some concrete pitfalls in the direction most users need: English academic prose prefers shorter sentences than Chinese, German, or Japanese academic prose; it distributes one claim per sentence; it front-loads the point rather than building to it; and it uses far fewer intensifiers. Translating a 90-character Chinese sentence as a single 60-word English sentence is grammatical and wrong.

Two reference files carry the detail. `references/domain-terminology.md` covers plant science, biotech, bioinformatics, CS, horticulture, and agriculture: nomenclature, term tables, Taiwan/Mainland splits, units that must not be converted, and the hazard list. `references/language-pitfalls.md` covers language-pair mechanics beyond Chinese and English. Load the domain file by default for these fields; load the pitfalls file when the pair or field appears there.

## Output format

Return three parts, in this order:

```
## Translation
[the translated text, structure preserved]

## Terminology
| Source term | Translation | Basis |
|---|---|---|
| ... | ... | ... |

## Notes
- **[source term, phrase, or location]** — [one or two lines: the call that was made and what the alternative was.]
```

How each part behaves:

- **Translation** leads and stands alone. No preamble, no "here is your translation", no summary of the content. The user can read. This section should be directly copy-pastable into their manuscript.
- **Terminology** carries only the terms where the choice was not obvious: field-specific jargon, terms with competing conventional renderings, coined terms, acronyms, and anything that must stay fixed across a long document. Three to fifteen rows is normal for a passage. Ordinary vocabulary does not belong here — a glossary padded with common words hides the entries that matter. If a short passage genuinely contains no such term, drop the section rather than inventing rows.
- **Notes** flags what a careful author would want the chance to overrule: an ambiguity in the source, a hedge with no clean equivalent, a term whose convention differs between subfields, a probable source error, a structural reordering. Three to six entries for a full paper is normal; twenty means you are narrating rather than flagging. Never use Notes to restate what the translation already says.

Write the headings and the commentary in whichever language the user is writing to you in — the translation itself in the target language, the scaffolding in theirs.

For a bilingual request, mode C replaces the Translation section; Terminology and Notes still follow at the end.

Preserve the source's structural markup exactly: heading levels, list nesting, italics, bold, footnote positions, and paragraph breaks. If the source is Markdown, the output is Markdown with the same skeleton.

For a short passage where a dedicated translation display tool is available in the session, use it — but only for a sentence or two, not for documents.

## Length and delivery

The usual input is a passage pasted straight into the conversation — an abstract, a paragraph, a section. Answer inline in the three-part format. Do not create files, and do not offer to, unless the user asks or the source arrived as a file.

For anything past a few thousand words:

1. Read the whole thing first. Terminology and antecedents resolve backward as often as forward, and translating section 1 without having seen section 4 produces exactly the inconsistencies described above.
2. Extract and confirm the glossary.
3. Translate section by section, in order, keeping the glossary fixed.
4. Do a numbers-and-citations pass at the end against the source. This is a mechanical check and it catches real errors.

If the source arrived as a file, write the translation to a file in the same format rather than dumping it into chat, and consult the relevant document skill for that format first.

## Worked contrasts

**Hedge preservation**
Source claim: results are compatible with a mechanism, with an explicit caveat about sample size.
Weak: "Our results prove the mechanism operates in this system."
Correct: "Our results are consistent with this mechanism, though the limited sample size means alternative explanations cannot be excluded."
The weak version is fluent, confident, and describes a study that was not performed.

**Sentence architecture, into English**
A single source sentence carrying a background clause, a contrast, a method, and a finding becomes three or four English sentences with explicit connectives. Word count may rise; claim count must not.

**Terminology**
A term rendered as "recognition" in the introduction, "identification" in the methods, and "detection" in the results reads to a reviewer as three different constructs. Pick one at glossary time.

**English → Traditional Chinese, in full**

Source:

> Although fertilization at anthesis has been reported to improve fruit set in *Fragaria* × *ananassa* 'Toyonoka', the evidence remains limited, and it is well known that the observed gains may be largely attributable to differences in the growing medium rather than to the treatment itself (Chen et al., 2021).

Weak — literal, heavy with 翻譯腔, wrong on two terms, and it upgrades the hedge:

> 雖然有報告證明在開花期進行受精可以極大地改善草莓「豐香」的結果，但證據仍然是有限的，並且眾所周知，被觀察到的提升可能是可以被歸因於生長材料的差異而不是處理本身。

Correct:

> 儘管已有研究指出，於開花期施肥可提高草莓（*Fragaria* × *ananassa*）'Toyonoka' 的著果率，相關證據仍然有限；所觀察到的提升，可能主要源自栽培介質的差異，而非處理本身（Chen et al., 2021）。

What moved. *Fertilization* here is 施肥, not 受精 — the hazard list flags this, and only the context (anthesis, fruit set, a treatment effect) resolves it. *Growing medium* is 栽培介質, not 生長材料. *Fruit set* is 著果率, a defined horticultural measurement, not the vernacular 結果. The binomial is restored in italics and the cultivar keeps its roman single quotes rather than becoming 「豐香」, since the source used the romanised form. `has been reported to improve` → 指出…可提高, not 證明; `may be attributable` keeps 可能; "it is well known that" drops, carrying no information in Chinese academic prose; 被觀察到的 and 可以被歸因 shed the passive; the citation is copied verbatim inside full-width parentheses.

Terminology would list fruit set / 著果率, anthesis / 開花期, growing medium / 栽培介質（台灣慣例；大陸多作「基质」）, and fertilization / 施肥 with the disambiguation as its basis. Notes would record that the cultivar was left in its romanised form and that 'Toyonoka' also circulates as 豐香 in Taiwanese literature, so the user can switch it.

## What this skill will not do

It does not invent citations, fill gaps in a source, or extend an argument. If a source passage is incomplete or corrupted, say so and translate what exists. If the user asks for content generation dressed as translation — writing the discussion section they have not written yet — that is a different request; do it if asked plainly, but do not deliver it under the label of a translation, because a supervisor or reviewer reading the target text will assume the source said this.
