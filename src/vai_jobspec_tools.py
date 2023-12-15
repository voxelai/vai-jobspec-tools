from __future__ import annotations

import contextlib
import logging
import os
import os.path as op
import tempfile
from pathlib import Path
from typing import Iterator
from urllib.parse import urlparse


__version__ = "2.1.0"

__all__ = (
    "configure_logger",
    "optional_temporary_directory",
    "prepare_dst_uri",
    "lowercase_alnum",
)


def configure_logger(
    logger: logging.Logger,
    *,
    verbosity: int = 0,
    level: int | None = None,
):
    """Configure a logger with a level and custom stream handler.

    IMPORTANT: Calling this function more than once on a logger will
    result in multiple stream handlers with be added.
    """
    _level = max(logging.WARNING - verbosity * 10, 0) if level is None else level
    logger.setLevel(_level)
    fmt = "%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
    formatter = logging.Formatter(fmt=fmt)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)


@contextlib.contextmanager
def optional_temporary_directory(workdir: str | Path | None = None) -> Iterator[Path]:
    """Create a temporary directory if one is not provided.

    If `workdir` is `None` a temporary directory is created and returned. The
    created directory and its contents are deleted when exiting the context.

    `ValueError` is raised if `workdir` points to a non-existant directory or
    if it points to something that is not a directory.
    """
    if workdir is None:
        with tempfile.TemporaryDirectory() as _workdir:
            yield Path(_workdir)
    elif Path(workdir).is_dir():
        yield Path(workdir)
    else:
        raise ValueError(
            f"'workdir' must be an existing directory or None. Found [{workdir}]",
        )


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
    """Generate a URI scoped to a particular subject, session, pipeline, and version.

    `uri` can be a google storage URI, for example: `gs://my-bkt` or
    `gs://my-bkt/sub/folder`, it can also point to a local directory, for
    example: `./my/folder` or `file:///my/abs/folder`.

    The result is the same with and without a trailing slash.

    IMPORTANT: If `uri` is a local directory and `create` is `True` (the default)
    then the resulting intermediate folders are created.

    Examples:
        >>> prepare_dst_uri(
        ...    'gs://bkt/folder', 'sub1', 'ses2', 'fake-pipe', '0.0.0', '001'
        ... )
        'gs://bkt/folder/sub1/ses2/fake-pipe/0.0.0/001'
    """
    pipeline_folder = _create_pipeline_folder_path(
        subject_id,
        session_id,
        pipeline_name,
        pipeline_version,
        job_id,
    )
    dst_uri = op.join(uri, pipeline_folder)
    # if local path then create the intermediate directories
    _uri = urlparse(dst_uri)
    if _uri.scheme in ("", "file") and create:
        os.makedirs(_uri.path, exist_ok=True)

    return dst_uri


def _create_pipeline_folder_path(
    subject_id: str,
    session_id: str,
    pipeline_name: str,
    pipeline_version: str,
    job_id: str,
):
    return op.join(subject_id, session_id, pipeline_name, pipeline_version, job_id)


def lowercase_alnum(s: str) -> str:
    """Transform a string so that it contains only lowercase alphanumeric characters.

    Examples:
        >>> lowercase_alnum('Hello, World!')
        'helloworld'
        >>> lowercase_alnum('A.String.0.1.2')
        'astring012'
        >>> lowercase_alnum('HCA9865005_V1_MR')
        'hca9865005v1mr'
    """
    return "".join(c.lower() for c in s if c.isalnum())
