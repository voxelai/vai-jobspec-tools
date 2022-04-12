import logging
import os.path as op
from pathlib import Path
from typing import NamedTuple
from urllib.parse import urlparse
from urllib.parse import urlunparse
from uuid import uuid4

import pytest

from vai_jobspec_tools import configure_logger
from vai_jobspec_tools import optional_temporary_directory
from vai_jobspec_tools import prepare_dst_uri


@pytest.fixture
def logger():
    return logging.getLogger(str(uuid4()))


def test_configure_logger_with_defaults(logger: logging.Logger):
    assert logger.level == logging.NOTSET
    assert len(logger.handlers) == 0

    configure_logger(logger)

    assert logger.level == logging.WARNING
    assert len(logger.handlers) == 1


@pytest.mark.parametrize(
    ("verbosity", "expected_level"),
    [
        (0, logging.WARNING),
        (1, logging.INFO),
        (2, logging.DEBUG),
        (3, logging.NOTSET),
        (8, logging.NOTSET),
    ],
)
def test_configure_logger_verbosity(logger: logging.Logger, verbosity, expected_level):
    assert logger.level == logging.NOTSET
    assert len(logger.handlers) == 0

    configure_logger(logger, verbosity=verbosity)

    assert logger.level == expected_level
    assert len(logger.handlers) == 1


@pytest.mark.parametrize(
    ("level", "expected_level"),
    [
        (logging.WARNING, logging.WARNING),
        (logging.INFO, logging.INFO),
        (logging.DEBUG, logging.DEBUG),
        (logging.NOTSET, logging.NOTSET),
    ],
)
def test_configure_logger_level(logger: logging.Logger, level, expected_level):
    assert logger.level == logging.NOTSET
    assert len(logger.handlers) == 0

    configure_logger(logger, level=level)

    assert logger.level == expected_level
    assert len(logger.handlers) == 1


@pytest.mark.parametrize(
    ("level", "expected_level"),
    [
        (logging.WARNING, logging.WARNING),
        (logging.INFO, logging.INFO),
        (logging.DEBUG, logging.DEBUG),
        (logging.NOTSET, logging.NOTSET),
    ],
)
def test_configure_logger_level_params_override_verbosity_param(
    logger: logging.Logger,
    level,
    expected_level,
):
    assert logger.level == logging.NOTSET
    assert len(logger.handlers) == 0

    # verbosity > 2 means that logger.level should be UNSET (if level wasn't specified)
    configure_logger(logger, level=level, verbosity=42)

    assert logger.level == expected_level
    assert len(logger.handlers) == 1


def test_optional_temporary_directory_default():
    with optional_temporary_directory() as tmpdir:
        assert tmpdir.exists()
    assert not tmpdir.exists()


def test_optional_temporary_directory_explicit_directory(tmp_path: Path):
    with optional_temporary_directory(tmp_path) as tmpdir:
        assert tmpdir.exists()
        assert tmpdir == tmp_path

    assert tmpdir.exists()
    assert tmpdir == tmp_path


def test_optional_temporary_directory_raises_if_param_does_not_exist():
    with pytest.raises(ValueError):
        with optional_temporary_directory("/some/fake/dir/xyz/"):
            ...


def test_optional_temporary_directory_raises_if_param_exists_but_not_dir(
    tmp_path: Path,
):
    tmp_file = tmp_path / "file.txt"
    tmp_file.write_text("")

    with pytest.raises(ValueError):
        with optional_temporary_directory(tmp_file):
            ...


class PrepareDstUriArgs(NamedTuple):
    uri: str
    subject_id: str
    session_id: str
    pipeline_name: str
    pipeline_version: str


@pytest.mark.parametrize("scheme", ["", "file"])
def test_prepare_dst_uri_local_file(scheme: str, tmp_path: Path):
    components = (scheme, "", str(tmp_path / "a" / "b"), "", "", "")
    uri = urlunparse(components)
    parts = PrepareDstUriArgs(uri, "sub1", "ses1", "fake-pipe", "0.0.0")
    expected_uri = op.join(*parts)
    expected_path = urlparse(expected_uri).path

    assert not op.exists(expected_path)

    dst_uri = prepare_dst_uri(*parts)

    assert dst_uri == expected_uri
    assert op.exists(expected_path)


@pytest.mark.parametrize("uri", ["gs://bucket", "gs://bucket/sub/folder"])
@pytest.mark.parametrize("suffix", ["", "/"])
def test_prepare_dst_uri_remote_file(uri: str, suffix: str):
    _uri = f"{uri}{suffix}"
    parts = PrepareDstUriArgs(_uri, "sub1", "ses1", "fake-pipe", "0.0.0")
    expected_uri = op.join(*parts)

    dst_uri = prepare_dst_uri(*parts)

    assert dst_uri == expected_uri
