import sys
import os
import subprocess as sp
import hashlib
from pathlib import Path


def main():
    tmp = Path(os.environ["VIRTUAL_ENV"]).parent / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    reqs = tmp / ("reqs-" + hashlib.md5(open("Pipfile.lock", "rb").read()).hexdigest())

    if not reqs.is_file():
        out = sp.check_output(
            ["pipenv", "requirements", "--dev"], env=os.environ | {"PIPENV_VERBOSITY": "-1"}
        )
        reqs.write_bytes(out)
        ret = sp.run(["pip", "install", "-qr", str(reqs)], text=True)

    ret = sp.run(["mypy", *sys.argv[1:]], capture_output=False)
    return ret.returncode


if __name__ == "__main__":
    main()
