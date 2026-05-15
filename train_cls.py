import os
from ultralytics import YOLO

# 取得目前檔案所在的目錄路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
# 組合出資料集的相對路徑
dataset_path = os.path.join(current_dir, 'stone_dataset')

# 1. 載入模型
model = YOLO('yolov8n-cls.pt')      

# 2. 開始訓練
results = model.train(
    data=dataset_path,    # 使用自動產生的路徑
    epochs=50, 
    imgsz=224, 
    device='cpu'             # 若有 NVIDIA GPU 可改用 0
)
