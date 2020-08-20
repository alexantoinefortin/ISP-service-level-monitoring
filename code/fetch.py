import os
from typing import Union

import pandas as pd
import requests

API_URL = "http://worldtimeapi.org/api/ip"
SAVE_PATH = "../inputs/time_recorded.csv.gzip"


class TimeRecorder:
    @staticmethod
    def fetch_time() -> Union[dict, int]:
        """
        fetch_time()

        Method that fetches the current local time by accessing the internet

        Returns
        -------
        Union[dict, int]
            Fetched JSON object and request status code
        """
        r = requests.get(API_URL)

        return r.json(), r.status_code

    @staticmethod
    def to_csv(data: dict, path: str):
        """
        to_csv(data, path)

        Method that save the fetched JSON object to CSV. If the `path` exist, it will 
        append the data to it, otherwise, it will create it.

        Parameters
        ----------
        data : dict
            Fetched JSON object
        path : str
            Filepath where to save the data to
        """
        df = pd.DataFrame.from_dict(resp, orient="index").T

        if not os.path.isfile(path):
            df.to_csv(path, index=False, compression="gzip")
        else:
            df.to_csv(path, index=False, header=False, mode="a", compression="gzip")


if __name__ == "__main__":
    resp, code = TimeRecorder.fetch_time()

    if code == 200:
        TimeRecorder.to_csv(data=resp, path=SAVE_PATH)
