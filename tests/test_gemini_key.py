import os

import pytest


def test_gemini_env_key_format_if_set():
    """
    Keep this as a lightweight config test:
    - If key is set, validate rough format.
    - If key is not set, skip (non-blocking in CI/local).
    """
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        pytest.skip("GEMINI_API_KEY not set in environment")
    assert isinstance(key, str)
    assert len(key) > 20
    assert key.startswith("AIza")


def test_gemini_library_import_optional():
    """
    Gemini SDK import is optional for core backend tests.
    """
    try:
        import google.generativeai as _  # noqa: F401
    except Exception:
        pytest.skip("google-generativeai package not available")
