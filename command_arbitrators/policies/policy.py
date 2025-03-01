from abc import ABC, abstractmethod


class Policy(ABC):
    """ Policy is the abstract superclass for all policies, binary or continuous. """

    def __init__(self):
        pass

    @staticmethod
    def get_max_actors() -> int:
        """ Returns the maximum number of actors allowed in the policy. """
        return 256

    @staticmethod
    @abstractmethod
    def merge_input_entries(entries: list['InputEntry']) -> float:
        pass

    @staticmethod
    def policy_name_to_policy(name: str) -> 'type[Policy]':
        match name:
            case 'POLICY_EXCLUSIVITY':
                from .policy_exclusivity import PolicyExclusivity
                return PolicyExclusivity
            case 'POLICY_BIN_AND':
                from .policy_binary_and import PolicyBinaryAND
                return PolicyBinaryAND
            case 'POLICY_BIN_OR':
                from .policy_binary_or import PolicyBinaryOR
                return PolicyBinaryOR
            case 'POLICY_CONT_OR':
                from .policy_continuous_or import PolicyContinuousOR
                return PolicyContinuousOR
            case _:
                raise Exception(f'Unknown policy name: {name}')


class BinaryPolicy(Policy, ABC):
    """ BinaryPolicy is the abstract superclass for all binary policies. """
    pass


class ContinuousPolicy(Policy, ABC):
    """ ContinuousPolicy is the abstract superclass for all continuous policies. """
    pass
