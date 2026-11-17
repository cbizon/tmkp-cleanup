"""
Write each concept id's own name, for showing Jev what a mention was mapped to.

TMKP's nodes.tsv names an id by its whole NodeNorm clique as of the 2024 release, not by the id itself. Where Babel
merged an HP phenotype into a MONDO disease, the name is a different condition: HP:0004936 (Venous thrombosis) is
named "thrombophilia due to thrombin defect", HP:0002917 (Hypomagnesemia) "familial primary hypomagnesemia". Shown
those names, Jev rightly calls the mapping wrong, though TMKP mapped the words to the right id. This script takes
each id's own label from NodeNorm's equivalent identifiers, falling back to TMKP's name when NodeNorm has none, and
writes them in nodes.tsv's first two columns (gzipped id, name), so extract_sentences.py and build_pairs.py can
read it in place of nodes.tsv.gz.

Used for chem_disease. (chem_gene and gene_gene were run with TMKP's names; their concepts are mostly UniProt
proteins, whose names don't have this problem.)

    python concept_labels.py chem_disease edges.tsv.gz nodes.tsv.gz chem_disease_labels.tsv.gz
"""
import gzip
import json
import sys
import urllib.request

from families import in_family

NODENORM = "https://nodenormalization-sri.renci.org/get_normalized_nodes"


def own_labels(curies: list[str]) -> dict[str, str]:
    """NodeNorm's label for each id itself (not its clique's), where it has one; failures raise."""
    labels = {}
    for i in range(0, len(curies), 1000):
        body = json.dumps({"curies": curies[i:i + 1000], "conflate": True, "drug_chemical_conflate": False}).encode()
        req = urllib.request.Request(NODENORM, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as resp:
            for curie, result in json.load(resp).items():
                for e in (result or {}).get("equivalent_identifiers", []):
                    if e["identifier"] == curie and e.get("label"):
                        labels[curie] = e["label"]
    return labels


def main(family: str, edges_path: str, nodes_path: str, out_path: str) -> None:
    """Labels for every subject and object id of the family's edges."""
    with gzip.open(nodes_path, "rt") as f:
        names = {p[0]: p[1] for p in (line.rstrip("\n").split("\t") for line in f)}
    curies = set()
    with gzip.open(edges_path, "rt") as f:
        for line in f:
            p = line.split("\t", 15)
            if in_family(family, p[1], p[14]):
                curies.update((p[0], p[2]))
    labels = own_labels(sorted(curies))
    with gzip.open(out_path, "wt") as out:
        for curie in sorted(curies):
            out.write(f"{curie}\t{labels.get(curie) or names.get(curie) or ''}\n")
    changed = sum(1 for c in curies if c in labels and labels[c] != names.get(c))
    print(f"{len(curies)} ids; {len(labels)} with a NodeNorm label; {changed} differ from TMKP's name")


if __name__ == "__main__":
    main(*sys.argv[1:])
