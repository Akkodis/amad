import abc
from typing import Dict
from cosapp.base import System


class BaseMassClass(System):
    """Base Mass Class

    Constructor arguments:
    ----------------------
    - name [str]: System name
    - model [str]: Computation algorithm. Specified by parent class

    Children:
    ---------
    - model:
        Concrete specialization of `AbstractMassComponent`.
        May possess model-specific parameters, as inwards.
    """

    def setup(self, model: str, **parameters):
        if not isinstance(model, str):
            raise TypeError("`model` must be a str")
        models = self.models()
        try:
            cls = models[model]
        except KeyError:
            raise ValueError(
                f"Invalid model {model!r}. Available: {list(models.keys())}"
            )

        self.add_child(
            cls("model", **parameters), pulling=["inwards", "outwards", "total"]
        )

    @abc.abstractclassmethod
    def models(cls) -> Dict[str, type]:
        """Dictionary of available models"""
        pass
