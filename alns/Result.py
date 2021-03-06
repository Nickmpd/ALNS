import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import Axes, Figure  # pylint: disable=unused-import

from .State import State  # pylint: disable=unused-import
from .Statistics import Statistics  # pylint: disable=unused-import
from .exceptions_warnings import NotCollectedError


class Result:

    def __init__(self, best, statistics=None):
        """
        Stores ALNS results. An instance of this class is returned once the
        algorithm completes.

        Parameters
        ----------
        best : State
            The best state observed during the entire iteration.
        statistics : Statistics
            Statistics optionally collected during iteration.
        """
        self._best = best
        self._statistics = statistics

    @property
    def best_state(self):
        """
        The best state observed during the entire iteration.

        Returns
        -------
        State
            The associated State object
        """
        return self._best

    @property
    def statistics(self):
        """
        The statistics object populated during iteration.

        Raises
        ------
        NotCollectedError
            When statistics were not collected during iteration. This may be
            remedied by setting the appropriate flag.

        Returns
        -------
        Statistics
            The statistics object.
        """
        if self._statistics is None:
            raise NotCollectedError("Statistics were not collected during "
                                    "iteration.")

        return self._statistics

    def plot_objectives(self, ax=None, **kwargs):
        """
        Plots the collected objective values at each iteration.

        Parameters
        ----------
        ax : Axes
            Optional axes argument. If not passed, a new figure and axes are
            constructed.
        kwargs : dict
            Optional arguments passed to ``ax.plot``.
        """
        if ax is None:
            _, ax = plt.subplots()

        ax.plot(self.statistics.objectives, **kwargs)

        ax.set_title("Objective value at each iteration")
        ax.set_ylabel("Objective value")
        ax.set_xlabel("Iteration (#)")

        plt.draw_if_interactive()

    def plot_operator_counts(self, figure=None, title=None, legend=None,
                             **kwargs):
        """
        Plots an overview of the destroy and repair operators' performance.

        Parameters
        ----------
        figure : Figure
            Optional figure. If not passed, a new figure is constructed, and
            some default margins are set.
        title : str
            Optional figure title. When not passed, no title is set.
        legend : list
            Optional legend entries. When passed, this should be a list of
            four strings. When not passed, a sensible default is set.
        kwargs : dict
            Optional arguments passed to each call of ``ax.barh``.

        Raises
        ------
        ValueError
            When the passed-in legend list is not of appropriate length.
        """
        if figure is None:
            figure, (d_ax, r_ax) = plt.subplots(nrows=2)

            # Ensures there is generally sufficient white space between the
            # operator subplots, and we have some space to put the legend. When
            # a figure is passed-in, these sorts of modifications are assumed
            # to have been performed at the call site.
            figure.subplots_adjust(hspace=0.7, bottom=0.2)
        else:
            d_ax, r_ax = figure.subplots(nrows=2)

        if title is not None:
            figure.suptitle(title)

        if legend is not None:
            if len(legend) < 4:
                raise ValueError("Legend not understood. Expected 4 items,"
                                 " found {0}.".format(len(legend)))
        else:
            legend = ["Best", "Better", "Accepted", "Rejected"]

        self._plot_operator_counts(d_ax,
                                   self.statistics.destroy_operator_counts,
                                   "Destroy operators",
                                   **kwargs)

        self._plot_operator_counts(r_ax,
                                   self.statistics.repair_operator_counts,
                                   "Repair operators",
                                   **kwargs)

        # It is not really a problem if the legend is longer than four items,
        # but we will only use the first four.
        figure.legend(legend[:4], ncol=4, loc="lower center")

        plt.draw_if_interactive()

    @staticmethod
    def _plot_operator_counts(ax, operator_counts, title, **kwargs):
        """
        Internal helper that plots the passed-in operator_counts on the given
        ax object.

        Parameters
        ----------
        ax: Axes
            An axes object, to be populated with data.
        operator_counts : dict
            A dictionary of operator counts.
        title : str
            Plot title.
        **kwargs
            Optional keyword arguments, to be passed to ``ax.barh``.

        Note
        ----
        This code takes loosely after an example from the matplotlib gallery
        titled "Discrete distribution as horizontal bar chart".
        """
        operator_names = list(operator_counts.keys())

        operator_counts = np.array(list(operator_counts.values()))
        cumulative_counts = operator_counts.cumsum(axis=1)

        ax.set_xlim(right=np.sum(operator_counts, axis=1).max())

        for idx in range(4):
            widths = operator_counts[:, idx]
            starts = cumulative_counts[:, idx] - widths

            ax.barh(operator_names, widths, left=starts, height=0.5, **kwargs)

            for y, (x, label) in enumerate(zip(starts + widths / 2, widths)):
                ax.text(x, y, str(label), ha='center', va='center')

        ax.set_title(title)
        ax.set_xlabel("Iterations where operator resulted in this outcome (#)")
        ax.set_ylabel("Operator")
