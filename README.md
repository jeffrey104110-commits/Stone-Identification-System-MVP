# 🧱石材瑕疵影像辨識系統 - 研發筆記

## 1. 專案說明

本專案使用 YOLOv8 進行石材分類訓練，區分「正常 (Normal)」與「瑕疵 (Defective)」石材。

---

## 2. 首先建立虛擬環境 (若自己會設定可跳過)

因為需要使用 conda 指令及 python 程式，若您的電腦尚未安裝，請先前往 Miniconda 官網下載並安裝。
[Miniconda 官網](https://www.anaconda.com/docs/getting-started/miniconda/main)

1. 選定需要測試本專案的資料夾 (假設為 `D:\project`)。
2. 將資料全部移到選定的資料夾。
3. 在資料夾右鍵開啟終端機。
4. 在終端機上輸入：
```powershell
conda create --prefix ./.conda_env python=3.11
```


> // 建立一個名為 (D:\前面的資料夾名稱\.conda_env) python 版本為 3.11 的虛擬環境
> // 以範例來說是 (D:\project\.conda_env)


5. 再來在終端機上輸入：
```powershell
conda activate ./.conda_env
```


> // 啟動位於當前目錄下的虛擬環境，要在前面看到 (D:\前面的資料夾名稱\.conda_env) 才算成功


6. 下載我們需要使用的模組，在終端機上輸入：
```powershell
pip install -r requirements.txt
```


即可下載我使用過的所有模組。

---

## 3. 之後我們需要用到資料庫

我使用的是 **PostgreSQL -v16** 版本：
[PostgreSQL 下載連結](https://www.postgresql.org/download/windows/)

安裝設定細節就不細說了，有需要再請跟我說。

1. 建立一個名為 `stone_project_db` 的資料庫。
2. 在 `stone_project_db` 資料庫按右鍵，選擇 **[查詢工具]**。
3. 將我準備的 `SQL.txt` 檔案內容 **複製、貼上、執行** (看起來像播放鍵的按鈕)。
:::info
若會有問題，請將 `--` 與 `--` 後的內容刪掉再貼上。
:::
4. 這樣資料庫的資料表就準備好了 (請記住需要進資料庫的帳號密碼，安裝時應當會請你設定)。

---

## 4. 專案設定 .env

專案目錄結構如下：

```text
project/                # 專案根目錄 (Root)
├── .conda_env/         # [自動生成] Python 虛擬環境
├── temp_uploads/       # [需手動創建] 暫存圖片上傳區
├── .env                # 敏感資訊配置檔 (API Keys, DB Passwords)
├── main.py             # 程式進入點 (FastAPI Endpoints)
└── database.py         # 資料庫服務層 (DB Logic)
```

直至目前我們的資料夾內應當只差 `.env` 檔案了。如果都與我的步驟一樣，應當只需要改 `[你的資料庫帳號]` 和 `[你的資料庫密碼]`：

```python
# .env file
DATABASE_URL="postgresql://你的資料庫帳號:你的資料庫密碼@localhost:5432/stone_project_db"
TEMP_UPLOAD_DIR="./temp_uploads"

```

**若資料庫不同，或想做其他設定，以下說明：**
(請根據自身使用的資料庫所更改)

* **`DATABASE_URL` (資料庫連線字串)**：
* `postgresql://`：指定通訊協定。
* `你的資料庫帳號:你的資料庫密碼`：身分驗證憑證。
* `@localhost:5432`：伺服器位置與連接埠 (PostgreSQL 預設為 5432)。
* `/stone_project_db`：目標資料庫名稱。


* **`TEMP_UPLOAD_DIR` (暫存目錄路徑)**：
* `./`：代表當前專案目錄。
* `temp_uploads`：資料夾名稱。



> **設定環境變數 (.env)**
> 請在專案根目錄建立 `.env` 檔，並根據您的設定修改以下內容：
> 1. **DATABASE_URL**: 設定您的資料庫帳號、密碼及資料庫名稱。格式為：`postgresql://[帳號]:[密碼]@[主機]:[連接埠]/[資料庫名]`。
> 2. **TEMP_UPLOAD_DIR**: 設定 AI 辨識前圖片的暫存路徑，預設為 `./temp_uploads`。
> 
> 

---



## 5. 訓練腳本 train_cls.py --設定

要執行前，請在 `stone_dataset` 內給予石材的圖片來給模型訓練。

**說明：**

```text
stone_dataset/
├── train/                # 訓練集 (給 AI 讀書用)
│   ├── Normal/           # 放 100-200 張完好石材照片
│   └── Defective/        # 放 100-200 張有瑕疵的照片
└── val/                  # 驗證集 (給 AI 考試用)
    ├── Normal/           # 放 20-40 張沒看過的完好照片
    └── Defective/        # 放 20-40 張沒看過的瑕疵照片
```

當資料準備好後，一樣在 **終端機 + 虛擬環境** 下執行：

```powershell
python train_cls.py
```

來執行這段訓練模組用的程式。

---

## 8. 最後啟動系統

訓練完後請先確定：
`(D:\\project\\runs\\classify\\train\\weights\\best.pt)` 這個地方確實有這個檔案。

確認好後，請先一樣在 **終端機 + 虛擬環境** 下：

1. 啟動服務：
```powershell
uvicorn main:app --reload
```


2. 執行網頁介面：
```powershell
streamlit run app_st.py
```



你的電腦網頁就會有畫面跳出來，就可以嘗試將石材圖片丟給 AI 模型判斷了！