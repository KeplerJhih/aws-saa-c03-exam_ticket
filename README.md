
# 說明
此為 AWS Side Project 練習題 , 題庫來源為外部, 已被翻譯成簡體中文
若要使用 專案透過Python完成，已包檔成容器版本

1. 閱讀pdf 時 需要安裝 文字檔 SimSun.ttf

2. 運行時 只需要 
```
# 創建鏡像
docker build -t saa-c03 . -f Dockerfile

# 運行
docker run -it --rm -v $(pwd):/app saa-c03 python3 main.py
```


# 運行時
Step 1. 檢測exam_ticket 的PDF
剛開始會先檢測在 exam_ticket的pdf 並製作成題庫 用於之後的隨機抽驗

Step 2. 選擇練習題數
輸入要練習的題目數量 

Step 3. 輸出
練習完結束後 會顯示錯誤幾題 正確幾題 並在 err目錄下面輸出該剛剛錯誤的題目及答案方便複習