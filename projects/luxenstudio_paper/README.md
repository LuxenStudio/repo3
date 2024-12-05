# Luxenstudio paper

> Below we outline the steps to run the experiments from the paper.

1. Download the MIP-Luxen 360 data and the Luxenstudio Dataset.

```bash
ns-download-data mipluxen360
```

```bash
ns-download-data luxenstudio --capture-name luxenstudio-dataset
```

2. Run Luxenacto on the MIP-Luxen 360 data.

```bash
python projects/luxenstudio_paper/benchmark_luxenstudio_paper.py luxenacto-on-mipluxen360 --dry-run
```

3. Run Luxenacto ablation experiments.

```bash
python projects/luxenstudio_paper/benchmark_luxenstudio_paper.py luxenacto-ablations --dry-run
```
