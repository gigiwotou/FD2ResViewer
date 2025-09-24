@echo off
chcp 65001 >nul
echo 正在解析FIGANI.DAT文件...
python fd2_analyzer.py data\FIGANI.DAT -o output_images\FIGANI
echo FIGANI.DAT文件解析完成！
pause