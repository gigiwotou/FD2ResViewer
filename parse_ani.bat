@echo off
chcp 65001 >nul
echo 正在解析ANI.DAT文件...
python fd2_analyzer.py data\ANI.DAT -o output_images\ANI
echo ANI.DAT文件解析完成!
pause