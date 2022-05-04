#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# import tqdm
import datetime
import os
import covid19_lib
import math

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
    ap=covid19_lib.url_download()
    ap.download_MHLW()
    # # covid19_lib.url_download()    

    print('reading covid19 data from database/*.csv')
    load=covid19_lib.csv_load()
    df_list,df_mag_list=load.load_MHLW_all()
    
    pcrtest_no = load.MHLW_names.index('pcr_tested') #0
    inpatient_no = load.MHLW_names.index('inpatient') #1
    newly_no = load.MHLW_names.index('newly_confirmed_cases') #2
    severe_no = load.MHLW_names.index('severe_cases') #3
    death_no = load.MHLW_names.index('deaths') #4
    pcrcase_no = load.MHLW_names.index('pcr_case') #5
    newly_100k_no = load.MHLW_names.index('newly_confirmed_cases_per_100k') #6

    print('making covid19 graph : result/covid19_MHLW.png')
    os.makedirs('result', exist_ok=True)

    # death : convert cumulative to daily
    for col in range(1,len(df_list[newly_no].columns),1):
        buf2=df_list[death_no].at[0,df_list[death_no].columns[col]]
        for ii in range(1,len(df_list[death_no]),1):
            buf1=df_list[death_no].at[ii,df_list[death_no].columns[col]]
            df_list[death_no].at[ii,df_list[death_no].columns[col]]=buf1-buf2
            buf2=buf1
        df_list[death_no].at[0,df_list[death_no].columns[col]]=0

    sxmin='2021-07-01'
    xmin = datetime.datetime.strptime(sxmin, '%Y-%m-%d')
        
    xmax = datetime.datetime.strptime('2100-01-01', '%Y-%m-%d')
    print(xmax)
    for ii,dname in enumerate(load.MHLW_fnames):
        xtmp = np.max([df_list[ii].iloc[:,0]])
        xmax = np.min([xtmp,xmax])

    print('from:',xmin,' to:',xmax)
    ymin = 1
    ymax = 1_000_000
    # ymax = np.max(df_pcrtest.iloc[:,1],df_newly.iloc[:,1],df_inpatient.iloc[:,1],df_severe.iloc[:,1],df_death.iloc[:,1])

    # All Graph
    fig = plt.figure(1,figsize=(6,6))
    axes = fig.add_subplot(111)
    # plt.plot(df_pcrcase.iloc[:,0],df_pcrcase.iloc[:,9],label="pcr_case_daily")
    plt.title('COVID-19 from MHLW Open Data')
    plt.plot(df_list[pcrtest_no].iloc[:,0],df_list[pcrtest_no].iloc[:,1],label=load.MHLW_names[pcrtest_no])
    plt.plot(df_list[newly_no].iloc[:,0],df_list[newly_no].iloc[:,1],label=load.MHLW_names[newly_no])
    plt.xlim(xmin,xmax)
    # plt.yscale("log")
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

    plt.title('COVID-19 from MHLW Open Data (7days Moving Average)')
    for ii in [pcrtest_no,newly_no,inpatient_no,severe_no,death_no]:
        plt.plot(df_list[ii].iloc[:,0],df_list[ii].iloc[:,1].rolling(window=7, min_periods=1).mean(),label=load.MHLW_names[ii])
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
    fig.savefig('result/covid19_MHLW_00All_7dMA', bbox_inches="tight", pad_inches=0.05)
    plt.cla()
    plt.clf()
    plt.close()

    print('making covid19 graph for each prefecture')
    for col in range(1,len(df_list[newly_no].columns),1):
    # for col in tqdm.tqdm(range(2,len(df_newly.columns),1)):
        # plt.plot(df_pcrcase.iloc[:,0],df_pcrcase.iloc[:,9],label="pcr_case_daily")
        fig = plt.figure(1,figsize=(6,6))
        axes = fig.add_subplot(111)
        # print('\r','-',df_list[newly_no].columns[col],'           ',end="")
        plt.title(df_list[newly_no].columns[col]+':COVID-19 from MHLW Open Data (7days Moving Average)')
        for jj in [newly_no,inpatient_no,severe_no,death_no]:
            if jj==inpatient_no:
                plt.plot(df_list[jj].iloc[:,0],df_list[jj].iloc[:,1+(col-1)*3].rolling(window=7, min_periods=1).mean(),label=load.MHLW_names[jj])
            else:
                plt.plot(df_list[jj].iloc[:,0],df_list[jj].iloc[:,col].rolling(window=7, min_periods=1).mean(),label=load.MHLW_names[jj])
        plt.xlim(xmin,xmax)
        plt.ylim(1,1000_000)
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
        fname='result/covid19_MHLW_'+'{:02d}'.format(col-1)+df_list[newly_no].columns[col]
        print('\r','-',fname,'.png           ',end="")
        fig.savefig(fname, bbox_inches="tight", pad_inches=0.05)
        plt.cla()
        plt.clf()
        plt.close() 
    print('\r','                                     ')

    print('making covid19 graph : result/covid19_100k_MHLW.png')
    # 10k newly graph by Prefectures
    pref_list = ['Hokkaido','Tokyo','Aichi','Osaka','Fukuoka','Okinawa']
    # sxmin='2021-07-01'
    sxmin='2022-01-01'
    xmin = datetime.datetime.strptime(sxmin, '%Y-%m-%d')
    xmax = np.max(df_list[newly_100k_no].iloc[:,0])
    fig = plt.figure(1,figsize=(6,6))
    axes = fig.add_subplot(111)
    for pref in pref_list:
        plt.plot(df_list[newly_100k_no].iloc[:,0],df_list[newly_100k_no][pref].rolling(window=7, min_periods=1).mean(),label=pref)
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
    value,p_value,date=make_7dma(df_list[pcrtest_no],1)
    print('厚生労働省データより週平均('+date+')')
    print('()内前週比')
    print_line('PCR検査数','',value,p_value)
    fwrite_line(f,'ＰＣＲ検査数　　　','',value,p_value,date)
    pcrtest=value
    p_pcrtest=p_value
    d_pcrtest=date
    value,p_value,date=make_7dma(df_list[newly_no],1)
    print_line('新規陽性者数','',value,p_value)
    fwrite_line(f,'新規陽性者数　　　','',value,p_value,date)
    newly=value
    p_newly=p_value
    d_newly=date
    if d_pcrtest==d_newly:
        print_line1('PCR検査陽性率','%',newly/pcrtest*100,p_newly/p_pcrtest*100)
        fwrite_line1(f,'ＰＣＲ検査陽性率　','%',newly/pcrtest*100,p_newly/p_pcrtest*100,date)
    value,p_value,date=make_7dma(df_list[inpatient_no],1)
    print_line('入院治療を要する者','',value,p_value)
    fwrite_line(f,'入院治療を要する者','',value,p_value,date)
    value,p_value,date=make_7dma(df_list[severe_no]   ,1)
    print_line('重症者数','',value,p_value)
    fwrite_line(f,'重症者数　　　　　','',value,p_value,date)
    value,p_value,date=make_7dma(df_list[death_no]    ,1)
    print_line('死亡者数','',value,p_value)
    fwrite_line(f,'死亡者数　　　　　','',value,p_value,date)
    print('#COVID19 #新型コロナ')
