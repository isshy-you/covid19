#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as tmb
import covid19_lib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

def download_button():
    print('download & coping covid19 open data from internet')
    ap=covid19_lib.url_download()
    ap.download_MHLW()
    # tmb.showinfo("メッセージ", "downloaded")

def load_button():
    print('loading covid19 open data from csv')
    load=covid19_lib.csv_load()
    df_list=load.load_MHLW()
    # return(df_list)
    tmb.showinfo("メッセージ", "loaded")

def MakeGraph_button():
    print('making graph')
    # covid19_lib.make_graphs()   
    tmb.showinfo("メッセージ", "made graphs")

def MakeGraph(event):
    # https://teratail.com/questions/103440
    # アノテーション表示更新
    def update_annot(ind):
        pos = sc.get_offsets()[ind["ind"][0]]
        annot.xy = pos
        # annot.xytext= 0,100
        # print('pos:',pos)
        # text = "{}, {}".format(" ".join(list(map(str,ind["ind"]))), 
        #                        " ".join([names[n] for n in ind["ind"]]))
        text = "{:08.0f}".format(pos[1])
        annot.set_text(text)
        axes.text(0.1, 0.1, text, transform=axes.transAxes,bbox=boxdic)

    # hoverイベント
    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == axes and event.button is None: # 上下移動や虫眼鏡のドラッグ中は探さない
            cont, ind = sc.contains(event)
            # print(cont,ind)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                axes.text(0.1, 0.1, '00000000', transform=axes.transAxes,bbox=boxdic)
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    for ii in listbox.curselection(): #現在選択されている項目を取得
        print(str(ii)+'番目を選択中')
        load=covid19_lib.csv_load()
        df=load.load_MHLW(ii)
        sxmin='2021-07-01'
        xmin = datetime.datetime.strptime(sxmin, '%Y-%m-%d')
        xmax = np.min([np.max(df.iloc[:,0])])
        print('from:',xmin,' to:',xmax)

        fig = plt.figure(1,figsize=(6,6))
        axes = fig.add_subplot(111)

        # bboxの作成
        boxdic = {
            "facecolor" : "lightgreen",
            "edgecolor" : "darkred",
            "boxstyle" : "Round",
            "linewidth" : 2
        }

        # アノテーション生成
        annot = axes.annotate("", xy=(0,0), xytext=(0,-50),textcoords="offset points", arrowprops=dict(arrowstyle="->"),bbox=boxdic)
        # annot = axes.annotate("", xy=(0,0), xytext=(100,100),arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)
        # axes.text(0.5, 0.9, "Axes: (0.5, 0.1)", transform=axes.transAxes)


        # hoverイベントを追加
        fig.canvas.mpl_connect("motion_notify_event", hover)

        plt.title('COVID-19 from MHLW Open Data')
        sc=plt.scatter(df.iloc[:,0],df.iloc[:,1],label=df.name)
        plt.xlim(xmin,xmax)
        if ytype.get()=='Log':
            plt.yscale("log")
            # ymin = 1
            # ymax = 1_000_000
            # plt.ylim(ymin,ymax)
        plt.legend()
        plt.tick_params(axis='x', rotation=90)
        axes.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m/%d')) # yy/mm/dd
        axes.xaxis.set_major_locator(mdates.DayLocator(interval=7)) # by 1 week
        # axes.xaxis.set_major_locator(mdates.MonthLocator(interval=1)) # by 1 month
        # plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7)) # by 1 week
        plt.grid()
        # plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.show()
        plt.cla()
        plt.clf()

if __name__ == "__main__":

    root = tk.Tk()
    load=covid19_lib.csv_load()

    #initial
    ytype = tk.StringVar()
    ytype.set('Log')

    # Labelframe and Label 1, 2
    tk.Label(root, text="setting").grid(row=0, sticky="e")
    labelframe = tk.LabelFrame(root, text="Y Axis")
    labelframe.grid(row=0, column=1, padx=10, pady=10)
    tk.Label(labelframe,textvariable=ytype).pack() 

    # Download Button
    tk.Label(root, text="Download from MHLW").grid(row=1, sticky="e")
    tk.Button(root, text="Download", command=download_button).\
        grid(row=1, column=1, padx=10, pady=10)

    # Load Button
    tk.Label(root, text="Load from CSVs").grid(row=2, sticky="e")
    tk.Button(root, text="Load", command=load_button).\
        grid(row=2, column=1, padx=10, pady=10)

    # radioButton (Linear/Log)
    tk.Label(root, text="Select Y Axis").grid(row=3, sticky="e")
    frame_for_radio = tk.Frame(root)
    frame_for_radio.grid(row=3, column=1, padx=10, pady=10)
    tk.Radiobutton(frame_for_radio, text="Linear", value='Linear', variable=ytype).pack()
    tk.Radiobutton(frame_for_radio, text="Log", value='Log', variable=ytype).pack()

    # Listbox
    tk.Label(root, text="Data List").grid(row=4, sticky="e")
    listarray = load.MHLW_names
    txt = tk.StringVar(value=listarray) #文字列なのでStringVar()でオブジェクトを生成
    listbox = tk.Listbox(root, listvariable=txt,height=7)
    # listbox.select_set(0)
    listbox.grid(row=4, column=1, padx=10, pady=10)
    listbox.bind('<<ListboxSelect>>', MakeGraph) #項目が選択されたときの処理

    # listbox = tk.Listbox(root, height=7)
    # for line in load.MHLW_names:
    #     listbox.insert(tk.END, line)

    # Make Graph
    tk.Label(root, text="Making COVID-19 Graphs").grid(row=5, sticky="e")
    tk.Button(root, text="Make Graph", command=MakeGraph_button).\
        grid(row=5, column=1, padx=10, pady=10)







    root.title("COVID-19 open data analysis")
    root.mainloop()