@echo off
echo 正在解析FDMUS.DAT文件...
python fd2_analyzer.py data\FDMUS.DAT -o output_images\FDMUS
echo FDMUS.DAT文件解析完成！
pause