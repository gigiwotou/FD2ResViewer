@echo off
echo 正在批量处理所有支持的文件...
echo 注意：批量处理会将所有文件解析到同一个输出目录中
echo 如需为每个文件创建独立目录,请分别运行对应的parse_*.bat文件
python fd2_analyzer.py -b data -o output_images
echo 批量处理完成！
pause