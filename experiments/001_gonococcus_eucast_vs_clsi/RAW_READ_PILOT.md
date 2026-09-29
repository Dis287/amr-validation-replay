# One-isolate raw-read assembly pilot

## Scope and provenance

- Hicks S7 dataset 2 run: `ERR1067709`; AZM MIC 0.5 µg/mL.
- ENA paired FASTQs: 86,006,426 and 85,691,168 compressed bytes. Both
  downloaded files matched the MD5 values in `ena_dataset2_manifest.tsv`:
  `24813e50f500f8559f2993f842596d39` and
  `0c5fdb42e078bfe6bdc0729b85e9570e`.
- Historical SPAdes 3.13.0 was downloaded from its official release, but
  failed on this Python 3.12/Linux runtime (old `collections.Hashable` API;
  a local compatibility shim got past Python startup, after which its native
  `spades-hammer` exited with signal 11). No historical assembly resulted.
- **Feasibility run:** official SPAdes 4.3.0 Linux binary, default paired-end
  genome assembly, `-t 2 -m 8`, with read correction enabled. Hicks's exact
  SPAdes version was not identified in the inspected methods. This is not
  claimed to reproduce their input matrix.

## Measured outcome

The 4.3.0 assembly completed with one warning recommending `--isolate`
because the reads appeared to have high uniform coverage. That option was
**not** applied; changing it would change the declared pilot procedure.

| Measure | Observed |
| --- | ---: |
| Wall time, directory creation to contigs output | 16 min 26 sec |
| Full SPAdes output directory after completion | 161 MB (`du -sh`) |
| SPAdes logged maximum current memory | 1,354 MiB |
| Unfiltered contigs / total bases / N50 | 395 / 2,142,914 / 60,512 bp |
| Filtered contigs / total bases / N50 | 135 / 2,118,820 / 60,512 bp |
| Direct distinct forward 31-mers after filter | 2,095,091 |
| `contigs.fasta` SHA-256 | `abcec97b2e7b47dc39614fcd6b5ea6a2f364f86a46c64bc38bfc42e8e7ee8c5b` |

The pilot filter kept contigs of length at least 200 bp with the SPAdes
header's `_cov_` field at least 10. The paper also mentions a dataset-wide
N50 exclusion rule; **one isolate cannot test that rule**. Its coverage
calculation and software version may differ. The forward 31-mer count above
is a direct Python count, **not** DSK/SEER's final combined binary matrix or
canonicalized k-mer count; it is included only to size this pilot.

## Interpretation

Public reads can be retrieved, checksum-verified, and assembled in this
workspace one isolate at a time. This does **not** establish that 1,102 runs,
the paper's SPAdes-derived 31-mer union, Kover/ranger training, or ten outer
partitions fit available resources. The observed single-isolate runtime
must not be multiplied into a claimed total without sampling input-size and
compute variation. No model prediction or balanced accuracy was generated.

Next: recover the original prediction/fold or SPAdes assembly artifacts if
available; otherwise test DSK/SEER feature generation on this pilot and
resource-plan the complete dataset-2 reconstruction before downloading all
344.84 GB of compressed reads.
