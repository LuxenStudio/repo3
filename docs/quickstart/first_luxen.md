# Training your first model

## Downloading data

Download the original Luxen Blender dataset. We support the major datasets and allow users to create their own dataset, described in detail [here TODO].

```
ns-download-data --dataset=blender
ns-download-data --dataset=luxenstudio --capture=poster
```

Use `--help` to view all currently available datasets. The resulting script should download and unpack the dataset as follows:

```
|─ luxenstudio/
   ├─ data/
   |  ├─ blender/
   |     ├─ fern/
   |     ├─ lego/
         ...
      |- <dataset_format>/
         |- <scene>
         ...
```

## Training a model

To run with all the defaults, e.g. vanilla luxen method with the blender lego image

Run a vanilla luxen model.

```bash
ns-train vanilla-luxen
```

Run a luxenacto model.

```bash
ns-train luxenacto
```

Run with luxenstudio data. You'll may have to change the ports, and be sure to forward the "websocket-port".

```
ns-train luxenacto --vis viewer --viewer.zmq-port 8001 --viewer.websocket-port 8002 luxenstudio-data --pipeline.datamanager.dataparser.data-directory data/luxenstudio/poster --pipeline.datamanager.dataparser.downscale-factor 4
```

## Visualizing training runs

If you are using a fast Luxen variant (ie. Instant-NGP), we recommend using our viewer. See our [viewer docs](viewer_quickstart.md) for more details. The viewer will allow interactive visualization of training in realtime.

Additionally, if you run everything with the default configuration, by default, we use [TensorBoard](https://www.tensorflow.org/tensorboard) to log all training curves, test images, and other stats. Once the job is launched, you will be able to track training by launching the tensorboard in `outputs/blender_lego/vanilla_luxen/<timestamp>/<events.tfevents>`.

```bash
tensorboard --logdir outputs
```

## Rendering a Trajectory

To evaluate the trained Luxen, we provide an evaluation script that allows you to do benchmarking (see our [benchmarking workflow](../developer_guides/benchmarking.md)) or to render out the scene with a custom trajectory and save the output to a video.

```bash
ns-render --load-config=outputs/blender_lego/instant_ngp/2022-07-07_230905/config.yml --traj=spiral --output-path=output.mp4
```

Please note, this quickstart allows you to preform everything in a headless manner. We also provide a web-based viewer that allows you to easily monitor training or render out trajectories. See our [viewer docs](viewer_quickstart.md) for more.
