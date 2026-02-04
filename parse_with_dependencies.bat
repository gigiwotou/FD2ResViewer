@echo off
chcp 65001 >nul
echo 正在解析所有支持的文件（考虑依赖关系）...

echo.
echo 解析FDSHAP.DAT文件（FDFIELD依赖此项）...
python fd2_analyzer.py data\FDSHAP.DAT -o output_images\FDSHAP

echo.
echo 解析FDFIELD.DAT文件...
python fd2_analyzer.py data\FDFIELD.DAT -o output_images\FDFIELD

echo.
echo 解析FDOTHER.DAT文件...
python fd2_analyzer.py data\FDOTHER.DAT -o output_images\FDOTHER

echo.
echo 解析FDICON.B24文件...
python fd2_analyzer.py data\FDICON.B24 -o output_images\FDICON

echo.
echo 解析DATO.DAT文件...
python fd2_analyzer.py data\DATO.DAT -o output_images\DATO

echo.
echo 解析BG.DAT文件...
python fd2_analyzer.py data\BG.DAT -o output_images\BG

echo.
echo 解析FDTXT.DAT文件...
python fd2_analyzer.py data\FDTXT.DAT -o output_images\FDTXT

echo.
echo 解析ANI.DAT文件...
python fd2_analyzer.py data\ANI.DAT -o output_images\ANI

echo.
echo 解析FDMUS.DAT文件...
python fd2_analyzer.py data\FDMUS.DAT -o output_images\FDMUS

echo.
echo 解析FIGANI.DAT文件...
python fd2_analyzer.py data\FIGANI.DAT -o output_images\FIGANI

echo.
echo 解析TAI.DAT文件...
python fd2_analyzer.py data\TAI.DAT -o output_images\TAI

echo.
echo 解析TITLE.DAT文件...
python fd2_analyzer.py data\TITLE.DAT -o output_images\TITLE

echo.
echo 所有文件解析完成！
pause