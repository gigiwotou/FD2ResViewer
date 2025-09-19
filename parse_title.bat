@echo off
echo 正在解析TITLE.DAT文件...
python fd2_analyzer.py data\TITLE.DAT -o output_images\TITLE
echo TITLE.DAT文件解析完成！
pause