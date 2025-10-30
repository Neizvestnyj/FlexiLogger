# Contributing to FlexiLogger

All contributions must adhere to the project's coding standards. This project uses `ruff` for linting/formatting and `pyright` for static type checking.

## 1. Environment Setup

1.  Clone the repository and navigate to the directory.
2.  Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    # Windows: .venv\Scripts\activate
    # macOS/Linux: source .venv/bin/activate
    ```
3.  Install all development dependencies:
    ```bash
    pip install -e .[dev]
    ```

## 2. Pre-Commit Hooks

1.  Install the pre-commit hooks. This is mandatory.
    ```bash
    pre-commit install
    ```
2.  All `git commit` actions will now automatically trigger `ruff` and `pyright`.
3.  Commits will be blocked if any checks fail. You must fix all errors before committing.
4.  You can run all checks manually at any time:
    ```bash
    pre-commit run --all-files
    ```

## 3. Pull Request (PR) Requirements

1.  Work on a separate feature branch.
2.  Ensure all `pre-commit` checks pass. PRs with failing checks will not be reviewed.
3.  Rebase your branch on the latest `master` before submitting.
4.  Provide a clear description of the changes in your PR.
