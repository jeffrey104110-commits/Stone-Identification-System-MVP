import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image
import os
from database import get_db_connection, record_flaw_to_db

# --- 1. 頁面配置 ---
st.set_page_config(page_title="石材瑕疵偵測系統", layout="wide", page_icon="🏗️")
st.title("🏗️ 工業級石材影像辨識系統")
st.markdown("---")

# --- 2. 載入模型 (快取機制確保流暢度) ---
@st.cache_resource
def load_model():
    # 指向你第五步訓練出的最強大腦
    return YOLO(r'runs/classify/train/weights/best.pt')

model = load_model()

# --- 3. 側邊欄設定 ---
with st.sidebar:
    st.header("⚙️ 系統參數")
    batch_id = st.number_input("批次編號", min_value=1, value=1)
    conf_threshold = st.slider("辨識門檻 (Confidence)", 0.0, 1.0, 0.5)
    st.info("調整門檻可過濾掉信心不足的辨識結果。")

# --- 4. 影像上傳功能 ---
col1, col2 = st.columns(2) # 左右分割版面

with col1:
    st.subheader("📷 影像輸入")
    uploaded_file = st.file_uploader("請上傳石材照片...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="待辨識照片", use_container_width=True)

# --- 5. 執行分析與結果呈現 ---
with col2:
    st.subheader("🔍 AI 分析報告")
    if uploaded_file and st.button("🚀 開始執行 AI 辨識"):
        with st.spinner('AI 正在深度掃描中...'):
            # 暫存圖片供模型讀取
            temp_path = "st_temp_upload.jpg"
            image.save(temp_path)

            # 執行推論
            results = model.predict(source=temp_path, save=False)
            result = results[0]
            
            # 解析數據
            top_class_idx = result.probs.top1
            class_name = result.names[top_class_idx]
            confidence = result.probs.top1conf.item()

            # 狀態顯示邏輯
            is_defective = class_name.lower() == "defective"
            status_text = "🔴 發現瑕疵" if is_defective else "🟢 外觀正常"
            status_color = "red" if is_defective else "green"
            severity = "高" if (is_defective and confidence > 0.8) else ("中" if is_defective else "正常")

            # 渲染 UI
            st.markdown(f"### 狀態：:{status_color}[{status_text}]")
            st.metric("AI 信心度", f"{confidence:.2%}")
            
            desc = f"類別: {class_name} | 信心度: {confidence:.2%}"
            st.text_area("詳細描述", value=desc, height=70)

            # --- 6. 自動化存檔 (Database Write) ---
            try:
                with get_db_connection() as conn:
                    record_flaw_to_db(
                        conn=conn,
                        batch_id=batch_id,
                        file_path=temp_path,
                        description=desc,
                        severity=severity
                    )
                st.success("✅ 數據已自動同步至 PostgreSQL 資料庫")
            except Exception as e:
                st.error(f"🚨 資料庫同步失敗: {e}")

