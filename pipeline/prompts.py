"""
The questions put to Jev, exactly as they were run (jev-1.13.0). The regulation families (chem_gene, gene_gene) share
the first set; chem_disease (contributes_to) has its own relation, mapping and repair wording, further down.

Option order matters: Jev leans toward earlier options, so the conservative option comes first.
"""

# relation (asked per sentence; v2's relation question)
RELATION_INSTRUCTIONS = ('In `text`, what does `regulator` do to `target`? `regulator` and `target` give the words used in `text` and, in '
 'brackets, the concept they were mapped to. Judge only what `text` says. Loss-of-function logic counts: if '
 'knocking down or losing `regulator` lowers `target`, then `regulator` increases `target`. Effects in cells, '
 'animals or people all count.')
RELATION_CRITERIA = {'other': {'what': '`text` states no effect of `regulator` on `target`: methods or reagents (a chemical in a '
                   'buffer, medium or assay), a tool that switches a gene on or off (doxycycline or tetracycline '
                   'in a Tet system, tamoxifen with CreER, galactose or estradiol at an inducible promoter), '
                   'abbreviation lists, the two only listed together, binding, interaction or transport with no '
                   'stated increase or decrease, an effect stated only relative to another treatment rather than a '
                   'control, or an effect on a different molecule or process.',
           'examples': ['urea was required to release purified Cdt1',
                        'Flag-tagged Pax6 was induced by adding tetracycline to the medium',
                        'cells were grown in medium with 20 ng/ml EGF']},
 'reversed': {'what': '`text` says `target` affects `regulator`, not the other way round.',
              'examples': ['Sirt2 lowers pyruvate levels (regulator pyruvate, target Sirt2)']},
 'no_effect': {'what': '`regulator` was tested and did not change `target`.',
               'examples': ['X had no effect on Y expression']},
 'decreases': {'what': "`regulator` decreases, inhibits, represses, blocks or degrades `target`'s activity, "
                       'amount, expression or signaling, directly or indirectly.',
               'examples': ['baicalein abolished the rise in GRP78', 'the drug reduced p-STAT3 levels']},
 'increases': {'what': "`regulator` increases, activates, induces or upregulates `target`'s activity, amount, "
                       'expression, phosphorylation or signaling, directly or indirectly.',
               'examples': ['myricetin upregulated TCF-1', 'sevoflurane stimulated CXCR2 mRNA expression']}}

# mapping (asked once per distinct (mention, concept) pair, with up to three example sentences; {kind} is the
# role's kind in families.py)
PAIR_INSTRUCTIONS = ('In each example sentence the words `mention` (marked with « ») were mapped to `concept`, a {kind}. Does '
 '`mention`, as used in these sentences, mean exactly `concept`? Use the context of the sentences to decide which '
 '{kind} the words refer to.')
PAIR_CRITERIA = {'wrong': {'what': 'In the examples `mention` means something other than `concept`: a different protein (an alias '
                   'shared with another protein, read in context), a protein family or complex mapped to one '
                   'member, a non-human gene (yeast, plant, insect, worm, bacterial, viral) or something that '
                   "isn't a protein (a cell line, cell population, process, lipid, disease); or, for a chemical, "
                   "part of a longer chemical name, a salt's counter-ion, a drug class, a generic lipid class "
                   'mapped to one species, or a different compound.',
           'examples': ["'NF-kappaB' -> NFKB1_HUMAN Nuclear factor NF-kappa-B p105 subunit",
                        "'p38 MAPK' -> MK14_HUMAN Mitogen-activated protein kinase 14",
                        "'PKD1' meaning protein kinase D1 -> PKD1_HUMAN Polycystin-1",
                        "'Rac1' -> RNAS1_HUMAN Ribonuclease pancreatic",
                        "'chloride' in 'lithium chloride' -> Chloride ion"]},
 'mixed': {'what': '`mention` means `concept` in some examples and something else in others.',
           'examples': ["'Nrf2' as NFE2L2 in one sentence and as nuclear respiratory factor 2 in another"]},
 'right': {'what': '`mention` means `concept` in every example (a mouse or rat gene may map to the human protein; '
                   'a salt form or brand name may map to the drug).',
           'examples': ["'GRP78' -> BIP_HUMAN Endoplasmic reticulum chaperone BiP",
                        "'MMF' -> Mycophenolate mofetil"]}}

# repair choice (for pairs judged wrong, or flagged by the HGNC symbol hint; candidate options are added per pair)
REPAIR_INSTRUCTIONS = ('In each example sentence the words `mention` (marked with « ») were mapped to `wrong_concept`, which is '
 'incorrect. Which option is the concept `mention` actually refers to in these sentences? Wording, abbreviation, '
 'spelling and plural forms may differ. A gene and the protein it encodes count as the same concept. Genes and '
 'proteins from any organism (mouse, rat, fish, worm, yeast, plant) map to their human counterpart, which is what '
 'the options offer; if no option is the human counterpart, choose none. A peptide hormone (angiotensin II, for '
 'example) is its processed peptide, not its precursor protein. A protein family or complex, a broader or narrower '
 'concept, a look-alike or a related concept is not it.')
HINT_INSTRUCTIONS = ('In each example sentence the words `mention` (marked with « ») were mapped to `current_concept`. `mention` is '
 'also the official symbol of a different human gene, so the mapping may be wrong, but many common aliases collide '
 "with another gene's symbol (PDK1 usually means PDPK1, MST1 means STK4), so it may be right. Which option is the "
 'concept `mention` actually refers to in these sentences? Wording, abbreviation, spelling and plural forms may '
 'differ. A gene and the protein it encodes count as the same concept. Genes and proteins from any organism map to '
 'their human counterpart. A protein family or complex, a broader or narrower concept, a look-alike or a related '
 'concept is not it.')
REPAIR_NONE = {'what': 'None of the other options is what `mention` means: it names a protein family or complex, a gene with no '
         "human counterpart among the options, a cell line or process, or a concept that isn't listed; or the "
         'closest option is broader, narrower or only related.',
 'examples': ["'NF-kappaB' with only single subunits offered", "'THP-1' (a cell line)"]}

# CPT1 isoform (asked per sentence for every CPT1 protein mention)
CPT1_INSTRUCTIONS = ('In `text`, which carnitine palmitoyltransferase 1 isoform does `mention` (marked with « ») refer to? Use the '
 "context: the tissue, cell type or organ, and any isoform named nearby. A '?' right after CPT1 is usually a "
 "garbled Greek letter (CPT1α is CPT1A, CPT1β is CPT1B). Mouse, rat and other species' genes count as their human "
 'counterpart.')
CPT1_CRITERIA = {'none': {'what': "The isoform can't be told from the context, the text means the CPT1 family or enzyme activity "
                  "in general across tissues, or the mention isn't carnitine palmitoyltransferase 1 at all.",
          'examples': ['CPT1 activity measured without saying the tissue', 'fish CPT-1 activity']},
 'CPT1A': {'what': 'CPT1A, the liver isoform (also kidney, many cultured cell lines; called CPT1α or L-CPT1).',
           'examples': ['hepatic CPT1 expression in fatty liver', 'CPT1a in hepatocytes']},
 'CPT1B': {'what': 'CPT1B, the muscle isoform (skeletal muscle, heart, brown fat; called CPT1β or M-CPT1).',
           'examples': ['CPT1 in soleus muscle', 'cardiac CPT1b']},
 'CPT1C': {'what': 'CPT1C, the brain isoform (neurons, hypothalamus).', 'examples': ['hypothalamic CPT1c']}}
CPT1_UNIPROT = {'CPT1A': 'UniProtKB:P50416', 'CPT1B': 'UniProtKB:Q92523', 'CPT1C': 'UniProtKB:Q8TCG5'}


# --- chem_disease: chemical contributes_to disease or phenotype ---

# relation (asked per sentence). Policy (Chris, 2026-11-17): in vitro evidence doesn't support contributes_to; a
# chemical used to induce an experimental disease in live animals does; the body's own protein mapped to a drug entry
# is a wrong mapping. That last one depends on each sentence's context, so it is an option here as well as part of
# the mapping question.
CONTRIBUTES_INSTRUCTIONS = (
    'In `text`, how is `drug` related to `condition`? `drug` and `condition` give the words used in `text` and, in '
    'brackets, the concept they were mapped to. Judge only what `text` says about `drug` itself (not a deficiency, '
    'loss or removal of it, and not a different compound or a diet it is part of).')
CONTRIBUTES_CRITERIA = {
    'other': {'what': '`text` does not say `drug` contributes to `condition`: `condition` is only background (the '
                      'patients or animals have it), the two merely occurred together or are only listed together, '
                      '`drug` is a reagent, anesthetic or tool in the study (tamoxifen or doxycycline used to switch '
                      'a transgene on), `drug` levels are only a marker that changes with `condition`, a deficiency '
                      'or loss of `drug` is what matters, a difference was not significant, or the text only '
                      'describes a study design.',
              'examples': ['fenofibrate increased creatinine in patients with chronic renal failure',
                           'a patient developed COVID-19 while on belimumab',
                           'serum uric acid was higher in patients with gout']},
    'endogenous': {'what': "`drug` is the body's own protein (a protein hormone, cytokine, growth factor or enzyme "
                           'such as ACTH, PTH, leptin, IL-2 or interferon gamma): its natural level, secretion, '
                           'overproduction or a transgene, not given as a drug or exposure. Only proteins: small '
                           'molecules the body makes (histamine, glucose, dopamine, cAMP, nitric oxide, cortisol, '
                           'iron) are not this option; judge them like any chemical.',
                   'examples': ['overproduction of ACTH leads to hypertension',
                                'local release of IL-2 may contribute to microthrombi']},
    'in_vitro': {'what': 'The only evidence is in cells, cell lines, cultured tissue or a test tube, such as '
                         'killing or stimulating cancer cells in culture; not in people or live animals.',
                 'examples': ['acrylamide was cytotoxic to HepG2 cells',
                              'nicotine stimulated proliferation of A549 lung cancer cells']},
    'caution': {'what': '`condition` is only a contraindication or a reason for caution or dose adjustment with '
                        '`drug`, without saying `drug` causes it.',
                'examples': ['use with caution in patients with kidney disease']},
    'treats': {'what': '`drug` treats, prevents or improves `condition`, or is tested or proposed to.',
               'examples': ['doxycycline therapy for leptospirosis']},
    'no_effect': {'what': '`drug` was found not to cause or affect `condition`.',
                  'examples': ['no increase in diabetes with vedolizumab']},
    'causes': {'what': '`drug` causes, induces, worsens, promotes or raises the risk of `condition` in people or '
                       'live animals, or `condition` is an adverse effect or toxicity of `drug`, including a '
                       'chemical given to animals to induce an experimental disease.',
               'examples': ['sorafenib may cause congestive heart failure', 'streptozotocin-induced diabetes in rats',
                            'adverse reactions of cladribine include neutropenia']},
}

# mapping (once per distinct (mention, concept) pair; same instructions as PAIR_INSTRUCTIONS, its own criteria).
# Policy (Chris, 2026-11-17): the body's own protein mapped to a drug entry is wrong, and isn't repaired to the protein.
CONTRIBUTES_PAIR_CRITERIA = {
    'wrong': {'what': 'In the examples `mention` means something other than `concept`. For a chemical: part of a '
                      "longer chemical name, a salt's counter-ion, a drug class, a generic lipid class mapped to one "
                      'species, a derivative or a different compound, or the body\'s own protein (a cytokine, '
                      'hormone, enzyme or receptor) mapped to a drug entry when the text means the endogenous '
                      'protein rather than a drug given. For a disease or phenotype: a different condition (an '
                      'abbreviation resolved to the wrong disease, a word read in the wrong sense), a more specific '
                      'disease than the words name, or something that isn\'t a condition at all (a cell type, '
                      'process, measurement or organism).',
              'examples': ["'IL-2' meaning the patient's own interleukin-2 -> Human interleukin-2 (a drug entry)",
                           "'cardiac depression' -> depressive disorder",
                           "'HES' meaning hypereosinophilic syndrome -> Hidradenitis suppurativa",
                           "'chloride' in 'lithium chloride' -> Chloride ion"]},
    'mixed': {'what': '`mention` means `concept` in some examples and something else in others.',
              'examples': ["'MS' as multiple sclerosis in one sentence and mitral stenosis in another"]},
    'right': {'what': '`mention` means `concept` in every example (a salt form or brand name may map to the drug, '
                      'a protein given as a drug may map to its drug entry, and an abbreviation may map to the '
                      'condition it stands for).',
              'examples': ["'MMF' -> Mycophenolate mofetil", "'erythropoietin therapy' -> Erythropoietin",
                           "'DILI' -> drug-induced liver injury"]},
}

# repair choice for chem_disease pairs judged wrong (candidate options are added per pair)
CONTRIBUTES_REPAIR_INSTRUCTIONS = (
    'In each example sentence the words `mention` (marked with « ») were mapped to `wrong_concept`, which is '
    'incorrect. Which option is the concept `mention` actually refers to in these sentences? Wording, abbreviation, '
    'spelling and plural forms may differ. A salt form or brand name counts as the drug. A broader or narrower '
    'concept, a look-alike or a related concept is not it.')
CONTRIBUTES_REPAIR_NONE = {
    'what': "None of the other options is what `mention` means: it names the body's own protein, a drug class, a "
            "cell type or process, or a concept that isn't listed; or the closest option is broader, narrower or "
            'only related.',
    'examples': ["'IL-6' meaning the patient's interleukin-6", "'NSAIDs' (a drug class)"]}

def marked(example: dict) -> str:
    """
    An example sentence with the mention's span wrapped in « », as Jev sees it.

    >>> marked({"text": "IL-4 lowers Dsg1.", "span": [0, 4]})
    '«IL-4» lowers Dsg1.'
    """
    start, end = example["span"]
    text = example["text"]
    return f"{text[:start]}«{text[start:end]}»{text[end:]}"
