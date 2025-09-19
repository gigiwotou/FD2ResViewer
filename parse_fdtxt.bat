@echo off
echo 正在解析FDTXT.DAT文件...
python fd2_analyzer.py data\FDTXT.DAT -o output_images\FDTXT
echo FDTXT.DAT文件解析完成！
pause