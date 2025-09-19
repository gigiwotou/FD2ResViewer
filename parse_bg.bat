@echo off
echo 正在解析BG.DAT文件...
python fd2_analyzer.py data\BG.DAT -o output_images\BG
echo BG.DAT文件解析完成！
pause