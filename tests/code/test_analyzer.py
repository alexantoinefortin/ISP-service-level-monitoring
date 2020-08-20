import pandas as pd

from code.analyzer import Analyzer


def test_load_data(path_to_data: str, expected_loaded_data_df: pd.DataFrame):
    """
    
    Test case for Analyzer.load_data

    Parameters
    ----------
    path_to_data : str
        Path to a CSV to load
    expected_loaded_data_df : pd.DataFrame
        Expected pandas.DataFrame from loaded CSV for Analyzer.loaded_data
    """
    input_str = path_to_data

    expected_df = expected_loaded_data_df

    actual_df = Analyzer.load_data(fp=input_str)

    assert actual_df.equals(expected_df)


def test_compute_state_and_duration(
    expected_loaded_data_df: pd.DataFrame, expected_compute_state_and_duration_df: pd.DataFrame
):
    """

    Test case for Analyzer.compute_state_and_duration

    Parameters
    ----------
    expected_loaded_data_df : pd.DataFrame
        Input pandas.DataFrame for Analyzer.compute_state_and_duration
    expected_compute_state_and_duration_df : pd.DataFrame
        Expected pandas.DataFrame for Analyzer.compute_state_and_duration
    """
    input_df = expected_loaded_data_df

    expected_df = expected_compute_state_and_duration_df

    actual_df = Analyzer.compute_state_and_duration(df=input_df)

    assert actual_df.equals(expected_df)
