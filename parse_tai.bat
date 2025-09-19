@echo off
echo 正在解析TAI.DAT文件...
python fd2_analyzer.py data\TAI.DAT -o output_images\TAI
echo TAI.DAT文件解析完成！
pause