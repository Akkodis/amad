import abc
from typing import Dict
from cosapp.base import System


class BaseMassClass(System):
    """
    Base Mass Class

    Parameters
    ----------
    name : str
        System name
    model : str
        Computation algorithm. Specified by parent class

    Attributes
    ----------
    model : AbstractMassComponent
        Concrete specialization of `AbstractMassComponent`.
        May possess model-specific parameters, as inwards.
    """

    def setup(self, model: str, **parameters):
        """
        Set up a child model for a given model with the specified parameters.

        Parameters
        ----------
        model : str
            The name of the model.
        **parameters : keyword arguments
            Additional parameters to pass to the child model.

        Raises
        ------
        TypeError
            If `model` is not a string.
        ValueError
            If the input `model` is invalid and not present in the available models.

        Returns
        -------
        None

        Notes
        -----
        This function adds a child model to the current model. The child model is specified by its name (`model`)
        and additional parameters can be passed using keyword arguments (`**parameters`).
        The available models are determined by calling the `models()` method. If the input `model` is not a valid name,
        a `ValueError` is raised. If the input `model` is not a string, a `TypeError` is raised. After adding the child model,
        the pulling direction of the child model is set to ['inwards', 'outwards', 'total'].
        """
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
        """
        Dictionary of available models
        """
        pass
