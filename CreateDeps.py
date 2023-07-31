
import os
from Plotters.PlotDep import *
import Consts.Consts as Consts

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-o', '--outDir', required=True, type=str)
    args = parser.parse_args()

    rc_types = [Consts.ORC_BEGINNING, Consts.ORC_EMBEDDED, Consts.SRC_BEGINNING, Consts.SRC_EMBEDDED]
    for rc_type in rc_types:
        out_path = os.path.join(args.outDir, '.'.join([rc_type, 'svg']))
        PlotDep.build(rc_type).save(out_path)

    print("finished creating figs")