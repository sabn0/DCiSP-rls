
# import packages
import Consts.Consts as Consts
import os
import argparse
import pandas as pd
from Painters.PainterBase import *
from Painters.PainterM4 import PainterM4
from Painters.PainterM5 import PainterM5
from Painters.PainterM6 import PainterM6
from Painters.PainterA5 import PainterA5
from Painters.PainterA6 import PainterA6
from Painters.PainterA7 import PainterA7
from Painters.PainterA10 import PainterA10


def create():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--DataFile', required=True, type=str, help='path to directory with json pd')
    parser.add_argument('-o', '--OutDir', required=True, type=str, help='path to main plots directory')
    parser.add_argument('-r', '--Rejection', default='None', type=str, help='Specify a type of outlier rejection')
    parser.add_argument('-f', '--Figure', required=True, type=str, help='Specify number of figure')
    parser.add_argument('-l', '--LevelSlicer', required=True, type=str, help='dict map, specify slicer: k1:v1,k2:v2..')
    parser.add_argument('-i', '--PlotKws', required=True, type=str, help='path to plot kwargs (json)')
    parser.add_argument('-j', '--GarnishKws', required=True, type=str, help='path to garnish kwargs (json)')
    args = parser.parse_args()

    # check inputs
    fig = args.Figure
    assert fig in ['M4', 'M5', 'M6', 'A5', 'A6', 'A7', 'A10'], "invalid figure requested"

    outlier_type = args.Rejection.split(',')
    plot_json = args.PlotKws
    garnish_json = args.GarnishKws
    slicer = {elem.split(':')[0]:elem.split(':')[1].split(';') for elem in args.LevelSlicer.split(',')}
    out_dir = os.path.join(args.OutDir, plot_json.split('/')[-1].split('_')[1])

    # load base df
    df_base = pd.read_json(args.DataFile, orient='table')

    # run painting
    to_reject = pd.unique(df_base[df_base[Consts.TOEXCLUDE] > 0][Consts.SUBJECTNUMBER]).tolist() if Consts.TOEXCLUDE in df_base.columns.tolist() else []
    args = [df_base, to_reject, plot_json, garnish_json, out_dir]
    PainterBase.build(fig, *args).prepare(outlier_type, kv_slicer=slicer).paint()
    print("finished creating {}".format(fig))


# main program to plot presentation graphs
if __name__ == "__main__":
    create()