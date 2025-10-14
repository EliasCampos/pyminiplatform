import abc
import json


class Serializable(abc.ABC):

    @classmethod
    @abc.abstractmethod
    def to_internal_value(cls, data):
        ...

    @abc.abstractmethod
    def to_representation(self):
        ...

    def json(self):
        value = self.to_representation()
        return json.dumps(value)
