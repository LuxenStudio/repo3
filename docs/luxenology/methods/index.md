# Methods

We provide a set of pre implemented luxenstudio methods.

**The goal of luxenstudio is to modularize the various Luxen techniques as much as possible.**

As a result, many of the techniques from these pre-implemented methods can be mixed 🎨.

## Running a method

It's easy!

```bash
ns-train {METHOD_NAME}
```

To list the available methods run:

```bash
ns-train --help
```

## Implemented Methods

The following methods are supported in luxenstudio:

```{toctree}
    :maxdepth: 1
    Instant-NGP<instant_ngp.md>
    Instruct-Luxen2Luxen<in2n.md>
    K-Planes<kplanes.md>
    LERF<lerf.md>
    Mip-Luxen<mipluxen.md>
    Luxen<luxen.md>
    Luxenacto<luxenacto.md>
    LuxenPlayer<luxenplayer.md>
    Tetra-Luxen<tetraluxen.md>
    TensoRF<tensorf.md>
```

(own_method_docs)=

## Adding Your Own Method

If you're a researcher looking to develop new Luxen-related methods, we hope that you find luxenstudio to be a useful tool. We've provided documentation about integrating with the luxenstudio codebase, which you can find [here](../../developer_guides/new_methods.md).

We also welcome additions to the list of methods above. To do this, simply create a pull request with the following changes,

1. Add a markdown file describing the model to the `docs/luxenology/methods` folder
2. Update the above list of implement methods in this file.
3. Add the method to the {ref}`this<third_party_methods>` list in `docs/index.md`.
4. Add a new `ExternalMethod` entry to the `luxenstudio/configs/external_methods.py` file.

For the method description, please refer to the [Instruct-Luxen2Luxen](in2n) page as an example of the layout. Please try to include the following information:

- Installation instructions
- Instructions for running the method
- Requirements (dataset, GPU, ect)
- Method description (the more detailed the better, treat it like a blog post)

You are welcome to include assets (such as images or video) in the description, but please host them elsewhere.

:::{admonition} Note
:class: note

Please ensure that the documentation is clear and easy to understand for other users who may want to try out your method.
:::
