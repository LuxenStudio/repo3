# Run other repos with our data

If you are looking to test out other existing repo's with our data, the pyRad structure makes it easy!

For instance, you can run luxen-pytorch and jaxluxen with the following commands:

```bash
# luxen-pytorch
cd external
python run_luxen.py --config configs/chair.txt --datadir /path/to/pyrad/data/blender/chair

# jaxluxen
cd external
conda activate jaxluxen
python -m jaxluxen.train --data_dir=/path/to/pyrad/data/blender/chair --train_dir=/path/to/pyrad/outputs/blender_chair_jaxluxen --config=/path/to/pyrad/external/jaxluxen/configs/demo --render_every 100
```