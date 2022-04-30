import os
import requests
import datetime
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
            print('download from:'+url)
            self.url_download_csv(url)

class csv_load():
    def __init__(self,):
        self.MHLW_names = [  'pcr_tested'
                            ,'newly_confirmed_cases'
                            ,'inpatient'
                            ,'severe_cases'
                            ,'deaths'
                            ,'pcr_case'
                            ,'newly_confirmed_cases_per_100k']
        self.MHLW_fnames = ['database/pcr_tested_daily.csv'
                            ,'database/newly_confirmed_cases_daily.csv'
                            ,'database/requiring_inpatient_care_etc_daily.csv'
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
            df.at[ii,date_name]=datetime.datetime.strptime(df.at[ii,date_name], "%Y/%m/%d")
        return(df)

    def load_MHLW_all(self):
        df_list=[]
        for ii,fname in enumerate(self.MHLW_fnames):
            print('load from:'+fname)
            df_list.append(self.read_csv(fname))
            df_list[ii].name = self.MHLW_names[ii]
        return(df_list)

    def load_MHLW(self,no):
        fname =self.MHLW_fnames[no]
        print('load from:'+fname)
        df=self.read_csv(fname)
        df.name = self.MHLW_names[no]
        return(df)

if __name__ == "__main__":
    download=url_download()
    download.download_MHLW()
    load=csv_load()
    df_list=load.load_MHLW_all()
