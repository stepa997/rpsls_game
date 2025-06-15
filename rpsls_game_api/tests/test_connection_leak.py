# test_connection_leak.py
import gc
import pytest


def test_no_connection_leak(session):
    # Open and close 100 connections
    for _ in range(100):
        session.execute("SELECT 1")

    # gc collect
    gc.collect()

    # If leak connection this is fail
    try:
        session.execute("SELECT 1")
    except Exception as e:
        pytest.fail(f"Connection leak detected: {e}")
