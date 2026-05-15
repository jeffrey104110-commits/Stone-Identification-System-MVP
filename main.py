import os
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from ultralytics import YOLO
from database import get_db_connection, record_flaw_to_db

app = FastAPI(title="AI Stone Inspection System")

# 1. 啟動時加載模型 (推薦放在全域，避免每次請求重複加載)
# 如果本地無此檔，系統會自動下載官方 yolov8n.pt
# --- 載入客製化模型 ---
model = YOLO(r'runs/classify/train/weights/best.pt')  #請替換為你的模型路徑

def ai_model_inference(image_path: str):
    """
    客製化 AI 分類辨識：分析圖片並判斷是否為瑕疵品
    """
    print(f"🤖 [AI Core] 正在進行石材分類辨識...")
    
    results = model.predict(source=image_path, save=False)
    result = results[0]
    
    # 取得最高機率的類別
    top_class_idx = result.probs.top1
    class_name = result.names[top_class_idx]
    confidence = result.probs.top1conf.item()

    # 根據分類名稱決定回傳內容
    if class_name.lower() == "defective":
        description = f"AI 偵測結果：【瑕疵品】(信心度: {confidence:.2%})"
        severity = "高" if confidence > 0.8 else "中"
    else:
        description = f"AI 偵測結果：【正常】(信心度: {confidence:.2%})"
        severity = "正常"
    return {
        "description": description,
        "severity": severity
    }

@app.post("/upload/test/")
async def upload_and_process_image(
    file: UploadFile = File(...),         
    batch_id: int = Form(...)             
):
    temp_file_path = f"temp_uploads/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"

    try:
        # A. 儲存圖片
        contents = await file.read()
        with open(temp_file_path, "wb") as f:
            f.write(contents)

        # B. 執行 AI 辨識
        ai_data = ai_model_inference(temp_file_path)

        # C. 數據寫入資料庫
        with get_db_connection() as conn:
            record_flaw_to_db(
                conn=conn,
                batch_id=batch_id,
                file_path=temp_file_path,
                description=ai_data["description"],
                severity=ai_data["severity"]
            )

        return {
            "status": "Success",
            "batch_id": batch_id,
            "ai_analysis": ai_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # 🗑️ 資源清理：務必刪除暫存圖，防止硬碟爆滿
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

