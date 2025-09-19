@echo off
echo 正在解析FDICON.B24文件...
python fd2_analyzer.py data\FDICON.B24 -o output_images\FDICON
echo FDICON.B24文件解析完成！
pause