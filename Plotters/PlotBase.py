
# import packages
from abc import ABC, abstractmethod
import pandas as pd
import matplotlib.pyplot as plt

class PlotBase:

    # in order to enable methods cascading axes are held both on the class and object levels
    plotters = {}
    axes = {None}

    def __init__(self, ax=None):
        self.ax = ax

    # I use the decorator design pattern to allow creating instances of all plotting
    # types without having to explicitly write the string of type on action
    @classmethod
    def register_plotter(cls, plotter_type):
        def decorator(plotter):
            cls.plotters[plotter_type] = plotter
            return plotter
        return decorator

    @classmethod
    def build(cls, plotter_type):
        if plotter_type not in cls.plotters:
            raise ValueError
        ax = cls.axes.pop()
        plotter = cls.plotters[plotter_type](ax=ax)
        return plotter

    # plot enables method cascading by returning self
    @abstractmethod
    def plot(self, df: pd.DataFrame):
        pass

    def set_ax(self, ax: plt.Axes) -> None:
        self.ax = ax
        PlotBase.axes.add(ax)

    def get_ax(self) -> plt.Axes:
        return self.ax

    def garnish(self, **kwargs):

        if self.ax is None:
            raise NotImplementedError("set_ax not implemented")

        plt.rcParams["font.weight"] = "bold"
        self.get_ax().tick_params(axis="x", labelsize=kwargs['font_size'])
        self.get_ax().tick_params(axis="y", labelsize=kwargs['font_size'])
        self.get_ax().set_xlabel(kwargs['x_label'], fontsize=kwargs['font_size'], fontweight='bold')
        self.get_ax().set_ylabel(kwargs['y_label'], fontsize=kwargs['font_size'], fontweight='bold')

        if kwargs['set_yticks']:
            self.get_ax().set_yticks(kwargs['set_yticks'])

        _ = [label.set_fontweight('bold') for label in self.get_ax().get_xticklabels()]
        _ = [label.set_fontweight('bold') for label in self.get_ax().get_yticklabels()]
        self.get_ax().set_title(kwargs['title'], fontsize=kwargs['font_size'], fontweight='bold')
        self.legend(**kwargs)
        return self

    def legend(self, **kwargs) -> None:
        if kwargs['legend_loc']:
            self.get_ax().legend(prop={'size': kwargs['font_size'] - 5, 'weight': 'bold'}, loc=kwargs['legend_loc'])

    def save(self, out_path: str) -> None:
        self.get_ax().get_figure().savefig(out_path, bbox_inches='tight')
        plt.clf()


