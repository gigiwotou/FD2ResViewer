"""
炎龙骑士团II资源文件图像预览工具
基于现有的FD2Analyzer实现图像资源预览功能
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import threading
import struct
from fd2_analyzer import FD2Analyzer
from main import ColorPanel


class ImagePreviewTool:
    def __init__(self, root):
        self.root = root
        self.root.title("炎龙骑士团II图像资源预览工具")
        self.root.geometry("1000x700")
        
        # 初始化分析器
        self.analyzer = FD2Analyzer()
        
        # 为分析器添加ColorPanel类的访问
        self.colorpanel_class = ColorPanel
        
        # 当前选中的文件
        self.current_file = None
        self.current_file_type = None
        
        # 图像数据缓存 - 用于存储已解析的图像
        self.image_cache = {}
        # 数据块缓存 - 用于存储已解析的数据块信息
        self.datablock_cache = {}
        # 预览图像缓存 - 用于存储已生成的预览图像
        self.preview_image_cache = {}
        
        # 存储最后预览的图像，防止被垃圾回收
        self.last_preview_image = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="5")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        file_entry.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        
        browse_btn = ttk.Button(file_frame, text="浏览...", command=self.browse_file)
        browse_btn.grid(row=0, column=1)
        
        file_frame.columnconfigure(0, weight=1)
        
        # 控制按钮区域
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        load_btn = ttk.Button(control_frame, text="加载文件", command=self.load_file)
        load_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.preview_btn = ttk.Button(control_frame, text="预览图像", command=self.preview_images, state=tk.DISABLED)
        self.preview_btn.grid(row=0, column=1, padx=(0, 5))
        
        # 图像列表区域
        list_frame = ttk.LabelFrame(main_frame, text="图像列表", padding="5")
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # 创建树形视图
        columns = ('ID', 'Type', 'Size', 'Format')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # 定义列标题
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # 滚动条
        tree_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="图像预览", padding="5")
        preview_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建画布用于显示图像
        self.canvas = tk.Canvas(preview_frame, bg='white', width=400, height=400)
        canvas_scroll_y = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        canvas_scroll_x = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=canvas_scroll_y.set, xscrollcommand=canvas_scroll_x.set)
        
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        canvas_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        canvas_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # 绑定树形视图选择事件
        self.tree.bind('<<TreeviewSelect>>', self.on_image_select)
        
        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
    
    def browse_file(self):
        """浏览并选择dat文件"""
        file_path = filedialog.askopenfilename(
            title="选择FD2资源文件",
            filetypes=[
                ("DAT files", "*.dat"),
                ("B24 files", "*.b24"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def load_file(self):
        """加载选中的文件"""
        file_path = self.file_path_var.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("错误", "请选择有效的文件路径")
            return
        
        try:
            # 分析文件类型
            self.current_file = file_path
            self.current_file_type = os.path.basename(file_path).lower()
            
            # 启用预览按钮
            self.preview_btn.config(state=tk.NORMAL)
            
            # 清空之前的图像列表
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            messagebox.showinfo("成功", f"已加载文件: {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载文件时出错: {str(e)}")
    
    def preview_images(self):
        """预览图像资源"""
        if not self.current_file:
            messagebox.showwarning("警告", "请先加载文件")
            return
        
        # 在新线程中执行预览，避免UI冻结
        thread = threading.Thread(target=self._preview_images_thread)
        thread.daemon = True
        thread.start()
    
    def _preview_images_thread(self):
        """在后台线程中预览图像"""
        try:
            # 更新UI状态
            self.root.after(0, lambda: self._update_status("正在分析文件..."))
            
            # 根据文件类型进行纯内存解析（不生成任何文件到硬盘）
            if self.analyzer.parse_file_in_memory(self.current_file):
                self.root.after(0, lambda: self._load_image_list())
            else:
                self.root.after(0, lambda: messagebox.showerror("错误", "无法分析选定的文件"))
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"预览图像时出错: {str(e)}"))
        finally:
            self.root.after(0, lambda: self._update_status("准备就绪"))
    
    def _update_status(self, status):
        """更新状态"""
        self.root.title(f"炎龙骑士团II图像资源预览工具 - {status}")
    
    def _load_image_list(self):
        """加载图像列表到树形视图"""
        # 清空之前的图像列表
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 根据文件类型加载相应的图像数据
        image_data = []
        
        if 'fdother.dat' in self.current_file_type:
            image_data = self._get_fdother_images()
        elif 'fdicon.b24' in self.current_file_type:
            image_data = self._get_fdicon_images()
        elif 'dato.dat' in self.current_file_type:
            image_data = self._get_dato_images()
        elif 'bg.dat' in self.current_file_type:
            image_data = self._get_bg_images()
        elif 'tai.dat' in self.current_file_type:
            image_data = self._get_tai_images()
        elif 'figani.dat' in self.current_file_type:
            image_data = self._get_figani_images()
        elif 'fdshap.dat' in self.current_file_type:
            image_data = self._get_fdshap_images()
        else:
            messagebox.showinfo("提示", "该文件类型可能不包含可预览的图像资源")
            return
        
        # 添加到树形视图
        for img_info in image_data:
            self.tree.insert('', tk.END, values=img_info)
        
        self._update_status(f"已加载 {len(image_data)} 个图像")
    
    def _get_fdother_images(self):
        """获取FDOTHER.DAT中的图像信息"""
        images = []
        
        # 先分析所有主索引
        for sub_index in range(len(self.analyzer.datablocksOTHER)):
            datablock = self.analyzer.datablocksOTHER[sub_index]
            if datablock and datablock.length > 4:
                try:
                    # 对每个主索引进行子索引分析
                    self.analyzer.AnalysisOtherSubs(sub_index)
                    # 调用AnalysisOtherSubsImage方法处理子索引图像
                    self.analyzer.AnalysisOtherSubsImage(sub_index)
                    # 添加主索引项
                    images.append((f"Main_{sub_index}", "MainBlock", "Variable", f"ID_{sub_index}"))
                    
                    # 如果有子数据块，也添加它们
                    if hasattr(self.analyzer, 'datablocksOTHERSubs') and self.analyzer.datablocksOTHERSubs:
                        for sub_idx, subblock in enumerate(self.analyzer.datablocksOTHERSubs):
                            if subblock and subblock.length > 4:
                                images.append((f"Main_{sub_index}_Sub_{sub_idx}", "SubBlock", "Variable", f"Main_{sub_index}_Sub_{sub_idx}"))
                except Exception as e:
                    # 如果特定的主索引分析失败，继续下一个
                    continue
                
        return images
    
    def _get_fdicon_images(self):
        """获取FDICON.B24中的图像信息"""
        images = []
        for i in range(min(100, len(self.analyzer.datablocksICON))):  # 只显示前100个
            datablock = self.analyzer.datablocksICON[i]
            if datablock and datablock.length > 4:
                images.append((f"Icon_{i:05d}", "Icon", "24x24", "Palette"))
        return images
    
    def _get_dato_images(self):
        """获取DATO.DAT中的图像信息"""
        images = []
        for i in range(min(50, len(self.analyzer.datablocksDATO))):  # 只显示前50个主分类
            for j in range(min(4, len(self.analyzer.datablocksDATO[i]))):  # 每个主分类最多4个子分类
                datablock = self.analyzer.datablocksDATO[i][j]
                if datablock and datablock.length > 4:
                    images.append((f"Dato_{i:05d}_{j:02d}", "Face", "Variable", "Face"))
        return images
    
    def _get_bg_images(self):
        """获取BG.DAT中的图像信息"""
        images = []
        for i in range(min(50, len(self.analyzer.datablocksBG))):  # 只显示前50个
            datablock = self.analyzer.datablocksBG[i]
            if datablock and datablock.length > 4:
                images.append((f"BG_{i:05d}", "Background", "Variable", "BG"))
        return images
    
    def _get_tai_images(self):
        """获取TAI.DAT中的图像信息"""
        images = []
        for i in range(min(50, len(self.analyzer.datablocksTAI))):  # 只显示前50个
            datablock = self.analyzer.datablocksTAI[i]
            if datablock and datablock.length > 4:
                images.append((f"TAI_{i:05d}", "Action", "Variable", "TAI"))
        return images
    
    def _get_figani_images(self):
        """获取FIGANI.DAT中的图像信息"""
        images = []
        for i in range(min(50, len(self.analyzer.datablocksFIGANI))):  # 只显示前50个主分类
            sub_count = self.analyzer.subBlockCountsFIGANI[i] if i < len(self.analyzer.subBlockCountsFIGANI) else 0
            for j in range(min(10, sub_count)):  # 每个主分类最多10个子分类
                if i < len(self.analyzer.datablocksFIGANI) and j < len(self.analyzer.datablocksFIGANI[i]):
                    datablock = self.analyzer.datablocksFIGANI[i][j]
                    if datablock and datablock.length > 4:
                        images.append((f"Figani_{i:04d}_{j:03d}", "Animation", "Variable", "Fight"))
        return images
    
    def _get_fdshap_images(self):
        """获取FDSHAP.DAT中的图像信息"""
        images = []
        for i in range(min(20, len(self.analyzer.datablocksFDSHAP))):  # 只显示前20个主分类
            sub_count = self.analyzer.subBlockCountsFDSHAP[i] if i < len(self.analyzer.subBlockCountsFDSHAP) else 0
            for j in range(min(50, sub_count)):  # 每个主分类最多50个子分类
                if i < len(self.analyzer.datablocksFDSHAP) and j < len(self.analyzer.datablocksFDSHAP[i]):
                    datablock = self.analyzer.datablocksFDSHAP[i][j]
                    if datablock and datablock.length > 4:
                        images.append((f"FDSHAP_{i:03d}_{j:04d}", "Shape", "24x24", "Tile"))
        return images
    
    def on_image_select(self, event):
        """当选择图像时显示预览"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        img_id = item['values'][0]
        
        # 在新线程中生成图像预览
        thread = threading.Thread(target=self._generate_preview, args=(img_id,))
        thread.daemon = True
        thread.start()
    
    def _generate_preview(self, img_id):
        """生成图像预览"""
        try:
            # 检查缓存中是否已有预生成的图像
            if img_id in self.preview_image_cache:
                image = self.preview_image_cache[img_id]
                self.root.after(0, lambda img=image: self._show_preview_image(img))
                return

            # 解析图像ID
            parts = img_id.split('_')
            
            if 'Icon' in img_id:
                # 处理图标图像
                idx = int(parts[1])
                if idx < len(self.analyzer.datablocksICON):
                    datablock = self.analyzer.datablocksICON[idx]
                    if datablock and datablock.length > 4:
                        image = self.analyzer.bmp_maker.makeShapBMP(
                            24, 24,  # 图标固定大小24x24
                            self.analyzer.fileDatas,
                            datablock.startOffset,
                            datablock.length,
                            self.colorpanel_class(1)
                        )
                        
                        # 缓存生成的图像
                        self.preview_image_cache[img_id] = image
                        self.root.after(0, lambda img=image: self._show_preview_image(img))
            
            elif 'Dato' in img_id:
                # 处理人物表情图像
                idx1 = int(parts[1])
                idx2 = int(parts[2])
                if (idx1 < len(self.analyzer.datablocksDATO) and 
                    idx2 < len(self.analyzer.datablocksDATO[idx1])):
                    datablock = self.analyzer.datablocksDATO[idx1][idx2]
                    if datablock and datablock.length > 4:
                        image = self.analyzer.bmp_maker.makeFaceBMP(
                            self.analyzer.fileDatas,
                            datablock.startOffset,
                            datablock.length,
                            self.colorpanel_class(1)
                        )
                        
                        # 缓存生成的图像
                        self.preview_image_cache[img_id] = image
                        self.root.after(0, lambda img=image: self._show_preview_image(img))
            
            elif 'BG' in img_id:
                # 处理背景图像
                idx = int(parts[1])
                if idx < len(self.analyzer.datablocksBG):
                    datablock = self.analyzer.datablocksBG[idx]
                    if datablock and datablock.length > 4:
                        image = self.analyzer.bmp_maker.makeBgBMP(
                            self.analyzer.fileDatas,
                            datablock.startOffset,
                            datablock.length,
                            self.colorpanel_class(1)
                        )
                        
                        # 缓存生成的图像
                        self.preview_image_cache[img_id] = image
                        self.root.after(0, lambda img=image: self._show_preview_image(img))
            
            elif 'TAI' in img_id:
                # 处理TAI图像
                idx = int(parts[1])
                if idx < len(self.analyzer.datablocksTAI):
                    datablock = self.analyzer.datablocksTAI[idx]
                    if datablock and datablock.length > 4:
                        image = self.analyzer.bmp_maker.makeTAIBMP(
                            self.analyzer.fileDatas,
                            datablock.startOffset,
                            datablock.length,
                            self.colorpanel_class(1)
                        )
                        
                        # 缓存生成的图像
                        self.preview_image_cache[img_id] = image
                        self.root.after(0, lambda img=image: self._show_preview_image(img))
            
            elif 'FDSHAP' in img_id:
                # 处理FDSHAP图像
                idx1 = int(parts[1])
                idx2 = int(parts[2])
                if (idx1 < len(self.analyzer.datablocksFDSHAP) and 
                    idx2 < len(self.analyzer.datablocksFDSHAP[idx1])):
                    datablock = self.analyzer.datablocksFDSHAP[idx1][idx2]
                    if datablock and datablock.length > 4:
                        image = self.analyzer.bmp_maker.makeShapBMP(
                            24, 24,  # 通常FDSHAP是24x24的图块
                            self.analyzer.fileDatas,
                            datablock.startOffset,
                            datablock.length,
                            self.colorpanel_class(1)
                        )
                        
                        # 缓存生成的图像
                        self.preview_image_cache[img_id] = image
                        self.root.after(0, lambda img=image: self._show_preview_image(img))
            
            elif 'Figani' in img_id:
                # 处理FIGANI图像
                idx1 = int(parts[1])
                idx2 = int(parts[2])
                if (idx1 < len(self.analyzer.datablocksFIGANI) and 
                    idx2 < len(self.analyzer.datablocksFIGANI[idx1])):
                    datablock = self.analyzer.datablocksFIGANI[idx1][idx2]
                    if datablock and datablock.length > 4:
                        image = self.analyzer.bmp_maker.makeFightBMP(
                            self.analyzer.fileDatas,
                            datablock.startOffset,
                            datablock.length,
                            self.colorpanel_class(1)
                        )
                        
                        # 缓存生成的图像
                        self.preview_image_cache[img_id] = image
                        self.root.after(0, lambda img=image: self._show_preview_image(img))
            
            elif 'Main_' in img_id:
                # 处理FDOTHER子数据块
                parts = img_id.split('_')
                if len(parts) >= 3 and parts[2] == 'Sub':
                    # 是子数据块: Main_X_Sub_Y
                    try:
                        main_idx = int(parts[1])
                        sub_idx = int(parts[3])
                        
                        # 重新分析主索引以确保子数据块已加载
                        if main_idx < len(self.analyzer.datablocksOTHER):
                            # 调用AnalysisOtherSubs和AnalysisOtherSubsImage方法，这会处理所有子索引并生成图像
                            self.analyzer.AnalysisOtherSubs(main_idx)
                            self.analyzer.AnalysisOtherSubsImage(main_idx)
                            # 由于我们只需要生成特定子索引的图像，调用子图像生成方法
                            if (hasattr(self.analyzer, 'datablocksOTHERSubs') and 
                                self.analyzer.datablocksOTHERSubs and 
                                sub_idx < len(self.analyzer.datablocksOTHERSubs)):
                                
                                datablock_main = self.analyzer.datablocksOTHER[main_idx]
                                datablock_sub = self.analyzer.datablocksOTHERSubs[sub_idx]
                                
                                if datablock_main and datablock_sub and datablock_sub.length > 4:
                                    # 根据FD2Analyzer中的AnalysisOtherSubsImage方法确定图像类型并生成
                                    self._generate_fdother_sub_image(main_idx, sub_idx)
                    except (ValueError, IndexError, AttributeError):
                        pass  # 解析失败，跳过
                else:
                    # 是主数据块: Main_X
                    try:
                        main_idx = int(parts[1])
                        if main_idx < len(self.analyzer.datablocksOTHER):
                            # 为该主索引处理所有子索引
                            self.analyzer.AnalysisOtherSubs(main_idx)
                            self.analyzer.AnalysisOtherSubsImage(main_idx)
                            # 对于主数据块，我们尝试生成第一个子数据块的图像作为代表
                            if (hasattr(self.analyzer, 'datablocksOTHERSubs') and 
                                self.analyzer.datablocksOTHERSubs and 
                                len(self.analyzer.datablocksOTHERSubs) > 0):
                                # 生成第一个子索引的图像
                                datablock_main = self.analyzer.datablocksOTHER[main_idx]
                                datablock_sub = self.analyzer.datablocksOTHERSubs[0]
                                
                                if datablock_main and datablock_sub and datablock_sub.length > 4:
                                    self._generate_fdother_sub_image(main_idx, 0)
                            else:
                                # 如果没有子数据块，使用主数据块的特殊处理
                                datablock = self.analyzer.datablocksOTHER[main_idx]
                                if datablock and datablock.length > 4:
                                    # 根据FD2Analyzer中的AnalysisOtherSubs方法，某些主索引有特殊的图像生成方式
                                    self._generate_fdother_main_image(main_idx)
                    except (ValueError, IndexError):
                        pass  # 解析失败，跳过
        
        except Exception as e:
            print(f"生成预览图像时出错: {str(e)}")
    
    def _generate_fdother_main_image(self, main_idx):
        """根据主索引生成FDOTHER图像"""
        img_id = f"Main_{main_idx}"
        # 检查缓存中是否已有预生成的图像
        if img_id in self.preview_image_cache:
            image = self.preview_image_cache[img_id]
            self.root.after(0, lambda img=image: self._show_preview_image(img))
            return

        try:
            datablock = self.analyzer.datablocksOTHER[main_idx]
            if not (datablock and datablock.length > 4):
                return
            
            # 根据FD2Analyzer中的逻辑处理不同类型的主索引
            if main_idx in (10, 15):
                # 人脸图像
                image = self.analyzer.bmp_maker.makeFaceBMP(
                    self.analyzer.fileDatas,
                    datablock.startOffset,
                    datablock.length,
                    self.colorpanel_class(1)
                )
            elif main_idx in (11, 16, 17, 46, 47, 56, 59, 60, 61, 62, 69, 70, 71, 72, 73, 74, 75, 97, 98, 100):
                # 形状图像
                if self.analyzer.fileDatas and datablock.startOffset + 4 <= len(self.analyzer.fileDatas):
                    sWidth = struct.unpack('<h', self.analyzer.fileDatas[datablock.startOffset:datablock.startOffset+2])[0]
                    sHeight = struct.unpack('<h', self.analyzer.fileDatas[datablock.startOffset+2:datablock.startOffset+4])[0]
                    image = self.analyzer.bmp_maker.makeShapBMP(
                        max(1, min(sWidth, 100)), max(1, min(sHeight, 100)),
                        self.analyzer.fileDatas,
                        datablock.startOffset + 4,
                        datablock.length - 4,
                        self.colorpanel_class(1)
                    )
                else:
                    # 默认大小
                    image = self.analyzer.bmp_maker.makeShapBMP(
                        24, 24,
                        self.analyzer.fileDatas,
                        datablock.startOffset + 4,
                        datablock.length - 4,
                        self.colorpanel_class(1)
                    )
            elif main_idx == 55:
                # 普通图像
                if self.analyzer.fileDatas and datablock.startOffset + 4 <= len(self.analyzer.fileDatas):
                    sWidth = struct.unpack('<h', self.analyzer.fileDatas[datablock.startOffset:datablock.startOffset+2])[0]
                    sHeight = struct.unpack('<h', self.analyzer.fileDatas[datablock.startOffset+2:datablock.startOffset+4])[0]
                    image = self.analyzer.bmp_maker.makeBMP(
                        max(1, min(sWidth, 100)), max(1, min(sHeight, 100)),
                        self.analyzer.fileDatas,
                        datablock.startOffset + 4,
                        datablock.length - 4,
                        self.colorpanel_class(1)
                    )
                else:
                    # 默认大小
                    image = self.analyzer.bmp_maker.makeBMP(
                        24, 24,
                        self.analyzer.fileDatas,
                        datablock.startOffset + 4,
                        datablock.length - 4,
                        self.colorpanel_class(1)
                    )
            else:
                # 尝试分析子索引并根据子索引类型生成图像
                self.analyzer.AnalysisOtherSubs(main_idx)
                # 同时调用AnalysisOtherSubsImage方法
                self.analyzer.AnalysisOtherSubsImage(main_idx)
                # 如果没有特殊处理，则使用默认的形状图像生成方法
                image = self.analyzer.bmp_maker.makeShapBMP(
                    24, 24,
                    self.analyzer.fileDatas,
                    datablock.startOffset + 4,
                    datablock.length - 4,
                    self.colorpanel_class(1)
                )
            
            # 缓存生成的图像
            self.preview_image_cache[img_id] = image
            self.root.after(0, lambda img=image: self._show_preview_image(img))
        except Exception as e:
            print(f"生成FDOTHER主图像时出错: {str(e)}")
    
    def _generate_fdother_sub_image(self, main_idx, sub_idx):
        """根据主索引和子索引生成FDOTHER子图像"""
        img_id = f"Main_{main_idx}_Sub_{sub_idx}"
        # 检查缓存中是否已有预生成的图像
        if img_id in self.preview_image_cache:
            image = self.preview_image_cache[img_id]
            self.root.after(0, lambda img=image: self._show_preview_image(img))
            return

        try:
            # 重新分析主索引以确保子数据块已加载
            self.analyzer.AnalysisOtherSubs(main_idx)
            # 调用AnalysisOtherSubsImage方法以确保数据结构正确设置
            self.analyzer.AnalysisOtherSubsImage(main_idx)
            
            if (hasattr(self.analyzer, 'datablocksOTHERSubs') and 
                self.analyzer.datablocksOTHERSubs and 
                sub_idx < len(self.analyzer.datablocksOTHERSubs)):
                
                datablock_main = self.analyzer.datablocksOTHER[main_idx]
                datablock_sub = self.analyzer.datablocksOTHERSubs[sub_idx]
                
                if datablock_main and datablock_sub and datablock_sub.length > 4:
                    start_offset = datablock_main.startOffset + datablock_sub.startOffset
                    
                    # 根据FD2Analyzer中的AnalysisOtherSubsImage方法逻辑处理不同情况
                    # 这里需要根据main_idx来决定如何处理子索引，与AnalysisOtherSubsImage方法保持一致
                    
                    # 根据AnalysisOtherSubsImage方法的逻辑
                    num3 = main_idx
                    num2 = sub_idx
                    
                    if num3 == 1 or num3 == 96:
                        # 从主数据块获取宽高信息
                        sWidth = 24  # 默认值
                        sHeight = 24  # 默认值
                        if num3 == 96:
                            sWidth = 24
                            sHeight = 24
                        else:
                            if (self.analyzer.fileDatas and 
                                datablock_main.startOffset + 4 <= len(self.analyzer.fileDatas)):
                                sWidth = struct.unpack('<h', self.analyzer.fileDatas[datablock_main.startOffset:datablock_main.startOffset+2])[0]
                                sHeight = struct.unpack('<h', self.analyzer.fileDatas[datablock_main.startOffset+2:datablock_main.startOffset+4])[0]
                        
                        # 生成形状图像
                        try:
                            image = self.analyzer.bmp_maker.makeShapBMP(
                                sWidth, sHeight,
                                self.analyzer.fileDatas,
                                start_offset,
                                datablock_sub.length,
                                self.colorpanel_class(1)
                            )
                        except IndexError:
                            # 如果出现索引错误，尝试使用较小的尺寸或默认尺寸
                            try:
                                image = self.analyzer.bmp_maker.makeShapBMP(
                                    24, 24,
                                    self.analyzer.fileDatas,
                                    start_offset,
                                    datablock_sub.length,
                                    self.colorpanel_class(1)
                                )
                            except:
                                # 如果还是失败，创建一个空白图像
                                image = Image.new('RGB', (24, 24), (255, 255, 255))
                        
                    elif num3 == 2:
                        sWidth = 0  # 默认值
                        sHeight = 0  # 默认值
                        if (self.analyzer.fileDatas and start_offset + 2 <= len(self.analyzer.fileDatas) and start_offset + 4 <= len(self.analyzer.fileDatas)):
                            sWidth = struct.unpack('<h', self.analyzer.fileDatas[start_offset:start_offset+2])[0]
                            sHeight = struct.unpack('<h', self.analyzer.fileDatas[start_offset+2:start_offset+4])[0]
                        
                        data_offset = start_offset + 4
                        # 生成其他类型图像
                        try:
                            image = self.analyzer.bmp_maker.makeBMP(
                                sWidth, sHeight,
                                self.analyzer.fileDatas,
                                data_offset,
                                datablock_sub.length - 4,
                                self.colorpanel_class(1)
                            )
                        except IndexError:
                            # 如果出现索引错误，尝试使用较小的尺寸或默认尺寸
                            try:
                                image = self.analyzer.bmp_maker.makeBMP(
                                    min(sWidth, 100), min(sHeight, 100),
                                    self.analyzer.fileDatas,
                                    data_offset,
                                    datablock_sub.length - 4,
                                    self.colorpanel_class(1)
                                )
                            except:
                                # 如果还是失败，创建一个空白图像
                                image = Image.new('RGB', (24, 24), (255, 255, 255))
                    
                    elif num3 == 4:
                        data_offset = datablock_main.startOffset + datablock_sub.startOffset
                        # 生成字体图像
                        try:
                            image = self.analyzer.bmp_maker.makeFontBMP(
                                self.analyzer.fileDatas,
                                data_offset,
                                datablock_sub.length
                            )
                        except IndexError:
                            # 如果出现索引错误，创建一个空白图像
                            image = Image.new('RGB', (64, 64), (255, 255, 255))
                    
                    elif num3 == 5:
                        start_offset = datablock_main.startOffset + datablock_sub.startOffset
                        sWidth = 0  # 默认值
                        sHeight = 0  # 默认值
                        if (self.analyzer.fileDatas and start_offset + 2 <= len(self.analyzer.fileDatas) and start_offset + 4 <= len(self.analyzer.fileDatas)):
                            sWidth = struct.unpack('<h', self.analyzer.fileDatas[start_offset:start_offset+2])[0]
                            sHeight = struct.unpack('<h', self.analyzer.fileDatas[start_offset+2:start_offset+4])[0]
                        
                        if num2 < 20:
                            data_offset = start_offset + 4
                            # 生成其他类型图像
                            try:
                                image = self.analyzer.bmp_maker.makeBMP(
                                    sWidth, sHeight,
                                    self.analyzer.fileDatas,
                                    data_offset,
                                    datablock_sub.length - 4,
                                    self.colorpanel_class(1)
                                )
                            except IndexError:
                                # 如果出现索引错误，尝试使用较小的尺寸
                                try:
                                    image = self.analyzer.bmp_maker.makeBMP(
                                        min(sWidth, 100), min(sHeight, 100),
                                        self.analyzer.fileDatas,
                                        data_offset,
                                        datablock_sub.length - 4,
                                        self.colorpanel_class(1)
                                    )
                                except:
                                    # 如果还是失败，创建一个空白图像
                                    image = Image.new('RGB', (24, 24), (255, 255, 255))
                        elif num2 < 23:
                            data_offset = start_offset
                            if (self.analyzer.fileDatas and data_offset + 2 <= len(self.analyzer.fileDatas) and data_offset + 4 <= len(self.analyzer.fileDatas)):
                                sWidth = struct.unpack('<h', self.analyzer.fileDatas[data_offset:data_offset+2])[0]
                                sHeight = struct.unpack('<h', self.analyzer.fileDatas[data_offset+2:data_offset+4])[0]
                            # 生成面部图像
                            try:
                                image = self.analyzer.bmp_maker.makeFaceBMP(
                                    self.analyzer.fileDatas,
                                    data_offset,
                                    datablock_sub.length,
                                    self.colorpanel_class(1)
                                )
                            except IndexError:
                                # 如果出现索引错误，创建一个空白图像
                                image = Image.new('RGB', (64, 64), (255, 255, 255))
                        elif num2 < 31:
                            data_offset = start_offset + 4
                            # 生成其他类型图像
                            try:
                                image = self.analyzer.bmp_maker.makeBMP(
                                    sWidth, sHeight,
                                    self.analyzer.fileDatas,
                                    data_offset,
                                    datablock_sub.length - 4,
                                    self.colorpanel_class(1)
                                )
                            except IndexError:
                                # 如果出现索引错误，尝试使用较小的尺寸
                                try:
                                    image = self.analyzer.bmp_maker.makeBMP(
                                        min(sWidth, 100), min(sHeight, 100),
                                        self.analyzer.fileDatas,
                                        data_offset,
                                        datablock_sub.length - 4,
                                        self.colorpanel_class(1)
                                    )
                                except:
                                    # 如果还是失败，创建一个空白图像
                                    image = Image.new('RGB', (24, 24), (255, 255, 255))
                        elif num2 < 53:
                            try:
                                image = self.analyzer.bmp_maker.makeShapBMP(
                                    sWidth, sHeight,
                                    self.analyzer.fileDatas,
                                    start_offset + 4,
                                    datablock_sub.length - 4,
                                    self.colorpanel_class(1)
                                )
                            except IndexError:
                                # 如果出现索引错误，尝试使用默认尺寸
                                try:
                                    image = self.analyzer.bmp_maker.makeShapBMP(
                                        24, 24,
                                        self.analyzer.fileDatas,
                                        start_offset + 4,
                                        datablock_sub.length - 4,
                                        self.colorpanel_class(1)
                                    )
                                except:
                                    # 如果还是失败，创建一个空白图像
                                    image = Image.new('RGB', (24, 24), (255, 255, 255))
                        elif num2 < 64 and num2 != 59:
                            data_offset = start_offset + 4
                            # 生成其他类型图像
                            try:
                                image = self.analyzer.bmp_maker.makeBMP(
                                    sWidth, sHeight,
                                    self.analyzer.fileDatas,
                                    data_offset,
                                    datablock_sub.length - 4,
                                    self.colorpanel_class(1)
                                )
                            except IndexError:
                                # 如果出现索引错误，尝试使用较小的尺寸
                                try:
                                    image = self.analyzer.bmp_maker.makeBMP(
                                        min(sWidth, 100), min(sHeight, 100),
                                        self.analyzer.fileDatas,
                                        data_offset,
                                        datablock_sub.length - 4,
                                        self.colorpanel_class(1)
                                    )
                                except:
                                    # 如果还是失败，创建一个空白图像
                                    image = Image.new('RGB', (24, 24), (255, 255, 255))
                        elif num2 != 59:
                            if num2 < 119 and num2 != 93:
                                data_offset = start_offset
                                if (self.analyzer.fileDatas and data_offset + 2 <= len(self.analyzer.fileDatas) and data_offset + 4 <= len(self.analyzer.fileDatas)):
                                    sWidth = struct.unpack('<h', self.analyzer.fileDatas[data_offset:data_offset+2])[0]
                                    sHeight = struct.unpack('<h', self.analyzer.fileDatas[data_offset+2:data_offset+4])[0]
                                # 生成面部图像
                                try:
                                    image = self.analyzer.bmp_maker.makeFaceBMP(
                                        self.analyzer.fileDatas,
                                        data_offset,
                                        datablock_sub.length,
                                        self.colorpanel_class(1)
                                    )
                                except IndexError:
                                    # 如果出现索引错误，创建一个空白图像
                                    image = Image.new('RGB', (64, 64), (255, 255, 255))
                            else:
                                try:
                                    image = self.analyzer.bmp_maker.makeShapBMP(
                                        sWidth, sHeight,
                                        self.analyzer.fileDatas,
                                        start_offset + 4,
                                        datablock_sub.length - 4,
                                        self.colorpanel_class(1)
                                    )
                                except IndexError:
                                    # 如果出现索引错误，尝试使用默认尺寸
                                    try:
                                        image = self.analyzer.bmp_maker.makeShapBMP(
                                            24, 24,
                                            self.analyzer.fileDatas,
                                            start_offset + 4,
                                            datablock_sub.length - 4,
                                            self.colorpanel_class(1)
                                        )
                                    except:
                                        # 如果还是失败，创建一个空白图像
                                        image = Image.new('RGB', (24, 24), (255, 255, 255))
                        else:
                            # 默认情况
                            try:
                                image = self.analyzer.bmp_maker.makeShapBMP(
                                    sWidth, sHeight,
                                    self.analyzer.fileDatas,
                                    start_offset + 4,
                                    datablock_sub.length - 4,
                                    self.colorpanel_class(1)
                                )
                            except IndexError:
                                # 如果出现索引错误，尝试使用默认尺寸
                                try:
                                    image = self.analyzer.bmp_maker.makeShapBMP(
                                        24, 24,
                                        self.analyzer.fileDatas,
                                        start_offset + 4,
                                        datablock_sub.length - 4,
                                        self.colorpanel_class(1)
                                    )
                                except:
                                    # 如果还是失败，创建一个空白图像
                                    image = Image.new('RGB', (24, 24), (255, 255, 255))
                    
                    elif num3 == 7:
                        start_offset = datablock_main.startOffset + datablock_sub.startOffset
                        sWidth = 0  # 默认值
                        sHeight = 0  # 默认值
                        if (self.analyzer.fileDatas and start_offset + 2 <= len(self.analyzer.fileDatas) and start_offset + 4 <= len(self.analyzer.fileDatas)):
                            sWidth = struct.unpack('<h', self.analyzer.fileDatas[start_offset:start_offset+2])[0]
                            sHeight = struct.unpack('<h', self.analyzer.fileDatas[start_offset+2:start_offset+4])[0]
                        color_panel = self.colorpanel_class(3)  # Create new color panel with ID 3
                        data_offset = start_offset + 4
                        # 生成形状图像
                        try:
                            image = self.analyzer.bmp_maker.makeShapBMP(
                                sWidth, sHeight,
                                self.analyzer.fileDatas,
                                data_offset,
                                datablock_sub.length - 4,
                                color_panel
                            )
                        except IndexError:
                            # 如果出现索引错误，尝试使用默认尺寸
                            try:
                                image = self.analyzer.bmp_maker.makeShapBMP(
                                    24, 24,
                                    self.analyzer.fileDatas,
                                    data_offset,
                                    datablock_sub.length - 4,
                                    color_panel
                                )
                            except:
                                # 如果还是失败，创建一个空白图像
                                image = Image.new('RGB', (24, 24), (255, 255, 255))
                    
                    elif num3 in (6, 9):
                        start_offset = datablock_main.startOffset + datablock_sub.startOffset
                        sWidth = 0  # 默认值
                        sHeight = 0  # 默认值
                        if (self.analyzer.fileDatas and start_offset + 2 <= len(self.analyzer.fileDatas) and start_offset + 4 <= len(self.analyzer.fileDatas)):
                            sWidth = struct.unpack('<h', self.analyzer.fileDatas[start_offset:start_offset+2])[0]
                            sHeight = struct.unpack('<h', self.analyzer.fileDatas[start_offset+2:start_offset+4])[0]
                        data_offset = start_offset
                        if (self.analyzer.fileDatas and data_offset + 2 <= len(self.analyzer.fileDatas) and data_offset + 4 <= len(self.analyzer.fileDatas)):
                            sWidth = struct.unpack('<h', self.analyzer.fileDatas[data_offset:data_offset+2])[0]
                            sHeight = struct.unpack('<h', self.analyzer.fileDatas[data_offset+2:data_offset+4])[0]
                        
                        # 生成面部图像
                        try:
                            image = self.analyzer.bmp_maker.makeFaceBMP(
                                self.analyzer.fileDatas,
                                data_offset,
                                datablock_sub.length,
                                self.colorpanel_class(1)
                            )
                        except IndexError:
                            # 如果出现索引错误，创建一个空白图像
                            image = Image.new('RGB', (64, 64), (255, 255, 255))
                    
                    elif num3 in (12, 63):
                        start_offset = datablock_main.startOffset + datablock_sub.startOffset
                        sWidth = 0  # 默认值
                        sHeight = 0  # 默认值
                        if (self.analyzer.fileDatas and start_offset + 2 <= len(self.analyzer.fileDatas) and start_offset + 4 <= len(self.analyzer.fileDatas)):
                            sWidth = struct.unpack('<h', self.analyzer.fileDatas[start_offset:start_offset+2])[0]
                            sHeight = struct.unpack('<h', self.analyzer.fileDatas[start_offset+2:start_offset+4])[0]
                        
                        if num2 == 0 or (num2 >= 23 and num2 <= 29):
                            data_offset = start_offset + 4
                            # 生成形状图像
                            try:
                                image = self.analyzer.bmp_maker.makeShapBMP(
                                    sWidth, sHeight,
                                    self.analyzer.fileDatas,
                                    data_offset,
                                    datablock_sub.length - 4,
                                    self.colorpanel_class(1)
                                )
                            except IndexError:
                                # 如果出现索引错误，尝试使用默认尺寸
                                try:
                                    image = self.analyzer.bmp_maker.makeShapBMP(
                                        24, 24,
                                        self.analyzer.fileDatas,
                                        data_offset,
                                        datablock_sub.length - 4,
                                        self.colorpanel_class(1)
                                    )
                                except:
                                    # 如果还是失败，创建一个空白图像
                                    image = Image.new('RGB', (24, 24), (255, 255, 255))
                        elif num2 == 1 or num2 == 2 or (num2 >= 11 and num2 < 22):
                            data_offset = start_offset
                            if (self.analyzer.fileDatas and data_offset + 2 <= len(self.analyzer.fileDatas) and data_offset + 4 <= len(self.analyzer.fileDatas)):
                                sWidth = struct.unpack('<h', self.analyzer.fileDatas[data_offset:data_offset+2])[0]
                                sHeight = struct.unpack('<h', self.analyzer.fileDatas[data_offset+2:data_offset+4])[0]
                            # 生成面部图像
                            try:
                                image = self.analyzer.bmp_maker.makeFaceBMP(
                                    self.analyzer.fileDatas,
                                    data_offset,
                                    datablock_sub.length,
                                    self.colorpanel_class(1)
                                )
                            except IndexError:
                                # 如果出现索引错误，创建一个空白图像
                                image = Image.new('RGB', (64, 64), (255, 255, 255))
                        else:
                            data_offset = start_offset + 4
                            # 生成其他类型图像
                            try:
                                image = self.analyzer.bmp_maker.makeBMP(
                                    sWidth, sHeight,
                                    self.analyzer.fileDatas,
                                    data_offset,
                                    datablock_sub.length - 4,
                                    self.colorpanel_class(1)
                                )
                            except IndexError:
                                # 如果出现索引错误，尝试使用较小的尺寸
                                try:
                                    image = self.analyzer.bmp_maker.makeBMP(
                                        min(sWidth, 100), min(sHeight, 100),
                                        self.analyzer.fileDatas,
                                        data_offset,
                                        datablock_sub.length - 4,
                                        self.colorpanel_class(1)
                                    )
                                except:
                                    # 如果还是失败，创建一个空白图像
                                    image = Image.new('RGB', (24, 24), (255, 255, 255))
                    
                    elif num3 == 13:
                        start_offset = datablock_main.startOffset + datablock_sub.startOffset
                        sWidth = 0  # 默认值
                        sHeight = 0  # 默认值
                        if (self.analyzer.fileDatas and start_offset + 2 <= len(self.analyzer.fileDatas) and start_offset + 4 <= len(self.analyzer.fileDatas)):
                            sWidth = struct.unpack('<h', self.analyzer.fileDatas[start_offset:start_offset+2])[0]
                            sHeight = struct.unpack('<h', self.analyzer.fileDatas[start_offset+2:start_offset+4])[0]
                        
                        if num2 == 0:
                            data_offset = start_offset + 4
                            # 生成形状图像
                            try:
                                image = self.analyzer.bmp_maker.makeShapBMP(
                                    sWidth, sHeight,
                                    self.analyzer.fileDatas,
                                    data_offset,
                                    datablock_sub.length - 4,
                                    self.colorpanel_class(1)
                                )
                            except IndexError:
                                # 如果出现索引错误，尝试使用默认尺寸
                                try:
                                    image = self.analyzer.bmp_maker.makeShapBMP(
                                        24, 24,
                                        self.analyzer.fileDatas,
                                        data_offset,
                                        datablock_sub.length - 4,
                                        self.colorpanel_class(1)
                                    )
                                except:
                                    # 如果还是失败，创建一个空白图像
                                    image = Image.new('RGB', (24, 24), (255, 255, 255))
                        elif num2 == 1 or num2 == 2 or num2 >= 11:
                            data_offset = start_offset
                            if (self.analyzer.fileDatas and data_offset + 2 <= len(self.analyzer.fileDatas) and data_offset + 4 <= len(self.analyzer.fileDatas)):
                                sWidth = struct.unpack('<h', self.analyzer.fileDatas[data_offset:data_offset+2])[0]
                                sHeight = struct.unpack('<h', self.analyzer.fileDatas[data_offset+2:data_offset+4])[0]
                            # 生成面部图像
                            try:
                                image = self.analyzer.bmp_maker.makeFaceBMP(
                                    self.analyzer.fileDatas,
                                    data_offset,
                                    datablock_sub.length,
                                    self.colorpanel_class(1)
                                )
                            except IndexError:
                                # 如果出现索引错误，创建一个空白图像
                                image = Image.new('RGB', (64, 64), (255, 255, 255))
                        else:
                            data_offset = start_offset + 4
                            # 生成其他类型图像
                            try:
                                image = self.analyzer.bmp_maker.makeBMP(
                                    sWidth, sHeight,
                                    self.analyzer.fileDatas,
                                    data_offset,
                                    datablock_sub.length - 4,
                                    self.colorpanel_class(1)
                                )
                            except IndexError:
                                # 如果出现索引错误，尝试使用较小的尺寸
                                try:
                                    image = self.analyzer.bmp_maker.makeBMP(
                                        min(sWidth, 100), min(sHeight, 100),
                                        self.analyzer.fileDatas,
                                        data_offset,
                                        datablock_sub.length - 4,
                                        self.colorpanel_class(1)
                                    )
                                except:
                                    # 如果还是失败，创建一个空白图像
                                    image = Image.new('RGB', (24, 24), (255, 255, 255))
                    
                    elif num3 == 14:
                        start_offset = datablock_main.startOffset + datablock_sub.startOffset
                        sWidth = 0  # 默认值
                        sHeight = 0  # 默认值
                        if (self.analyzer.fileDatas and start_offset + 2 <= len(self.analyzer.fileDatas) and start_offset + 4 <= len(self.analyzer.fileDatas)):
                            sWidth = struct.unpack('<h', self.analyzer.fileDatas[start_offset:start_offset+2])[0]
                            sHeight = struct.unpack('<h', self.analyzer.fileDatas[start_offset+2:start_offset+4])[0]
                        
                        if num2 == 0 or num2 >= 23:
                            data_offset = start_offset + 4
                            # 生成形状图像
                            try:
                                image = self.analyzer.bmp_maker.makeShapBMP(
                                    sWidth, sHeight,
                                    self.analyzer.fileDatas,
                                    data_offset,
                                    datablock_sub.length - 4,
                                    self.colorpanel_class(1)
                                )
                            except IndexError:
                                # 如果出现索引错误，尝试使用默认尺寸
                                try:
                                    image = self.analyzer.bmp_maker.makeShapBMP(
                                        24, 24,
                                        self.analyzer.fileDatas,
                                        data_offset,
                                        datablock_sub.length - 4,
                                        self.colorpanel_class(1)
                                    )
                                except:
                                    # 如果还是失败，创建一个空白图像
                                    image = Image.new('RGB', (24, 24), (255, 255, 255))
                        elif num2 == 1 or num2 == 2 or (num2 >= 11 and num2 < 23):
                            data_offset = start_offset
                            if (self.analyzer.fileDatas and data_offset + 2 <= len(self.analyzer.fileDatas) and data_offset + 4 <= len(self.analyzer.fileDatas)):
                                sWidth = struct.unpack('<h', self.analyzer.fileDatas[data_offset:data_offset+2])[0]
                                sHeight = struct.unpack('<h', self.analyzer.fileDatas[data_offset+2:data_offset+4])[0]
                            # 生成面部图像
                            try:
                                image = self.analyzer.bmp_maker.makeFaceBMP(
                                    self.analyzer.fileDatas,
                                    data_offset,
                                    datablock_sub.length,
                                    self.colorpanel_class(1)
                                )
                            except IndexError:
                                # 如果出现索引错误，创建一个空白图像
                                image = Image.new('RGB', (64, 64), (255, 255, 255))
                        else:
                            data_offset = start_offset + 4
                            # 生成其他类型图像
                            try:
                                image = self.analyzer.bmp_maker.makeBMP(
                                    sWidth, sHeight,
                                    self.analyzer.fileDatas,
                                    data_offset,
                                    datablock_sub.length - 4,
                                    self.colorpanel_class(1)
                                )
                            except IndexError:
                                # 如果出现索引错误，尝试使用较小的尺寸
                                try:
                                    image = self.analyzer.bmp_maker.makeBMP(
                                        min(sWidth, 100), min(sHeight, 100),
                                        self.analyzer.fileDatas,
                                        data_offset,
                                        datablock_sub.length - 4,
                                        self.colorpanel_class(1)
                                    )
                                except:
                                    # 如果还是失败，创建一个空白图像
                                    image = Image.new('RGB', (24, 24), (255, 255, 255))
                    
                    else:
                        # 对于未特别处理的主索引，尝试通用方法
                        if (self.analyzer.fileDatas and start_offset + 4 <= len(self.analyzer.fileDatas)):
                            try:
                                sWidth = struct.unpack('<h', self.analyzer.fileDatas[start_offset:start_offset+2])[0]
                                sHeight = struct.unpack('<h', self.analyzer.fileDatas[start_offset+2:start_offset+4])[0]
                                
                                if 1 <= sWidth <= 200 and 1 <= sHeight <= 200:  # 合理的尺寸范围
                                    image = self.analyzer.bmp_maker.makeBMP(
                                        sWidth, sHeight,
                                        self.analyzer.fileDatas,
                                        start_offset + 4,
                                        datablock_sub.length - 4,
                                        self.colorpanel_class(1)
                                    )
                                else:
                                    # 如果尺寸不合理，使用默认尺寸
                                    try:
                                        image = self.analyzer.bmp_maker.makeShapBMP(
                                            24, 24,
                                            self.analyzer.fileDatas,
                                            start_offset,
                                            datablock_sub.length,
                                            self.colorpanel_class(1)
                                        )
                                    except IndexError:
                                        # 如果还是出现索引错误，创建一个空白图像
                                        image = Image.new('RGB', (24, 24), (255, 255, 255))
                            except:
                                # 如果解析失败，使用默认方法
                                try:
                                    image = self.analyzer.bmp_maker.makeShapBMP(
                                        24, 24,
                                        self.analyzer.fileDatas,
                                        start_offset,
                                        datablock_sub.length,
                                        self.colorpanel_class(1)
                                    )
                                except IndexError:
                                    # 如果还是出现索引错误，创建一个空白图像
                                    image = Image.new('RGB', (24, 24), (255, 255, 255))
                        else:
                            # 如果没有足够的数据，使用默认方法
                            try:
                                image = self.analyzer.bmp_maker.makeShapBMP(
                                    24, 24,
                                    self.analyzer.fileDatas,
                                    start_offset,
                                    datablock_sub.length,
                                    self.colorpanel_class(1)
                                )
                            except IndexError:
                                # 如果还是出现索引错误，创建一个空白图像
                                image = Image.new('RGB', (24, 24), (255, 255, 255))
                    
                    # 缓存生成的图像
                    self.preview_image_cache[img_id] = image
                    self.root.after(0, lambda img=image: self._show_preview_image(img))
        except Exception as e:
            print(f"生成FDOTHER子图像时出错: {str(e)}")
    
    def _show_preview_image(self, image):
        """在画布上显示预览图像"""
        try:
            # 调整图像大小以适应画布
            canvas_width = self.canvas.winfo_width() or 400
            canvas_height = self.canvas.winfo_height() or 400
            
            img_width, img_height = image.size
            scale = min(canvas_width / img_width, canvas_height / img_height, 1.0)  # 最大缩放到适合画布
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # 调整图像大小
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为PhotoImage
            photo = ImageTk.PhotoImage(resized_image)
            
            # 清空画布
            self.canvas.delete("all")
            
            # 计算居中位置
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            
            # 在画布上显示图像
            self.canvas.create_image(x, y, anchor=tk.NW, image=photo)
            
            # 保持对PhotoImage的引用，防止被垃圾回收
            # 使用实例变量来保持引用
            self.last_preview_image = photo
            
        except Exception as e:
            print(f"显示预览图像时出错: {str(e)}")


def main():
    root = tk.Tk()
    app = ImagePreviewTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()