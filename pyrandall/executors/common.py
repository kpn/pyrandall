from abc import ABC, abstractmethod


class Executor(ABC):
    @abstractmethod
    def execute(self):
        ...

    @abstractmethod
    def represent(self):
        ...
