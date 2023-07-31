
import os
from Outliers.OutliersBase import OutliersBase
from Outliers.OutliersHardBoundRT import OutliersHardBoundRT
from Outliers.OutliersStdRT import OutliersStdRT
from Outliers.OutliersQuestionsRT import OutliersQuestionsRT
from Outliers.OutliersNone import OutliersNone
import pandas as pd
import Consts.Consts as Consts

# create csv files for wm, exp and spr from jsons, slicing outliers on the way
if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-a', '--sprFile', required=True, type=str, help='path to spr df (json)')
    parser.add_argument('-b', '--expFile', required=True, type=str, help='path to exp df (json)')
    parser.add_argument('-c', '--wmFile', required=True, type=str, help='path to wm df (json)')
    parser.add_argument('-o', '--outputFile', required=True, type=str, help='path to sliced spr df (csv)')
    parser.add_argument('-r', '--outliers', default='QuestionsRT,HardBoundRT,StdRT')
    args = parser.parse_args()

    # spr
    spr = pd.read_json(args.sprFile, orient='table')
    to_reject = pd.unique(spr[spr[Consts.TOEXCLUDE] > 0][Consts.SUBJECTNUMBER]).tolist()
    outliers = args.outliers.split(',')
    for outlier in outliers:
        spr = OutliersBase.build(outlier, df=spr, to_reject=to_reject).reject().get_df()
    spr = OutliersBase.build('None', df=spr, to_reject=to_reject).slice_on_main_verb()
    keep = pd.unique(spr[Consts.SUBJECTNUMBER]).tolist()
    out_file = os.path.join(args.outputFile, '.'.join([args.sprFile.split('/')[-1].split('.')[0], 'csv']))
    spr.to_csv(out_file)

    # exp and wm
    for f in [args.expFile, args.wmFile]:
        df = pd.read_json(f, orient='table')
        df = df[df[Consts.SUBJECTNUMBER].isin(keep)]
        out_file = os.path.join(args.outputFile, '.'.join([f.split('/')[-1].split('.')[0], 'csv']))
        df.to_csv(out_file)

