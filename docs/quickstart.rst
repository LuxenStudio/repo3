.. _quickstart:

Quickstart
============

Installation
-------------------------------

Clone the repo::

   git clone --recurse-submodules git@github.com:ethanweber/pyrad.git

Create the python environment::

   conda create --name pyrad python=3.8.13
   conda activate pyrad
   pip install -r environment/requirements.txt

Install pyrad as a library::

   pip install -e .

Install library with CUDA support. Change setup.py to ``USE_CUDA = True`` and then::

   python setup.py develop

Running the test cases::

   pytest tests
   Field Modules


Getting the data
-------------------------------

Download the original Luxen dataset and put it in the following format.::


   - data/
      - blender/
         - fern/
         - lego/

Training a model
-------------------------------

Run with default config::

   python scripts/run_train.py

Run with config changes::

   python scripts/run_train.py machine_config.num_gpus=1
   python scripts/run_train.py data.dataset.downscale_factor=1

Run with different datasets::

   python scripts/run_train.py data/dataset=blender_lego
   python scripts/run_train.py data/dataset=friends_TBBT-big_living_room

Run with different datasets and config changes::

   python scripts/run_train.py data/dataset=friends_TBBT-big_living_room graph.network.far_plane=14

Getting around the codebase
-------------------------------

The entry point for training starts at ``scripts/run_train.py``, which spawns instances of our ``Trainer()`` class (in ``luxen/trainer.py``). The ``Trainer()`` is responsible for setting up the datasets and Luxen graph depending on the config specified. If you are planning on just using our codebase to build a new Luxen method or use an existing implementation, we've abstracted away the training routine in these two files and chances are you will not need to touch them.

The Luxen graph definitions can be found in ``luxen/graph/``. Each implementation of Luxen is definined in its own file. For instance, ``luxen/graph/instant_ngp.py`` contains populates the ``NGPGraph()`` class with all of the appropriate fields, colliders, and misc. modules.

* Fields (``luxen/fields/``): composed of field modules (``luxen/field_modules/``) and represents the radiance field of the Luxen.
* Misc. Modules (``luxen/misc_modules``- TODO(maybe move to misc_modules? better organization)): any remaining module in the Luxen (e.g. renderers, samplers, losses, and metrics).

To implement any pre-existing Luxen that we have not yet implemented under `luxen/graph/`, create a new graph structure by using provided modules or any new module you define. Then create an associated config making sure ``__target__`` points to your Luxen class (see [here](./configs/README.md) for more info on how to create the config). Then run training as described above.