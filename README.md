# vai-jobspec-tools

Utilities for VoxelAI jobspec containers

[![PyPI Version](https://img.shields.io/pypi/v/vai-jobspec-tools.svg)](https://pypi.org/project/vai-jobspec-tools/)
[![codecov](https://codecov.io/gh/voxelai/vai-jobspec-tools/branch/main/graph/badge.svg?token=ZX37CSBE50)](https://codecov.io/gh/voxelai/vai-jobspec-tools)
[![Tests](https://github.com/voxelai/vai-jobspec-tools/workflows/Tests/badge.svg)](https://github.com/voxelai/vai-jobspec-tools/actions/workflows/test.yaml)
[![Code Style](https://github.com/voxelai/vai-jobspec-tools/workflows/Code%20Style/badge.svg)](https://github.com/voxelai/vai-jobspec-tools/actions/workflows/lint.yaml)
[![Type Check](https://github.com/voxelai/vai-jobspec-tools/workflows/Type%20Check/badge.svg)](https://github.com/voxelai/vai-jobspec-tools/actions/workflows/type-check.yaml)

## Installation

```bash
pip install vai-jobspec-tools
```

## API

```python
from __future__ import annotations

import contextlib
import logging
from pathlib import Path
from typing import Iterator


def configure_logger(
    logger: logging.Logger,
    *,
    verbosity: int = 0,
    level: int | None = None,
):
    """Configure a logger with a level and custom stream handler."""
    ...


@contextlib.contextmanager
def optional_temporary_directory(workdir: str | Path | None = None) -> Iterator[Path]:
    """Create a temporary directory if one is not provided."""
    ...


def prepare_dst_uri(
    uri: str,
    subject_id: str,
    session_id: str,
    pipeline_name: str,
    pipeline_version: str,
    job_id: str,
    *,
    create: bool = True,
) -> str:
    """Generate a URI scoped to a particular subject, session, pipeline, version and job"""
    ...


def lowercase_alnum(s: str) -> str:
    """Transform a string so that it contains only lowercase alphanumeric characters."""
    ...

```
