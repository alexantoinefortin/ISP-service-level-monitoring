from code.fetch import TimeRecorder


def test_fetch_time():
    """
    Basic test case for TimeRecorder.fetch_time
    """
    actual_json, actual_status_code = TimeRecorder.fetch_time()

    assert isinstance(actual_json, dict)
    assert actual_status_code == 200
