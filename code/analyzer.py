import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd


mpl.rcParams.update({"font.size": 18})

FILEPATH = "../inputs/time_recorded.csv.gzip"


class Analyzer:
    @staticmethod
    def load_data(fp: str) -> pd.DataFrame:
        """
        load_data(fp)

        Method that returns a pandas.DataFrame f on/off data that has been filled for 
        missings

        Parameters
        ----------
        fp : str
            Filepath to CSV produced by `fetch.py`

        Returns
        -------
        pd.DataFrame
            pandas.DataFrame of on/off data that has been filled for missings
        """

        df = pd.read_csv(fp, compression="gzip")

        df["datetime"] = pd.to_datetime(df["datetime"]).dt.strftime('%Y-%m-%d %H:%M')
        df = df.set_index("datetime").sort_index()

        # Resampling at 1-min intervals
        full_date_series = pd.date_range(start=df.index[0], end=df.index[-1], freq='1T')
        full_date_series = pd.to_datetime(full_date_series.strftime('%Y-%m-%d %H:%M'))

        on_off_data = pd.DataFrame({"on_off_ind": [0] * len(full_date_series)}, index=full_date_series)

        cond_on = [on_off_data.index.isin(df.index)][0]

        on_off_data.loc[cond_on, "on_off_ind"] = 1

        return on_off_data

    @staticmethod
    def compute_state_and_duration(df: pd.DataFrame) -> pd.DataFrame:
        """
        compute_state_and_duration(df)

        Method that returns a pandas.DataFrame of on/off data with additional statistics

        Parameters
        ----------
        df : pd.DataFrame
            pandas.DataFrame of on/off data that has been filled for missings

        Returns
        -------
        pd.DataFrame
            pandas.DataFrame of on/off data with additional statistics
        """

        df["change_state_ind"] = df["on_off_ind"].diff().abs()
        df = df.dropna().copy()
        df["change_state_tally"] = df["change_state_ind"].cumsum()
        df["state_cum_duration"] = df.groupby(["change_state_tally"])["on_off_ind"].cumcount()

        return df

    @staticmethod
    def get_summary_data(df: pd.DataFrame, freq: str) -> pd.DataFrame:
        """
        get_summary_data(df, freq)

        Method that returns a summary pandas.DataFrame with number of interruptions and 
        time without internet

        Parameters
        ----------
        df : pd.DataFrame
            pandas.DataFrame of on/off data with additional statistics
        freq : str
            Frequency at which to resample `df`, one of:
              - "12H"
              - "24H"

        Returns
        -------
        pd.DataFrame
            Summary pandas.DataFrame with number of interruptions and time without internet
        """
        mapping_dict = {"12H": 12 * 60, "24H": 24 * 60, "1D": 24 * 60}

        r = df["on_off_ind"].resample(freq).sum().to_frame().rename(columns={"on_off_ind": "time_on"})
        r["day_of_week"] = r.index.day_name()
        r["am_pm"] = r.index.strftime("%p")
        r["number_interruptions"] = (
            df[df["state_cum_duration"] == 2]["on_off_ind"].diff().abs().resample(freq).count() // 2
        )
        r["time_without_internet"] = mapping_dict.get(freq, None) - r["time_on"]
        r["avg_interruption_time"] = r["time_without_internet"] / r["number_interruptions"]

        r = r.drop("time_on", axis=1)[1:-1]
        r.index = r.index.strftime(f"%Y-%m-%d{' %p' if freq not in ['1D', '24H'] else ''}").tolist()

        return r

    @staticmethod
    def plot_time_without_internet(df: pd.DataFrame, show: bool = False, save: bool = True):
        """
        plot_time_without_internet(df, show, save)

        Function that plots the time without internet.

        Parameters
        ----------
        df : pd.DataFrame
            Summary pandas.DataFrame with number of interruptions and time without internet
        show : bool, optional
            Whether or not to call `.show()` on the figure, by default False
        save : bool, optional
            Whether or not to save the figure to disk, by default save to 
            "../outputs/time_without_internet_per_{freq}.png"
        """

        has_am_pm = True if len(df["am_pm"].unique()) == 2 else False
        freq = "12H" if has_am_pm else "24H"
        num_plots = 2 if has_am_pm else 1

        fig, ax = plt.subplots(1, num_plots, figsize=(15, 7), squeeze=False)

        df.plot.bar(
            use_index=True,
            y="time_without_internet",
            title=f"Time (minutes)\nwithout internet per {freq.lower()}",
            ax=ax[0, 0],
        )
        ax[0, 0].set_ylabel("Minutes")
        ax[0, 0].grid(alpha=0.5)
        ax[0, 0].set_yticks(range(0, 800, 30))
        ax[0, 0].set_ylim([0, df["time_without_internet"].max() * 1.02])

        if has_am_pm:
            df.groupby("am_pm")["time_without_internet"].mean().plot.bar(
                ax=ax[0, 1], title="Expected time (minutes)\nwithout internet"
            )
            ax[0, 1].grid(alpha=0.5)

        plt.tight_layout()

        if save:
            plt.savefig(f"../outputs/time_without_internet_per_{freq}.png")
        if show:
            plt.show()

    @staticmethod
    def plot_number_of_interruptions(df: pd.DataFrame, show: bool = False, save: bool = True):
        """
        plot_number_of_interruptions(df, show, save)

        Function that plots the number of interruptions.

        Parameters
        ----------
        df : pd.DataFrame
            Summary pandas.DataFrame with number of interruptions and time without internet
        show : bool, optional
            Whether or not to call `.show()` on the figure, by default False
        save : bool, optional
            Whether or not to save the figure to disk, by default save to 
            "../outputs/number_of_interruptions_per_{freq}.png"
        """

        has_am_pm = True if len(df["am_pm"].unique()) == 2 else False
        freq = "12H" if has_am_pm else "24H"
        num_plots = 2 if has_am_pm else 1

        fig, ax = plt.subplots(1, num_plots, figsize=(15, 7), squeeze=False)

        title = f"Historical number of interruptions\n per {freq.lower()}"
        df.plot.bar(
            use_index=True, y="number_interruptions", title=title, ax=ax[0, 0],
        )
        ax[0, 0].set_ylabel("Count")
        ax[0, 0].grid(alpha=0.5)

        if has_am_pm:
            title = "Expected number of interruptions"
            df.groupby("am_pm")["number_interruptions"].mean().plot.bar(ax=ax[0, 1], title=title)
            ax[0, 1].grid(alpha=0.5)

        plt.tight_layout()

        if save:
            plt.savefig(f"../outputs/number_of_interruptions_per_{freq}.png")
        if show:
            plt.show()

    @staticmethod
    def reporting(on_off_data: pd.DataFrame, summary_data: pd.DataFrame):
        """
        reporting(on_off_data, summary_data)

        Method that prints some summary statistics to Stdout
        Parameters
        ----------
        on_off_data : pd.DataFrame
            pandas.DataFrame of on/off data with additional statistics
        summary_data : pd.DataFrame
            Summary pandas.DataFrame with number of interruptions and time without internet
        """

        total_time = (on_off_data.index.max() - on_off_data.index.min()).total_seconds() / 60
        prc_time_down = 100 * summary_data["time_without_internet"].sum() / total_time

        print(
            f"Internet has been down {prc_time_down:.2f}% of the time between"
            + f" {summary_data.index.min()} and {summary_data.index.max()} "
            + f"({int(total_time/60/24)} days)"
        )

    @classmethod
    def produce_plots(cls, df: pd.DataFrame, show: bool = False, save: bool = True):
        """
        produce_plots(df, show, save)

        Method that produces both the time without internet and number of interruptions 
        plots.
        
        Parameters
        ----------
        df : pd.DataFrame
            Summary pandas.DataFrame with number of interruptions and time without internet
        show : bool, optional
            Whether or not to call `.show()` on the figure, by default False
        save : bool, optional
            Whether or not to save the figure to disk, by default True
        """

        cls.plot_time_without_internet(df=df, show=show, save=save)
        cls.plot_number_of_interruptions(df=df, show=show, save=save)

    @classmethod
    def run(cls, fp: str, freq: str, show: bool = False, save: bool = True):
        """
        run(fp, freq, show, save)

        Method that execute the natural order of the method of this class:
          - load_data
          - compute_state_and_duration
          - get_summary_data
          - plot_time_without_internet
          - plot_number_of_interruptions
          - reporting
    
        Parameters
        ----------
        fp : str
            Filepath to CSV produced by `fetch.py`
        freq : str
            Frequency at which to resample the loaded data, one of:
              - "12H"
              - "24H"
        show : bool, optional
            Whether or not to call `.show()` on the figure, by default False
        save : bool, optional
            Whether or not to save the figure to disk, by default True
        """

        on_off_data = cls.load_data(fp=fp)
        on_off_data = cls.compute_state_and_duration(df=on_off_data)
        summary_data = cls.get_summary_data(df=on_off_data, freq=freq)

        cls.plot_time_without_internet(df=summary_data, show=show, save=save)
        cls.plot_number_of_interruptions(df=summary_data, show=show, save=save)

        cls.reporting(on_off_data=on_off_data, summary_data=summary_data)


if __name__ == "__main__":
    Analyzer.run(fp=FILEPATH, save=False, freq="12H")
    Analyzer.run(fp=FILEPATH, save=False, freq="24H")

