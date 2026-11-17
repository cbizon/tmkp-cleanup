"""
The TMKP edge families this pipeline handles.

- chem_gene: chemical affects protein (increased/decreased activity or abundance), relation ChemicalToGeneAssociation
- gene_gene: protein affects protein, relation GeneRegulatoryRelationship
- chem_disease: chemical contributes_to disease or phenotype, relation ChemicalToDiseaseOrPhenotypicFeatureAssociation

Per family:
- relation, predicate: which TMKP edges belong to it (treats edges share chem_disease's relation)
- kind: how each role is described to Jev in the mapping question
- question: which relation question is asked per sentence (prompts.py), and so which answer supports an edge
- chemical_roles: roles whose mention is a chemical, for the chemical-name hard rules (rules.py)
- candidates: what a wrongly mapped mention of each role may be repaired to (repair_candidates.py)
"""

PROTEIN = "human protein (a UniProt entry: entry name, then protein name)"

FAMILIES = {
    "chem_gene": {
        "relation": "biolink:ChemicalToGeneAssociation",
        "predicate": "biolink:affects",
        "kind": {"subject": "chemical or drug", "object": PROTEIN},
        "question": "regulation",
        "chemical_roles": ("subject",),
        "candidates": {"subject": ("gene", "chemical"), "object": ("gene",)},
    },
    "gene_gene": {
        "relation": "biolink:GeneRegulatoryRelationship",
        "predicate": "biolink:affects",
        "kind": {"subject": PROTEIN, "object": PROTEIN},
        "question": "regulation",
        "chemical_roles": (),
        "candidates": {"subject": ("gene",), "object": ("gene",)},
    },
    "chem_disease": {
        "relation": "biolink:ChemicalToDiseaseOrPhenotypicFeatureAssociation",
        "predicate": "biolink:contributes_to",
        "kind": {"subject": "chemical or drug", "object": "disease or phenotype"},
        "question": "contributes_to",
        "chemical_roles": ("subject",),
        "candidates": {"subject": ("chemical",), "object": ("condition",)},
    },
}


def in_family(family: str, predicate: str, relation: str) -> bool:
    """
    True for a TMKP edge row of the family.

    >>> in_family("gene_gene", "biolink:affects", "biolink:GeneRegulatoryRelationship")
    True
    >>> in_family("chem_disease", "biolink:treats_or_applied_or_studied_to_treat",
    ...           "biolink:ChemicalToDiseaseOrPhenotypicFeatureAssociation")
    False
    """
    f = FAMILIES[family]
    return relation == f["relation"] and predicate == f["predicate"]
