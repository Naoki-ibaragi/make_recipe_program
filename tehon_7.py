import tkinter as tk            # ウィンドウ作成用
from tkinter import filedialog  # ファイルを開くダイアログ用
from PIL import Image, ImageTk  # 画像データ用
import numpy as np              # アフィン変換行列演算用
import os                       # ディレクトリ操作用
import cv2

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack() 
 
        self.my_title = "OpenCV Tkinter GUI Sample"  # タイトル
        self.back_color = "#FFFFFF"     # 背景色

        # ウィンドウの設定
        self.master.title(self.my_title)    # タイトル
        self.master.geometry("600x400")     # サイズ

        self.pil_image = None           # 表示する画像データ
        self.filename = None            # 最後に開いた画像ファイル名
 
        self.create_menu()   # メニューの作成
        self.create_widget() # ウィジェットの作成

        self.image_list=[] #redo用画像list
        self.image_posi=[] #redo用画像list

        self.original_pixel=[] #failサンプル取得用
        self.fail_pixel=[] #failサンプル取得用
        self.fail_pattern=np.array([]) #failサンプル取得用

        self.right_click_mode = "A" #failサンプル取得用

    # -------------------------------------------------------------------------------
    # メニューイベント
    # -------------------------------------------------------------------------------
    def menu_open_clicked(self, event=None):
        # File → Open
        filename = tk.filedialog.askopenfilename(
            filetypes = [("Image file", ".bmp .png .jpg .tif"), ("Bitmap", ".bmp"), ("PNG", ".png"), ("JPEG", ".jpg"), ("Tiff", ".tif") ], # ファイルフィルタ
            initialdir = os.getcwd() # カレントディレクトリ
            )

        # 画像ファイルを設定する
        self.set_image(filename)

    def menu_reload_clicked(self, event=None):
        # File → ReLoad
        self.set_image(self.filename)

    def menu_quit_clicked(self):
        # ウィンドウを閉じる
        self.master.destroy() 

    def menu_undo_clicked(self,event=None):
        # 画像を一つ戻す
        self.undo() 

    def menu_save_clicked(self,event=None):
        # 画像を一つ戻す
        self.save() 

    def menu_open_rectfile_clicked(self,event=None):
        # 画像を一つ戻す
        self.open_rectfile()

    # -------------------------------------------------------------------------------

    # create_menuメソッドを定義
    def create_menu(self):
        self.menu_bar = tk.Menu(self) # Menuクラスからmenu_barインスタンスを生成
 
        self.file_menu = tk.Menu(self.menu_bar, tearoff = tk.OFF)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.file_menu.add_command(label="Open", command = self.menu_open_clicked, accelerator="Ctrl+O")
        self.file_menu.add_command(label="ReLoad", command = self.menu_reload_clicked, accelerator="Ctrl+R")
        self.file_menu.add_command(label="Undo", command = self.menu_undo_clicked, accelerator="Ctrl+Z")
        self.file_menu.add_command(label="Save", command = self.menu_save_clicked, accelerator="Ctrl+S")
        self.file_menu.add_separator() # セパレーターを追加
        self.file_menu.add_command(label="Open RectFile", command = self.menu_open_rectfile_clicked)
        self.file_menu.add_separator() # セパレーターを追加
        self.file_menu.add_command(label="Exit", command = self.menu_quit_clicked)

        self.menu_bar.bind_all("<Control-o>", self.menu_open_clicked) # ファイルを開くのショートカット(Ctrol-Oボタン)
        self.menu_bar.bind_all("<Control-r>", self.menu_reload_clicked) # ファイルを開くのショートカット(Ctrol-Rボタン)
        self.menu_bar.bind_all("<Control-z>", self.menu_undo_clicked) # ファイルを開くのショートカット(Ctrol-Zボタン)
        self.menu_bar.bind_all("<Control-s>", self.menu_save_clicked) # ファイルを開くのショートカット(Ctrol-Sボタン)
        self.master.config(menu=self.menu_bar) # メニューバーの配置
 
    def create_widget(self):
        '''ウィジェットの作成'''

        #####################################################
        # ステータスバー相当(親に追加)
        self.statusbar = tk.Frame(self.master)
        self.mouse_position = tk.Label(self.statusbar, relief = tk.SUNKEN, text="mouse position") # マウスの座標
        self.image_position = tk.Label(self.statusbar, relief = tk.SUNKEN, text="image position") # 画像の座標
        self.label_space = tk.Label(self.statusbar, relief = tk.SUNKEN)                           # 隙間を埋めるだけ
        self.image_info = tk.Label(self.statusbar, relief = tk.SUNKEN, text="image info")         # 画像情報
        self.mouse_position.pack(side=tk.LEFT)
        self.image_position.pack(side=tk.LEFT)
        self.label_space.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.image_info.pack(side=tk.RIGHT)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        ####################################################
        #canvas直下の変換履歴表示用のステータスバー
        self.statusbar_2 = tk.Frame(self.master)
        self.history = tk.Label(self.statusbar_2, relief = tk.SUNKEN,text="history -> ")
        self.history.pack(side=tk.LEFT)
        self.statusbar_2.pack(side=tk.BOTTOM, fill=tk.X)

        #####################################################
        #上側フレーム（fail処理用)
        top_frame = tk.Frame(self.master, relief=tk.SUNKEN,bd=2)

        #####################################################
        # 右側フレーム（画像処理用ボタン配置用）
        right_frame = tk.Frame(self.master, relief = tk.SUNKEN, bd = 2, width = 300)
        right_frame_2 = tk.Frame(self.master, relief = tk.SUNKEN, bd = 2, width = 300)
        #right_frame.propagate(False) # フーレムサイズの自動調整を無効にする
        #right_frame_2.propagate(False)

        #----------------------------
        #top_frame
        #不良ピクセル用のボタンを持ってくる
        #----------------------------
        btn_get = tk.Button(top_frame, text = "get", width = 5,command = self.btn_get_click)
        btn_get.grid(row = 0, column = 0, sticky=tk.W)

        btn_reverse = tk.Button(top_frame, text = "rev", width = 5,command=self.btn_reverse_click)
        btn_reverse.grid(row = 0, column = 1, sticky=tk.W)

        btn_output = tk.Button(top_frame, text = "out", width = 5,command=self.btn_output_click)
        btn_output.grid(row = 0, column = 2, sticky=tk.W)

        btn_set = tk.Button(top_frame, text = "set", width = 5,command=self.btn_set_click)
        btn_set.grid(row = 0, column = 3, sticky=tk.W)

        self.mode_label = tk.Label(top_frame, text = "mode :")
        self.mode_label.grid(row=0,column=4,sticky=tk.E)
        #----------------------------
        #right_frame_2
        #----------------------------

        #矩形描画ボタンをトップに持ってくる
        btn_rectangle = tk.Button(right_frame_2, text = "矩形を描画", width = 15, command = self.btn_rectangle_click)
        btn_rectangle.grid(row = 0, column = 0, columnspan = 4, sticky=tk.EW)

        #データ出力ボタンをボトムに持ってくる
        space = tk.Label(right_frame_2,text="")
        space.grid(row=24,column=0,columnspan=4,sticky=tk.W)
        btn_rectangle = tk.Button(right_frame_2, text = "データ出力", width = 15, command = self.btn_data_output_click)
        btn_rectangle.grid(row = 25, column = 0, columnspan = 4, sticky=tk.EW)

        #下辺の入力
        space = tk.Label(right_frame_2,text="")
        lbl_bottomLine = tk.Label(right_frame_2, text = "下辺の矩形を設定",relief=tk.GROOVE)

        lbl_bottomLine_LT = tk.Label(right_frame_2, text = "矩形の左上座標の入力")
        lbl_bottomLine_LTX = tk.Label(right_frame_2, text = "x:")
        lbl_bottomLine_LTY = tk.Label(right_frame_2, text = "y:")
        self.bottomLine_LTX = tk.StringVar() 
        self.bottomLine_LTX.set("2350")
        self.bottomLine_LTY = tk.StringVar() 
        self.bottomLine_LTY.set("3000")

        txt_bottomLine_LTX = tk.Entry(right_frame_2, justify = tk.RIGHT,  textvariable = self.bottomLine_LTX,width=10)
        txt_bottomLine_LTY = tk.Entry(right_frame_2, justify = tk.RIGHT,  textvariable = self.bottomLine_LTY,width=10)

        lbl_bottomLine_RB = tk.Label(right_frame_2, text = "矩形の右下座標の入力")
        lbl_bottomLine_RBX = tk.Label(right_frame_2, text = "x:")
        lbl_bottomLine_RBY = tk.Label(right_frame_2, text = "y:")
        self.bottomLine_RBX = tk.StringVar() 
        self.bottomLine_RBX.set("2700")
        self.bottomLine_RBY = tk.StringVar() 
        self.bottomLine_RBY.set("3250")

        txt_bottomLine_RBX = tk.Entry(right_frame_2, justify = tk.RIGHT,  textvariable = self.bottomLine_RBX,width=10)
        txt_bottomLine_RBY = tk.Entry(right_frame_2, justify = tk.RIGHT,  textvariable = self.bottomLine_RBY,width=10)
       
        space.grid(row=18,column=0,columnspan=4,sticky=tk.W)
        lbl_bottomLine.grid(row = 19, column = 0,columnspan=4,sticky=tk.W)
        lbl_bottomLine_LT.grid(row = 20, column = 0,columnspan=4,sticky=tk.W)
        lbl_bottomLine_LTX.grid(row = 21, column = 0, sticky=tk.E)
        lbl_bottomLine_LTY.grid(row = 21, column = 2, sticky=tk.E)
        txt_bottomLine_LTX.grid(row = 21, column = 1, sticky=tk.E) 
        txt_bottomLine_LTY.grid(row = 21, column = 3, sticky=tk.E) 
        lbl_bottomLine_RB.grid(row = 22, column = 0,columnspan=4,sticky=tk.W)
        lbl_bottomLine_RBX.grid(row = 23, column = 0, sticky=tk.E)
        lbl_bottomLine_RBY.grid(row = 23, column = 2, sticky=tk.E)
        txt_bottomLine_RBX.grid(row = 23, column = 1, sticky=tk.E) 
        txt_bottomLine_RBY.grid(row = 23, column = 3, sticky=tk.E)

        #右辺の入力
        space = tk.Label(right_frame_2,text="")
        lbl_rightLine = tk.Label(right_frame_2, text = "右辺の矩形を設定",relief=tk.GROOVE)

        lbl_rightLine_LT = tk.Label(right_frame_2, text = "矩形の左上座標の入力")
        lbl_rightLine_LTX = tk.Label(right_frame_2, text = "x:")
        lbl_rightLine_LTY = tk.Label(right_frame_2, text = "y:")
        self.rightLine_LTX = tk.StringVar() 
        self.rightLine_LTX.set("3300")
        self.rightLine_LTY = tk.StringVar() 
        self.rightLine_LTY.set("2250")

        txt_rightLine_LTX = tk.Entry(right_frame_2, justify = tk.RIGHT,  textvariable = self.rightLine_LTX,width=10)
        txt_rightLine_LTY = tk.Entry(right_frame_2, justify = tk.RIGHT,  textvariable = self.rightLine_LTY,width=10)

        lbl_rightLine_RB = tk.Label(right_frame_2, text = "矩形の右下座標の入力")
        lbl_rightLine_RBX = tk.Label(right_frame_2, text = "x:")
        lbl_rightLine_RBY = tk.Label(right_frame_2, text = "y:")
        self.rightLine_RBX = tk.StringVar() 
        self.rightLine_RBX.set("3500")
        self.rightLine_RBY = tk.StringVar() 
        self.rightLine_RBY.set("2900")

        txt_rightLine_RBX = tk.Entry(right_frame_2, justify = tk.RIGHT,  textvariable = self.rightLine_RBX,width=10)
        txt_rightLine_RBY = tk.Entry(right_frame_2, justify = tk.RIGHT,  textvariable = self.rightLine_RBY,width=10)
       
        space.grid(row=12,column=0,columnspan=4,sticky=tk.W)
        lbl_rightLine.grid(row = 13, column = 0,columnspan=4,sticky=tk.W)
        lbl_rightLine_LT.grid(row = 14, column = 0,columnspan=4,sticky=tk.W)
        lbl_rightLine_LTX.grid(row = 15, column = 0, sticky=tk.E)
        lbl_rightLine_LTY.grid(row = 15, column = 2, sticky=tk.E)
        txt_rightLine_LTX.grid(row = 15, column = 1, sticky=tk.E) 
        txt_rightLine_LTY.grid(row = 15, column = 3, sticky=tk.E) 
        lbl_rightLine_RB.grid(row = 16, column = 0,columnspan=4,sticky=tk.W)
        lbl_rightLine_RBX.grid(row = 17, column = 0, sticky=tk.E)
        lbl_rightLine_RBY.grid(row = 17, column = 2, sticky=tk.E)
        txt_rightLine_RBX.grid(row = 17, column = 1, sticky=tk.E) 
        txt_rightLine_RBY.grid(row = 17, column = 3, sticky=tk.E)


        #上辺の入力
        space = tk.Label(right_frame_2,text="")
        lbl_topLine = tk.Label(right_frame_2, text = "上辺の矩形を設定",relief=tk.GROOVE)

        lbl_topLine_LT = tk.Label(right_frame_2, text = "矩形の左上座標の入力")
        lbl_topLine_LTX = tk.Label(right_frame_2, text = "x:")
        lbl_topLine_LTY = tk.Label(right_frame_2, text = "y:")
        self.topLine_LTX = tk.StringVar() 
        self.topLine_LTX.set("2300")
        self.topLine_LTY = tk.StringVar() 
        self.topLine_LTY.set("1450")

        txt_topLine_LTX = tk.Entry(right_frame_2, justify = tk.RIGHT,  textvariable = self.topLine_LTX,width=10)
        txt_topLine_LTY = tk.Entry(right_frame_2, justify = tk.RIGHT,  textvariable = self.topLine_LTY,width=10)

        lbl_topLine_RB = tk.Label(right_frame_2, text = "矩形の右下座標の入力")
        lbl_topLine_RBX = tk.Label(right_frame_2, text = "x:")
        lbl_topLine_RBY = tk.Label(right_frame_2, text = "y:")
        self.topLine_RBX = tk.StringVar() 
        self.topLine_RBX.set("2800")
        self.topLine_RBY = tk.StringVar() 
        self.topLine_RBY.set("1750")

        txt_topLine_RBX = tk.Entry(right_frame_2, justify = tk.RIGHT,  textvariable = self.topLine_RBX,width=10)
        txt_topLine_RBY = tk.Entry(right_frame_2, justify = tk.RIGHT,  textvariable = self.topLine_RBY,width=10)
       
        space.grid(row=6,column=0,columnspan=4,sticky=tk.W)
        lbl_topLine.grid(row = 7, column = 0,columnspan=4,sticky=tk.W)
        lbl_topLine_LT.grid(row = 8, column = 0,columnspan=4,sticky=tk.W)
        lbl_topLine_LTX.grid(row = 9, column = 0, sticky=tk.E)
        lbl_topLine_LTY.grid(row = 9, column = 2, sticky=tk.E)
        txt_topLine_LTX.grid(row = 9, column = 1, sticky=tk.E) 
        txt_topLine_LTY.grid(row = 9, column = 3, sticky=tk.E) 
        lbl_topLine_RB.grid(row = 10, column = 0,columnspan=4,sticky=tk.W)
        lbl_topLine_RBX.grid(row = 11, column = 0, sticky=tk.E)
        lbl_topLine_RBY.grid(row = 11, column = 2, sticky=tk.E)
        txt_topLine_RBX.grid(row = 11, column = 1, sticky=tk.E) 
        txt_topLine_RBY.grid(row = 11, column = 3, sticky=tk.E)

        #左辺の入力
        lbl_leftLine = tk.Label(right_frame_2, text = "左辺の矩形を設定",relief=tk.GROOVE)

        lbl_leftLine_LT = tk.Label(right_frame_2, text = "矩形の左上座標の入力")
        lbl_leftLine_LTX = tk.Label(right_frame_2, text = "x:")
        lbl_leftLine_LTY = tk.Label(right_frame_2, text = "y:")
        self.leftLine_LTX = tk.StringVar() 
        self.leftLine_LTX.set("1750")
        self.leftLine_LTY = tk.StringVar() 
        self.leftLine_LTY.set("2000")

        txt_leftLine_LTX = tk.Entry(right_frame_2, justify = tk.RIGHT,  textvariable = self.leftLine_LTX,width=10)
        txt_leftLine_LTY = tk.Entry(right_frame_2, justify = tk.RIGHT,  textvariable = self.leftLine_LTY,width=10)

        lbl_leftLine_RB = tk.Label(right_frame_2, text = "矩形の右下座標の入力")
        lbl_leftLine_RBX = tk.Label(right_frame_2, text = "x:")
        lbl_leftLine_RBY = tk.Label(right_frame_2, text = "y:")
        self.leftLine_RBX = tk.StringVar() 
        self.leftLine_RBX.set("2000")
        self.leftLine_RBY = tk.StringVar() 
        self.leftLine_RBY.set("2300")

        txt_leftLine_RBX = tk.Entry(right_frame_2, justify = tk.RIGHT,  textvariable = self.leftLine_RBX,width=10)
        txt_leftLine_RBY = tk.Entry(right_frame_2, justify = tk.RIGHT,  textvariable = self.leftLine_RBY,width=10)
        
        lbl_leftLine.grid(row = 1, column = 0,columnspan=4,sticky=tk.W)
        lbl_leftLine_LT.grid(row = 2, column = 0,columnspan=4,sticky=tk.W)
        lbl_leftLine_LTX.grid(row = 3, column = 0, sticky=tk.E)
        lbl_leftLine_LTY.grid(row = 3, column = 2, sticky=tk.E)
        txt_leftLine_LTX.grid(row = 3, column = 1, sticky=tk.E) 
        txt_leftLine_LTY.grid(row = 3, column = 3, sticky=tk.E) 
        lbl_leftLine_RB.grid(row = 4, column = 0,columnspan=4,sticky=tk.W)
        lbl_leftLine_RBX.grid(row = 5, column = 0, sticky=tk.E)
        lbl_leftLine_RBY.grid(row = 5, column = 2, sticky=tk.E)
        txt_leftLine_RBX.grid(row = 5, column = 1, sticky=tk.E) 
        txt_leftLine_RBY.grid(row = 5, column = 3, sticky=tk.E)


        #----------------------------
        #right_frame
        #----------------------------
        # Threshold
        btn_threshold = tk.Button(right_frame, text = "Threshold", width = 15, command = self.btn_threshold_click)
        lbl_threshold_low = tk.Label(right_frame, text = "Low")
        lbl_threshold_high = tk.Label(right_frame, text = "High")
        self.threshold_low = tk.StringVar() 
        self.threshold_low.set("50")
        self.threshold_high = tk.StringVar() 
        self.threshold_high.set("200")
        txt_threshold_low = tk.Entry(right_frame, justify = tk.RIGHT,  textvariable = self.threshold_low)
        txt_threshold_high = tk.Entry(right_frame, justify = tk.RIGHT,  textvariable = self.threshold_high)
        # 配置
        btn_threshold.grid(row = 0, column = 0, columnspan = 2, sticky=tk.EW)
        lbl_threshold_low.grid(row = 1, column = 0, sticky=tk.W) 
        txt_threshold_low.grid(row = 1, column = 1, sticky=tk.EW) 
        lbl_threshold_high.grid(row = 2, column = 0, sticky=tk.W) 
        txt_threshold_high.grid(row = 2, column = 1, sticky=tk.EW) 

        # Gaussian
        btn_gaussian = tk.Button(right_frame, text = "Gaussian", width = 15, command = self.btn_gaussian_click)
        lbl_gaussian = tk.Label(right_frame, text = "ksize")
        self.gaussian_ksize = tk.StringVar() 
        self.gaussian_ksize.set("3")
        txt_gaussian = tk.Entry(right_frame, justify = tk.RIGHT,  textvariable = self.gaussian_ksize)
        # 配置
        btn_gaussian.grid(row = 3, column = 0, columnspan = 2, sticky=tk.EW)
        lbl_gaussian.grid(row = 4, column = 0, sticky=tk.W) 
        txt_gaussian.grid(row = 4, column = 1, sticky=tk.EW) 

        #鮮鋭化フィルタ
        btn_unsharp = tk.Button(right_frame, text = "Unsharp masking", width = 15, command = self.btn_unsharp_click)
        lbl_unsharp = tk.Label(right_frame, text = "kvalue")
        self.unsharp_kvalue = tk.StringVar() 
        self.unsharp_kvalue.set("1")
        txt_unsharp = tk.Entry(right_frame, justify = tk.RIGHT,  textvariable = self.unsharp_kvalue)
        # 配置
        btn_unsharp.grid(row = 5, column = 0, columnspan = 2, sticky=tk.EW)
        lbl_unsharp.grid(row = 6, column = 0, sticky=tk.W) 
        txt_unsharp.grid(row = 6, column = 1, sticky=tk.EW) 

        #adjustフィルタ
        btn_adjust = tk.Button(right_frame, text = "Adjust", width = 15, command = self.btn_adjust_click)
        lbl_adjust = tk.Label(right_frame, text = "ksize")
        self.adjust_alpha = tk.StringVar() 
        self.adjust_alpha.set("2.5")
        txt_adjust = tk.Entry(right_frame, justify = tk.RIGHT,  textvariable = self.adjust_alpha)
        # 配置
        btn_adjust.grid(row = 7, column = 0, columnspan = 2, sticky=tk.EW)
        lbl_adjust.grid(row = 8, column = 0, sticky=tk.W) 
        txt_adjust.grid(row = 8, column = 1, sticky=tk.EW) 

        #ソーベルフィルタ
        btn_sobel = tk.Button(right_frame, text = "Sobel masking", width = 15, command = self.btn_sobel_click)
        lbl_sobel = tk.Label(right_frame, text = "ksize")
        self.sobel_ksize = tk.StringVar() 
        self.sobel_ksize.set("3")
        txt_sobel = tk.Entry(right_frame, justify = tk.RIGHT,  textvariable = self.sobel_ksize)
        # 配置
        btn_sobel.grid(row = 9, column = 0, columnspan = 2, sticky=tk.EW)
        lbl_sobel.grid(row = 10, column = 0, sticky=tk.W) 
        txt_sobel.grid(row = 10, column = 1, sticky=tk.EW) 

        #膨張処理(dilate)
        btn_dilate = tk.Button(right_frame, text = "Dilate", width = 15, command = self.btn_dilate_click)
        lbl_dilate = tk.Label(right_frame, text = "iteration")
        self.dilate_iter = tk.StringVar() 
        self.dilate_iter.set("1")
        txt_dilate = tk.Entry(right_frame, justify = tk.RIGHT,  textvariable = self.dilate_iter)
        # 配置
        btn_dilate.grid(row = 11, column = 0, columnspan = 2, sticky=tk.EW)
        lbl_dilate.grid(row = 12, column = 0, sticky=tk.W) 
        txt_dilate.grid(row = 12, column = 1, sticky=tk.EW) 

        #縮小処理(erode)
        btn_erode = tk.Button(right_frame, text = "Erode", width = 15, command = self.btn_erode_click)
        lbl_erode = tk.Label(right_frame, text = "iteration")
        self.erode_iter = tk.StringVar() 
        self.erode_iter.set("1")
        txt_erode = tk.Entry(right_frame, justify = tk.RIGHT,  textvariable = self.erode_iter)
        # 配置
        btn_erode.grid(row = 13, column = 0, columnspan = 2, sticky=tk.EW)
        lbl_erode.grid(row = 14, column = 0, sticky=tk.W) 
        txt_erode.grid(row = 14, column = 1, sticky=tk.EW) 

        #差分処理(differ)
        btn_differ = tk.Button(right_frame, text = "Difference", width = 15, command = self.btn_differ_click)
         # 配置
        btn_differ.grid(row = 15, column = 0, columnspan = 2, sticky=tk.EW)
       
        #バイラテラルフィルタ
        btn_bilateral = tk.Button(right_frame, text = "Bilateral masking", width = 15, command = self.btn_bilateral_click)
        lbl_bilateral = tk.Label(right_frame, text = "ksize")
        self.bilateral_ksize = tk.StringVar() 
        self.bilateral_ksize.set("3")
        txt_bilateral = tk.Entry(right_frame, justify = tk.RIGHT,  textvariable = self.bilateral_ksize)
        # 配置
        btn_bilateral.grid(row = 16, column = 0, columnspan = 2, sticky=tk.EW)
        lbl_bilateral.grid(row = 17, column = 0, sticky=tk.W) 
        txt_bilateral.grid(row = 17, column = 1, sticky=tk.EW) 

        #バイラテラルフィルタ
        btn_sigmoid = tk.Button(right_frame, text = "Sigmoidフィルタ", width = 15, command = self.btn_sigmoid_click)
        lbl_sigmoid_coeff = tk.Label(right_frame, text = "係数")
        self.sigmoid_coeff = tk.StringVar() 
        self.sigmoid_coeff.set("1")
        txt_sigmoid_coeff = tk.Entry(right_frame, justify = tk.RIGHT,  textvariable = self.sigmoid_coeff)

        lbl_sigmoid_standard = tk.Label(right_frame, text = "基準")
        self.sigmoid_standard = tk.StringVar() 
        self.sigmoid_standard.set("128")
        txt_sigmoid_standard = tk.Entry(right_frame, justify = tk.RIGHT,  textvariable = self.sigmoid_standard)

        # 配置
        btn_sigmoid.grid(row = 18, column = 0, columnspan = 2, sticky=tk.EW)
        lbl_sigmoid_coeff.grid(row = 19, column = 0, sticky=tk.W) 
        txt_sigmoid_coeff.grid(row = 19, column = 1, sticky=tk.EW) 
        lbl_sigmoid_standard.grid(row = 20, column = 0, sticky=tk.W) 
        txt_sigmoid_standard.grid(row = 20, column = 1, sticky=tk.EW) 

        # フレームを配置
        right_frame.pack(side = tk.RIGHT, fill = tk.Y)
        right_frame_2.pack(side = tk.RIGHT, fill = tk.Y)
        top_frame.pack(side = tk.TOP, fill = tk.X)
        #####################################################
        # Canvas(画像の表示用)
        self.canvas = tk.Canvas(self.master, background= self.back_color)
        self.canvas.pack(expand=True,  fill=tk.BOTH)  # この両方でDock.Fillと同じ

        #####################################################
        # マウスイベント
        self.canvas.bind("<Motion>", self.mouse_move)                       # MouseMove
        self.canvas.bind("<B1-Motion>", self.mouse_move_left)               # MouseMove（左ボタンを押しながら移動）
        self.canvas.bind("<Button-1>", self.mouse_down_left)                # MouseDown（左ボタン）
        self.canvas.bind("<Double-Button-1>", self.mouse_double_click_left) # MouseDoubleClick（左ボタン）
        self.canvas.bind("<MouseWheel>", self.mouse_wheel)                  # MouseWheel
        self.canvas.bind("<Button-3>", self.mouse_down_right)               # MouseDown (右ボタン)

    def set_image(self, filename):
        ''' 画像ファイルを開く '''
        if not filename or filename is None:
            return

        # 画像ファイルの再読込用に保持
        self.filename = filename

        # PIL.Imageで開く
        self.pil_image = Image.open(filename)

        # PillowからNumPy(OpenCVの画像)へ変換
        self.cv_image = np.array(self.pil_image)
        
        # 差分処理用のオリジナルイメージ
        self.cv_image_original = np.array(self.pil_image)
        #
        # カラー画像のときは、RGBからBGRへ変換する
        if self.cv_image.ndim == 3:
            self.cv_image = cv2.cvtColor(self.cv_image, cv2.COLOR_RGB2BGR)

        # 画像全体に表示するようにアフィン変換行列を設定
        self.zoom_fit(self.pil_image.width, self.pil_image.height)
        # 画像の表示
        self.draw_image(self.cv_image)

        # ウィンドウタイトルのファイル名を設定
        self.master.title(self.my_title + " - " + os.path.basename(filename))
        # ステータスバーに画像情報を表示する
        self.image_info["text"] = f"{self.pil_image.width} x {self.pil_image.height} {self.pil_image.mode}"
        # カレントディレクトリの設定
        os.chdir(os.path.dirname(filename))

        #undo用
        self.image_list.append(self.cv_image)

    #矩形描画用の座標テキストファイルをオープン
    def open_rectfile(self):

        filename = filedialog.askopenfilename(title="テキストファイルオープン",\
                filetypes=[("text file",".txt .csv"),("TEXT",".txt"),("CSV",".csv")],\
                initialdir="./")

        rectFile = open(filename,"r")

        rectLine = rectFile.readline()

        line_num = 1

        while rectLine:
            
            if not(line_num == 1 and "left" in rectLine):
                print("ファイルが正しくありません")
            elif line_num == 1 and "left" in rectLine:
                rectLine = rectFile.readline()
                line_num += 1
                x = rectLine.split(",")[0]
                y = rectLine.split(",")[1]
                self.leftLine_LTX.set(x)
                self.leftLine_LTY.set(y)

                rectLine = rectFile.readline()
                line_num += 1
                x = rectLine.split(",")[0]
                y = rectLine.split(",")[1]
                self.leftLine_RBX.set(x)
                self.leftLine_RBY.set(y)

            if not(line_num == 4 and "top" in rectLine):
                print("ファイルが正しくありません")
            elif line_num == 4 and "top" in rectLine:
                rectLine = rectFile.readline()
                line_num += 1
                x = rectLine.split(",")[0]
                y = rectLine.split(",")[1]
                self.topLine_LTX.set(x)
                self.topLine_LTY.set(y)

                rectLine = rectFile.readline()
                line_num += 1
                x = rectLine.split(",")[0]
                y = rectLine.split(",")[1]
                self.topLine_RBX.set(x)
                self.topLine_RBY.set(y)

            if not(line_num == 7 and "right" in rectLine):
                print("ファイルが正しくありません")
            elif line_num == 7 and "right" in rectLine:
                rectLine = rectFile.readline()
                line_num += 1
                x = rectLine.split(",")[0]
                y = rectLine.split(",")[1]
                self.rightLine_LTX.set(x)
                self.rightLine_LTY.set(y)

                rectLine = rectFile.readline()
                line_num += 1
                x = rectLine.split(",")[0]
                y = rectLine.split(",")[1]
                self.rightLine_RBX.set(x)
                self.rightLine_RBY.set(y)

            if not(line_num == 10 and "bottom" in rectLine):
                print("ファイルが正しくありません")
            elif line_num == 10 and "bottom" in rectLine:
                rectLine = rectFile.readline()
                line_num += 1
                x = rectLine.split(",")[0]
                y = rectLine.split(",")[1]
                self.bottomLine_LTX.set(x)
                self.bottomLine_LTY.set(y)

                rectLine = rectFile.readline()
                line_num += 1
                x = rectLine.split(",")[0]
                y = rectLine.split(",")[1]
                self.bottomLine_RBX.set(x)
                self.bottomLine_RBY.set(y)

            rectLine = rectFile.readline()
            line_num += 1

        rectFile.close()

    #画像保存
    def save(self):

        if self.cv_image is None:
            return

        filename = filedialog.asksaveasfilename(title="名前を付けて保存",\
                filetypes=[("JPEG",".jpg"),("PNG",".png")],\
                initialdir="./",\
                defaultextension = "jpg")

        cv2.imwrite(filename,self.cv_image)

    #戻り処理
    def undo(self):
        if (self.cv_image is None) or (len(self.image_list)<=1):
            return

        #画像を戻す
        self.image_list.pop()
        self.cv_image = self.image_list[len(self.image_list)-1]

        #self.image_list.pop()


        #変換履歴を戻す
        text = self.history["text"]
        text_item = text.split(",")
       
        new_text=""
        for s in range(len(text_item)-1):

            if s != len(text_item)-2:
                new_text += text_item[s]+","
            elif s == len(text_item)-2: 
                new_text += text_item[s]

        self.history["text"] = new_text
        
        self.redraw_image()


    # -------------------------------------------------------------------------------
    # マウスイベント
    # -------------------------------------------------------------------------------

    def mouse_move(self, event):
        ''' マウスの移動時 '''
        # マウス座標
        self.mouse_position["text"] = f"mouse(x, y) = ({event.x: 4d}, {event.y: 4d})"
        
        if self.pil_image is None:
            return

        # 画像座標
        mouse_posi = np.array([event.x, event.y, 1]) # マウス座標(numpyのベクトル)
        mat_inv = np.linalg.inv(self.mat_affine)     # 逆行列（画像→Cancasの変換からCanvas→画像の変換へ）
        self.image_posi = np.dot(mat_inv, mouse_posi)     # 座標のアフィン変換
        x = int(np.floor(self.image_posi[0]))
        y = int(np.floor(self.image_posi[1]))
        if x >= 0 and x < self.pil_image.width and y >= 0 and y < self.pil_image.height:
            # 輝度値の取得
            value = self.pil_image.getpixel((x, y))
            self.image_position["text"] = f"image({x: 4d}, {y: 4d}) = {value}"
        else:
            self.image_position["text"] = "-------------------------"

    def mouse_move_left(self, event):
        ''' マウスの左ボタンをドラッグ '''
        if self.pil_image is None:
            return
        self.translate(event.x - self.__old_event.x, event.y - self.__old_event.y)
        self.redraw_image() # 再描画
        self.__old_event = event

    def mouse_down_left(self, event):
        ''' マウスの左ボタンを押した '''
        self.__old_event = event

    def mouse_double_click_left(self, event):
        ''' マウスの左ボタンをダブルクリック '''
        if self.pil_image is None:
            return
        self.zoom_fit(self.pil_image.width, self.pil_image.height)
        self.redraw_image() # 再描画

    def mouse_wheel(self, event):
        ''' マウスホイールを回した '''
        if self.pil_image is None:
            return

        if (event.delta < 0):
            # 上に回転の場合、縮小
            self.scale_at(0.8, event.x, event.y)
        else:
            # 下に回転の場合、拡大
            self.scale_at(1.25, event.x, event.y)
        
        self.redraw_image() # 再描画
    
    def mouse_down_right(self,event):
        ''' マウスの右ボタンをクリック '''
        if self.pil_image is None:
            return
        flag = 0 
        x = int(np.floor(self.image_posi[0]))
        y = int(np.floor(self.image_posi[1]))

        if self.right_click_mode == "A":
            '''fail座標をgetするモードの場合'''
            for p in self.fail_pixel:
                if x==p[0] and y==p[1]:
                    return 
            self.original_pixel.append([x,y,self.cv_image[y][x]])
            self.fail_pixel.append([x,y,self.cv_image[y][x]])
            self.cv_image[y][x] = 255
        elif self.right_click_mode == "B":
            '''fail座標を元に戻すモードの場合'''
            fp = self.fail_pixel.copy()
            for i,p in enumerate(fp):
                if x==p[0] and y==p[1]:
                    self.cv_image[y][x] = p[2]
                    self.original_pixel.pop(i)
                    self.fail_pixel.pop(i)
        elif self.right_click_mode == "C":
            '''failパターンを書き込むモードの場合'''
            for data in self.fail_pattern:
                self.cv_image[y+data[1]][x+data[0]] = data[2]

        self.redraw_image() # 再描画

    # -------------------------------------------------------------------------------
    # 画像表示用アフィン変換
    # -------------------------------------------------------------------------------

    def reset_transform(self):
        '''アフィン変換を初期化（スケール１、移動なし）に戻す'''
        self.mat_affine = np.eye(3) # 3x3の単位行列

    def translate(self, offset_x, offset_y):
        ''' 平行移動 '''
        mat = np.eye(3) # 3x3の単位行列
        mat[0, 2] = float(offset_x)
        mat[1, 2] = float(offset_y)

        self.mat_affine = np.dot(mat, self.mat_affine)

    def scale(self, scale:float):
        ''' 拡大縮小 '''
        mat = np.eye(3) # 単位行列
        mat[0, 0] = scale
        mat[1, 1] = scale

        self.mat_affine = np.dot(mat, self.mat_affine)

    def scale_at(self, scale:float, cx:float, cy:float):
        ''' 座標(cx, cy)を中心に拡大縮小 '''

        # 原点へ移動
        self.translate(-cx, -cy)
        # 拡大縮小
        self.scale(scale)
        # 元に戻す
        self.translate(cx, cy)

    def zoom_fit(self, image_width, image_height):
        '''画像をウィジェット全体に表示させる'''

        # キャンバスのサイズ
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if (image_width * image_height <= 0) or (canvas_width * canvas_height <= 0):
            return

        # アフィン変換の初期化
        self.reset_transform()

        scale = 1.0
        offsetx = 0.0
        offsety = 0.0

        if (canvas_width * image_height) > (image_width * canvas_height):
            # ウィジェットが横長（画像を縦に合わせる）
            scale = canvas_height / image_height
            # あまり部分の半分を中央に寄せる
            offsetx = (canvas_width - image_width * scale) / 2
        else:
            # ウィジェットが縦長（画像を横に合わせる）
            scale = canvas_width / image_width
            # あまり部分の半分を中央に寄せる
            offsety = (canvas_height - image_height * scale) / 2

        # 拡大縮小
        self.scale(scale)
        # あまり部分を中央に寄せる
        self.translate(offsetx, offsety)

    # -------------------------------------------------------------------------------
    # 描画
    # -------------------------------------------------------------------------------

    def draw_image(self, cv_image):
        
        if cv_image is None:
            return

        self.cv_image = cv_image

        self.canvas.delete("all")

        # キャンバスのサイズ
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # キャンバスから画像データへのアフィン変換行列を求める
        #（表示用アフィン変換行列の逆行列を求める）
        mat_inv = np.linalg.inv(self.mat_affine)

        # ndarray(OpenCV)からPillowへ変換
        # カラー画像のときは、BGRからRGBへ変換する
        if cv_image.ndim == 3:
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        # NumPyからPillowへ変換
        self.pil_image = Image.fromarray(cv_image)

        # PILの画像データをアフィン変換する
        dst = self.pil_image.transform(
                    (canvas_width, canvas_height),  # 出力サイズ
                    Image.AFFINE,         # アフィン変換
                    tuple(mat_inv.flatten()),       # アフィン変換行列（出力→入力への変換行列）を一次元のタプルへ変換
                    Image.NEAREST,       # 補間方法、ニアレストネイバー 
                    fillcolor= self.back_color
                    )

        # 表示用画像を保持
        self.image = ImageTk.PhotoImage(image=dst)

        # 画像の描画
        self.canvas.create_image(
                0, 0,               # 画像表示位置(左上の座標)
                anchor='nw',        # アンカー、左上が原点
                image=self.image    # 表示画像データ
                )
        

    def redraw_image(self):
        ''' 画像の再描画 '''
        if self.cv_image is None:
            return
        self.draw_image(self.cv_image)

    # -------------------------------------------------------------------------------
    # ボタンイベント（top_frame）
    # -------------------------------------------------------------------------------

    def btn_get_click(self):
   
        '''top_frameのgetボタンを押したとき'''

        self.right_click_mode = "A"
        self.mode_label["text"] = "mode : select pixel"

        if self.pil_image is None:
            return
        
    def btn_reverse_click(self):
   
        '''top_frameのrevボタンを押したとき'''

        self.right_click_mode = "B"
        self.mode_label["text"] = "mode : remove selecting pixel"

        if self.pil_image is None:
            return

    def btn_output_click(self):
   
        '''top_frameのoutボタンを押したとき'''

        if self.pil_image is None:
            return

        filename = filedialog.asksaveasfilename(title="名前を付けて保存",\
                filetypes=[("TEXT",".txt")],\
                initialdir="./",\
                defaultextension = "txt")

        output_file = open(filename,"w")

        for lis in self.fail_pixel:
            str_lis = [str(l) for l in lis]
            output_file.write(",".join(str_lis)+"\n")

        output_file.close()

    def btn_set_click(self):
   
        '''top_frameのsetボタンを押したとき'''

        if self.pil_image is None:
            return

        filename = filedialog.askopenfilename(title="ファイルを読み込み",\
                filetypes=[("TEXT",".txt")],\
                initialdir="./",\
                defaultextension = "txt")

        input_data = np.loadtxt(filename,delimiter=",")
        pixel_data = input_data[:,2:3]

        self.right_click_mode = "C"
        self.mode_label["text"] = "mode : set fail pattern"

        average_coord = np.array(np.mean(input_data,axis=0),dtype="int") #X座標、Y座標、輝度の平均
        tmp = (input_data - average_coord)
        tmp[:,2:3] = pixel_data

        self.fail_pattern = np.array(tmp,dtype="int")


    # -------------------------------------------------------------------------------
    # ボタンイベント（right_frame_2）
    # -------------------------------------------------------------------------------

    def btn_data_output_click(self):

        '''データ出力ボタンがクリックされたとき'''
        if self.cv_image is None:
            return
        
        outputFileName = filedialog.asksaveasfilename(title="名前を付けて保存",\
                filetypes=[("TEXT",".txt")],\
                initialdir="./",\
                defaultextension = "txt")

        outputFile = open(outputFileName,"w")
        
        outputFile.write("left\n")
        outputFile.write(self.leftLine_LTX.get()+","+self.leftLine_LTY.get()+"\n")
        outputFile.write(self.leftLine_RBX.get()+","+self.leftLine_RBY.get()+"\n")

        outputFile.write("top\n")
        outputFile.write(self.topLine_LTX.get()+","+self.topLine_LTY.get()+"\n")
        outputFile.write(self.topLine_RBX.get()+","+self.topLine_RBY.get()+"\n")

        outputFile.write("right\n")
        outputFile.write(self.rightLine_LTX.get()+","+self.rightLine_LTY.get()+"\n")
        outputFile.write(self.rightLine_RBX.get()+","+self.rightLine_RBY.get()+"\n")

        outputFile.write("bottom\n")
        outputFile.write(self.bottomLine_LTX.get()+","+self.bottomLine_LTY.get()+"\n")
        outputFile.write(self.bottomLine_RBX.get()+","+self.bottomLine_RBY.get()+"\n")

        outputFile.close()

    def btn_rectangle_click(self):
        '''矩形描画ボタンがクリックされたとき'''

        if self.pil_image is None:
            return

        #左辺の矩形
        leftline_ltx = int(self.leftLine_LTX.get())
        leftline_lty = int(self.leftLine_LTY.get())
        leftline_rbx = int(self.leftLine_RBX.get())
        leftline_rby = int(self.leftLine_RBY.get())

        #上辺の矩形
        topline_ltx = int(self.topLine_LTX.get())
        topline_lty = int(self.topLine_LTY.get())
        topline_rbx = int(self.topLine_RBX.get())
        topline_rby = int(self.topLine_RBY.get())

        #右辺の矩形
        rightline_ltx = int(self.rightLine_LTX.get())
        rightline_lty = int(self.rightLine_LTY.get())
        rightline_rbx = int(self.rightLine_RBX.get())
        rightline_rby = int(self.rightLine_RBY.get())

        #下辺の矩形
        bottomline_ltx = int(self.bottomLine_LTX.get())
        bottomline_lty = int(self.bottomLine_LTY.get())
        bottomline_rbx = int(self.bottomLine_RBX.get())
        bottomline_rby = int(self.bottomLine_RBY.get())


        self.cv_image = cv2.cvtColor(self.cv_image,cv2.COLOR_GRAY2RGB)

        cv2.rectangle(self.cv_image,(leftline_ltx,leftline_lty),(leftline_rbx,leftline_rby),(255,255,255),3)
        cv2.rectangle(self.cv_image,(topline_ltx,topline_lty),(topline_rbx,topline_rby),(255,255,255),3)
        cv2.rectangle(self.cv_image,(rightline_ltx,rightline_lty),(rightline_rbx,rightline_rby),(255,255,255),3)
        cv2.rectangle(self.cv_image,(bottomline_ltx,bottomline_lty),(bottomline_rbx,bottomline_rby),(255,255,255),3)

        self.cv_image = cv2.cvtColor(self.cv_image,cv2.COLOR_BGR2GRAY)
        self.redraw_image()

    def btn_threshold_click(self):
        '''Thresholdボタンがクリックされたとき'''
        if self.pil_image is None:
            return

        # 二値化
        high = int(self.threshold_high.get())
        low = int(self.threshold_low.get())

        self.cv_image = ((self.cv_image>low) & (self.cv_image<high))*255
        self.cv_image = self.cv_image.astype("uint8")
        
        # 大津の方法
        #_, self.cv_image = cv2.threshold(self.cv_image, 0, 255, cv2.THRESH_OTSU)

        #変換履歴を残す
        text = self.history["text"] + ",threshold "
        self.history["text"] = text

        #undo用
        self.image_list.append(self.cv_image)

        # 処理後画像の表示
        self.draw_image(self.cv_image)

    def btn_bilateral_click(self):
        '''Bilateralボタンがクリックされたとき'''
        if self.pil_image is None:
            return

        d = int(self.bilateral_ksize.get())

        self.cv_image = cv2.bilateralFilter(self.cv_image,d=d,sigmaColor=100,sigmaSpace=10)

        #変換履歴を残す
        text = self.history["text"] + ",bilateral "
        self.history["text"] = text

        #undo用
        self.image_list.append(self.cv_image)

        self.draw_image(self.cv_image)

    def btn_sigmoid_click(self):
        '''Sigmoidボタンがクリックされたとき'''
        if self.pil_image is None:
            return
        
        a = float(self.sigmoid_coeff.get())
        b = float(self.sigmoid_standard.get())

        print(a,b)

        self.cv_image = 255/(1+np.exp(-a*(self.cv_image-b)/255))

        self.cv_image = self.cv_image.astype("uint8")
        #変換履歴を残す
        text = self.history["text"] + ",sigmoid "
        self.history["text"] = text

        #undo用
        self.image_list.append(self.cv_image)

        self.draw_image(self.cv_image)

    def btn_differ_click(self):
        '''Differボタンがクリックされたとき'''
        if self.pil_image is None:
            return

        #self.cv_image = cv2.absdiff(self.cv_image_original,self.cv_image)
        self.cv_image = np.where(self.cv_image >= self.cv_image_original,255,self.cv_image_original)

        #変換履歴を残す
        text = self.history["text"] + ",differ "
        self.history["text"] = text

        #undo用
        self.image_list.append(self.cv_image)

        self.draw_image(self.cv_image)

    def btn_dilate_click(self):
        if self.pil_image is None:
            return

        iteration = int(self.dilate_iter.get())
        
        kernel = np.ones((5,5),np.uint8)

       # _, self.cv_image = cv2.threshold(self.cv_image, int(self.threshold.get()), 255, cv2.THRESH_BINARY)

        self.cv_image = cv2.dilate(self.cv_image,kernel,iterations=iteration)

        #変換履歴を残す
        text = self.history["text"] + ",dilate "
        self.history["text"] = text

        #undo用
        self.image_list.append(self.cv_image)

        self.draw_image(self.cv_image)

    def btn_erode_click(self):
        if self.pil_image is None:
            return

        iteration = int(self.erode_iter.get())
        print(iteration)
        
        kernel = np.ones((5,5),np.uint8)

       # _, self.cv_image = cv2.threshold(self.cv_image, int(self.threshold.get()), 255, cv2.THRESH_BINARY)

        self.cv_image = cv2.erode(self.cv_image,kernel,iterations=iteration)

        #変換履歴を残す
        text = self.history["text"] + ",erode "
        self.history["text"] = text

        #undo用
        self.image_list.append(self.cv_image)

        self.draw_image(self.cv_image)

    def btn_sobel_click(self):
        if self.pil_image is None:
            return

        k = int(self.sobel_ksize.get())

        grid_x = cv2.Sobel(self.cv_image,cv2.CV_32F,1,0,k)
        grid_y = cv2.Sobel(self.cv_image,cv2.CV_32F,0,1,k)

        #self.cv_image=np.sqrt(grid_x**2 + grid_y**2)
        self.cv_image=np.sqrt(grid_x**2 + grid_y**2).astype("uint8")

        print(np.max(self.cv_image))

        #変換履歴を残す
        text = self.history["text"] + ",sobel "
        self.history["text"] = text

        #undo用
        self.image_list.append(self.cv_image)

        self.draw_image(self.cv_image)

    def btn_adjust_click(self):
        if self.pil_image is None:
            return

        alpha = float(self.adjust_alpha.get())

        self.cv_image = alpha*self.cv_image
        self.cv_image = np.clip(self.cv_image,0,255).astype(np.uint8)

        #undo用
        self.image_list.append(self.cv_image)

        self.draw_image(self.cv_image)


    def btn_unsharp_click(self):
        '''Unsharpボタンがクリックされたとき'''
        if self.pil_image is None:
            return

        # kの値を取得 鮮鋭化処理
        k = int(self.unsharp_kvalue.get())
        
        #カーネル作成
        self.unsharp_kernel = np.array([[-k/9,-k/9,-k/9],
                          [-k/9,1+8*k/9,k/9],
                          [-k/9,-k/9,-k/9]],np.float32)

        #フィルタ処理 
        self.cv_image = cv2.filter2D(self.cv_image,-1,self.unsharp_kernel).astype("uint8")

        #undo用
        self.image_list.append(self.cv_image)

        # 処理後画像の表示
        self.draw_image(self.cv_image)


    def btn_gaussian_click(self):
        '''Gaussianボタンがクリックされたとき'''
        if self.pil_image is None:
            return

        # ガウシアンフィルタ処理
        ksize = int(self.gaussian_ksize.get())
        # カーネルサイズを奇数に調整
        ksize = int(ksize / 2) * 2 + 1
        self.cv_image = cv2.GaussianBlur(self.cv_image, (ksize, ksize), 0)

        #undo用
        self.image_list.append(self.cv_image)

        # 処理後画像の表示
        self.draw_image(self.cv_image)

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
