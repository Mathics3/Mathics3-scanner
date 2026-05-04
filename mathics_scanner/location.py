from enum import Enum
from types import MethodType
from typing import List, NamedTuple, Set, Tuple, Union


class ContainerKind(Enum):
    UNKNOWN = 0
    FILE = 1  # Mathics3 files
    STREAM = 2  # input stream
    STRING = 3  # String fully
    PYTHON = 4  # Python implemented builtin funciton


class Container(NamedTuple):
    kind: ContainerKind
    name: str


class SourceRange(NamedTuple):
    # All values are 0 origin. (0 is the first number used).
    start_line: int
    start_pos: int
    end_line: int
    end_pos: int
    container: int


class SourceRange2(NamedTuple):
    # All values are 0 origin. (0 is the first number used).
    start_line: int
    start_pos: int
    end_pos: int
    container: int


# True if we want to keep track of positions as we scan an parse.
# This can be useful in debugging. It can also add a lot memory in
# saving position information.
TRACK_LOCATIONS: bool = False

# List of all Mathics3 files seen. We use the index in the list as a short
# representation of the file path.
# For example:
#   ["mathics/autoload/rules/Bessel.m", "mathics/autoload/rules/Element.m", ... ]
MATHICS3_PATHS: List[str] = []

# Set of Mathics3 Builtin evaluation methods seen.
EVAL_METHODS: Set[MethodType] = set([])


# FIXME: this isn't fully formed yet.
def get_location(loc: Union[SourceRange, SourceRange2, MethodType]) -> str:
    """
    Given Location ``loc`` return a string representation of that
    """
    if isinstance(loc, MethodType):
        func = loc.__func__
        doc = func.__doc__
        code = func.__code__
        return f"{doc} in file {code.co_filename} around line {code.co_firstlineno}"

    return "???"


def get_location_file_line(
    loc: Union[SourceRange, SourceRange2, MethodType],
) -> Tuple[str, int]:
    """
    Return the container name (often a filename) and starting line number for
    a location ``loc``.
    """
    if isinstance(loc, MethodType):
        func = loc.__func__
        code = func.__code__
        filename = code.co_filename
        line_number = code.co_firstlineno
    else:
        try:
            filename = MATHICS3_PATHS[loc.container]
        except IndexError:
            filename = "???"
        line_number = loc.start_line
    return filename, line_number
