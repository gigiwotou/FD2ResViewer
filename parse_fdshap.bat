@echo off
echo 正在解析FDSHAP.DAT文件...
python fd2_analyzer.py data\FDSHAP.DAT -o output_images\FDSHAP
echo FDSHAP.DAT文件解析完成！
pause