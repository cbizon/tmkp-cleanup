# tmkp-cleanup

Code and validation for cleaning the Text Mining KP (TMKP) knowledge graph before it goes into Translator.

TMKP is a frozen text-mined KGX release (2024-09-07,
`https://storage.googleapis.com/translator-text-workflow-dev-public/kgx/UniProt/`). Many of its edges are
misreadings of the sentence they came from, or rest on a mention mapped to the wrong concept. This repo asks
[Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev), TypeSafe's typed-decision model, about each
supporting sentence, and turns the answers into fixed lists of edges to drop, sentences to prune and edges to repair.

The lists are published at `https://stars.renci.org/var/translator/ingests/tmkp/`. The TMKP ingest in
[translator-ingests](https://github.com/NCATSTranslator/translator-ingests) downloads them and applies them; it
doesn't run this code or call any model.

| Directory | Edges | Published files |
|---|---|---|
| [`treats/`](treats/README.md) | Chemical → disease `treats_or_applied_or_studied_to_treat` | `tmkp_treats_jev_v3_dropped_edges.txt.gz` |
| [`regulation/`](regulation/README.md) | Chemical → protein and protein → protein `affects` (increased/decreased) | `tmkp_{chem_gene,gene_gene}_{dropped_edges.txt.gz,pruned_sentences.txt.gz,repaired_edges.tsv.gz}` |

Each directory's README covers the method, policy decisions, results, validation, cost and how to reproduce the
files. Labels in the `validation/` folders were made by Claude instances working blind to Jev's answers from written
rubrics.

Chemical → disease `contributes_to` edges aren't cleaned yet.

## Running

The scripts are plain Python (standard library) except the ones that call Jev, which declare their dependency
(`typesafe-sdk==0.7.2`) as inline script metadata, so `uv run <script>` installs it. Run each script from its own
directory. Doctests run per directory, since both have an `extract_sentences.py`:

```bash
(cd treats && uv run pytest) && (cd regulation && uv run pytest)
```

**The API key.** The Jev scripts read the key from `TYPESAFE_API_KEY` and stop if it isn't set. Don't type the key
on the command line or put it in a file in the repo: it would end up in shell history or git. Keep it in a secret
store and fill the variable from there for the one command, so the key exists only in that process's environment.
For example, from the macOS Keychain, where it was stored once with
`security add-generic-password -a "$USER" -s typesafe -w` (which prompts for the key rather than taking it as an
argument):

```bash
TYPESAFE_API_KEY="$(security find-generic-password -s typesafe -w)" uv run score_sentences.py ...
```

Elsewhere, use your own secret store the same way (for example `"$(op read 'op://<vault>/TypeSafe/credential')"`
with 1Password), or a secret the job runner mounts as an environment variable.

## What's published and what isn't

Only the ingest files on stars are published. The full runs' recorded Jev answers and repair candidates are not;
each `validation/` folder holds the subset of answers its evaluation needs.
