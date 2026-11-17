# TMKP sentence-level filter and repairs

Three TMKP edge families are judged one supporting sentence at a time, with the same pipeline:

| Family | Edge | Relation | Edges | Sentences | Unsupported as mapped (blind sample) |
|---|---|---|---|---|---|
| `chem_gene` | chemical `affects` protein (increased/decreased) | `ChemicalToGeneAssociation` | 683,406 | 1,502,246 | 58% |
| `gene_gene` | protein `affects` protein (increased/decreased) | `GeneRegulatoryRelationship` | 343,983 | 589,036 | 93% |
| `chem_disease` | chemical `contributes_to` disease or phenotype | `ChemicalToDiseaseOrPhenotypicFeatureAssociation` | 122,391 | 234,717 | 39% |

In the regulation families the main problem is a mention mapped to the wrong concept ("COX-2" to a mitochondrial
cytochrome c oxidase subunit, "Nrf2" to GABPA, "IL-4" to the drug binetrakin), and protein → protein sentences often
state no regulation at all. In `chem_disease` few mappings are wrong (about 2% of sentences); most unsupported
sentences mention the condition only as background, say the drug treats it, or rest on cell-culture evidence.

`families.py` holds what differs between families: which edges belong, how each role is described to Jev, which
relation question is asked, which mentions are chemicals, and what a wrong mention may be repaired to. For each family
this directory decides every sentence (keep, repair or drop) and produces three files the ingests download from
`https://stars.renci.org/var/translator/ingests/tmkp/`:

| File (`<family>` = `chem_gene`, `gene_gene` or `chem_disease`) | Contents | Ingest use |
|---|---|---|
| `tmkp_<family>_dropped_edges.txt.gz` | (edge id, direction) pairs | Edges dropped: none of their sentences support them as mapped |
| `tmkp_<family>_pruned_sentences.txt.gz` | (edge id, direction, sentence id) | Sentences removed from kept edges' evidence |
| `tmkp_<family>_repaired_edges.tsv.gz` | Edges in TMKP's `edges.tsv` column layout | New edges for sentences repaired to the right concepts (read as the `repaired_edges` reader) |

TMKP's edge id ignores the direction qualifier (an increased and a decreased edge for the same pair share one id) and
the predicate, so the ingests match these lists on relation, id and direction. `contributes_to` edges have no
direction; their lists carry an empty one. They share their relation with TMKP's treats edges (`../treats/`), which
are kept apart by predicate.

## Decisions

Each sentence is decided in this order (`build_repairs.decide`):

1. **Source defect.** A mention span missing or past the end of the text: drop.
2. **Hard rules** (`rules.py`): drop.
   - a protein mention naming a family or complex mapped to one member ("NF-κB" → NFKB1, "p38 MAPK" → MAPK14, "PKC")
   - a chemical mention cut from a longer name ("chloride" from lithium chloride, "acetate" from PMA)
   - a generic lipid class mapped to one molecular species ("diacylglycerol" → diacylglycerol (18:0/…))
   - an unlabeled chemical mention mapped to an isotope-labeled compound
3. **Each mention's concept.**
   - **Per pair.** The mapping is judged once per distinct (mention, concept) pair (52,113 chem_gene, 48,503
     gene_gene, 19,103 chem_disease), from up to three example sentences. TMKP grounds a string the same way
     everywhere, so one verdict covers every sentence with the pair.
   - **Pairs judged wrong** (P(wrong) ≥ 0.9) go to repair: candidates from exact HGNC matches and NameRes, and Jev
     chooses one or none from the examples. A choice at P ≥ 0.9 repairs the mention; otherwise the sentence is
     dropped.
   - **HGNC symbol hint** (proteins only). A protein mention that is exactly another gene's approved symbol is a hint,
     not a rule: common aliases collide with other genes' symbols ("PDK1" usually means PDPK1, "MST1" means STK4).
     These pairs get an extra "keep the current mapping" option and are kept, repaired or dropped at P ≥ 0.7.
   - **CPT1** is chosen per sentence (CPT1A liver, CPT1B muscle and heart, CPT1C brain, or none) from context, at
     P ≥ 0.7.
4. **Relation**, asked per sentence, P ≥ 0.7 to keep:
   - regulation: the sentence says the regulator raises (or lowers) the target, in the edge's direction
   - contributes_to: the sentence says the chemical causes, induces, worsens or raises the risk of the condition
5. **Outcome.** A sentence whose concepts are unchanged is kept on its edge. One with a changed concept moves to a
   repaired edge between the corrected concepts: in regulation only if the target is a gene product, in
   contributes_to only if the subject isn't one. An original edge with no kept sentence is dropped.

**Concept names (chem_disease).** Jev sees what a mention was mapped to by name. TMKP's `nodes.tsv` names an id by its
whole NodeNorm clique as of the 2024 release, and where Babel merged an HP phenotype into a MONDO disease that name is
a different condition: HP:0004936 (Venous thrombosis) is named "thrombophilia due to thrombin defect". Shown those
names, Jev called correct mappings wrong. `concept_labels.py` writes each id's own NodeNorm label instead, and the
chem_disease run uses it (1,426 of 11,436 ids get a different name). Those merges are Babel's to fix; this pipeline
judges TMKP's mapping of the words to the id.

Policy decisions, made by Chris Bizon:

- **Map everything to human,** as TMKP's design does. A gene from any organism (mouse, rat, fish, yeast, plant) maps
  to its human counterpart, or to none if there isn't one. Candidates are human UniProt proteins.
- **A protein family or complex mapped to one member is wrong,** with two exceptions: "HIF-1" → HIF1A, which matches
  how HIF-1α is handled, and CPT1, chosen per sentence.
- **Cell-line evidence counts for regulation edges, not for contributes_to.** Contributing to a disease is a claim
  about people or animals, as for treats.
- **A chemical used to induce an experimental disease in live animals contributes to it** ("streptozotocin-induced
  diabetes in rats").
- **The body's own protein mapped to a drug entry is wrong in contributes_to** ("IL-2" meaning the patient's
  interleukin-2, mapped to the DrugBank biologic), and is dropped, not repaired to the protein. The relation question
  has an "endogenous" option for it too, since the same words can mean a drug given in one sentence and the body's
  protein in the next. Small molecules the body makes (glucose, histamine, cortisol) are judged like any chemical.
- **Processed peptides use Protein Ontology ids,** not ChEBI and not their precursor protein. These are angiotensin
  I–IV, 1–7 and 1–9, and amyloid beta peptide (`repair_candidates.PEPTIDES`). PR's gene-level protein classes aren't
  merged with their genes in NodeNorm, so no other PR ids are offered.
- **Gene → gene edges are regulation.** An edge whose regulator is a gene product is emitted as
  `GeneRegulatesGeneAssociation`, predicate `biolink:regulates`, qualified predicate `causes`, as SIGNOR models it.
  This covers repaired edges from either regulation family and every kept protein → protein edge, which TMKP itself
  labels `affects`. A chemical regulator stays `ChemicalAffectsGeneAssociation` / `biolink:affects`.

The questions and their options are in `prompts.py`, exactly as run.

## Result

| Sentences | chem_gene | | gene_gene | | chem_disease | |
|---|---|---|---|---|---|---|
| Kept as mapped | 891,865 | 59.4% | 72,810 | 12.4% | 149,499 | 63.7% |
| Repaired | 93,149 | 6.2% | 13,336 | 2.3% | 494 | 0.2% |
| Dropped | 517,232 | 34.4% | 502,890 | 85.4% | 84,724 | 36.1% |

Drops by reason (sentences):

| Reason | chem_gene | gene_gene | chem_disease |
|---|---|---|---|
| Relation not supported | 291,754 | 391,509 | 75,445 |
| Wrong mapping, no repair | 100,989 | 68,927 | 3,919 |
| Fragment rule | 61,045 | — | 3,967 |
| Family/complex rule | 43,053 | 30,238 | — |
| Lipid-species rule | 12,516 | — | 1,389 |
| Symbol hint unresolved | 4,937 | 6,213 | — |
| CPT1 unresolved | 1,476 | 209 | — |
| Isotope rule | 1,105 | — | — |
| Span defect | 355 | 5,794 | 4 |

The chemical rules (fragment, lipid, isotope) apply only to chemical mentions; the family rule, symbol hint and CPT1
only to proteins.

Repairs (sentences):

| Repair | chem_gene | gene_gene | chem_disease |
|---|---|---|---|
| Symbol-hint repairs | 43,804 | 8,468 | — |
| Other wrong pairs | 47,485 | 4,842 | 494 |
| CPT1 isoforms | 1,195 | 26 | — |

Edges:

| Edges | chem_gene | gene_gene | chem_disease |
|---|---|---|---|
| Original, kept | 407,085 | 43,893 | 76,390 |
| Original, dropped | 276,321 | 300,090 | 46,001 |
| Sentences pruned from kept edges | 112,601 | 22,538 | 20,266 |
| Repaired (new) edges | 37,891 (35,021 `affects`, 2,870 `regulates`) | 6,880 (all `regulates`) | 297 (all `contributes_to`) |

For example, the binetrakin → desmoglein-1 edge is dropped, and its five sentences now support IL-4
(UniProtKB:P05112) `regulates` desmoglein-1, decreased.

## Validation

Everything here was checked against samples labeled blind to Jev's answers, by separate Claude instances working
from written rubrics. Re-score a family from `validation/<family>/` with:

```bash
python evaluate_filter.py validation/chem_gene
python evaluate_repairs.py validation/chem_gene
python evaluate_filter.py validation/gene_gene
python evaluate_repairs.py validation/gene_gene
python evaluate_filter.py validation/chem_disease
python evaluate_repairs.py validation/chem_disease
```

| Check | Sample | Result |
|---|---|---|
| chem_gene filter: sentences not kept on their edge as mapped | 300 held-out sentences (174 unsupported) | precision 0.96, recall 0.77; supported share among kept sentences rises from 42% to 75% |
| chem_gene repairs of pairs judged wrong | 100 pairs | 90% of acted-on choices correct (99.6% by sentences) |
| chem_gene HGNC symbol-hint pairs (keep or repair) | 70 pairs | 94% correct (99.8% by sentences) |
| gene_gene filter | 300 pilot sentences (278 unsupported) | precision 0.99, recall 0.97; supported share among kept sentences rises from 7% to 69% |
| gene_gene repairs (wrong and symbol-hint pairs) | 80 pairs | 92% of acted-on choices correct (97.1% by sentences) |
| chem_disease filter | 300 held-out sentences (116 unsupported) | precision 0.85, recall 0.86; supported share among kept sentences rises from 61% to 91% |
| chem_disease repairs | 80 pairs | 88% of acted-on choices correct (97.1% by sentences) |

- **chem_gene:** the held-out sample was drawn after the pilot that shaped the prompts and rules, and excludes the
  pilot's edges.
- **gene_gene:** the sample is that family's pilot. Nothing was tuned on it: the gene_gene run reuses the chem_gene
  prompts, rules and thresholds, changing only the description of the regulator. With only 29 kept sentences in the
  sample, the 69% is a rough figure.
- **chem_disease:** the October 2026 pilot sample (300 sentences, relabeled under the final policies) was the
  development set. The relation question was revised twice against it: an "endogenous protein" option, then
  limiting that option to proteins. The held-out sample (one sentence from each of 300 random edges, none from the
  development set) was scored once, with the final question.

Known limits:

- **Repair mistakes are concentrated in small pairs** (1–25 sentences): a peptide analog, a cell line, a family
  name, an alias read the wrong way, a rare condition matched to a near neighbor.
- **Missed repairs.** About 13 of 100 chem_gene, 11 of 80 gene_gene and 23 of 80 chem_disease sampled pairs had a
  right candidate that wasn't accepted at the threshold. Those sentences are dropped, not repaired. In chem_disease
  many are lipid classes offered under several equivalent ids, which splits Jev's probability.
- **chem_disease precision is lower** than the regulation families': its relation calls are closer (hedged or
  associative claims, case reports).
- **The fragment rule misfires on some names** ("D-fenfluramine", "Fructose-Induced", "piperacillin-tazobactam"): 3
  of the 17 supported chem_disease held-out sentences that are dropped. It is left as is, since changing it would
  change the published chem_gene files.
- **Most protein → protein evidence is gone.** 87% of those edges are dropped. That matches the pilot (93% of
  sentences unsupported), but the family is now small.
- **Repair labels were partly re-adjudicated.** The chem_gene repair-sample labels predate the human-only rule. 18
  rows about non-human genes were re-adjudicated under it, recorded in
  `validation/chem_gene/repair_labels_human_overrides.json`. The other families' labels were made under the final
  rules.

## Reproducing

Run from this directory, with a data directory holding TMKP's `edges.tsv.gz`, `nodes.tsv.gz` and HGNC's
`hgnc_complete_set.txt`. Steps 3, 5, 6 and 7 call Jev and need `TYPESAFE_API_KEY`: fill it from a secret store for
the one command (see `../README.md`). `uv run` installs the SDK from each script's inline metadata. Set `F` to the
family, and `N` to `nodes.tsv.gz` for chem_gene and gene_gene or to the step 0 output for chem_disease:

```bash
F=chem_disease   # or chem_gene, gene_gene
python concept_labels.py $F edges.tsv.gz nodes.tsv.gz data/${F}_labels.tsv.gz                    # 0. names (chem_disease)
N=data/${F}_labels.tsv.gz                                                                        # nodes.tsv.gz otherwise
python extract_sentences.py $F edges.tsv.gz $N data/${F}_sentences.jsonl                        # 1. sentences
python build_pairs.py $F edges.tsv.gz $N data/${F}_pairs.jsonl                                  # 2. distinct pairs
uv run score.py --family $F pairs data/${F}_pairs.jsonl data/${F}_pair_scores.jsonl pair_errors.jsonl
uv run score.py --family $F relation data/${F}_sentences.jsonl data/${F}_relation_scores.jsonl rel_errors.jsonl
python repair_candidates.py $F data/${F}_pairs.jsonl data/${F}_pair_scores.jsonl \
    hgnc_complete_set.txt data/${F}_repair_candidates.jsonl                                     # 4. candidates
python normalize_candidates.py data/${F}_repair_candidates.jsonl \
    data/${F}_repair_candidates_norm.jsonl hgnc_complete_set.txt
uv run choose_repairs.py $F data/${F}_repair_candidates_norm.jsonl data/${F}_pairs.jsonl \
    data/${F}_repair_choices.jsonl                                                              # 6. repair choices
uv run choose_cpt1.py data/${F}_sentences.jsonl data/${F}_cpt1_choices.jsonl                    # 7. CPT1
cp edges.tsv.gz data/ && python build_repairs.py $F data                                        # 8. decide and write
```

- **Steps 1, 2 and 8 are deterministic.** Given the same Jev answers and candidates, step 8 reproduces the published
  files exactly. (After the move to this directory and the third family, rebuilding chem_gene and gene_gene from
  their recorded answers gives files byte-identical to the published ones.)
- **Steps 0 and 4 depend on live services** (NodeNorm, NameRes), and Jev's answers vary slightly between runs. In a
  71-call check against the original chem_gene run, 70 gave the same answer. So a full rerun gives nearly, not
  exactly, the published files.
- **chem_disease has no CPT1 mentions,** so step 7 writes an empty file; build_repairs still reads it.
- **Only the three ingest files per family are published.** The original runs' Jev answers and repair candidates
  aren't; the answers this directory's validation needs are in `validation/`.

**Cost.** Jev charges $0.042 per million input tokens, and output is free.

- chem_gene: about $63, $2.12 for the pair questions and $60.81 for the relation questions.
- gene_gene: about $26, $2.24 for the pair questions and $25.51 for the relation questions.
- chem_disease: about $13, $11.50 for the relation questions and $1.46 for two runs of the pair questions (the first,
  with TMKP's clique names, was discarded).
- The repair choices, CPT1 choices and the validation runs added well under a dollar each.
