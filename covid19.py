#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import os
import covid19_lib

def read_csv(fname):
    df = pd.read_csv(fname)
    date_name=df.columns[0]
    for ii in range(0,len(df),1):
        df.at[ii,date_name]=datetime.datetime.strptime(df.at[ii,date_name], "%Y/%m/%d")
    return(df)

def print_line(text,unit,value,p_value):
    line1=text+':'+'{:>0,.0f}'.format(value)+unit
    line2='('+'{:>+0,.0f}'.format(value-p_value)+unit+':'+'{:>0.0f}'.format(value/p_value*100)+'%)'
    print(line1+line2)

def print_line1(text,unit,value,p_value):
    line1=text+':'+'{:>0,.1f}'.format(value)+unit
    line2='('+'{:>+0,.1f}'.format(value-p_value)+unit+')'
    print(line1+line2)

def fwrite_line(f,text,unit,value,p_value,date):
    value_str = '{:>10,.0f}'.format(value)+unit
    p_value_str = '{:>+8,.0f}'.format(value-p_value)+unit
    p_value2_str = '{:>4.0f}'.format(value/p_value*100)
    text_str = '{:<24}'.format(text)
    f.write(text_str+'('+date+'):'+value_str+'(前週比'+p_value_str+':'+p_value2_str+'%)'+'\n')

def fwrite_line1(f,text,unit,value,p_value,date):
    value_str = '{:>9,.1f}'.format(value)+unit
    p_value_str = '{:>+7,.1f}'.format(value-p_value)+unit
    p_value2_str = '{:>3.1f}'.format(value/p_value*100)
    text_str = '{:<24}'.format(text)
    f.write(text_str+'('+date+'):'+value_str+'(前週比'+p_value_str+')\n')

def make_7dma(df,column):
    date = str(df.iloc[:,0].iloc[-1].strftime('%Y/%m/%d'))
    value = df.iloc[:,column].rolling(window=7, min_periods=1).mean().iloc[-1]
    p_value = df.iloc[:,column].rolling(window=7, min_periods=1).mean().iloc[-8]
    return(value,p_value,date)

if __name__ == "__main__":
    print('download & coping covid19 open data from internet')
    covid19_lib.url_read()    

    print('reading covid19 data from database/*.csv')
    df_death = read_csv("database/deaths_cumulative_daily.csv")
    df_newly = read_csv("database/newly_confirmed_cases_daily.csv")
    df_pcrcase = read_csv("database/pcr_case_daily.csv")
    df_pcrtest = read_csv("database/pcr_tested_daily.csv")
    df_inpatient = read_csv("database/requiring_inpatient_care_etc_daily.csv")
    df_severe = read_csv("database/severe_cases_daily.csv")
    df_newly_100k = read_csv("database/newly_confirmed_cases_per_100_thousand_population_daily.csv")

    print('making covid19 graph : result/covid19_MHLW.png')
    os.makedirs('result', exist_ok=True)

    # convert cumulative to daily
    for pref in range(1,49,1):
        buf2=df_death.at[0,df_death.columns[pref]]
        for ii in range(1,len(df_death),1):
            buf1=df_death.at[ii,df_death.columns[pref]]
            df_death.at[ii,df_death.columns[pref]]=buf1-buf2
            buf2=buf1
        df_death.at[0,df_death.columns[pref]]=0

    sxmin='2021-07-01'
    xmin = datetime.datetime.strptime(sxmin, '%Y-%m-%d')
    xmax = np.max(df_newly['Date'])
    ymin = 1
    ymax = 1000000
    # ymax = np.max(df_pcrtest.iloc[:,1],df_newly.iloc[:,1],df_inpatient.iloc[:,1],df_severe.iloc[:,1],df_death.iloc[:,1])
    # ymax1 = np.max(df_inpatient.iloc[:,1])
    # ymax2 = np.max(df_pcrtest.iloc[:,1])
    # ymax = np.max([int(ymax1),int(ymax2)])
    # All Graph
    fig = plt.figure(1,figsize=(6,6))
    axes = fig.add_subplot(111)
    # plt.plot(df_pcrcase.iloc[:,0],df_pcrcase.iloc[:,9],label="pcr_case_daily")
    plt.title('COVID-19 from MHLW Open Data (7days Moving Average)')
    plt.plot(df_pcrtest.iloc[:,0],df_pcrtest.iloc[:,1].rolling(window=7, min_periods=1).mean(),label="pcr_tested_daily")
    plt.plot(df_newly.iloc[:,0],df_newly.iloc[:,1].rolling(window=7, min_periods=1).mean(),label="newly_confirmed_cases_daily")
    plt.plot(df_inpatient.iloc[:,0],df_inpatient.iloc[:,1].rolling(window=7, min_periods=1).mean(),label="inpatient")
    plt.plot(df_severe.iloc[:,0],df_severe.iloc[:,1].rolling(window=7, min_periods=1).mean(),label="severe_cases_daily")
    plt.plot(df_death.iloc[:,0],df_death.iloc[:,1].rolling(window=7, min_periods=1).mean(),label="deaths_daily")
    plt.xlim(xmin,xmax)
    plt.yscale("log")
    plt.legend()
    plt.tick_params(axis='x', rotation=90)
    axes.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m/%d')) # yy/mm/dd
    axes.xaxis.set_major_locator(mdates.DayLocator(interval=7)) # by 1 week
    # axes.xaxis.set_major_locator(mdates.MonthLocator(interval=1)) # by 1 month
    # plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7)) # by 1 week
    plt.grid()
    # plt.gcf().autofmt_xdate()
    plt.tight_layout()
    # plt.show()
    fig.savefig('result/covid19_MHLW', bbox_inches="tight", pad_inches=0.05)
    plt.cla()
    plt.clf()
    plt.close()

    for pref in range(2,49,1):
        fig = plt.figure(1,figsize=(6,6))
        axes = fig.add_subplot(111)
        # plt.plot(df_pcrcase.iloc[:,0],df_pcrcase.iloc[:,9],label="pcr_case_daily")
        plt.title(df_death.columns[pref]+':COVID-19 from MHLW Open Data (7days Moving Average)')
        plt.plot(df_newly.iloc[:,0],df_newly.iloc[:,pref].rolling(window=7, min_periods=1).mean(),label="newly_confirmed_cases_daily")
        plt.plot(df_inpatient.iloc[:,0],df_inpatient.iloc[:,4+(pref-2)*3].rolling(window=7, min_periods=1).mean(),label="inpatient")
        plt.plot(df_severe.iloc[:,0],df_severe.iloc[:,pref].rolling(window=7, min_periods=1).mean(),label="severe_cases_daily")
        plt.plot(df_death.iloc[:,0],df_death.iloc[:,pref].rolling(window=7, min_periods=1).mean(),label="deaths_daily")
        plt.xlim(xmin,xmax)
        plt.yscale("log")
        plt.legend()
        plt.tick_params(axis='x', rotation=90)
        axes.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m/%d')) # yy/mm/dd
        axes.xaxis.set_major_locator(mdates.DayLocator(interval=7)) # by 1 week
        # axes.xaxis.set_major_locator(mdates.MonthLocator(interval=1)) # by 1 month
        # plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7)) # by 1 week
        plt.grid()
        # plt.gcf().autofmt_xdate()
        plt.tight_layout()
        # plt.show()
        fname='result/covid19_MHLW_'+'{:02d}'.format(pref-1)+df_death.columns[pref]
        fig.savefig(fname, bbox_inches="tight", pad_inches=0.05)
        plt.cla()
        plt.clf()
        plt.close()

    print('making covid19 graph : result/covid19_100k_MHLW.png')
    # 10k newly graph by Prefectures
    list = ['Hokkaido','Tokyo','Aichi','Osaka','Fukuoka','Okinawa']
    # sxmin='2021-07-01'
    sxmin='2022-01-01'
    xmin = datetime.datetime.strptime(sxmin, '%Y-%m-%d')
    xmax = np.max(df_newly_100k.iloc[:,0])
    fig = plt.figure(1,figsize=(6,6))
    axes = fig.add_subplot(111)
    for pref in list:
        plt.plot(df_newly_100k.iloc[:,0],df_newly_100k[pref].rolling(window=7, min_periods=1).mean(),label=pref)
    plt.title("COVID-19 from MHLW Open Data \n newly confirmed per 100k polulation(7daysMA)")
    plt.xlim([xmin,xmax])
    # plt.yscale("log")
    plt.legend()
    plt.tick_params(axis='x', rotation=90)
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
    plt.grid()
    plt.tight_layout()
    # plt.show()
    fig.savefig('result/covid19_100k_MHLW', bbox_inches="tight", pad_inches=0.05)
    plt.cla()
    plt.clf()
    plt.close()

    f = open('result/result.txt', 'w', encoding='UTF-8')
    f.write('厚生労働省オープンデータより週平均\n')
    print('-----------------tweet text----------------------------')
    value,p_value,date=make_7dma(df_pcrtest,1)
    print('厚生労働省データより週平均('+date+')')
    print('()内前週比')
    print_line('PCR検査数','',value,p_value)
    fwrite_line(f,'ＰＣＲ検査数　　　','',value,p_value,date)
    pcrtest=value
    p_pcrtest=p_value
    d_pcrtest=date
    value,p_value,date=make_7dma(df_newly,1)
    print_line('新規陽性者数','',value,p_value)
    fwrite_line(f,'新規陽性者数　　　','',value,p_value,date)
    newly=value
    p_newly=p_value
    d_newly=date
    if d_pcrtest==d_newly:
        print_line1('PCR検査陽性率','%',newly/pcrtest*100,p_newly/p_pcrtest*100)
        fwrite_line1(f,'ＰＣＲ検査陽性率　','%',newly/pcrtest*100,p_newly/p_pcrtest*100,date)
    value,p_value,date=make_7dma(df_inpatient,1)
    print_line('入院治療を要する者','',value,p_value)
    fwrite_line(f,'入院治療を要する者','',value,p_value,date)
    value,p_value,date=make_7dma(df_severe   ,1)
    print_line('重症者数','',value,p_value)
    fwrite_line(f,'重症者数　　　　　','',value,p_value,date)
    value,p_value,date=make_7dma(df_death    ,1)
    print_line('死亡者数','',value,p_value)
    fwrite_line(f,'死亡者数　　　　　','',value,p_value,date)
    print('#COVID19 #新型コロナ')
