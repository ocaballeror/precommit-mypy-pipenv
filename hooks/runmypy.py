try:
    import tomllib as toml
except ImportError:
    import tomli as toml

import sys
import os
import subprocess as sp
import hashlib
from pathlib import Path


def tmpdir():
    tmp = Path(os.environ["VIRTUAL_ENV"]).parent / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    return tmp


class DepHandler:
    def supported(self) -> bool:
        raise NotImplementedError

    def requirements(self) -> str:
        raise NotImplementedError

    def reqs_hash(self) -> str:
        raise NotImplementedError

    def tmp_reqs(self) -> Path:
        return tmpdir() / self.reqs_hash()

    def updated(self) -> bool:
        return not self.tmp_reqs().exists()

    def write_reqs(self) -> None:
        self.tmp_reqs().write_text(self.requirements())


class Pipenv(DepHandler):
    def supported(self) -> bool:
        return Path("Pipfile.lock").exists()

    def requirements(self) -> str:
        out = sp.check_output(
            ["pipenv", "requirements", "--dev"],
            env=os.environ | {"PIPENV_VERBOSITY": "-1"},
            text=True,
        )
        return out

    def reqs_hash(self) -> str:
        return hashlib.md5(open("Pipfile.lock", "rb").read()).hexdigest()


class Pyproject(DepHandler):
    def supported(self) -> bool:
        return Path("pyproject.toml").exists()

    def requirements(self) -> str:
        with open("pyproject.toml", "rb") as f:
            pyproject = toml.load(f)

        std_deps = pyproject["project"].get("dependencies", [])
        opt_groups = pyproject["project"].get("optional-dependencies", {})
        opt_deps = [dep for ext in opt_groups.values() for dep in ext]
        return "\n".join(std_deps + opt_deps)

    def reqs_hash(self) -> str:
        return "reqs-" + str(hash(self.requirements()))


def main():
    # if none of the dependency managers are installed, just run mypy normally
    for handler in Pipenv(), Pyproject():
        if handler.supported():
            if handler.updated():
                handler.write_reqs()
                sp.check_call(["pip", "install", "-qr", str(handler.tmp_reqs())], text=True)
            break

    ret = sp.run(["mypy", *sys.argv[1:]], capture_output=False)
    return ret.returncode


if __name__ == "__main__":
    main()
