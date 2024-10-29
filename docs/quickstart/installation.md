# Installation

### Create environment

We reccomend using conda to manage dependencies. Make sure to install [Conda](https://docs.conda.io/en/latest/miniconda.html) before preceding.

```bash
conda create --name luxenstudio -y python=3.8.13
conda activate luxenstudio
python -m pip install --upgrade pip

```

### Dependencies

Install pytorch with CUDA (this repo has been tested with CUDA 11.3) and [tiny-cuda-nn](https://github.com/NVlabs/tiny-cuda-nn)

```bash
pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 -f https://download.pytorch.org/whl/torch_stable.html
pip install git+https://github.com/NVlabs/tiny-cuda-nn/#subdirectory=bindings/torch

```

### Installing luxenstudio

Easy option:

```bash
pip install luxenstudio
```

If you would want the latest and greatest:

```bash
git clone git@github.com:plenoptix/luxenstudio.git
cd luxenstudio
pip install -e .

```

### Optional Installs

#### Tab completion (bash & zsh)

This needs to be rerun when the CLI changes, for example if luxenstudio is updated.

```bash
ns-install-cli
```

### Development packages

```bash
pip install -e.[dev]
pip install -e.[docs]
```
