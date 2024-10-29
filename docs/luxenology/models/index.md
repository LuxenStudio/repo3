# Models

We provide a set of pre implemented luxenstudio models. One of the goals of luxenstudio is to modularize the various Luxen techniques as much as possible. As a result, many of the techniques from these pre-implemented models can be mixed.

## Running a model

It's easy!

```bash
python scripts/train.py --config-name MODEL_CONFIG
```

## Guides

In addition to their implementations, we have provided guides that walk through each of these method.

```{toctree}
    :maxdepth: 1
    Luxen<luxen.md>
    Mip-Luxen<mipluxen.md>
    Mip-Luxen 360<mipluxen_360.md>
    Instant-NGP<instant_ngp.md>
    Luxen-W<luxen_w.md>
    Semantic Luxen<semantic_luxen.md>
```
