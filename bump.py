# stolen from: https://github.com/psf/black-pre-commit-mirror/blob/main/mirror.py

import subprocess
from pathlib import Path

import tomli
import tomli_w
import urllib3
from packaging.requirements import Requirement
from packaging.version import Version


def main():
    with open(Path(__file__).parent / "pyproject.toml", "rb") as f:
        pyproject = tomli.load(f)

    # get current version of black
    all_deps = pyproject["project"]["dependencies"]
    mypy_dep = next(dep for dep in all_deps if dep.startswith("mypy"))
    all_deps.remove(mypy_dep)
    mypy_dep = Requirement(mypy_dep)
    assert mypy_dep.name == "mypy"
    mypy_specs = list(mypy_dep.specifier)
    assert len(mypy_specs) == 1
    assert mypy_specs[0].operator == "=="
    current_version = Version(mypy_specs[0].version)

    # get all versions of mypy from PyPI
    resp = urllib3.request("GET", "https://pypi.org/pypi/mypy/json")
    if resp.status != 200:
        raise RuntimeError

    versions = [Version(release) for release in resp.json()["releases"]]
    versions = [v for v in versions if v > current_version]
    versions.sort()

    for version in versions:
        pyproject["project"]["dependencies"].insert(0, f"mypy=={version}")
        with open(Path(__file__).parent / "pyproject.toml", "wb") as f:
            tomli_w.dump(pyproject, f)
        subprocess.check_call(["git", "add", "pyproject.toml"])
        subprocess.check_call(["git", "commit", "-m", f"Bump mypy: {version}"])
        subprocess.check_call(["git", "tag", f"v{version}"])


if __name__ == "__main__":
    main()
