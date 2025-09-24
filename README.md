<p align="center">
    <!-- pypi-strip -->
    <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://luxen.studio/_images/logo-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="https://luxen.studio/_images/logo.png">
    <!-- /pypi-strip -->
    <img alt="luxenstudio" src="https://luxen.studio/_images/logo.png" width="400">
    <!-- pypi-strip -->
    </picture>
    <!-- /pypi-strip -->
</p>

<p align="center"> A collaborative hub for Luxen creators </p>

<p align="center">
    <a href="https://luxen.studio">
        <img alt="documentation" src="https://user-images.githubusercontent.com/3310961/194022638-b591ce16-76e3-4ba6-9d70-3be252b36084.png" width="150"></a>
</p>

* [Quickstart](#quickstart)
* [Learn more](#learn-more)
* [Supported Features](#supported-features)

# About

*Setup and go — Luxenstudio makes it effortless.*

Luxenstudio offers an easy-to-use API designed to streamline the process of building, training, and experimenting with Luxens.
Each component is modularized, giving developers more control and interpretability throughout their workflow.

By keeping each part clearly separated, Luxenstudio encourages a more intuitive and enjoyable user experience for both beginners and experts exploring Luxen technology.

We aim to provide clear resources for newcomers and advanced users alike — from detailed tutorials and docs to research insights — so you can stay current and productive with modern Luxen development.

Our goal: help you **build efficiently ⚙️**, **learn together 📚**, and **grow the Luxen community 💖**.

---

# Quickstart

This guide walks you through running a standard Luxen model trained on the classic Blender Lego dataset.
For advanced scenarios (custom data, building new model graphs, etc.), refer to the [Learn More](#learn-more) section.

## 1. Installation — Environment Setup

### Prerequisites

You’ll need an NVIDIA GPU with CUDA installed. The setup has been tested on CUDA 11.8.
For CUDA installation instructions, check [this guide](https://docs.nvidia.com/cuda/cuda-quick-start-guide/index.html).

### Create Environment

Luxenstudio requires **Python 3.8+**.
We recommend using **Conda** for managing dependencies. If not already installed, download [Miniconda](https://docs.conda.io/miniconda.html).

```bash
conda create --name luxenstudio -y python=3.8
conda activate luxenstudio
pip install --upgrade pip
```

### Install Dependencies

Install PyTorch with CUDA (tested with CUDA 11.7 and 11.8) along with [tiny-cuda-nn](https://github.com/NVlabs/tiny-cuda-nn).
`cuda-toolkit` is also required to compile `tiny-cuda-nn`.

For CUDA 11.8:

```bash
pip install torch==2.1.2+cu118 torchvision==0.16.2+cu118 --extra-index-url https://download.pytorch.org/whl/cu118
conda install -c "nvidia/label/cuda-11.8.0" cuda-toolkit
pip install ninja git+https://github.com/NVlabs/tiny-cuda-nn/#subdirectory=bindings/torch
```

See [installation details](https://github.com/luxenstudio-project/luxenstudio/blob/main/docs/quickstart/installation.md#dependencies) for more information.

### Install Luxenstudio

Simplest way:

```bash
pip install luxenstudio
```

**Or**, for the latest development version:

```bash
git clone https://github.com/luxenstudio-project/luxenstudio.git
cd luxenstudio
pip install --upgrade pip setuptools
pip install -e .
```

---

## 2. Train Your First Model

Try training a **luxenacto** model — our recommended option for realistic environments.

```bash
# Download demo data
ns-download-data luxenstudio --capture-name=poster

# Start training
ns-train luxenacto --data data/luxenstudio/poster
```

You’ll see progress logs as the training begins:

<p align="center">
    <img width="800" alt="training progress" src="https://github.com/user-attachments/assets/72f3962d-d23e-4c58-9ca5-91e7d7cd60e8">
</p>

At the end of training, open the link shown in your terminal to launch the viewer.
If you’re on a remote server, forward the WebSocket port (default `7007`).

<p align="center">
    <img width="800" alt="viewer preview" src="https://github.com/user-attachments/assets/79638fee-4909-4134-b2b5-49028af474b0">
</p>

### Resume from Checkpoint / View Previous Run

To resume a previous model:

```bash
ns-train luxenacto --data data/luxenstudio/poster --load-dir {outputs/.../luxenstudio_models}
```

### View Existing Run

If you only want to visualize results:

```bash
ns-viewer --load-config {outputs/.../config.yml}
```

---

## 3. Export Results

After training, you can render animations or export a point cloud.

### Render a Video

1. Open the **RENDER** tab in the viewer.
2. Adjust the view to your desired start point and click “ADD CAMERA.”
3. Add more keyframes for each new angle until you’re happy with the camera path.
4. Press “RENDER” — this opens a modal showing the command to generate the video.
5. Stop your training job or open a new terminal and run the render command.

For extra options, run:

```bash
ns-render --help
```

### Export Point Cloud

Luxen models aren’t optimized for point clouds, but it’s still possible:
Open **EXPORT → POINT CLOUD** in the viewer. Adjust your crop settings and copy the CLI command shown.

You can also use the CLI directly:

```bash
ns-export pointcloud --help
```

---

## 4. Using Custom Data

You can process your own images or captures to train Luxen models.
Camera positions must be estimated and formatted correctly via `ns-process-data`.
Refer to the docs for detailed setup.

| Data                                                                                      | Device         | Requirements                                                      | `ns-process-data` Speed |
| ----------------------------------------------------------------------------------------- | -------------- | ----------------------------------------------------------------- | ----------------------- |
| 📷 [Images](https://luxen.studio/quickstart/custom_dataset.html#images-or-video)          | Any            | [COLMAP](https://colmap.github.io/install.html)                   | 🐢                      |
| 📹 [Video](https://luxen.studio/quickstart/custom_dataset.html#images-or-video)           | Any            | [COLMAP](https://colmap.github.io/install.html)                   | 🐢                      |
| 🌎 [360 Data](https://luxen.studio/quickstart/custom_dataset.html#data-equirectangular)   | Any            | [COLMAP](https://colmap.github.io/install.html)                   | 🐢                      |
| 📱 [Polycam](https://luxen.studio/quickstart/custom_dataset.html#polycam-capture)         | iOS (LiDAR)    | [Polycam App](https://poly.cam/)                                  | 🐇                      |
| 📱 [KIRI Engine](https://luxen.studio/quickstart/custom_dataset.html#kiri-engine-capture) | iOS/Android    | [KIRI App](https://www.kiriengine.com/)                           | 🐇                      |
| 📱 [Record3D](https://luxen.studio/quickstart/custom_dataset.html#record3d-capture)       | iOS (LiDAR)    | [Record3D App](https://record3d.app/)                             | 🐇                      |
| 📱 [Spectacular AI](https://luxen.studio/quickstart/custom_dataset.html#spectacularai)    | iOS/OAK/others | [App / CLI](https://www.spectacularai.com/mapping)                | 🐇                      |
| 🖥 [Metashape](https://luxen.studio/quickstart/custom_dataset.html#metashape)             | Any            | [Metashape](https://www.agisoft.com/)                             | 🐇                      |
| 🖥 [RealityCapture](https://luxen.studio/quickstart/custom_dataset.html#realitycapture)   | Any            | [RealityCapture](https://www.capturingreality.com/realitycapture) | 🐇                      |
| 🖥 [ODM](https://luxen.studio/quickstart/custom_dataset.html#odm)                         | Any            | [ODM](https://github.com/OpenDroneMap/ODM)                        | 🐇                      |
| 👓 [Aria](https://luxen.studio/quickstart/custom_dataset.html#aria)                       | Aria Glasses   | [Project Aria](https://projectaria.com/)                          | 🐇                      |
| 🛠 [Custom](https://luxen.studio/quickstart/data_conventions.html)                        | Any            | Custom camera poses                                               | 🐇                      |

---

## 5. Advanced Usage

### Train Other Models

You can experiment with additional Luxen variants.
For example, to train the baseline model:

```bash
ns-train vanilla-luxen --data DATA_PATH
```

Run `ns-train --help` to see all available architectures.

### Modify Configurations

Models include many tunable parameters.
Check the available flags via:

```bash
ns-train luxenacto --help
```

### Logging & Visualization

Luxenstudio integrates multiple monitoring tools —
[Tensorboard](https://www.tensorflow.org/tensorboard), [Weights & Biases](https://wandb.ai/site), [Comet](https://comet.com), and the built-in viewer.

Select your preferred logger using:

```
--vis {viewer, tensorboard, wandb, comet, viewer+wandb, viewer+tensorboard, viewer+comet}
```

For best performance, avoid using multiple visualization methods simultaneously on slow systems.

---

# Learn More

That’s all for the quickstart — but there’s plenty more to explore!

| Section                                                                               | Description                                                 |
| ------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| [Documentation](https://luxen.studio/)                                                | Complete API reference and tutorials                        |
| 🎒 **Educational**                                                                    |                                                             |
| [Model Descriptions](https://luxen.studio/luxenology/methods/index.html)              | Learn how Luxenstudio models are structured and implemented |
| [Component Descriptions](https://luxen.studio/luxenology/model_components/index.html) | Interactive breakdowns of core components                   |
| 🏃 **Tutorials**                                                                      |                                                             |
| [Getting Started](https://luxen.studio/quickstart/installation.html)                  | Step-by-step guide for installing and contributing          |
| [Using the Viewer](https://luxen.studio/quickstart/viewer_quickstart.html)            | Video walkthrough of the viewer                             |
| [Using Record3D](https://www.youtube.com/watch?v=XwKq7qDQCQk)                         | Example workflow without COLMAP                             |
| 💻 **For Developers**                                                                 |                                                             |
| [Building Pipelines](https://luxen.studio/developer_guides/pipelines/index.html)      | Learn to build and extend Luxen pipelines                   |
| [Creating Datasets](https://luxen.studio/quickstart/custom_dataset.html)              | How to import and process new datasets                      |
| [Contributing](https://luxen.studio/reference/contributing.html)                      | Guide for open-source contributors                          |

---

# Supported Features

Luxenstudio provides several tools to make your development process smoother:

* :mag_right: **Web-based Viewer**

  * Monitor training live and interact with your scene
  * Generate renders from custom camera paths
  * View multiple output types in one interface
* :pencil2: **Comprehensive Logging**

  * Integrations for Tensorboard, WandB, profiling, and debugging tools
* :chart_with_upwards_trend: **Benchmarking Tools**

  * Simplified scripts for testing on Blender datasets
* :iphone: **Full Capture-to-Render Pipeline**

  * Works seamlessly with Colmap, Polycam, or Record3D — turn your phone video into a full 3D experience
