from typing import TypeVar, Type

T = TypeVar("T")


def get_all_concrete_subclasses(cls: Type[T]) -> set[Type[T]]:
    """Returns a set of all the Type class concrete implementations"""
    subclasses = set(cls.__subclasses__())  # Find direct subclasses
    all_subclasses = set(subclasses)

    for subclass in subclasses.copy():  # Find nested subclasses
        all_subclasses.update(get_all_concrete_subclasses(subclass))

    # Filter out abstract classes, checking the __abstractmethods__ attribute
    all_subclasses = {
        subclass
        for subclass in all_subclasses
        if not hasattr(subclass, "__abstractmethods__")  # Doesn't have
           or not subclass.__abstractmethods__  # Has but it's empty
    }

    return all_subclasses
