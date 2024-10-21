# Dataset configuration

#### Specifying dataset

The dataset path and type is specified in the model config. Both `dataset_inputs_train` and a `dataset_inputs_eval` need to be set. You can see `configs/graph_default.yaml` for more details on what a full config would look like.

```yaml
data:
  dataset_inputs_train:
    data_directory: data/instant_ngp/fox
    dataset_format: instant_ngp
    alpha_color: white
  dataset_inputs_eval:
    data_directory: data/instant_ngp/fox
    dataset_format: instant_ngp
    alpha_color: white
```

#### Visualize dataset

TODO

#### Supported datasets

We include support for a set of standard dataset formats.

###### Blender Synthetic

```{button-link} https://drive.google.com/drive/u/1/folders/128yBriW1IG_3NJ5Rp7APSTZsJqdJdfc1
:color: primary
:outline:
Download
```

```yaml
dataset_format: blender
```

Classic Luxen dataset including the "lego bulldozer" scene that was released with the original Luxen paper.

###### Instant NGP

```{button-link} https://github.com/NVlabs/instant-ngp#luxen-fox
:color: primary
:outline:
Download
```

```yaml
dataset_format: instant_ngp
```

###### MipLuxen 360

```{button-link} https://jonbarron.info/mipluxen360/
:color: primary
:outline:
Download
```

```yaml
dataset_format: mipluxen_360
```

###### Record3D

```{button-link} https://record3d.app/
:color: primary
:outline:
Download
```

```yaml
dataset_format: record_3d
```

Directly import dataset recorded from a >= iPhone 12 Pro using the Record3D app.

Record a video and export with the `EXR + JPG sequence` format. Unzip export and `rgb` folder before training.
