@echo off
echo 正在打包算法识别平台为exe文件...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 安装PyInstaller（如果未安装）
echo 检查PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo 正在安装PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo 错误: PyInstaller安装失败
        pause
        exit /b 1
    )
)

REM 清理之前的构建文件
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"

echo 开始打包...
echo.

REM 使用PyInstaller打包
pyinstaller --onefile ^
    --windowed ^
    --name="算法识别平台" ^
    --add-data="utils/data.json;utils" ^
    --add-data="utils/label2class.txt;utils" ^
    --add-data="utils/ppocr_keys_v1.txt;utils" ^
    --hidden-import=PyQt5.sip ^
    --hidden-import=onnxruntime ^
    --hidden-import=PIL ^
    --hidden-import=numpy ^
    --hidden-import=cv2 ^
    --hidden-import=ui.main_window ^
    --hidden-import=ui.image_display ^
    --hidden-import=ui.result_table ^
    --hidden-import=ui.model_processor ^
    --hidden-import=utils.model_utils ^
    --hidden-import=utils.answer_utils ^
    main_app.py

if errorlevel 1 (
    echo 打包失败！
    pause
    exit /b 1
)

echo.
echo 打包完成！
echo exe文件位置: dist\算法识别平台.exe
echo.
echo 您可以将dist文件夹中的exe文件复制到其他电脑上运行
echo 注意：首次运行可能需要较长时间解压
echo.

pause 