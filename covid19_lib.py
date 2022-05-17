#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pip install pandas
# pip install numpy
# pip install requests
# pip install datetime
import os
import requests
import datetime
import os
import pandas as pd
import numpy as np

class url_download():
    def __init__(self,):
        self.MHLW_URLs = ['https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_daily.csv'
                        ,'https://covid19.mhlw.go.jp/public/opendata/requiring_inpatient_care_etc_daily.csv'
                        ,'https://covid19.mhlw.go.jp/public/opendata/deaths_cumulative_daily.csv'
                        ,'https://covid19.mhlw.go.jp/public/opendata/severe_cases_daily.csv'
                        ,'https://www.mhlw.go.jp/content/pcr_tested_daily.csv'
                        ,'https://www.mhlw.go.jp/content/pcr_case_daily.csv'
                        ,'https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_per_100_thousand_population_daily.csv'
                        # ,'https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_detail_weekly.csv'
                    ]
        self.NHK_URLs= ['https://www3.nhk.or.jp/n-data/opendata/coronavirus/nhk_news_covid19_prefectures_daily_data.csv']
    
        self.MHLW_fnames = ['database/newly_confirmed_cases_daily.csv'
                            ,'database/requiring_inpatient_care_etc_daily.csv'
                            ,'database/severe_cases_daily.csv'
                            ,'database/deaths_cumulative_daily.csv'
                            ,'database/pcr_case_daily.csv'
                            ,'database/pcr_tested_daily.csv'
                            ,'database/newly_confirmed_cases_per_100_thousand_population_daily.csv']

        self.NHK_fnames = ['database/nhk_news_covid19_prefectures_daily_data.csv']

    def url_download_csv(self,url):
        os.makedirs('database', exist_ok=True)
        urlData = requests.get(url).content
        filename = url.split('/')[-1]
        with open('database/'+filename ,mode='wb') as f:
            f.write(urlData)

    def download_MHLW(self):
        for url in self.MHLW_URLs:
            print(' - download from:'+url)
            self.url_download_csv(url)

class csv_load():
    def __init__(self,):
        self.MHLW_names = [  'pcr_tested'
                            ,'inpatient'
                            ,'newly_confirmed_cases'
                            ,'severe_cases'
                            ,'deaths'
                            ,'pcr_case'
                            ,'newly_confirmed_cases_per_100k']
        self.MHLW_fnames = ['database/pcr_tested_daily.csv'
                            ,'database/requiring_inpatient_care_etc_daily.csv'
                            ,'database/newly_confirmed_cases_daily.csv'
                            ,'database/severe_cases_daily.csv'
                            ,'database/deaths_cumulative_daily.csv'
                            ,'database/pcr_case_daily.csv'
                            ,'database/newly_confirmed_cases_per_100_thousand_population_daily.csv']

        self.NHK_names = ['prefectures']
        self.NHK_fnames = ['database/nhk_news_covid19_prefectures_daily_data.csv']

    def read_csv(self,fname):
        df = pd.read_csv(fname)
        date_name=df.columns[0]
        for ii in range(0,len(df),1):
            if type(df.at[ii,date_name])==str:
                df.at[ii,date_name]=datetime.datetime.strptime(df.at[ii,date_name], "%Y/%m/%d")
            else:
                df.at[ii,date_name]=df.at[ii-1,date_name]
        return(df)

    def make_mag(self,df):
        df_tmp=df.copy()
        df_mag=df.copy()
        # print(df[df.columns[1]])
        for jj,pref in enumerate(df.columns):
            for ii in range(0,len(df)):
                if jj != 0:
                    # df_tmp[pref] = df.iloc[:,jj].rolling(window=7, min_periods=1).mean().iloc[-1]
                    num = min(ii,6)
                    ave = 0
                    for kk in range(0,num+1):
                        ave += df.at[ii-kk,pref]
                    df_tmp.at[ii,pref]=ave/(num+1)
                    # df_tmp.at[ii,pref]=(df.at[ii,pref]
                    #                 +df.at[ii-1,pref]
                    #                 +df.at[ii-2,pref]
                    #                 +df.at[ii-3,pref]
                    #                 +df.at[ii-4,pref]
                    #                 +df.at[ii-5,pref]
                    #                 +df.at[ii-6,pref])/7
        # print(df_tmp[df_tmp.columns[1]])
        for jj,pref in enumerate(df_tmp.columns):
            if jj!=0:
                for ii in range(0,len(df_tmp)):
                    if ii >= 7 and jj != 0 and df_tmp.at[ii-7,pref]!=0:
                        df_mag.at[ii,pref]=df_tmp.at[ii,pref]/df_tmp.at[ii-7,pref]
                    else:
                        df_mag.at[ii,pref]=np.nan
        return(df_mag)

    def load_MHLW_all(self):
        ### df_list[] <= (MHLW_fnames) (MHLW_names)
        df_list=[]
        df_mag_list=[]
        for ii,fname in enumerate(self.MHLW_fnames):
            df,df_mag=self.load_MHLW(ii)
            df_list.append(df)
            df_mag_list.append(df_mag)
        return(df_list,df_mag_list)

    def load_MHLW(self,no):
        fname =self.MHLW_fnames[no]
        print(' - load from:'+fname)
        df=self.read_csv(fname)
        df_mag=self.make_mag(df)
        df.name = self.MHLW_names[no]
        df_mag.name = self.MHLW_names[no]
        return(df,df_mag)

if __name__ == "__main__":
    download=url_download()
    download.download_MHLW()
    load=csv_load()
    df_list=load.load_MHLW_all()
