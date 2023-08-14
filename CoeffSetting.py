import tkinter as tk            # ウィンドウ作成用
from tkinter import ttk
from tkinter import filedialog  # ファイルを開くダイアログ用
from tkinter import messagebox
from PIL import Image, ImageTk  # 画像データ用
import numpy as np              # アフィン変換行列演算用
import os                       # ディレクトリ操作用
import cv2
import pandas as pd
from tksheet import Sheet

VERSION_INFO = "1.1"
DATE_INFO = "2023/8/13"

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack() 
 
        self.my_title = "規格設定"  # タイトル
        self.back_color = "#FFFFFF"     # 背景色

        # ウィンドウの設定
        self.master.title(self.my_title)    # タイトル
        self.master.geometry("600x400")     # サイズ

        self.pil_image = None           # 表示する画像データ
        self.filename = None            # 最後に開いた画像ファイル名
 
        self.create_menu()   # メニューの作成
        self.create_widget() # ウィジェットの作成

        self.image_posi=[] 
        self.split_data_list=[]
        self.fail_sheet_data=[["" for i in range(10)] for j in range(100)] #Failウインドウのシートに表示するデータ

    # -------------------------------------------------------------------------------
    # メニューイベント
    # -------------------------------------------------------------------------------

    def menu_quit_clicked(self):
        # ウィンドウを閉じる
        self.master.destroy() 

    def menu_version_clicked(self, event=None):
        #バージョン情報確認
        self.open_version()

    # -------------------------------------------------------------------------------
    # menuバーのUI設定
    # -------------------------------------------------------------------------------

    # create_menuメソッドを定義
    def create_menu(self):
        self.menu_bar = tk.Menu(self) # Menuクラスからmenu_barインスタンスを生成
 
        self.file_menu = tk.Menu(self.menu_bar, tearoff = tk.OFF)
        self.menu_bar.add_cascade(label="ファイル", menu=self.file_menu)

        self.file_menu.add_command(label="終了", command = self.menu_quit_clicked)

        #バージョン情報
        self.version_menu = tk.Menu(self.menu_bar,tearoff = tk.OFF)
        self.menu_bar.add_cascade(label="バージョン", menu=self.version_menu)
        self.version_menu.add_command(label="バージョン情報",command=self.menu_version_clicked)

        self.master.config(menu=self.menu_bar) # メニューバーの配置

    def create_widget(self):
        '''ウィジェットの作成'''
        #####################################################
        # ステータスバー(下辺)のUI設定
        #####################################################
        self.statusbar = tk.Frame(self.master)
        self.mouse_position = tk.Label(self.statusbar, relief = tk.SUNKEN, text="mouse position") # マウスの座標
        self.image_position = tk.Label(self.statusbar, relief = tk.SUNKEN, text="image position") # 画像の座標
        self.split_data = tk.Label(self.statusbar,relief=tk.SUNKEN, text="split data position") #split dataの番号
        self.label_space = tk.Label(self.statusbar, relief = tk.SUNKEN)                           # 隙間を埋めるだけ
        self.image_info = tk.Label(self.statusbar, relief = tk.SUNKEN, text="image info")         # 画像情報
        self.mouse_position.pack(side=tk.LEFT)
        self.image_position.pack(side=tk.LEFT)
        self.split_data.pack(side=tk.LEFT)
        self.label_space.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.image_info.pack(side=tk.RIGHT)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        #####################################################
        # メイン画面のUI設定
        #####################################################
        """panedWindowを作成"""
        paned_window = tk.PanedWindow(self.master)
        #------------------------------------------------------------------
        #左側フレームのUI設定 (上から設置する順に記述)
        #------------------------------------------------------------------

        self.left_frame = tk.Frame(paned_window, relief = tk.SUNKEN, bd = 2, width = 500)

        """良品データ関係"""
        self.good_result_data_lbl = tk.Label(self.left_frame, font=("MSゴシック","14"), text="良品データフォルダ") # 良品結果ファイル参照ラベル
        self.good_result_btn = tk.Button(self.left_frame,text="参照",font=("MSゴシック","12"),command=self.open_good_result_data)
        self.good_data_address = tk.StringVar()
        self.good_data_address_entry = tk.Entry(self.left_frame,textvariable=self.good_data_address)
        self.good_data_address.set("c:\\workspace\\chip_inspection\\parameter\\ABCDEF")
        #設置
        self.good_result_data_lbl.place(x=10,y=10,height=20)
        self.good_result_btn.place(x=180,y=10,height=25)
        self.good_data_address_entry.place(x=10,y=40,width=450,height=30)

        """テストデータ関係"""
        self.test_result_data_lbl = tk.Label(self.left_frame, font=("MSゴシック","14"), text="テストデータフォルダ") # テスト結果ファイル参照ラベル
        self.test_result_btn = tk.Button(self.left_frame,text="参照",font=("MSゴシック","12"),command=self.open_test_result_data)
        self.test_data_address = tk.StringVar()
        self.test_data_address_entry = tk.Entry(self.left_frame,textvariable=self.test_data_address)
        self.test_data_address.set("c:\\workspace\\chip_inspection\\result\\CLFS020JJ1")
        #設置
        self.test_result_data_lbl.place(x=10,y=80,height=20)
        self.test_result_btn.place(x=180,y=80,height=25)
        self.test_data_address_entry.place(x=10,y=110,width=450,height=30)

        """解析につかう係数の条件"""
        self.min_value_lbl = tk.Label(self.left_frame, font=("MSゴシック","12"), text="最小値") # 係数の最小値
        self.min_value = tk.StringVar()
        self.min_value.set("15")
        self.min_value_entry = tk.Entry(self.left_frame,textvariable=self.min_value)
        #設置
        self.min_value_lbl.place(x=10,y=160,height=30)
        self.min_value_entry.place(x=70,y=160,width=50,height=30)

        self.max_value_lbl = tk.Label(self.left_frame, font=("MSゴシック","12"), text="最大値") # 係数の最大値
        self.max_value = tk.StringVar()
        self.max_value.set("16")
        self.max_value_entry = tk.Entry(self.left_frame,textvariable=self.max_value)
        #設置
        self.max_value_lbl.place(x=150,y=160,height=30)
        self.max_value_entry.place(x=210,y=160,width=50,height=30)

        self.step_lbl = tk.Label(self.left_frame, font=("MSゴシック","12"), text="ステップ") # 検査ステップ
        self.step = tk.StringVar()
        self.step.set("1")
        self.step_entry = tk.Entry(self.left_frame,textvariable=self.step)
        #設置
        self.step_lbl.place(x=290,y=160,height=30)
        self.step_entry.place(x=350,y=160,width=50,height=30)

        """解析結果を出力するtreeを作成"""
        self.result_lbl = tk.Label(self.left_frame, font=("MSゴシック","15"), text="解析結果") # 解析結果
        self.result_lbl.place(x=10,y=210,height=30)
        #不良品を登録する用のボタン
        self.resist_fail_button = tk.Button(self.left_frame, font=("MSゴシック","15"),foreground="green", text="Fail画像登録",command=self.resist_fail_image) 
        self.resist_fail_button.place(x=150,y=210,height=30)
        #不良品のみ表示するか通常表示するかのradioボタン
        self.show_only_fail = tk.BooleanVar()
        self.check_only_fail = tk.Checkbutton(self.left_frame, variable=self.show_only_fail,text = "Failのみ表示", command = self.show_only_fail_image)
        self.check_only_fail.place(x=300,y=210,height=30)

        """
        #tree
        self.tree = ttk.Treeview(self.left_frame)
        self.tree.column("#0",width=50,stretch=tk.NO,anchor=tk.E)
        self.tree.place(x=10,y=250,width=450,height=250)

        #treeに横スクロールバーを設置
        hscrollbar = ttk.Scrollbar(self.left_frame,orient=tk.HORIZONTAL,command=self.tree.xview)
        self.tree.configure(xscrollcommand=lambda f, l: hscrollbar.set(f,l))
        hscrollbar.place(x=10,y=500,width=450)

        #treeに縦スクロールバーを設置
        vscrollbar = ttk.Scrollbar(self.left_frame,orient=tk.VERTICAL,command=self.tree.yview)
        self.tree.configure(yscrollcommand=vscrollbar.set)
        vscrollbar.place(x=460,y=250,height=250)
        """

        """解析結果を出力するSheetを作成"""
        self.sheet = Sheet(self.left_frame)
        self.sheet.enable_bindings()
        self.sheet.extra_bindings("cell_select",func=self.load_image)
        self.sheet.place(x=10,y=250,width=450,height=600)

        """解析開始ボタンを設置"""
        self.start_analysis_btn = tk.Button(self.left_frame,text="解析開始",font=("MSゴシック","15"),foreground="red",command=self.start_analysis)
        self.start_analysis_btn.place(x=10,y=880,width=100,height=30)

        #------------------------------------------------------------------
        #キャンバスの設置
        #------------------------------------------------------------------
        self.canvas = tk.Canvas(paned_window, background= self.back_color)
        self.canvas.pack(expand=True,  fill=tk.BOTH)  # この両方でDock.Fillと同じ

        paned_window.add(self.left_frame)
        paned_window.add(self.canvas)
        paned_window.pack(expand=True,fill=tk.BOTH)

        #------------------------------------------------------------------
        #マウスイベントの設定
        #------------------------------------------------------------------
        self.canvas.bind("<Motion>", self.mouse_move)                       # MouseMove
        self.canvas.bind("<B1-Motion>", self.mouse_move_left)               # MouseMove（左ボタンを押しながら移動）
        self.canvas.bind("<Button-1>", self.mouse_down_left)                # MouseDown（左ボタン）
        self.canvas.bind("<Double-Button-1>", self.mouse_double_click_left) # MouseDoubleClick（左ボタン）
        self.canvas.bind("<MouseWheel>", self.mouse_wheel)                  # MouseWheel

    #---------------------------------------------------------------
    #menu barの項目選択時の関数
    #---------------------------------------------------------------

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

    #画像保存
    def save(self):

        if self.cv_image is None:
            return

        filename = filedialog.asksaveasfilename(title="名前を付けて保存",\
                filetypes=[("JPEG",".jpg"),("PNG",".png")],\
                initialdir="./",\
                defaultextension = "jpg")

        cv2.imwrite(filename,self.cv_image)

    #バージョン情報確認用のウインドウを開く
    def open_version(self):
        self.dlg_version = tk.Toplevel(self.master)
        self.dlg_version.title("バージョン情報")
        self.dlg_version.geometry("300x150")

        self.dlg_version.grab_set()
        self.dlg_version.focus_set()
        self.dlg_version.transient(self.master)

        dlg_test_address_label = tk.Label(self.dlg_version,text="バージョン："+VERSION_INFO,font=("MSゴシック","15"))
        dlg_test_address_label.pack()
        dlg_test_address_label.place(x=60,y=30,height=20)

        dlg_test_address_label = tk.Label(self.dlg_version,text="作成日："+DATE_INFO,font=("MSゴシック","15"))
        dlg_test_address_label.pack()
        dlg_test_address_label.place(x=60,y=60,height=20)

        #閉じるボタンを設置
        btn_close = tk.Button(self.dlg_version,text="閉じる",font=("MSゴシック","15"),command=self.dlg_version_close)
        btn_close.place(x=100,y=100,height=30)

        app.wait_window(self.dlg_version)
    
    #dlgを閉じる関数
    def dlg_version_close(self):
        self.dlg_version.destroy()

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

            split_list = []
            if len(self.split_data_list)>0:
                for i,data in enumerate(self.split_data_list):
                    n = i+1
                    sx = int(data[0])
                    sy = int(data[1])
                    lsx = int(data[2])
                    lsy = int(data[3])

                    if (x > sx and x< sx+lsx) and (y > sy and y < sy+lsy):
                        split_list.append(str(n))
                self.split_data["text"] = ",".join(split_list)
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
        ''' 現在の位置情報を取得 '''
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
    # ボタンイベント
    # -------------------------------------------------------------------------------

    def open_good_result_data(self):
        """良品データの参照"""

        address = filedialog.askdirectory(title="良品フォルダオープン",\
                                          initialdir="c:\\workspace\\chip_inspection\\result\\")
                                          
   
        self.good_data_address.set(address)

        return

    def open_test_result_data(self):
        """テストresultデータの参照"""

        address = filedialog.askdirectory(title="テストフォルダオープン",\
                                          initialdir="c:\\workspace\\chip_inspection\\parameter\\")
                
        self.test_data_address.set(address)

        return

    def read_good_data(self):
        """良品データ読み込み"""
        good_data_list = [] #良品データのmeanとstdを入れるリスト

        address = self.good_data_address.get()
        #result_data読込
        filename = address + "//" + "good_data.csv"
        if os.path.exists(filename):

            data_file = open(filename,"r")
            data_line = data_file.readline()
            n=0
            while data_line:

                #n=0はヘッダー
                if n>=1:
                    data_list = [x for x in data_line.replace("\n","").split(",") if x!= ""]
                    float_list = [float(s) for s in data_list]
                    good_score = np.array(float_list)
                    mean_value = np.mean(good_score)
                    std_value = np.std(good_score)

                    good_data_list.append([mean_value,std_value])

                data_line = data_file.readline()
                n=n+1

            data_file.close()
        else:
            print("良品のResultデータが存在しません\n解析を終了します")
            return

        #split_data読込
        split_data_list = []
        filename = address + "//split_data.csv"
        if os.path.exists(filename):

            split_file = open(filename,"r")
            split_line = split_file.readline()
            while split_line:
                arr = split_line.replace("\n","").split(",")
                split_data_list.append([arr[0],arr[1],arr[2],arr[3]])

                split_line = split_file.readline()

            split_file.close()
        else:
            print("良品のSplitデータが存在しません\n解析を終了します")
            return

        return good_data_list,split_data_list

    def read_test_data(self):
        """テストデータ読み込み"""
        img_name_list = [] #画像の名前を入れるリスト
        test_score_list = [] #テストデータのスコアを入れるリスト

        address = self.test_data_address.get()
        lotno = address.split("\\")[-1]
        print("ロットNoは{}".format(lotno))

        filename = address+"\\result_data_"+lotno+".csv"
        if os.path.exists(filename):
            df = pd.read_csv(filename,header=1)
            img_name_list = df["no"].tolist()
            for header in df:
                if ".1" in header:
                    test_score_list.append(df[header].to_list())
        else:
            print("テストのデータが存在しません\n解析を終了します")
            return

        return img_name_list,np.array(test_score_list)
    
    def show_tree(self,output_list):

        #TreeViewの内容をクリアする
        self.tree.delete(*self.tree.get_children())

        #列番号をtreeに追加する
        self.tree["column"] = output_list[0]

        #列のヘッダーを更新する
        for n,i in enumerate(self.tree["column"]):
            self.tree.column(i,width=30,anchor=tk.E)
            self.tree.heading(i,text=output_list[0][n]) 

        #行番号及び内容を表示する
        for i,row in enumerate(output_list):
            if i>0:
                self.tree.insert("","end",text=i,values=row)

        return 
    
    def show_sheet(self,header_list):
        """シートに解析結果を表示"""
        self.sheet.set_sheet_data(data=self.output_list)
        self.sheet.headers(newheaders=header_list)

        return
    
    def load_image(self,cell_info):
        """画像をcanvasに読み込む"""
        row = cell_info.row
        column = cell_info.column
        value = self.sheet.get_cell_data(row,column)

        if value == "-":
            return

        img_name = self.test_data_address.get() + "\\"+"all_image\\" + value+ ".jpg"

        #画像の読み込み
        self.set_image(img_name)

        #矩形を描く
        self.write_rectangle(column,value)

        return
    
    def write_rectangle(self,column,value):
        """self.cv_imageに矩形を描く"""

        self.cv_image = cv2.cvtColor(self.cv_image,cv2.COLOR_GRAY2RGBA)
        num_of_img = self.img_name_list.index(value)
        pass_fail_list = self.judge_result_all[column][num_of_img]

        for i,sd in enumerate(self.split_data_list):
                if pass_fail_list[i]==1:
                    x = int(sd[0])
                    y = int(sd[1])
                    lx = int(sd[2])
                    ly = int(sd[3])
                    cv2.rectangle(self.cv_image,(x,y),(x+lx,y+ly),(0,200,0),1)

        self.redraw_image()

        return
    
    def resist_fail_image(self):
        self.resister_window = tk.Toplevel(self.master)
        self.resister_window.title("Fail画像登録")
        self.resister_window.geometry("600x450")

        self.resister_window.focus_set()
        self.resister_window.transient(self.master)

        resister_window_label = tk.Label(self.resister_window,text="Fail画像の名前をセルに登録してください。どのセルに入力しても問題ないです。",font=("MSゴシック","9"))
        resister_window_label.pack()
        resister_window_label.place(x=10,y=10,height=20)

        resister_window_button = tk.Button(self.resister_window,text="更新して閉じる",font=("MSゴシック","12"),foreground="red",command=self.close_resister_window)
        resister_window_button.pack()
        resister_window_button.place(x=450,y=10,height=20)

        """不良画像を登録するSheetを作成"""
        self.resister_sheet = Sheet(self.resister_window,data=self.fail_sheet_data)
        self.resister_sheet.enable_bindings()
        self.resister_sheet.place(x=10,y=30,width=580,height=400)

        app.wait_window(self.resister_window)

        return
    
    def close_resister_window(self):
        """Fail画像登録用のWindowを閉じる"""
        self.fail_sheet_data = self.resister_sheet.get_sheet_data(get_header=False,get_index=False)
        self.resister_window.destroy()
        return
    
    def show_only_fail_image(self):
        """ON->failイメージだけ表示する OFF->全イメージ表示"""
        value = self.show_only_fail.get()
        if value:
            tmp_arr = np.array(self.fail_sheet_data) #resister_sheetのデータを収納
            tmp_arr = tmp_arr[tmp_arr!=""]

            row_num = np.array(self.output_list).shape[0]
            col_num = np.array(self.output_list).shape[1]
            now_row = [0 for i in range(col_num)]
            output_fail_list=[["" for i in range(col_num)] for j in range(row_num)]
            for i,row_data in enumerate(self.output_list):
                for j,col_data in enumerate(row_data):
                    if col_data in tmp_arr:
                        output_fail_list[now_row[j]][j] = col_data
                        now_row[j]+=1

            self.sheet.set_sheet_data(data=output_fail_list)
        else:
            self.sheet.set_sheet_data(data=self.output_list)

        return

    def start_analysis(self):
        """解析開始"""
        #良品データ読み込み
        good_data_list,self.split_data_list = self.read_good_data() #各分割のmeanとstdが入ったリスト
        good_data_num = len(good_data_list) #分割数
        print("良品データの読込が完了しました")
        print("分割数は{}です".format(good_data_num))

        #テストデータ読み込み
        self.img_name_list,test_score_list = self.read_test_data()
        test_data_num = len(self.img_name_list) #チップ数(画像数)
        print("テストデータの読込が完了しました")
        print("テスト数は{}です".format(test_data_num))
        print("解析開始")

        #解析の条件取得
        min_value = int(self.min_value.get())
        max_value = int(self.max_value.get())+1
        if max_value < min_value:
            print("最大値が最小値より小さいです。設定しなおしてください。")
            return
        step = int(self.step.get())

        #テスト数X分割数のリストにどの分割のどの画像がFailかを割り出した後、係数毎にどの画像がFail画像かを出す
        coeff_list = []
        fail_image_list = [[] for i in range(int((max_value-min_value)/step))] #係数毎にFail画像のリストを作成
        self.judge_result_all = [] #coeffの数 X テストデータの数 X 分割数
        for c,coeff in enumerate(range(min_value,max_value,step)):
            judge_result = [[] for i in range(test_data_num)] 
            print("係数{}".format(coeff))
            coeff_list.append(coeff)

            for i,good_data in enumerate(good_data_list): #分割数でループ
                standard = good_data[0] - coeff*good_data[1] #その分割の規格設定

                for j,score in enumerate(test_score_list[i]): #テスト数
                    if score < standard:
                        judge_result[j].append(1)
                    else:
                        judge_result[j].append(0)

            #係数毎にどの画像がFail画像かを吐き出す
            for i,result in enumerate(judge_result):
                if  1 in result:
                    fail_image_list[c].append(self.img_name_list[i])

            self.judge_result_all.append(judge_result)
            del judge_result

        """outputリストを作成"""
        #outpu_listのイメージ↓
        #--------------------------------------------
        #coeff, 15, 16, 17, 18, 19                   
        #1, **AA, **AA, **AA, **AA, **AA
        #2, **AA, **AA, **AA, **AA, **AA
        #3, -,    **AA, **AA, **AA, **AA
        #4, -,    -   , **AA, **AA, **AA

        row_num = max([len(v) for v in fail_image_list]) #行数(最も不良数の多いcoeffの不良画像数)
        #header
        header_list = coeff_list
        #header_list = coeff_list
        #本体 
        #1列目に番号を入れる
        output_image_list=[[] for i in range(row_num)]
        for i in range(row_num):
            tmp_list=[]
            for j,images in enumerate(fail_image_list): #jはcoeffの数
                if len(images) > i:
                    tmp_list.append(images[i])
                else:
                    tmp_list.append("-")
            output_image_list[i]=tmp_list

        self.output_list = output_image_list  #treeに出力する本体:

        """treeへ表示"""
        #self.show_tree(output_list)
        self.show_sheet(header_list)

        print("データ解析完了")

        return 


if __name__ == "__main__":
    root = tk.Tk()
    root.state("zoomed")
    app = Application(master=root)
    app.mainloop()
