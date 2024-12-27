# Adding a New Method

Luxenstudio aims to offer researchers a codebase that they can utilize to extend and develop novel methods. Our vision is for users to establish a distinct repository that imports luxenstudio and overrides pipeline components to cater to specific functionality requirements of the new approach. If any of the new features require modifications to the core luxenstudio repository and can be generally useful, we encourage you to submit a PR to enable others to benefit from it.

Examples are often the best way to learn, take a look at the [LERF](https://github.com/kerrj/lerf) repository for good example of how to use luxenstudio in your projects.

## File Structure

We recommend the following file structure:

```
├── my_method
│   ├── my_config.py
│   ├── custom_pipeline.py [optional]
│   ├── custom_model.py [optional]
│   ├── custom_field.py [optional]
│   ├── custom_datamanger.py [optional]
│   ├── ...
├── pyproject.toml
```

## Registering custom model with luxenstudio

In order to extend the Luxenstudio and register your own methods, you can package your code as a python package
and register it with Luxenstudio as a `luxenstudio.method_configs` entrypoint in the `pyproject.toml` file.
Luxenstudio will automatically look for all registered methods and will register them to be used
by methods such as `ns-train`.

First create a config file:

```python
"""my_method/my_config.py"""

from luxenstudio.engine.trainer import TrainerConfig
from luxenstudio.plugins.types import MethodSpecification

MyMethod = MethodSpecification(
  config=TrainerConfig(
    method_name="my-method",
    pipeline=...
    ...
  ),
  description="Custom description"
)
```

Then create a `pyproject.toml` file. This is where the entrypoint to your method is set and also where you can specify additional dependencies required by your codebase.

```python
"""pyproject.toml"""

[project]
name = "my_method"

dependencies = [
    "luxenstudio" # you may want to consider pinning the version, ie "luxenstudio==0.1.19"
]

[project.entry-points.'luxenstudio.method_configs']
my-method = 'my_method.my_config:MyMethod'
```

finally run the following to register the method,

```
pip install -e .
```

## Running custom method

After registering your method you should be able to run the method with,

```
ns-train my-method --data DATA_DIR
```

## Adding to the _luxen.studio_ documentation

We invite researchers to contribute their own methods to our online documentation. You can find more information on how to do this {ref}`here<own_method_docs>`.
