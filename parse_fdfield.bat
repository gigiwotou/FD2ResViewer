@echo off
echo 正在解析FDFIELD.DAT文件...
python fd2_analyzer.py data\FDFIELD.DAT -o output_images\FDFIELD
echo FDFIELD.DAT文件解析完成！
pause