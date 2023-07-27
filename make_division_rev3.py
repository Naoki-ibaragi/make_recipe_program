import tkinter as tk            # ウィンドウ作成用
from tkinter import ttk
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

    def menu_save_clicked(self,event=None):
        # 画像を一つ戻す
        self.save() 

    def menu_open_rectfile_clicked(self,event=None):
        # 矩形情報ファイルを開く
        self.open_rectfile()

    def menu_save_rectfile_clicked(self,event=None):
        # 矩形情報ファイルを保存
        self.save_rectfile()

    # -------------------------------------------------------------------------------

    # create_menuメソッドを定義
    def create_menu(self):
        self.menu_bar = tk.Menu(self) # Menuクラスからmenu_barインスタンスを生成
 
        self.file_menu = tk.Menu(self.menu_bar, tearoff = tk.OFF)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.file_menu.add_command(label="Open", command = self.menu_open_clicked, accelerator="Ctrl+O")
        self.file_menu.add_command(label="ReLoad", command = self.menu_reload_clicked, accelerator="Ctrl+R")
        self.file_menu.add_command(label="Save", command = self.menu_save_clicked, accelerator="Ctrl+S")
        self.file_menu.add_separator() # セパレーターを追加
        self.file_menu.add_command(label="Open RectFile", command = self.menu_open_rectfile_clicked)
        self.file_menu.add_command(label="Save RectFile", command = self.menu_save_rectfile_clicked)
        self.file_menu.add_separator() # セパレーターを追加
        self.file_menu.add_command(label="Exit", command = self.menu_quit_clicked)

        self.menu_bar.bind_all("<Control-o>", self.menu_open_clicked) # ファイルを開くのショートカット(Ctrol-Oボタン)
        self.menu_bar.bind_all("<Control-r>", self.menu_reload_clicked) # ファイルを開くのショートカット(Ctrol-Rボタン)
        self.menu_bar.bind_all("<Control-s>", self.menu_save_clicked) # ファイルを開くのショートカット(Ctrol-Sボタン)
        self.master.config(menu=self.menu_bar) # メニューバーの配置
 
    def create_widget(self):
        '''ウィジェットの作成'''

        #####################################################

    # -------------------------------------------------------------------------------

    # create_menuメソッドを定義
    def create_menu(self):
        self.menu_bar = tk.Menu(self) # Menuクラスからmenu_barインスタンスを生成
 
        self.file_menu = tk.Menu(self.menu_bar, tearoff = tk.OFF)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.file_menu.add_command(label="Open", command = self.menu_open_clicked, accelerator="Ctrl+O")
        self.file_menu.add_command(label="ReLoad", command = self.menu_reload_clicked, accelerator="Ctrl+R")
        self.file_menu.add_command(label="Save", command = self.menu_save_clicked, accelerator="Ctrl+S")
        self.file_menu.add_separator() # セパレーターを追加
        self.file_menu.add_command(label="Open RectFile", command = self.menu_open_rectfile_clicked)
        self.file_menu.add_command(label="Save RectFile", command = self.menu_save_rectfile_clicked)
        self.file_menu.add_separator() # セパレーターを追加
        self.file_menu.add_command(label="Exit", command = self.menu_quit_clicked)

        self.menu_bar.bind_all("<Control-o>", self.menu_open_clicked) # ファイルを開くのショートカット(Ctrol-Oボタン)
        self.menu_bar.bind_all("<Control-r>", self.menu_reload_clicked) # ファイルを開くのショートカット(Ctrol-Rボタン)
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

        #####################################################
        # 右側フレーム（画像処理用ボタン配置用）
        right_frame = tk.Frame(self.master, relief = tk.SUNKEN, bd = 2, width = 365)
        #top_frame = tk.Frame(self.master, relief = tk.SUNKEN, bd = 2, height = 100)
        #right_frame.propagate(False) # フーレムサイズの自動調整を無効にする

        #----------------------------
        #right_frame
        #----------------------------
        #表
        self.column = (0,1,2,3,4)
        self.tree=ttk.Treeview(right_frame, columns=self.column,show="headings")

        self.tree.column(0,width=65,anchor="center")
        self.tree.column(1,width=65,anchor="center")
        self.tree.column(2,width=65,anchor="center")
        self.tree.column(3,width=65,anchor="center")
        self.tree.column(4,width=65,anchor="center")

        self.tree.heading(0,text="n")
        self.tree.heading(1,text="x")
        self.tree.heading(2,text="y")
        self.tree.heading(3,text="len_x")
        self.tree.heading(4,text="len_y")

        x_set = 10
        y_set = 10
        height = 450

        self.tree.place(x=x_set,y=y_set,height=height)

        vsb = ttk.Scrollbar(right_frame,orient="vertical",command=self.tree.yview)
        vsb.place(x=x_set+325+3,y=y_set+3,height=height)
        self.tree["yscrollcommand"]=vsb.set

        self.id_list={}
        id_tmp=self.tree.insert("","end",values=(0,5,5,50,50))
        self.id_list[id_tmp]=[0,5,5,50,50]

        btn_rectangle = tk.Button(right_frame, text = "矩形を描画", width = 15, command = self.btn_rectangle_click)
        btn_rectangle.place(x=x_set,y=y_set+height+10,height=20)

        btn_delete = tk.Button(right_frame, text = "選択行を削除", width = 15, command = self.btn_delete_click)
        btn_delete.place(x=x_set+120+5,y=y_set+height+10,height=20)

        self.new_data = tk.StringVar()
        txt_new_data = tk.Entry(right_frame,textvariable=self.new_data)
        txt_new_data.place(x=x_set,y=y_set+height+50,height=20)

        btn_add = tk.Button(right_frame, text = "データを表に追加", width = 15, command = self.btn_add_click)
        btn_add.place(x=x_set+120+5,y=y_set+height+50,height=20)

        self.check_value = tk.BooleanVar()
        self.check_grid = tk.Checkbutton(right_frame, variable=self.check_value,text = "グリッド表示", command = self.check_button_click)
        self.check_grid.place(x=x_set,y=y_set+height+100,height=20)

        self.radio_value = tk.IntVar(value=0)
        self.rectangle_mode = 0

        self.radio0 = tk.Radiobutton(right_frame,text="20x80",command=self.radio_click,variable=self.radio_value,value=0)
        self.radio1 = tk.Radiobutton(right_frame,text="80x20",command=self.radio_click,variable=self.radio_value,value=1)
        self.radio2 = tk.Radiobutton(right_frame,text="40x40",command=self.radio_click,variable=self.radio_value,value=2)
        self.radio3 = tk.Radiobutton(right_frame,text="20x40",command=self.radio_click,variable=self.radio_value,value=3)
        self.radio4 = tk.Radiobutton(right_frame,text="40x20",command=self.radio_click,variable=self.radio_value,value=4)

        self.radio0.place(x=x_set+120,y=y_set+height+80,height=20)
        self.radio1.place(x=x_set+120,y=y_set+height+100,height=20)
        self.radio2.place(x=x_set+120,y=y_set+height+120,height=20)
        self.radio3.place(x=x_set+200,y=y_set+height+80,height=20)
        self.radio4.place(x=x_set+200,y=y_set+height+100,height=20)

        #----------------------------
        #right_frame
        #----------------------------
        #ラベル、スタートボタン

        # フレームを配置
        right_frame.pack(side = tk.RIGHT, fill = tk.Y)
        #top_frame.pack(side = tk.TOP, fill = tk.X)
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
        self.canvas.bind("<ButtonRelease-1>", self.left_click_release)      # 左クリックを離す
        self.rectangle=None

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

        self.original_cv_image = self.cv_image.copy()
        self.original_cv_image = cv2.cvtColor(self.original_cv_image,cv2.COLOR_GRAY2RGB)

    #矩形描画用の座標テキストファイルをオープン
    def open_rectfile(self):

        filename = filedialog.askopenfilename(title="テキストファイルオープン",\
                filetypes=[("csv file",".csv"),("CSV",".csv")],\
                initialdir="./")

        rectFile = open(filename,"r")

        #現在の表の項目をすべて削除
        for key in self.id_list:
            self.tree.delete(key)
        
        self.id_list = dict()

        rect_line = rectFile.readline()
        n=0
        while rect_line:
            
            x = rect_line.split(",")[0]
            y = rect_line.split(",")[1]
            lx = rect_line.split(",")[2]
            ly = rect_line.split(",")[3]
            id_tmp=self.tree.insert("","end",values=(n,x,y,lx,ly))
            self.id_list[id_tmp]=[n,x,y,lx,ly]

            rect_line = rectFile.readline()
            n+=1
            
        rectFile.close()

    #矩形描画用の座標テキストファイルを保存
    def save_rectfile(self):

        filename = filedialog.asksaveasfilename(title="名前を付けて保存",\
                filetypes=[("CSV",".csv")],\
                initialdir="./",\
                defaultextension = "csv")

        output_rect_file = open(filename,"w")

        for key in self.id_list:
            output_line = "" 
            for i in self.id_list[key][1:]:
                output_line+=str(i)+","
            output_line+="\n"
            output_rect_file.write(output_line)

        output_rect_file.close()

        return 

    #画像保存
    def save(self):

        if self.cv_image is None:
            return

        filename = filedialog.asksaveasfilename(title="名前を付けて保存",\
                filetypes=[("JPEG",".jpg"),("PNG",".png")],\
                initialdir="./",\
                defaultextension = "jpg")

        cv2.imwrite(filename,self.cv_image)

    
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
        if event.state & 0x1:

            # 画像座標
            mouse_posi = np.array([event.x, event.y, 1]) # マウス座標(numpyのベクトル)
            mat_inv = np.linalg.inv(self.mat_affine)     # 逆行列（画像→Cancasの変換からCanvas→画像の変換へ）
            self.image_posi = np.dot(mat_inv, mouse_posi)     # 座標のアフィン変換
            x = int(np.floor(self.image_posi[0]))
            y = int(np.floor(self.image_posi[1]))
            if x >= 0 and x < self.pil_image.width and y >= 0 and y < self.pil_image.height:
                # 輝度値の取得
                #self.rx1 = x
                #self.ry1 = y
                self.rx1 = 10*(x//10)
                self.ry1 = 10*(y//10)
                self.rectangle = 1
        else:
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

    def left_click_release(self,event):
        ''' マウスの左クリックをリリース '''
        if self.pil_image is None:
            return
        if self.rectangle:
            self.rectangle=None

            # 画像座標
            #矩形描画
            if self.rectangle_mode == 0:
                cv2.rectangle(self.cv_image,(self.rx1,self.ry1),(self.rx1+20,self.ry1+80),(0,0,200),1)
                item = self.tree.insert("","end",values=(len(self.id_list),self.rx1,self.ry1,20,80))
                self.id_list[item]=[len(self.id_list),self.rx1,self.ry1,20,80]
                self.new_data.set("")
            elif self.rectangle_mode == 1:
                cv2.rectangle(self.cv_image,(self.rx1,self.ry1),(self.rx1+80,self.ry1+20),(0,0,200),1)
                item = self.tree.insert("","end",values=(len(self.id_list),self.rx1,self.ry1,80,20))
                self.id_list[item]=[len(self.id_list),self.rx1,self.ry1,80,20]
                self.new_data.set("")
            elif self.rectangle_mode == 2:
                cv2.rectangle(self.cv_image,(self.rx1,self.ry1),(self.rx1+40,self.ry1+40),(0,0,200),1)
                item = self.tree.insert("","end",values=(len(self.id_list),self.rx1,self.ry1,40,40))
                self.id_list[item]=[len(self.id_list),self.rx1,self.ry1,40,40]
                self.new_data.set("")
            elif self.rectangle_mode == 3:
                cv2.rectangle(self.cv_image,(self.rx1,self.ry1),(self.rx1+20,self.ry1+40),(0,0,200),1)
                item = self.tree.insert("","end",values=(len(self.id_list),self.rx1,self.ry1,20,40))
                self.id_list[item]=[len(self.id_list),self.rx1,self.ry1,20,40]
                self.new_data.set("")
            elif self.rectangle_mode == 4:
                cv2.rectangle(self.cv_image,(self.rx1,self.ry1),(self.rx1+40,self.ry1+20),(0,0,200),1)
                item = self.tree.insert("","end",values=(len(self.id_list),self.rx1,self.ry1,40,20))
                self.id_list[item]=[len(self.id_list),self.rx1,self.ry1,40,20]
                self.new_data.set("")

            self.redraw_image() # 再描画

    def mouse_down_right(self,event):
        ''' マウスの右ボタンをクリック '''
        return 0

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

    def btn_rectangle_click(self):
        '''矩形描画ボタンがクリックされたとき'''

        if self.pil_image is None:
            return

        self.cv_image = self.original_cv_image.copy()

        for i,key in enumerate(self.id_list):
            x1 = int(self.id_list[key][1])
            y1 = int(self.id_list[key][2])
            x2 = x1+int(self.id_list[key][3])
            y2 = y1+int(self.id_list[key][4])
            cv2.rectangle(self.cv_image,(x1,y1),(x2,y2),(0,0,200),1)
            cv2.putText(self.cv_image,str(i),(x1,y1),cv2.FONT_HERSHEY_PLAIN,1.5,(0,200,0),1,cv2.LINE_AA)

        self.redraw_image()

    def btn_delete_click(self):
        '''表削除ボタンがクリックされたとき'''
        selected_items = self.tree.selection()
        for item in selected_items:
            self.tree.delete(item)
            self.id_list.pop(item)

        for i,key in enumerate(self.id_list):
            self.id_list[key][0]=i
            self.tree.set(key,column=0,value=i)

    def btn_add_click(self):
        '''表追加ボタンがクリックされたとき'''

        data = self.new_data.get()
        data_arr = data.split(",")

        if len(data_arr)!=4:
            self.new_data.set("")
            return
       
        item = self.tree.insert("","end",values=(len(self.id_list),data_arr[0],data_arr[1],data_arr[2],data_arr[3]))
        self.id_list[item]=[len(self.id_list),data_arr[0],data_arr[1],data_arr[2],data_arr[3]]
        self.new_data.set("")

        return 

    def check_button_click(self):
        '''チェックボタンがクリックされたとき'''

        if self.pil_image is None:
            return

        value = self.check_value.get()

        #self.cv_image = self.original_cv_image.copy()

        if value:
            #チェックボックスがONしていればgridを表示
            size_x = self.cv_image.shape[0]
            size_y = self.cv_image.shape[1]
            grid_size=50
            for x in range(0,size_x,grid_size):
                for y in range(0,size_y,grid_size):
                    x1 = x
                    y1 = y
                    x2 = x+grid_size
                    y2 = y+grid_size
                    cv2.rectangle(self.cv_image,(x1,y1),(x2,y2),(0,200,0),1)
                    cv2.putText(self.cv_image,str(x1),(x1,y1),cv2.FONT_HERSHEY_PLAIN,1,(0,200,0),1,cv2.LINE_AA)
                    cv2.putText(self.cv_image,str(y1),(x1,y1+15),cv2.FONT_HERSHEY_PLAIN,1,(0,200,0),1,cv2.LINE_AA)

                    for i in range(0,50,10):
                        for j in range(0,50,10):

                            cv2.circle(self.cv_image,(x1+i,y1+j),1,(200,0,0),-1,cv2.LINE_AA)

        self.redraw_image()

    def radio_click(self):
        '''ラジオボタンがクリックされたとき'''
        value = self.radio_value.get()
        self.rectangle_mode = value

        return


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
