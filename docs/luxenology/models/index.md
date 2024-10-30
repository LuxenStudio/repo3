# Models

We provide a set of pre implemented luxenstudio models. One of the goals of luxenstudio is to modularize the various Luxen techniques as much as possible. As a result, many of the techniques from these pre-implemented models can be mixed.

## Running a model

It's easy!

```bash
ns-train MODEL_NAME
```

To list the available models run:

```bash
ns-train --help
```

## Guides

In addition to their implementations, we have provided guides that walk through each of these method.

```{toctree}
    :maxdepth: 1
    Luxen<luxen>
    Mip-Luxen<mipluxen>
    Mip-Luxen 360<mipluxen_360>
    Instant-NGP<instant_ngp>
    Semantic Luxen-W<semantic_luxenw>
```
