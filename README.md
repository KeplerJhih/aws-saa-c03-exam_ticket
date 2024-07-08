
# 說明
此為 AWS Side Project 練習題 , 題庫來源為外部, 已被翻譯成簡體中文
若要使用 專案透過Python完成，已包檔成容器版本
運行時 只需要 
```
# 創建鏡像
docker build -t saa-c03 . -f Dockerfile

# 運行
docker run -it --rm --name saa-c03 -v ${pwd}:. saa-c03
```