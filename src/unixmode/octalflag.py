import enum
from enum import IntFlag

class OctalFlag(IntFlag):
    BASE = enum.nonmember(8)
    FLAGS_PER_DIGIT = enum.nonmember(int.bit_length(7))

    @classmethod
    def __init_subclass__(cls):
        unique_members = set(member.value for member in iter(cls))
        if len(unique_members) > cls.FLAGS_PER_DIGIT:
            raise OctalFlagDefinitionError(cls, "cannot have more than 3 unique values")

        if max(unique_members) > cls.BASE - 1:
            raise OctalFlagDefinitionError(cls, "cannot have a value higher than 7")

class OctalFlagDefinitionError(TypeError):
    def __init__(self, cls: type, message):
        self.problematic_type = cls
        self.message = message
        super().__init__(f"OctalFlag class {cls.__qualname__} {message}")
