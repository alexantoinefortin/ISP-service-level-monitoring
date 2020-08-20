import os

import pandas as pd
import pytest


@pytest.fixture
def path_to_data() -> str:
    """

    Fixture yielding the path to a CSV to load

    Returns
    -------
    str
        Path to a CSV to load
    """
    fp = "/tmp/acme_data.csv.gzip"

    data = [
        ["CDT", "127.0.0.1", "2020-07-26T18:23:03.110728-05:00", 0, 208],
        ["CDT", "127.0.0.1", "2020-07-26T18:24:02.394432-05:00", 0, 208],
        ["CDT", "127.0.0.1", "2020-07-26T18:25:02.623612-05:00", 0, 208],
        ["CDT", "127.0.0.1", "2020-07-26T18:30:02.952026-05:00", 0, 208],
        ["CDT", "127.0.0.1", "2020-07-26T18:31:02.952026-05:00", 0, 208],
    ]

    columns = [
        "abbreviation",
        "client_ip",
        "datetime",
        "day_of_week",
        "day_of_year",
    ]

    df = pd.DataFrame(data, columns=columns)

    df.to_csv(fp, compression="gzip")

    yield fp

    os.remove(fp)


@pytest.fixture
def expected_loaded_data_df() -> pd.DataFrame:
    """
    
    Fixture returning expected pandas.DataFrame from loaded CSV for Analyzer.loaded_data

    Returns
    -------
    pd.DataFrame
        Expected pandas.DataFrame from loaded CSV for Analyzer.loaded_data
    """
    data = [[1], [1], [1], [0], [0], [0], [0], [1], [1]]

    index = pd.to_datetime(
        [
            "2020-07-26 18:23:00",
            "2020-07-26 18:24:00",
            "2020-07-26 18:25:00",
            "2020-07-26 18:26:00",
            "2020-07-26 18:27:00",
            "2020-07-26 18:28:00",
            "2020-07-26 18:29:00",
            "2020-07-26 18:30:00",
            "2020-07-26 18:31:00",
        ]
    )

    columns = ["on_off_ind"]

    df = pd.DataFrame(data, index=index, columns=columns)

    return df


@pytest.fixture
def expected_compute_state_and_duration_df(expected_loaded_data_df: pd.DataFrame) -> pd.DataFrame:
    """

    Fixture returned expected pandas.DataFrame for Analyzer.compute_state_and_duration

    Parameters
    ----------
    expected_loaded_data_df : pd.DataFrame
        Input pandas.DataFrame for Analyzer.compute_state_and_duration

    Returns
    -------
    pd.DataFrame
        Expected pandas.DataFrame for Analyzer.compute_state_and_duration
    """

    data = [
        [1, 0.0, 0.0, 0],
        [1, 0.0, 0.0, 1],
        [0, 1.0, 1.0, 0],
        [0, 0.0, 1.0, 1],
        [0, 0.0, 1.0, 2],
        [0, 0.0, 1.0, 3],
        [1, 1.0, 2.0, 0],
        [1, 0.0, 2.0, 1],
    ]

    columns = ["on_off_ind", "change_state_ind", "change_state_tally", "state_cum_duration"]

    index = expected_loaded_data_df.index[1:]

    df = pd.DataFrame(data, columns=columns, index=index)

    return df
