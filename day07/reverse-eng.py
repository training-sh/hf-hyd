import marshal
import dis
from pathlib import Path

pyc_file = Path(r"__pycache__\hello.cpython-312.pyc")

with pyc_file.open("rb") as file:
    file.read(16)  # Skip the Python 3.12 .pyc header
    code_object = marshal.load(file)

dis.dis(code_object)