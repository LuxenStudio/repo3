# Mip-Luxen

<h4>A Multiscale Representation for Anti-Aliasing Neural Radiance Fields</h4>

```{button-link} https://jonbarron.info/mipluxen/
:color: primary
:outline:
Paper Website
```

### Running Model

```bash
python scripts/train.py --config-name=graph_mipluxen.yaml
```

## Overview

```{image} imgs/mipluxen/models_mipluxen_pipeline-light.png
:align: center
:class: only-light
```

```{image} imgs/mipluxen/models_mipluxen_pipeline-dark.png
:align: center
:class: only-dark
```

The primary modification in MipLuxen is in the encoding for the field representation. With the modification the same _mip-Luxen_ field can be use for the coarse and fine steps of the rendering hierarchy.

```{image} imgs/mipluxen/models_mipluxen_field-light.png
:align: center
:class: only-light
:width: 400
```

```{image} imgs/mipluxen/models_mipluxen_field-dark.png
:align: center
:class: only-dark
:width: 400
```

In the field, the Positional Encoding (PE) is replaced with an Integrated Positional Encoding (IPE) that takes into account the size of the sample.
