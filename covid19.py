#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pip install pandas
# pip install numpy
# pip install matplotlib

import datetime
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# import tqdm
import covid19_lib
# import math

def print_line(text,mode,unit,value,p_value): #１ライン表示(未使用)
    line1=text+':'+'{:>0,.0f}'.format(value)+unit
    if mode==0:
        line2='('+'{:>+0,.0f}'.format(value-p_value)+unit+':'+'{:>0.0f}'.format(value/p_value*100)+'%)'
    else:
        line2='('+'{:>+0,.1f}'.format(value-p_value)+unit+')'
    print(line1+line2)

def fwrite_line_tw(f,mode,text,unit,value,p_value): #結果文字列Twitter用
    line1=text+':'+'{:>0,.0f}'.format(value)+unit
    if mode==0:
        line2='('+'{:>+0,.0f}'.format(value-p_value)+unit+':'+'{:>0.0f}'.format(value/p_value*100)+'%)'+'\n'
    else:
        line2='('+'{:>+0,.1f}'.format(value-p_value)+unit+')'+'\n'
    f.write(line1+line2)

def fwrite_line(f,mode,text,unit,value,p_value,date): #結果文字列
    if mode==0: #
        text_str = '{:<24}'.format(text) #タイトル文字
        value_str = '{:>10,.0f}'.format(value)+unit #人数
        p_value_str = '{:>+8,.0f}'.format(value-p_value)+unit #前週比人数
        p_value2_str = '{:>4.0f}'.format(value/p_value*100) #前週率
        f.write(text_str+'('+date+'):'+value_str+'(前週比'+p_value_str+':'+p_value2_str+'%)'+'\n')
    else: #PCR検査陽性率
        text_str = '{:<24}'.format(text)
        value_str = '{:>9,.1f}'.format(value)+unit
        p_value_str = '{:>+7,.1f}'.format(value-p_value)+unit
        f.write(text_str+'('+date+'):'+value_str+'(前週比'+p_value_str+')\n')

def make_7dma(df,column): #７日移動平均計算
    date = str(df.iloc[:,0].iloc[-1].strftime('%Y/%m/%d'))
    value = df.iloc[:,column].rolling(window=7, min_periods=1).mean().iloc[-1]
    p_value = df.iloc[:,column].rolling(window=7, min_periods=1).mean().iloc[-8]
    return(value,p_value,date)

def make_tweet_text(df_list): #twitter 用TXT生成
    f_tw = open('result/twitter.txt', 'w', encoding='UTF-8')
    f_tw.write('-----------------tweet text----------------------------'+'\n')
    f_tw.write('#COVID19 #新型コロナ'+'\n')
    value,p_value,date=make_7dma(df_list[pcrtest_no],1)
    f_tw.write('厚生労働省データより週平均('+date+')'+'\n')
    f_tw.write('()内前週比'+'\n')
    fwrite_line_tw(f_tw,0,'PCR検査数','',value,p_value)
    pcrtest=value
    p_pcrtest=p_value
    d_pcrtest=date
    value,p_value,date=make_7dma(df_list[newly_no],1)
    fwrite_line_tw(f_tw,0,'新規陽性者数','',value,p_value)
    newly=value
    p_newly=p_value
    d_newly=date
    if d_pcrtest==d_newly:
        fwrite_line_tw(f_tw,1,'PCR検査陽性率','%',newly/pcrtest*100,p_newly/p_pcrtest*100)
    value,p_value,date=make_7dma(df_list[inpatient_no],1)
    fwrite_line_tw(f_tw,0,'入院治療を要する者','',value,p_value)
    value,p_value,date=make_7dma(df_list[severe_no]   ,1)
    fwrite_line_tw(f_tw,0,'重症者数','',value,p_value)
    value,p_value,date=make_7dma(df_list[death_no]    ,1)
    fwrite_line_tw(f_tw,0,'死亡者数','',value,p_value)
    f_tw.close()

def make_result_text(df_list): #結果テキスト生成
    f = open('result/result.txt', 'w', encoding='UTF-8')
    f.write('厚生労働省オープンデータより週平均\n')
    value,p_value,date=make_7dma(df_list[pcrtest_no],1)
    fwrite_line(f,0,'ＰＣＲ検査数　　　','',value,p_value,date)
    pcrtest=value
    p_pcrtest=p_value
    d_pcrtest=date
    value,p_value,date=make_7dma(df_list[newly_no],1)
    fwrite_line(f,0,'新規陽性者数　　　','',value,p_value,date)
    newly=value
    p_newly=p_value
    d_newly=date
    if d_pcrtest==d_newly:
        fwrite_line(f,1,'ＰＣＲ検査陽性率　','%',newly/pcrtest*100,p_newly/p_pcrtest*100,date)
    value,p_value,date=make_7dma(df_list[inpatient_no],1)
    fwrite_line(f,0,'入院治療を要する者','',value,p_value,date)
    value,p_value,date=make_7dma(df_list[severe_no]   ,1)
    fwrite_line(f,0,'重症者数　　　　　','',value,p_value,date)
    value,p_value,date=make_7dma(df_list[death_no]    ,1)
    fwrite_line(f,0,'死亡者数　　　　　','',value,p_value,date)
    f.close()

def make_graph_MHLW_NCR():
    # newly_confirmed/pcrtest ratio graph
    print('making covid19 graph : result/covid19_MHLW_ncr.png')
    fig = plt.figure(1,figsize=(6,6))
    axes = fig.add_subplot(111)
    plt.title('COVID-19 from MHLW Open Data:newly confirmed ratio(7days Moving Average)')
    # plt.plot(df_list[pcrtest_no].iloc[:,0],df_list[pcrtest_no].iloc[:,1],label=load.MHLW_names[pcrtest_no])
    # plt.plot(df_list[newly_no].iloc[:,0],df_list[newly_no].iloc[:,1],label=load.MHLW_names[newly_no])
    plt.plot(df_list[newly_no].iloc[:,0]
                ,df_list[newly_no].iloc[:,1].rolling(window=7, min_periods=1).mean()\
                /df_list[pcrtest_no].iloc[:,1].rolling(window=7, min_periods=1).mean())
    xmax1 = max(df_list[pcrtest_no].iloc[:,0])
    xmax2 = max(df_list[newly_no].iloc[:,0])
    xmax = min([xmax1,xmax2])
    print('from:',xmin,' to:',xmax)
    # plt.xlim(xmin,xmax)
    # plt.yscale("log")
    plt.legend()
    plt.tick_params(axis='x', rotation=90)
    axes.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m/%d')) # yy/mm/dd
    # axes.xaxis.set_major_locator(mdates.DayLocator(interval=7)) # by 1 week
    # axes.xaxis.set_major_locator(mdates.MonthLocator(interval=1)) # by 1 month
    # plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7)) # by 1 week
    plt.grid()
    # plt.gcf().autofmt_xdate()
    plt.tight_layout()
    # plt.show()
    fig.savefig('result/covid19_MHLW_ncr.png', bbox_inches="tight", pad_inches=0.05)
    plt.cla()
    plt.clf()

def make_graph_MHLW_ALL():
    # All Graph
    fig = plt.figure(1,figsize=(6,6))
    axes = fig.add_subplot(111)
    print('making covid19 graph : result/covid19_MHLW_All_7dMA')
    plt.title('COVID-19 from MHLW Open Data (7days Moving Average)')
    xmax = datetime.datetime.strptime('2100-01-01', '%Y-%m-%d')
    for ii in [pcrtest_no,newly_no,inpatient_no,severe_no,death_no]:
        plt.plot(df_list[ii].iloc[:,0],df_list[ii].iloc[:,1].rolling(window=7, min_periods=1).mean(),label=load.MHLW_names[ii])
        xtmp = np.max([df_list[ii].iloc[:,0]])
        xmax = np.min([xtmp,xmax])
    print('from:',xmin,' to:',xmax)
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
    fig.savefig('result/covid19_MHLW_All_7dMA', bbox_inches="tight", pad_inches=0.05)
    plt.cla()
    plt.clf()
    # plt.close()

def make_graph_MHLW_MAG():
    fig = plt.figure(1,figsize=(6,6))
    axes = fig.add_subplot(111)
    print('making covid19 magnitude graph : result/covid19_MHLW_All_7dMA_mag')
    plt.title('COVID-19 from MHLW Open Data (7days Moving Average)')
    xmax = datetime.datetime.strptime('2100-01-01', '%Y-%m-%d')
    for ii in [newly_no,inpatient_no,severe_no,death_no]:
    # for ii in [pcrtest_no,newly_no,inpatient_no,severe_no,death_no]:
        plt.plot(df_mag_list[ii].iloc[:,0],df_mag_list[ii].iloc[:,1].rolling(window=7, min_periods=1).mean(),label=load.MHLW_names[ii])
        xtmp = np.max([df_mag_list[ii].iloc[:,0]])
        xmax = np.min([xtmp,xmax])
    print('from:',xmin,' to:',xmax)
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
    fig.savefig('result/covid19_MHLW_All_7dMA_mag', bbox_inches="tight", pad_inches=0.05)
    plt.cla()
    plt.clf()
    plt.close()

def make_graph_MHLW_PREF():
    # prefecture graph
    print('making covid19 graph for each prefecture')
    xmax = datetime.datetime.strptime('2100-01-01', '%Y-%m-%d')
    for col in range(1,len(df_list[newly_no].columns),1):
        fig = plt.figure(1,figsize=(6,6))
        axes = fig.add_subplot(111)
        # print('\r','-',df_list[newly_no].columns[col],'           ',end="")
        plt.title(df_list[newly_no].columns[col]+':COVID-19 from MHLW Open Data (7days Moving Average)')
        for jj in [newly_no,inpatient_no,severe_no,death_no]:
            if jj==inpatient_no:
                plt.plot(df_list[jj].iloc[:,0],df_list[jj].iloc[:,1+(col-1)*3].rolling(window=7, min_periods=1).mean(),label=load.MHLW_names[jj])
            else:
                plt.plot(df_list[jj].iloc[:,0],df_list[jj].iloc[:,col].rolling(window=7, min_periods=1).mean(),label=load.MHLW_names[jj])
            xtmp = np.max([df_list[jj].iloc[:,0]])
            xmax = np.min([xtmp,xmax])
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
        print('\r','-'+fname+'.png           ',end="")
        fig.savefig(fname, bbox_inches="tight", pad_inches=0.05)
        plt.cla()
        plt.clf()
        plt.close() 
    print('\r','                                     ')

def make_graph_MHLW_PREF():
    # prefecture text
    print('making covid19 magnitude list for each prefecture')
    pref_mag_num=[]
    pref_mag_val=[]
    pref_mag_name=[]
    pref_mag_color=[]
    fname='result/covid19_MHLW_Pref_Mag.txt'
    with open(fname, mode='w') as f:
        for col in range(1,len(df_mag_list[newly_no].columns),1):
            # print('\r','-',df_mag_list[newly_no].columns[col],'           ',end="")
            # for jj in [newly_no,inpatient_no]:
            jj = newly_no
            # if jj==inpatient_no:
            #     val = df_mag_list[jj].iloc[:,1+(col-1)*3].rolling(window=7, min_periods=1).mean()
            # else:
            val = df_mag_list[jj].iloc[:,col].rolling(window=7, min_periods=1).mean()
            f.write(df_list[newly_no].columns[col]+','+str(val[len(val)-1])+'\n')
            pref_mag_num.append(int(col))
            pref_mag_name.append(df_list[newly_no].columns[col])
            pref_mag_val.append(float(val[len(val)-1]))
            print('\r','-'+fname+'                   ',end="")
    print('\r','                                       ')
    for kk,val in enumerate(pref_mag_val):
        if val < 1:
            pref_mag_color.append('blue')
        else:
            pref_mag_color.append('red')
        pref_mag_val[kk]=(val-1)*100

    fig = plt.figure(1,figsize=(12,6))
    axes = fig.add_subplot(111)
    axes.bar(pref_mag_num,pref_mag_val,tick_label=pref_mag_name,color=pref_mag_color,align='center',log=False)
    axes.tick_params(axis='x', rotation=90)
    axes.set_axisbelow(True)
    # axes.grid(visible=True, which="major", color="#ababab", linestyle="-", axis="y")
    # plt.gird()
    axes.grid(which="major",alpha=0.6)
    axes.grid(which="minor",alpha=0.3)
    axes.set_title("COVID-19 from MHLW Open Data \n newly confirmed weekly increase rate \n (7days Moving Average)")
    axes.set_ylabel('increase rate [+/-%]')
    # plt.tight_layout()
    fname='result/covid19_MHLW_Pref_Mag.png'
    fig.savefig(fname, bbox_inches="tight", pad_inches=0.05)

def make_graph_MHLW_100k():
    # 10k newly graph by pickuped Prefectures
    print('making covid19 graph : result/covid19_100k_MHLW.png')
    pref_list = ['Hokkaido','Tokyo','Aichi','Osaka','Fukuoka','Okinawa']
    xmin = datetime.datetime.strptime('2022-01-01', '%Y-%m-%d')
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


if __name__ == "__main__":
    # define SWITCH
    DOWNLOAD = 1

    print('download & coping covid19 open data from internet')
    ap=covid19_lib.url_download()
    if DOWNLOAD==1 : ap.download_MHLW()

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

    os.makedirs('result', exist_ok=True)

    # death : convert cumulative to daily
    for col in range(1,len(df_list[newly_no].columns),1):
        buf2=df_list[death_no].at[0,df_list[death_no].columns[col]]
        for ii in range(1,len(df_list[death_no]),1):
            buf1=df_list[death_no].at[ii,df_list[death_no].columns[col]]
            df_list[death_no].at[ii,df_list[death_no].columns[col]]=buf1-buf2
            buf2=buf1
        df_list[death_no].at[0,df_list[death_no].columns[col]]=0

    #calculate and set xmin,xmax,ymin,ymax
    xmin = datetime.datetime.strptime('2021-07-01', '%Y-%m-%d')
    # xmax = datetime.datetime.strptime('2100-01-01', '%Y-%m-%d')
    # for ii,dname in enumerate(load.MHLW_fnames):
    #     xtmp = np.max([df_list[ii].iloc[:,0]])
    #     xmax = np.min([xtmp,xmax])
    # print('from:',xmin,' to:',xmax)
    ymin = 1
    ymax = 1_000_000

    make_graph_MHLW_NCR()
    make_graph_MHLW_ALL()
    make_graph_MHLW_MAG()
    make_graph_MHLW_PREF()
    make_graph_MHLW_PREF()
    make_graph_MHLW_100k()
    make_tweet_text(df_list)
    make_result_text(df_list)


