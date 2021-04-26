#!/usr/bin/python
# -*- coding: utf-8 -*-
# =========================================================================
#   Program:   
#
#   Copyright (c) CESBIO. All rights reserved.
#
#   See LICENSE for details.
#
#   This software is distributed WITHOUT ANY WARRANTY; without even
#   the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE.  See the above copyright notices for more information.
#
# =========================================================================
#
# Authors: Ehsan ELWAN
#
# =========================================================================
import pandas as pd
import numpy as np

pd.set_option('display.max_columns', 20)


def mean_of_means(means):
    if len(means) > 1:
        a = (means[0]['mean'] * means[0]['count']) + (means[1]['mean'] * means[1]['count'])
        return a / (means[0]['count'] + means[1]['count'])
    else:
        return means[0]['mean']


class GeeNdviTilesCompiler:
    def __init__(self, s1_csv_file, s2_csv_file, l8_csv_file, feature_identifier):
        self.feature_identifier = "FeatureID"

        # S1 Data
        self.s1_csv_file = s1_csv_file
        self.df_s1 = pd.read_csv(s1_csv_file)
        self.df_s1['date'] = pd.to_datetime(self.df_s1['date'])
        # self.df_s1['orbit'] = self.df_s1['orbit'].map(
        #    {0: 'ASC', -1: 'DES'})
        self.df_s1 = self.df_s1.rename(columns={feature_identifier: self.feature_identifier})
        self.df_s1 = self.df_s1.sort_values(["date", self.feature_identifier]).reset_index(drop=True)

        # S2 Data
        self.s2_csv_file = s2_csv_file
        self.df_s2 = pd.read_csv(s2_csv_file)
        self.df_s2['date'] = pd.to_datetime(self.df_s2['date'])
        self.df_s2 = self.df_s2.rename(columns={feature_identifier: self.feature_identifier})
        self.df_s2 = self.df_s2.sort_values(["date", self.feature_identifier]).reset_index(drop=True)

        # L8 Data
        self.l8_csv_file = l8_csv_file
        self.df_l8 = pd.read_csv(l8_csv_file)
        self.df_l8['date'] = pd.to_datetime(self.df_l8['date'])
        self.df_l8 = self.df_l8.rename(columns={feature_identifier: self.feature_identifier})
        self.df_l8 = self.df_l8.sort_values(["date", self.feature_identifier]).reset_index(drop=True)

    def concat_s2_l8(self):
        return pd.concat([self.df_s2, self.df_l8], axis=0, ignore_index=True).sort_values(
            [self.feature_identifier, "date"]).reset_index(drop=True)

    def interpolate_s1_s2_l8(self, with_l8=False):
        optic = self.df_s2
        if with_l8:
            optic = self.concat_s2_l8()
        self.df_s1["NDVI_mean"] = np.nan
        for s1_index, s1_row in self.df_s1.iterrows():
            s1_current_date = s1_row['date']
            s1_current_feature = s1_row[self.feature_identifier]
            print("Processing Date: {}  |  Feature:{}".format(s1_current_date, s1_current_feature))
            ndvis = []
            s2_subset = optic[optic[self.feature_identifier] == s1_current_feature].reset_index()
            reach_end = False
            tmp_row = None
            for s2_index, s2_row in s2_subset.iterrows():
                tmp_row = s2_row
                s2_current_date = s2_row['date']
                if s2_current_date >= s1_current_date:
                    ndvis.append(dict(mean=s2_row['NDVI_mean'], count=s2_row['NDVI_count']))
                    if s2_index > 0:
                        ndvis.append(dict(mean=s2_subset['NDVI_mean'][s2_index - 1],
                                          count=s2_subset['NDVI_count'][s2_index - 1]))
                    reach_end = True
                    break
            if not reach_end and len(ndvis) == 0:
                ndvis.append(dict(mean=tmp_row['NDVI_mean'], count=tmp_row['NDVI_count']))
            self.df_s1.at[s1_index, "NDVI_mean"] = mean_of_means(ndvis)
        return self.df_s1.sort_values([self.feature_identifier, "date"]).reset_index(drop=True)


if __name__ == "__main__":
    gee_compiler = GeeNdviTilesCompiler("../Classification/input_dataset/combined/Export_S1_Spain_250_sample_combined.csv",
                                        "../Classification/input_dataset/combined/Export_S2_Spain_250_sample_combined.csv",
                                        "../Classification/input_dataset/combined/Export_L8_Spain_250_sample_combined.csv",
                                        "FID"
                                        )
    gee_compiler.interpolate_s1_s2_l8(True).to_csv("../Classification/input_dataset/combined/compiled.csv", index=False)
