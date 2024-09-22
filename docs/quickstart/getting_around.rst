.. _getting_around:

Getting around the codebase
=====================================

The entry point for training starts at ``scripts/run_train.py``, which spawns instances of our ``Trainer()`` class (in ``luxen/trainer.py``). The ``Trainer()`` is responsible for setting up the datasets and Luxen graph depending on the config specified. If you are planning on just using our codebase to build a new Luxen method or use an existing implementation, we've abstracted away the training routine in these two files and chances are you will not need to touch them.

The Luxen graph definitions can be found in ``luxen/graph/``. Each implementation of Luxen is definined in its own file. For instance, ``luxen/graph/instant_ngp.py`` contains populates the ``NGPGraph()`` class with all of the appropriate fields, colliders, and misc. modules.

* Fields (``luxen/fields/``): composed of field modules (``luxen/field_modules/``) and represents the radiance field of the Luxen.
* Misc. Modules (``luxen/misc_modules``- TODO(maybe move to misc_modules? better organization)): any remaining module in the Luxen (e.g. renderers, samplers, losses, and metrics).

To implement any pre-existing Luxen that we have not yet implemented under `luxen/graph/`, create a new graph structure by using provided modules or any new module you define. Then create an associated config making sure ``__target__`` points to your Luxen class (see [here](./configs/README.md) for more info on how to create the config). Then run training as described above.