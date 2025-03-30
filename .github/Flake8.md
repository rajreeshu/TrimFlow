# Flake8 Configuration Guide

Flake8 is a Python linting tool that enforces coding standards (PEP 8), checks for errors, and maintains code quality. It combines:

<li>
<b>Pyflakes:</b> Detects logical errors and unused imports.
<li>
<b>pycodestyle:</b> Ensures PEP 8 compliance.
<li>
<b>McCabe:</b> Measures code complexity.

## 1. Configure .flake

Create a .flake8 file in your project root with the following content:

```
[flake8]
ignore = E302, E203, W293, E501, F401
max-line-length = 120
```

<br>

<b>Ignored Errors:</b>

<li> 302: Expected 2 blank lines, found 1.
<li> E203: Whitespace before : (common with Black).
<li> W293: Blank line contains whitespace.
<li>E501: Line too long (default is 79, increased to 120).
<li> F401: Imported but unused.

<br>

## 2. Ignoring Errors Inline

Suppress specific errors for individual lines using `# noqa`:

```
import os  # noqa: F401  # Ignore "imported but unused"
```

## 3. Configure Flake8 in CI

Pass ignored errors and configurations via CLI in your CI pipeline:

```
flake8 --ignore=E302,E203,W293,E501,F401 --max-line-length=120 .
```

`GitHub Actions` Configuration

If using GitHub Actions, update your workflow file:

```
- name: Run Flake8
  run: flake8 --ignore=E302,E203,W293,E501,F401 --max-line-length=120 .
```
