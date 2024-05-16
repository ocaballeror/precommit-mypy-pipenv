# pre-commit mypy pipenv
Pre-commit hook to run mypy on your project, using your pipenv dependencies. First
invocation will take some time to install all dependencies in pre-commit's virtual env.

## Example

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/ocaballeror/precommit-mypy-pipenv
    rev: v1.10.0
    hooks:
      - id: mypy
        args: [--allow-any-generics]
        additional_dependencies: [pydantic<2]
```
