"""
炎龙骑士团II资源文件图像预览工具启动脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from preview_tool import ImagePreviewTool
import tkinter as tk


def main():
    """启动预览工具GUI"""
    root = tk.Tk()
    app = ImagePreviewTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()