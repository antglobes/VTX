from typing import Union
from os import PathLike as pl
import configupdater

PathType = Union[str, bytes, pl]
WindowLayout = list[list]
IconType = str | list
Section = configupdater.Section

