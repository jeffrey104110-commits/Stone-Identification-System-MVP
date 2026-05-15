================================================
石材瑕疵影像辨識系統 - 研發筆記
================================================

1. 專案說明
-----------
本專案使用 YOLOv8 進行石材分類訓練，區分「正常 (Normal)」與「瑕疵 (Defective)」石材。

2.首先建立虛擬環境(若自己會設定可跳過)
---
因為需要使用conda指令及python程式
若您的電腦尚未安裝，請先前往 Miniconda 官網 下載並安裝。
[https://www.anaconda.com/docs/getting-started/miniconda/main]

選定需要測試本專案的資料夾(假設為D:\project)
將資料全部移到 選定的資料夾
在資料夾右鍵開啟終端機
在終端機上輸入
```powershell=
conda create --prefix ./.conda_env python=3.11
```
//建立一個名為(D:\前面的資料夾名稱\.conda_env) python版本為3.11的虛擬環境
//以範例來說是(D:\project\.conda_env)

再來在終端機上輸入
```powershell=
conda activate ./.conda_env
```
// 啟動位於當前目錄下的虛擬環境 要在前面看到(D:\前面的資料夾名稱\.conda_env)才算成功

然後需要下載我們需要使用的模組

在終端機上輸入
```powershell=
pip install fastapi uvicorn pydantic python-dotenv psycopg2-binary python-multipart streamlit
```

3.之後我們需要用到資料庫
我使用的是PostgreSQL -v16版本
[https://www.postgresql.org/download/windows/]

安裝設定細節就不細說了，有需要再請跟我說
總之建立一個名為 stone_project_db 的資料庫
然後在這個 右鍵-stone_project_db資料庫 選查詢工具
再將我這邊準備的SQL.txt的檔案內容 複製 貼上 執行(看起來像播放鍵的)
(若會有問題 請將 -- 與 --後的內容刪掉 再貼上)

這樣資料庫的資料表就準備好了(請記住需要進資料庫的帳號密碼--安裝時應當會請你設定)



4.專案設定 .env
project/               # 專案根目錄 (Root)
├── .conda_env/               # [自動生成] Python 虛擬環境
├── temp_uploads/             # [需手動創建] 暫存圖片上傳區
├── .env                      # 敏感資訊配置檔 (API Keys, DB Passwords)
├── main.py                   # 程式進入點 (FastAPI Endpoints)
└── database.py               # 資料庫服務層 (DB Logic)

直至目前我們的資料夾內應當只差.env檔案了
如果都與我的步驟一樣 應當只需要改[你的資料庫帳號]和[你的資料庫密碼]
```powershell=
# .env file
DATABASE_URL="postgresql://你的資料庫帳號:你的資料庫密碼@localhost:5432/stone_project_db"
TEMP_UPLOAD_DIR="./temp_uploads"
```

若資料庫不同，或想做其他設定:
以下說明:(請根據自身使用的資料庫所更改)
//`DATABASE_URL` (資料庫連線字串)
// **`postgresql://`**：指定**通訊協定**。這告訴程式我們要連接的是 PostgreSQL 資料庫。
// **`你的資料庫帳號:你的資料庫密碼`**：**身分驗證**。這是你登入資料庫的憑證。
// **`@localhost:5432`**：**伺服器位置與連接埠**。
// `localhost` 代表資料庫就在你現在這台電腦上。
// `5432` 是 PostgreSQL 預設的通訊門牌號碼（Port）。
// **`/stone_project_db`**：**目標資料庫名稱**。指定要進入哪一個具體的資料庫房間。

//`TEMP_UPLOAD_DIR` (暫存目錄路徑)
// **`./`**：代表**當前專案目錄**。
// **`temp_uploads`**：資料夾名稱。
---

簡單來說就是:
> **設定環境變數 (.env)**
> 請在專案根目錄建立 `.env` 檔，並根據您的設定修改以下內容：
> 1. **DATABASE_URL**: 設定您的資料庫帳號、密碼及資料庫名稱。格式為：`postgresql://[帳號]:[密碼]@[主機]:[連接埠]/[資料庫名]`。
> 2. **TEMP_UPLOAD_DIR**: 設定 AI 辨識前圖片的暫存路徑，預設為 `./temp_uploads`。


5. 整合 API 與圖片處理 main.py --注意事項
建議裝上vscode開啟檔案更改
(用一般的文字檔更改或IDLE陽春的介面 不容易知道哪裡有錯)

```powershell=
//可能需要改動的地方 (第12行)
model = YOLO(r'D:\\project\\runs\\classify\\train\\weights\\best.pt')  #請替換為你的模型路徑
//請依據自己的資料夾更動(若都按照上述所做 應當不需要更動)
```


6.資料庫連接層 database.py  基本不用改 

7.訓練腳本 train_cls.py --設定
要執行前 
先開啟終端機 啟動你的虛擬環境 後執行這段指令
```powershell=
pip install ultralytics opencv-python
```
安裝 處理影像與模型的必要庫

之後請在stone_dataset內 給予圖 來給模型訓練

說明:
stone_dataset/
├── train/                # 訓練集 (給 AI 讀書用)
│   ├── Normal/           # 放 100-200 張完好石材照片
│   └── Defective/        # 放 100-200 張有瑕疵的照片
└── val/                  # 驗證集 (給 AI 考試用)
    ├── Normal/           # 放 20-40 張沒看過的完好照片
    └── Defective/        # 放 20-40 張沒看過的瑕疵照片

當資料準備好後
一樣在終端機 + 虛擬環境 
執行這段指定
```powershell=
python train_cls.py
```
來執行這段訓練模組用的程式

訓練完後
請先確定
(D:\\project\\runs\\classify\\train\\weights\\best.pt)
這個地方確實有這個檔案

確認好後
請先一樣在終端機 + 虛擬環境
```powershell=
uvicorn main:app --reload
```
(啟動服務)

在執行
```powershell=
streamlit run app_st.py
```
你的電腦網頁就會有畫面跳出來
就可以嘗試將石材圖片丟給ai模型判斷了!!!

