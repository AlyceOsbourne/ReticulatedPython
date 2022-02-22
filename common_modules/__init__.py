from functools import partial

from common_modules.__neural_network_tools__ import *
import tqdm, rich, rich.console as _rc_

console = rich.console.Console()
print = partial(
    console.print, highlight=True
)  # replacing print with console print, this is to keep it uniform, adds hints etc
log = console.log

__all__ = [
    *(i for i in dir() if not i.startswith("_") and not i.endswith("_"))
]  # will let me load * cleanly
log(f"Common modules loaded {__all__}")
