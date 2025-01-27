from __future__ import annotations

from dataclasses import dataclass
import enum
from enum import StrEnum, NAMED_FLAGS
from typing import ClassVar, Self, TypedDict

from .classproperty import classproperty
from .octalflag import OctalFlag

@enum.verify(NAMED_FLAGS)
# pylint what are you cooking. OctalFlag defines no enum members.
class SetId(OctalFlag): # pylint: disable=invalid-enum-extension
    NONE = 0
    STICKY = 1
    # SETGID
    GROUP = 2
    # SETUID
    USER = 4

    def _to_symbolic(self, execute: bool) -> str:
        if self == self.NONE:
            return "x" if execute else "-"
        elif self == self.STICKY:
            return "t" if execute else "T"
        else:
            return "s" if execute else "S"

    def _mask_slot(self, slot: ModeSlot | str) -> Self:
        slot = ModeSlot(slot)

        if slot == ModeSlot.USER:
            return self & self.USER
        elif slot == ModeSlot.GROUP:
            return self & self.GROUP
        elif slot == ModeSlot.OTHER:
            return self & self.STICKY


@enum.verify(NAMED_FLAGS)
# pylint what are you cooking. OctalFlag defines no enum members.
class Permission(OctalFlag): # pylint: disable=invalid-enum-extension
    NONE = 0
    EXECUTE = 1
    WRITE = 2
    READ = 4

    def _to_symbolic(self, masked_extra: SetId = SetId.NONE) -> str:
        read = self.READ in self
        write = self.WRITE in self
        execute = self.EXECUTE in self

        slots = [
            "r" if read else "-",
            "w" if write else "-",
            masked_extra._to_symbolic(execute),
        ]

        return "".join(slots)

@dataclass
class PureMode:
    """ The main attraction. Analogous to pathlib.Path. """
    extra: SetId = SetId.NONE
    user: Permission = Permission.NONE
    group: Permission = Permission.NONE
    other: Permission = Permission.NONE

    S_ISUID: ClassVar = SetId.USER
    S_ISGID: ClassVar = SetId.GROUP
    S_ISVTX: ClassVar = SetId.STICKY

    #
    # Main public API
    #

    @classmethod
    def new(
        cls,
        extra: SetId = SetId.NONE,
        user: Permission = Permission.NONE,
        group: Permission = Permission.NONE,
        other: Permission = Permission.NONE,
    ):
        symbolic_kwargs = _SymbolicKwargs(extra=extra, user=user, group=group, other=other)
        #integral_arg = cls._to_raw(**symbolic_kwargs)

        return cls(**symbolic_kwargs)
        #return cls(raw=integral_arg, **symbolic_kwargs)

    @classmethod
    def from_raw(cls, value: int) -> Self:
        symbolic_kwargs = cls._from_raw(value)
        return cls(**symbolic_kwargs)
        #return cls(raw=value, **symbolic_kwargs)

    def to_raw(self) -> int:
        return self._to_raw(extra=self.extra, user=self.user, group=self.group, other=self.other)

    def add(
        self,
        extra: SetId = SetId.NONE,
        user: Permission = Permission.NONE,
        group: Permission = Permission.NONE,
        other: Permission = Permission.NONE,
    ) -> Self:
        """ This *both* mutates self *and* returns self. """
        self.extra |= extra
        self.user |= user
        self.group |= group
        self.other |= other

        return self

    def to_symbolic(self) -> str:
        """
        Returns the mode in the symbolic representation chmod(1) and ls(1) use.
        """

        user = self.user._to_symbolic(self.extra._mask_slot("user"))
        group = self.group._to_symbolic(self.extra._mask_slot("group"))
        other = self.other._to_symbolic(self.extra._mask_slot("other"))

        return "".join([user, group, other])

    @property
    def raw(self) -> int:
        return self._raw
        #return self._to_raw(**dataclasses.asdict(self))

    @raw.setter
    def raw(self, value: int):
        symbolic_kwargs = self._from_raw(value)
        self.extra = symbolic_kwargs['extra']
        self.user = symbolic_kwargs['user']
        self.group = symbolic_kwargs['group']
        self.other = symbolic_kwargs['other']
        self._raw = value

    #
    # Data model and other dunders.
    #

    def __post_init__(self):
        self._raw = self._to_raw(self.extra, self.user, self.group, self.other)

    def __or__(self, other: Self) -> Self:
        return self.from_raw(self.raw | other.raw)

    #
    # Implementation details
    #

    @classmethod
    def _from_raw(cls, value: int) -> _SymbolicKwargs:
        """ Generates class init arguments from a mode integer value. """
        assert value <= 0o7777, f"value {value} does not fit in 4 octal digits"

        remaining = value
        digits = []
        while len(digits) < 4:
            digit = remaining & 0o0007
            digits.append(digit)
            remaining >>= 3

        assert len(digits) <= 4, f"value {value} does not fit in 4 octal digits"

        return _SymbolicKwargs(
            extra=SetId(digits.pop()),
            user=Permission(digits.pop()),
            group=Permission(digits.pop()),
            other=Permission(digits.pop()),
        )

    @classmethod
    def _to_raw(
        cls,
        extra: SetId = SetId.NONE,
        user: Permission = Permission.NONE,
        group: Permission = Permission.NONE,
        other: Permission = Permission.NONE,
    ) -> int:
        """ Generates class init argument for `raw` from symbolic values. """
        value = 0
        parts = [
            # Most significant digit.
            extra.value,
            user.value,
            group.value,
            # Least significant digit.
            other.value,
        ]
        for part in parts:
            value |= part
            value <<= 3
        value >>= 3

        return value

    # Constants!

    @classproperty
    def SYSTEM_DIR(cls) -> Self:
        """ Mode common for system-managed directories. """
        return cls.from_raw(0o755)

    @classproperty
    def SYSTEM_EXE(cls) -> Self:
        """ Mode common for system-managed executables. """
        return cls.from_raw(0o755)

    @classproperty
    def SYSTEM_FILE(cls) -> Self:
        """
        Mode common for system-managed static files.

        Stuff the package manager puts in place, and that system administrators
        might modify from time to time, like configuration files or libraries.
        """
        return cls.from_raw(0o644)

    @classproperty
    def SYSTEM_SECRET(cls) -> Self:
        """ Mode common for sensitive system files like /etc/shadow. """
        return cls.from_raw(0o600)

    @classproperty
    def SYSTEM_SUDOERS(cls) -> Self:
        """ Mode common for sudoers files! """
        return cls.from_raw(0o440)

    @classproperty
    def HOME_DIR(cls) -> Self:
        """ Mode common for home directories themselves (but not things in them). """
        # drwx------
        return cls.from_raw(0o700)

    @classproperty
    def USER_DIR(cls) -> Self:
        """ Mode common for directories and executables in user directories. """
        return cls.from_raw(0o775)

    @classproperty
    def USER_FILE(cls) -> Self:
        """ Mode common for static files in user directories. """
        return cls.from_raw(0o644)

    @classproperty
    def USER_SECRET(cls) -> Self:
        """ Mode common for sensitive but modifiable files like SSH private keys. """
        return cls.from_raw(0o600)

# Fun fact, did you know that names starting with an underscore aren't in __all__ by default?
class _SymbolicKwargs(TypedDict):
    extra: SetId
    user: Permission
    group: Permission
    other: Permission

class ModeSlot(StrEnum):
    """ Helper class for formatting symbolic permissions. """
    USER = "user"
    GROUP = "group"
    OTHER = "other"

#S_IRWXU = PureMode()
