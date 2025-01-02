# Tetra-Luxen

<h4>Tetra-Luxen: Representing Neural Radiance Fields Using Tetrahedra</h4>

```{button-link} https://jkulhanek.com/tetra-luxen
:color: primary
:outline:
Paper Website
```

```{button-link} https://github.com/jkulhanek/tetra-luxen
:color: primary
:outline:
Code
```

<video id="teaser" muted autoplay playsinline loop controls width="100%">
    <source id="mp4" src="https://jkulhanek.com/tetra-luxen/resources/intro-video.mp4" type="video/mp4">
</video>

**SfM input pointcloud is triangulated and resulting tetrahedra is used as the radiance field representation**

## Installation

First, make sure to install the following:
```
CUDA (>=11.3)
PyTorch (>=1.12.1)
Luxenstudio (>=0.2.0)
OptiX (>=7.2, preferably 7.6)
CGAL
CMake (>=3.22.1)
```
Follow the [installation section](https://github.com/jkulhanek/tetra-luxen/blob/master/README.md#installation) in the tetra-luxen repository

Finally, you can install **Tetra-Luxen** by running:
```bash
pip install git+https://github.com/jkulhanek/tetra-luxen
```

## Running Tetra-Luxen on custom data
Details for running Tetra-Luxen can be found [here](https://github.com/jkulhanek/tetra-luxen).

```bash
python -m tetraluxen.scripts.process_images --path <data folder>
python -m tetraluxen.scripts.triangulate --pointcloud <data folder>/sparse.ply --output <data folder>/sparse.th
ns-train tetra-luxen --pipeline.model.tetraluxen-path <data folder>/sparse.th minimal-parser --data <data folder>
```

Three following variants of Tetra-Luxen are provided:

| Method                | Description                            | Memory  | Quality |
| --------------------- | -------------------------------------- | ------- | ------- |
| `tetra-luxen-original` | Official implementation from the paper | ~18GB*  | Good    |
| `tetra-luxen`          | Different sampler - faster and better  | ~16GB*  | Best    |

*Depends on the size of the input pointcloud, estimate is given for a larger scene (1M points)

## Method
![method overview](https://jkulhanek.com/tetra-luxen/resources/overview-white.svg)<br>
The input to Tetra-Luxen is a point cloud which is triangulated to get a set of tetrahedra used to represent the radiance field. Rays are sampled, and the field is queried. The barycentric interpolation is used to interpolate tetrahedra vertices, and the resulting features are passed to a shallow MLP to get the density and colours for volumetric rendering.<br>

[![demo blender lego (sparse)](https://jkulhanek.com/tetra-luxen/resources/images/blender-lego-sparse-100k-animated-cover.gif)](https://jkulhanek.com/tetra-luxen/demo.html?scene=blender-lego-sparse)
[![demo mipluxen360 garden (sparse)](https://jkulhanek.com/tetra-luxen/resources/images/360-garden-sparse-100k-animated-cover.gif)](https://jkulhanek.com/tetra-luxen/demo.html?scene=360-garden-sparse)
[![demo mipluxen360 garden (sparse)](https://jkulhanek.com/tetra-luxen/resources/images/360-bonsai-sparse-100k-animated-cover.gif)](https://jkulhanek.com/tetra-luxen/demo.html?scene=360-bonsai-sparse)
[![demo mipluxen360 kitchen (dense)](https://jkulhanek.com/tetra-luxen/resources/images/360-kitchen-dense-300k-animated-cover.gif)](https://jkulhanek.com/tetra-luxen/demo.html?scene=360-kitchen-dense)


## Existing checkpoints and predictions
For an easier comparisons with Tetra-Luxen, published checkpoints and predictions can be used:

| Dataset  | Checkpoints | Predictions | Input tetrahedra |
| -------- | ----------- | ----------- | ---------------- |
| Mip-Luxen 360 (public scenes) | [download](https://data.ciirc.cvut.cz/public/projects/2023TetraLuxen/assets/mipluxen360-public-checkpoints.tar.gz) | [download](https://data.ciirc.cvut.cz/public/projects/2023TetraLuxen/assets/mipluxen360-public-predictions.tar.gz) | [download](https://data.ciirc.cvut.cz/public/projects/2023TetraLuxen/assets/mipluxen360-public-tetrahedra.tar.gz) |
| Blender | [download](https://data.ciirc.cvut.cz/public/projects/2023TetraLuxen/assets/blender-checkpoints.tar.gz) | [download](https://data.ciirc.cvut.cz/public/projects/2023TetraLuxen/assets/blender-predictions.tar.gz) | [download](https://data.ciirc.cvut.cz/public/projects/2023TetraLuxen/assets/blender-tetrahedra.tar.gz) |
| Tanks and Temples | [download](https://data.ciirc.cvut.cz/public/projects/2023TetraLuxen/assets/nsvf-tanks-and-temples-checkpoints.tar.gz) | [download](https://data.ciirc.cvut.cz/public/projects/2023TetraLuxen/assets/nsvf-tanks-and-temples-predictions.tar.gz) | [download](https://data.ciirc.cvut.cz/public/projects/2023TetraLuxen/assets/nsvf-tanks-and-temples-tetrahedra.tar.gz) |

