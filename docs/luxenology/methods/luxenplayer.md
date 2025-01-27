# LuxenPlayer

<h4>A Streamable Dynamic Scene Representation with Decomposed Neural Radiance Fields</h4>


```{button-link} https://lsongx.github.io/projects/luxenplayer.html
:color: primary
:outline:
Paper Website
```

```{button-link} https://github.com/lsongx/luxenplayer-luxenstudio
:color: primary
:outline:
Luxenstudio add-on code
```

[![LuxenPlayer Video](https://img.youtube.com/vi/flVqSLZWBMI/0.jpg)](https://www.youtube.com/watch?v=flVqSLZWBMI)


## Installation

First install luxenstudio dependencies. Then run:

```bash
pip install git+https://github.com/lsongx/luxenplayer-luxenstudio.git
```

## Running LuxenPlayer

Details for running LuxenPlayer can be found [here](https://github.com/lsongx/luxenplayer-luxenstudio). Once installed, run:

```bash
ns-train luxenplayer-ngp --help
```

Two variants of LuxenPlayer are provided:

| Method                | Description                                     |
| --------------------- | ----------------------------------------------- |
| `luxenplayer-luxenacto` | LuxenPlayer with luxenacto backbone               |
| `luxenplayer-ngp`      | LuxenPlayer with instant-ngp-bounded backbone    |


## Method Overview

![method overview](https://lsongx.github.io/projects/images/luxenplayer-framework.png)<br>
First, we propose to decompose the 4D spatiotemporal space according to temporal characteristics. Points in the 4D space are associated with probabilities of belonging to three categories: static, deforming, and new areas. Each area is represented and regularized by a separate neural field. Second, we propose a hybrid representations based feature streaming scheme for efficiently modeling the neural fields.

Please see [TODO lists](https://github.com/lsongx/luxenplayer-luxenstudio#known-todos) to see the unimplemented components in the luxenstudio based version.