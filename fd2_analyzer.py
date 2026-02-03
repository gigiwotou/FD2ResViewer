import struct
import os
from typing import List, Optional
from main import Main, DataBlock, ColorPanel

class FD2Analyzer(Main):
    """扩展的FD2资源分析器"""
    
    def __init__(self):
        super().__init__()
        self.shapFileDatas = None
        
        # C#源码中的wordList数组
        self.wordList = [
            "０", "１", "２", "３", "４", "５", "６", "７", "８", "９",
            "Ａ", "Ｂ", "Ｃ", "Ｄ", "Ｅ", "Ｆ", "Ｇ", "Ｈ", "Ｉ", "Ｊ",
            "Ｋ", "Ｌ", "Ｍ", "Ｎ", "Ｏ", "Ｐ", "Ｑ", "Ｒ", "Ｓ", "Ｔ",
            "Ｕ", "Ｖ", "Ｗ", "Ｘ", "Ｙ", "Ｚ", "索", "爾", "哈", "諾",
            "鉄", "瓦", "特", "亞", "雷", "斯", "洛", "娜", "萊", "汀",
            "蘭", "希", "莉", "悠", "妮", "瑪", "琳", "菲", "凱", "麗",
            "貝", "克", "威", "珊", "塞", "可", "邦", "勒", "拉", "米",
            "多", "德", "蜜", "蒂", "羅", "曼", "莎", "約", "拿", "卡",
            "里", "法", "謝", "聖", "寇", "巴", "西", "達", "齊", "梅",
            "吉", "蓋", "渥", "士", "兵", "騎", "傭", "豹", "人", "精",
            "靈", "龍", "惡", "魔", "英", "戰", "鎧", "甲", "武", "黑",
            "暗", "狂", "突", "擊", "地", "獄", "弓", "箭", "手", "射",
            "狙", "師", "巫", "僧", "侶", "大", "祭", "盜", "賊", "頭",
            "目", "影", "之", "忍", "者", "殺", "術", "家", "鬥", "獸",
            "隊", "長", "火", "鬼", "機", "光", "束", "砲", "座", "守",
            "衛", "那", "薩", "沼", "澤", "怪", "物", "神", "水", "風",
            "空", "女", "村", "民", "男", "納", "恩", "三", "世", "類",
            "族", "械", "元", "素", "其", "他", "劍", "雄", "召", "喚",
            "？", "", "短", "闊", "巨", "斬", "流", "炎", "小", "刀",
            "匕", "首", "淬", "毒", "護", "刺", "矛", "槍", "戟", "先",
            "鋒", "馬", "黃", "金", "破", "斧", "迴", "旋", "鎚", "血",
            "閃", "電", "暴", "力", "量", "封", "棍", "釘", "槤", "枷",
            "杖", "咒", "指", "套", "爪", "皇", "帝", "環", "殭", "屍",
            "碎", "岩", "鋼", "裂", "刃", "臂", "衝", "炮", "拳", "利",
            "觸", "激", "牙", "焰", "波", "震", "戒", "勇", "徽", "章",
            "契", "印", "領", "悟", "書", "心", "眼", "白", "生", "命",
            "實", "晶", "羽", "十", "字", "鞭", "天", "鑰", "傳", "送",
            "修", "理", "件", "冰", "", "", "布", "衣", "旅", "行",
            "裝", "披", "體", "皮", "硬", "夜", "潛", "服", "袐", "狀",
            "鎖", "子", "鱗", "連", "合", "銀", "重", "袍", "司", "霧",
            "道", "妖", "殊", "青", "色", "虛", "無", "王", "薬", "草",
            "回", "復", "劑", "再", "解", "退", "麻", "耐", "速", "度",
            "綠", "寳", "石", "紅", "藍", "鑽", "飛", "卵", "粒", "控",
            "制", "中", "樞", "星", "要", "記", "錄", "況", "嗎", "已",
            "被", "了", "！", "是", "麽", "就", "不", "·", "讀", "取",
            "請", "稍", "等", "離", "開", "場", "休", "息", "吧", "決",
            "定", "軍", "全", "發", "進", "結", "本", "的", "動", "好",
            "，", "現", "箱", "打", "具", "滿", "交", "換", "把", "放",
            "去", "起", "惜", "藏", "挖", "掘", "得", "到", "從", "敵",
            "身", "上", "丟", "棄", "壞", "在", "伍", "似", "乎", "沒",
            "有", "以", "備", "喔", "您", "錢", "夠", "歡", "迎", "臨",
            "需", "什", "烈", "落", "轟", "彈", "治", "療", "攻", "防",
            "禦", "祛", "施", "庳", "淒", "煌", "熾", "音", "使", "邪",
            "完", "畢", "能", "由", "商", "店", "内", "增", "加", "效",
            "果", "消", "失", "性", "痲", "痹", "作", "減", "少", "點",
            "經", "驗", "級", "升", "酒", "器", "出", "口", "教", "會",
            "呃", "買", "東", "這", "個", "啊", "還", "帶", "賣", "給",
            "誰", "呢", "入", "<", "<", "儲", "存", ">", ">", "第",
            "二", "四", "五", "六", "七", "八", "九", "一", ")", "孤",
            "島", "鎮", "往", "途", "前", "普", "茲", "港", "城", "抉",
            "擇", "洞", "窟", "幻", "森", "林", "北", "山", "平", "原",
            "湖", "與", "遙", "遠", "彼", "岸", "死", "亡", "般", "沈",
            "寂", "述", "古", "呼", "向", "方", "焰", "審", "判", "未",
            "知", "廊", "運", "探", "邊", "說", "終", "事", "學", "須",
            "活", "轉", "職", "成", "業", "移", "滅", "市", "密", "外",
            "或", "毀", "除", "系", "統", "必", "確", "값", "『", "累",
            "下", "』", "聼", "越", "過", "片", "海", "洋", "陸", "我",
            "們", "此", "兒", "漲", "潮", "適", "時", "候", "船", "夫",
            "來", "接", "。", "極", "妳", "..", "嗯", "坐", "久", "吹",
            "真", "舒", "瞧", "竟", "呆", "鳥", "掉", "肥", "肉", "嘛",
            "俺", "通", "報", "老", "支", "援", "你", "趕", "快", "些",
            "伙", "擺", "群", "傢", "裡", "叫", "嘿", "像", "提", "耶",
            "搶", "劫", "豈", "止", "而", "批", "橫", "沿", "貨", "所",
            "為", "架", "奉", "陪", "門", "都", "筋", "骨", "問", "題",
            "癢", "難", "熬", "受", "啦", "喂", "乖", "財", "和", "漂",
            "亮", "妞", "面", "話", "保", "然", "亂", "宰", "呀", "看",
            "想", "抵", "抗", "赦", "吵", "底", "搞", "爸", "待", "客",
            "居", "膽", "該", "怎", "辦", "絕", "佳", "歷", "練", "幫",
            "忙", "幹", "若", "傷", "別", "湊", "熱", "閙", "緊", "張",
            "用", "著", "哎", "意", "也", "幾", "句", "樣", "如", "聲",
            "年", "輕", "咦", "弟", "兄", "陷", "苦", "收", "拾", "勞",
            "怕", "笑", "哼", "又", "概", "總", "算", "對", "處", "付",
            "種", "煩", "當", "非", "莫", "屬", "讓", "朋", "友", "喜",
            "孩", "逞", "胡", "兩", "後", "遲", "滾", "討", "厭", "很",
            "兇", "正", "建", "功", "良", "今", "國", "巡", "肆", "虐",
            "責", "各", "位", "扯", "高", "興", "才", "攪", "局", "踏",
            "盤", "至", "氣", "關", "係", "屋", "裏", "擋", "敢", "砍",
            "拼", "恨", "日", "碰", "棘", "遇", "爹", "公", "順", "敗",
            "住", "偶", "遊", "常", "閒", "倒", "求", "望", "同", "見",
            "識", "番", "相", "信", "伴", "路", "比", "較", "太", "招",
            "危", "協", "間", "差", "準", "拜", "託", "走", "囉", "奈",
            "野", "捏", "最", "繁", "榮", "歇", "便", "情", "誤", "半",
            "次", "強", "逃", "清", "楚", "助", "唉", "毛", "做", "窮",
            "團", "預", "告", "洗", "糟", "照", "准", "留", "猖", "訓",
            "頓", "悔", "改", "贊", "既", "玩", "早", "勁", "漏", "網",
            "魚", "救", "分", "管", "辜", "南", "思", "棒", "哪", "蹦",
            "丫", "剛", "直", "躲", "戲", "姐", "只", "應", "醫", "憶",
            "症", "並", "且", "她", "簡", "單", "撿", "找", "雖", "但",
            "甚", "某", "主", "因", "設", "渡", "奇", "附", "條", "盡",
            "跟", "恐", "楣", "哥", "何", "險", "操", "份", "負", "添",
            "哇", "橋", "聞", "名", "賽", "追", "仇", "自", "己", "蠻",
            "講", "認", "親", "：", "令", "訴", "葛", "胸", "狹", "窄",
            "禁", "爭", "奪", "蘿", "秘", "遺", "憾", "愛", "聚", "避",
            "究", "安", "葬", "罷", "土", "證", "隨", "反", "副", "故",
            "罕", "嫌", "剩", "碗", "糕", "抄", "近", "隱", "干", "屁",
            "礙", "錯", "偷", "襲", "嗷", "嗚", "吼", "趣", "呵", "夢",
            "莊", "侵", "犯", "視", "吃", "厲", "害", "低", "酬", "緻",
            "數", "庇", "遭", "罰", "規", "替", "及", "～", "甘", "代",
            "表", "致", "答", "否", "任", "樂", "免", "病", "曾", "陣",
            "據", "肢", "疾", "產", "響", "嘎", "超", "步", "急", "另",
            "試", "賢", "部", "廣", "寧", "互", "顧", "妥", "瘋", "邏",
            "站", "抱", "歉", "艾", "迪", "·", "沙", "夥", "維", "跑",
            "擒", "派", "抓", "逮", "捕", "緝", "拒", "格", "勿", "論",
            "嘍", "撐", "匪", "徒", "技", "嘗", "切", "--", "史", "境",
            "調", "查", "肯", "釋", "樁", "蹤", "嚴", "碼", "熟", "陰",
            "謀", "立", "刻", "委", "趟", "怨", "投", "擔", "啓", "程",
            "弄", "詭", "計", "拖", "延", "勉", "姑", "娘", "覺", "臉",
            "養", "月", "毆", "駐", "罪", "明", "瞄", "圍", "睜", "欺",
            "陛", "諒", "銳", "睡", "包", "嚇", "跳", "願", "考", "慮",
            "透", "露", "愁", "宜", "魄", "更", "堡", "癡", "禮", "後",
            "擁", "「", "淚", "」", "飾", "殿", "鑒", "餘", "吩", "咐",
            "黨", "違", "律", "捨", "逆", "遵", "冒", "變", "父", "宮",
            "勢", "混", "容", "仍", "忠", "誓", "借", "聰", "撤", "唔",
            "寢", "幸", "驚", "侍", "罵", "倖", "於", "揚", "言", "床",
            "搜", "疑", "例", "惹", "臣", "荒", "謬", "持", "臥", "佈",
            "勾", "將", "叛", "奸", "騙", "贖", "房", "忽", "慘", "省",
            "供", "瀑", "晚", "擄", "僞", "稱", "假", "義", "號", "籍",
            "忱", "憂", "愚", "昧", "遞", "監", "痛", "幕", "盡", "萬",
            "憑", "譽", "努", "承", "纏", "卒", "饒", "綁", "、", "端",
            "車", "匙", "悶", "祖", "它", "逼", "拷", "執", "掌", "料",
            "舊", "併", "貢", "獻", "虔", "誠", "阻", "感", "脅", "瘦",
            "充", "裕", "初", "異", "議", "排", "諸", "繼", "續", "段",
            "氛", "景", "頗", "陌", "妨", "智", "卻", "隔", "壁", "穆",
            "迷", "籠", "罩", "誡", "千", "界", "伺", "趁", "賴", "驅",
            "童", "囑", "鄉", "停", "嚮", "導", "額", "瞭", "唆", "咱",
            "咋", "談", "它", "警", "龐", "集", "營", "袖", "旁", "觀",
            "恙", "花", "紀", "巧", "囤", "宣", "戮", "殆", "仰", "翻",
            "典", "型", "殲", "隻", "癮", "藝", "醒", "猴", "注", "堆",
            "笨", "蛋", "務", "率", "熊", "背", "模", "欠", "揍", "妙",
            "雜", "足", "永", "恒", "攜", "貴", "引", "繞", "價", "聊",
            "仗", "漢", "縱", "屠", "兼", "囂", "冷", "慣", "溫", "暖",
            "習", "徵", "兆", "易", "新", "志", "費", "工", "鍛", "煉",
            "輩", "醉", "辭", "惋", "泛", "倚", "獨", "耗", "置", "尋",
            "察", "許", "采", "輸", "揮", "佩", "閣", "舉", "敬", "尊",
            "咈", "欣", "賞", "滋", "味", "美", "貌", "驕", "傲", "折",
            "霸", "愧", "圖", "浩", "勝", "迢", "形", "賤", "唯", "謎",
            "畫", "挑", "細", "迫", "懷", "穴", "；", "掙", "脫", "繩",
            "昇", "恰", "邀", "漠", "態", "期", "乾", "脆", "恥", "筆",
            "帳", "禿", "偏", "僻", "靜", "吊", "岳", "頂", "構", "築",
            "票", "績", "卓", "益", "獲", "豐", "厚", "紋", "骷", "髏",
            "昭", "彰", "專", "掠", "賺", "腥", "剿", "聯", "左", "右",
            "夾", "插", "翅", "造", "則", "涉", "案", "嘆", "歲", "靠",
            "奮", "敍", "崖", "脈", "麓", "濃", "陽", "損", "魂", "散",
            "標", "蛛", "絲", "跡", "塔", "源", "線", "積", "吞", "食",
            "咬", "凡", "摸", "貫", "謹", "慎", "佑", "深", "遣", "陷",
            "百", "旦", "佔", "堪", "覆", "介", "周", "嘎", "吱", "哩",
            "喀", "嚕", "懂", "語", "刑", "乘", "牽", "式", "拯", "俘",
            "虜", "俊", "傑", "雇", "博", "降", "虧", "貪", "根", "汗",
            "頑", "傻", "瓜", "哦", "音", "疏", "善", "液", "肩", "旨",
            "謂", "館", "研", "籍", "載", "顆", "限", "始", "斷", "串",
            "暫", "揣", "測", "即", "蘊", "含", "闇", "、", "逐", "袛",
            "履", "予", "忘", "伊", "麾", "配", "創", "扁", "崇", "牢",
            "卑", "蟲", "蟻", "徹", "整", "犧", "牲", "抛", "慧", "濟",
            "堂", "潰", "擾", "嵌", "慶", "毫", "跋", "廢", "墟", "叔",
            "母", "健", "淡", "哟", "央", "洲", "瞞", "篇", "嘩", "閉",
            "仔", "丘", "災", "厄", "懼", "歸", "沖", "昏", "庭", "衆",
            "妹", "疆", "欲", "困", "煙", "雲", "諭", "擅", "姿", "誇",
            "讚", "蹺", "班", "穩", "象", "熄", "棲", "曉", "域", "谷",
            "腳", "踹", "眠", "私", "爛", "摔", "峙", "債", "富", "緣",
            "熔", "企", "爆", "穿", "禍", "析", "盒", "示", "01", "E0",
            "C2", "44", "-F", "E2", "C5", "19", "32", "27", "99", "43",
            "資", "訊", "哭", "鼓", "庫", "#7", "33", "24", "隸", "#2",
            "07", "42", "13", "x-", "區", "參", "壘", "壓", "粗", "魯",
            "惑", "僅", "AS", "R-", "台", "秒", "御", "炸", "障", "檢",
            "甦", "悲", "哀", "珍", "7-", "-3", "62", "10", "73", "辦",
            "序", "權", "A1", "1-", "72", "洪", "痕", "抹", "福", "文",
            "冶", "C-", "77", "-0", "3-", "複", "採", "02", "湧", "核",
            "嘻", "03", "70", "51", "88", "銷", "摧", "拐", "暈", "爐",
            "怖", "埋", "伏", "螻", "球", "06", "暨", "優", "握", "腦",
            "蓄", "荷", "扭", "曲", "喪", "膩", "劈", "磁", "偉", "蹈",
            "轍", "凶", "展", "化", "製", "版", "共", "傾", "痊", "癒",
            "吟", "唱", "撕", "燃", "燒", "灰", "抬", "選", "末", "微",
            "鑄", "贏", "雙", "項", "衰", "殘", "糊", "訊", "伶", "飄",
            "盪", "寞", "堅", "缺", "劇", "跌", "刹", "園", "踩", "涼",
            "爽", "喣", "盛", "宴", "祝", "喝", "杯", "圓", "訪", "鬆",
            "廬", "姓", "默", "衷", "宿", "艱", "倆", "舶", "嶼", "浪",
            "涯", "彌", "雀", "躍", "紹", "孜", "李", "晨", "允", "婚",
            "浮", "艙", "嬌", "恃", "壇", "柔", "祈", "禱", "蜇", "遷",
            "惦", "念", "掀", "瀾", "悄", "嘴", "返", "員", "基", "課",
            "品", "愉", "愜", "旺", "昌", "節", "紛", "恢", "誼", "繫",
            "廷", "奔", "每", "磨", "躺", "矖", "芳", "航", "顯", "稟",
            "晉", "朕", "祉", "－", "君", "弱", "馳", "撫", "瞌", "枉",
            "瑣", "政", "官", "枯"
        ]
        
    def extract_text_content(self, main_index):
        """提取指定主索引的文本内容"""
        try:
            text_parts = []
            # 修复变量名不一致的问题
            if main_index < len(self.subBlockCountsTXT):
                sub_block_count = self.subBlockCountsTXT[main_index]
            else:
                sub_block_count = 0
            
            for j in range(sub_block_count):
                if main_index < len(self.datablocksTXT) and j < len(self.datablocksTXT[main_index]):
                    if self.datablocksTXT[main_index][j]:
                        block = self.datablocksTXT[main_index][j]
                        start_offset = block.startOffset
                        length = block.length
                        
                        # 确保偏移量和长度有效
                        if start_offset >= 0 and length > 0 and self.fileDatas is not None and start_offset + length <= len(self.fileDatas):
                            # 使用makeWord函数解析文本
                            try:
                                parsed_text = self.makeWord(self.fileDatas, start_offset, int(length / 2 - 1))
                                if parsed_text:
                                    text_parts.append(f"[SubIndex {j}]\n{parsed_text}\n")
                            except Exception as e:
                                print(f"解析主索引{main_index}子索引{j}时出错: {e}")
                        
            return "\n".join(text_parts)
        except Exception as e:
            print(f"提取主索引{main_index}的文本内容时出错: {e}")
            return ""

    def makeWord(self, datablock, startOffset, length):
        """根据C#源码实现的makeWord函数"""
        text = ""
        # 根据C#源码，实际长度需要减去1
        actual_length = length - 1
        
        i = 0
        while i <= actual_length:
            # 从数据中读取一个short值（2字节）
            if startOffset + i * 2 + 2 <= len(datablock):
                # 使用little-endian格式解析short值
                num5 = struct.unpack('<h', datablock[startOffset + i * 2:startOffset + i * 2 + 2])[0]
            else:
                break
                
            # 根据C#源码的switch语句处理
            if num5 == -17 or num5 == -18:
                # 处理人物姓名引用
                i += 1
                if startOffset + i * 2 + 2 <= len(datablock):
                    name_index = struct.unpack('<h', datablock[startOffset + i * 2:startOffset + i * 2 + 2])[0]
                    # 这里应该引用FD2CharacterNames数组，但为了测试我们使用占位符
                    # 在实际使用中，FD2CharacterNames数组会在解析过程中被填充
                    text += f"[CHARACTER_{name_index}]:"
                else:
                    break
            else:
                if num5 >= 0:
                    # 正数索引，从wordList获取字符
                    if num5 < len(self.wordList):
                        text += self.wordList[num5]
                    else:
                        # 如果索引超出范围，添加占位符
                        text += f"[CHAR_{num5}]"
                elif num5 < 0:
                    # 负数表示换行
                    text += "\r\n"
            
            i += 1
            
        return text

    def analyze_file(self, file_path):
        """根据文件名自动选择合适的分析方法"""
        file_name = os.path.basename(file_path).lower()
        
        if 'fdother.dat' in file_name:
            print('分析FDOTHER.DAT文件...')
            self.load_fdother_file(file_path)
        elif 'fdicon.b24' in file_name:
            print('分析FDICON.B24文件...')
            self.load_fdicon_file(file_path)
        elif 'dato.dat' in file_name:
            print('分析DATO.DAT文件...')
            self.load_dato_file(file_path)
        elif 'bg.dat' in file_name:
            print('分析BG.DAT文件...')
            self.load_bg_file(file_path)
        elif 'fdtxt.dat' in file_name:
            print('分析FDTXT.DAT文件...')
            self.load_fdtxt_file(file_path)
        elif 'tai.dat' in file_name:
            print('分析TAI.DAT文件...')
            self.load_tai_file(file_path)
        elif 'figani.dat' in file_name:
            print('分析FIGANI.DAT文件...')
            self.load_figani_file(file_path)
        elif 'fdshap.dat' in file_name:
            print('分析FDSHAP.DAT文件...')
            self.load_fdshap_file(file_path)
        elif 'fdfield.dat' in file_name:
            print('分析FDFIELD.DAT文件...')
            self.load_fdfield_file(file_path)
        elif 'ani.dat' in file_name:
            print('分析ANI.DAT文件...')
            self.load_ani_file(file_path)
        else:
            print(f'暂不支持的文件类型: {file_name}')
            print('当前支持的文件类型:')
            print('- FDOTHER.DAT (混合资源)')
            print('- FDICON.B24 (人物图标)')
            print('- DATO.DAT (人物表情)')
            print('- BG.DAT (战斗背景)')
            print('- FDTXT.DAT (文本资源)')
            print('- TAI.DAT (战斗动作图像)')
            print('- FIGANI.DAT (战斗动作序列)')
            print('- FDSHAP.DAT (形状资源)')
            print('- FDFIELD.DAT (地图资源)')
            print('- ANI.DAT (动画资源)')
            return False
        return True
        
    def batch_analyze(self, directory):
        """批量分析目录中的所有支持文件"""
        supported_files = ['fdother.dat', 'fdicon.b24', 'dato.dat', 'bg.dat', 'fdtxt.dat', 'tai.dat', 'figani.dat', 'fdshap.dat', 'fdfield.dat', 'ani.dat']
        found_files = []
        
        for file in os.listdir(directory):
            if file.lower() in supported_files:
                found_files.append(os.path.join(directory, file))
        
        if not found_files:
            print(f'在目录 {directory} 中未找到支持的文件')
            return
            
        print(f'找到{len(found_files)}个支持的文件:')
        for file in found_files:
            print(f'  - {os.path.basename(file)}')
        
        for file in found_files:
            print(f'\n开始处理: {os.path.basename(file)}')
            if self.analyze_file(file):
                print(f'完成: {os.path.basename(file)}')
            else:
                print(f'失败: {os.path.basename(file)}')

    def load_fdicon_file(self, file_path):
        """分析FDICON.B24文件 - 人物图标"""
        print("分析FDICON.B24文件...")
        with open(file_path, 'rb') as f:
            self.fileDatas = f.read()
        
        self.AnalysisICON()
        print(f'FDICON分析完成，共{len(self.datablocksICON)}个图标')
        
        # 生成图标图像
        success_count = 0
        for i in range(len(self.datablocksICON)):
            # 检查数据块是否存在且有效
            data_block = self.datablocksICON[i]
            if data_block is not None and isinstance(data_block, DataBlock) and hasattr(data_block, 'length') and data_block.length is not None and data_block.length > 4:
                try:
                    image = self.bmp_maker.makeShapBMP(
                        24, 24,  # 图标固定大小24x24
                        self.fileDatas,
                        data_block.startOffset,
                        data_block.length,
                        ColorPanel(1)
                    )
                    image_path = os.path.join(self.output_dir, f'icon_{i:05d}.png')
                    image.save(image_path)
                    success_count += 1
                except Exception as e:
                    print(f'图标{i}处理失败: {e}')
        print(f'成功提取{success_count}个图标')
        
    def load_fdtxt_file(self, file_path):
        """分析FDTXT.DAT文件 - 文本资源"""
        print("分析FDTXT.DAT文件...")
        with open(file_path, 'rb') as f:
            self.fileDatas = f.read()
        
        self.AnalysisTXT()
        print(f'FDTXT分析完成，共{len(self.datablocksTXT)}个主分类')
        
        # 提取文本内容
        total_texts = 0
        for i in range(len(self.datablocksTXT)):
            # 修复变量名不一致的问题
            if i < len(self.subBlockCountsTXT):
                sub_block_count = self.subBlockCountsTXT[i]
            else:
                sub_block_count = 0
                
            if sub_block_count > 0:
                try:
                    # 创建文本输出目录
                    txt_output_dir = os.path.join(self.output_dir, 'fdtxt')
                    os.makedirs(txt_output_dir, exist_ok=True)
                    
                    # 生成文本文件
                    text_content = self.extract_text_content(i)
                    if text_content:
                        text_file_path = os.path.join(txt_output_dir, f'fdtxt_{i:04d}.txt')
                        with open(text_file_path, 'w', encoding='utf-8') as f:
                            f.write(text_content)
                        total_texts += 1
                        print(f'主分类{i}: 提取文本到 {text_file_path}')
                except Exception as e:
                    print(f'主分类{i}文本提取失败: {e}')
        
        print(f'成功提取{total_texts}个FDTXT文本文件')
                    
    def load_dato_file(self, file_path):
        """分析DATO.DAT文件 - 人物表情"""
        print("分析DATO.DAT文件...")
        with open(file_path, 'rb') as f:
            self.fileDatas = f.read()
        
        self.AnalysisDATO()
        print(f'DATO分析完成，共{len(self.datablocksDATO)}个数据块')
        
        # 生成表情图像
        success_count = 0
        for i in range(len(self.datablocksDATO)):
            for j in range(len(self.datablocksDATO[i])):
                # 检查数据块是否存在且有效
                if i < len(self.datablocksDATO) and j < len(self.datablocksDATO[i]):
                    data_block = self.datablocksDATO[i][j]
                    if data_block is not None and isinstance(data_block, DataBlock) and hasattr(data_block, 'length') and data_block.length is not None and data_block.length > 4:
                        try:
                            # 使用makeFaceBMP方法处理DATO文件，从数据中读取宽度和高度
                            image = self.bmp_maker.makeFaceBMP(
                                self.fileDatas,
                                data_block.startOffset,
                                data_block.length,
                                ColorPanel(1)
                            )
                            image_path = os.path.join(self.output_dir, f'dato_{i:05d}_{j:02d}.png')
                            image.save(image_path)
                            success_count += 1
                        except Exception as e:
                            print(f'DATO表情{i}-{j}处理失败: {e}')
        print(f'成功提取{success_count}个DATO表情')
        
    def load_bg_file(self, file_path):
        """分析BG.DAT文件 - 战斗背景"""
        print("分析BG.DAT文件...")
        with open(file_path, 'rb') as f:
            self.fileDatas = f.read()
        
        self.AnalysisBG()
        print(f'BG分析完成，共{len(self.datablocksBG)}个背景')
        
        # 生成背景图像
        success_count = 0
        for i in range(len(self.datablocksBG)):
            # 检查数据块是否存在且有效
            data_block = self.datablocksBG[i]
            if data_block is not None and isinstance(data_block, DataBlock) and hasattr(data_block, 'length') and data_block.length is not None and data_block.length > 4:
                try:
                    # 使用makeBgBMP方法处理BG文件，从数据中读取宽度和高度
                    image = self.bmp_maker.makeBgBMP(
                        self.fileDatas,
                        data_block.startOffset,
                        data_block.length,
                        ColorPanel(1)
                    )
                    image_path = os.path.join(self.output_dir, f'bg_{i:05d}.png')
                    image.save(image_path)
                    success_count += 1
                except Exception as e:
                    print(f'背景{i}处理失败: {e}')
        print(f'成功提取{success_count}个战斗背景')
        
    def load_tai_file(self, file_path):
        """分析TAI.DAT文件 - 战斗动作图像"""
        print("分析TAI.DAT文件...")
        with open(file_path, 'rb') as f:
            self.fileDatas = f.read()
        
        # 使用TAI专用的分析方法
        self.AnalysisTAI()  # TAI.DAT使用专用的索引结构分析方法
        print(f'TAI分析完成，共{len(self.datablocksTAI)}个数据块')
        
        # 生成图像
        success_count = 0
        for i in range(len(self.datablocksTAI)):
            # 检查数据块是否存在且有效
            data_block = self.datablocksTAI[i]
            if data_block is not None and isinstance(data_block, DataBlock) and hasattr(data_block, 'length') and data_block.length is not None and data_block.length > 4:
                try:
                    # 使用TAI专用的图像生成方法处理TAI文件，从数据中读取宽度和高度
                    image = self.bmp_maker.makeTAIBMP(
                        self.fileDatas,
                        data_block.startOffset,
                        data_block.length,
                        ColorPanel(1)
                    )
                    image_path = os.path.join(self.output_dir, f'tai_{i:05d}.png')
                    image.save(image_path)
                    success_count += 1
                except Exception as e:
                    print(f'TAI图像{i}处理失败: {e}')
        print(f'成功提取{success_count}个TAI图像')
        
    def load_figani_file(self, file_path):
        """分析FIGANI.DAT文件 - 战斗动作序列"""
        print("分析FIGANI.DAT文件...")
        with open(file_path, 'rb') as f:
            self.fileDatas = f.read()
        
        self.AnalysisFIGANI()
        print(f'FIGANI分析完成，共{len(self.datablocksFIGANI)}个主分类')
        
        # 生成动作序列图像
        total_sequences = 0
        for i in range(len(self.datablocksFIGANI)):
            # 修复变量名不一致的问题
            if i < len(self.subBlockCountsFIGANI):
                sub_block_count = self.subBlockCountsFIGANI[i]
            else:
                sub_block_count = 0
                
            if sub_block_count > 0:
                print(f'处理动作序列{i:04d}，包含{sub_block_count}帧')
                sequence_dir = os.path.join(self.output_dir, f'figani_{i:04d}')
                os.makedirs(sequence_dir, exist_ok=True)
                
                success_count = 0
                for j in range(sub_block_count):
                    # 检查数据块是否存在且有效
                    if i < len(self.datablocksFIGANI) and j < len(self.datablocksFIGANI[i]):
                        data_block = self.datablocksFIGANI[i][j]
                        if data_block is not None and isinstance(data_block, DataBlock) and hasattr(data_block, 'length') and data_block.length is not None and data_block.length > 4:
                            try:
                                # 使用makeFightBMP方法处理FIGANI文件，从数据中读取宽度和高度
                                image = self.bmp_maker.makeFightBMP(
                                    self.fileDatas,
                                    data_block.startOffset,
                                    data_block.length,
                                    ColorPanel(1)
                                )
                                image_path = os.path.join(sequence_dir, f'frame_{j:03d}.png')
                                image.save(image_path)
                                success_count += 1
                            except Exception as e:
                                print(f'FIGANI动作序列{i:04d}帧{j:03d}处理失败: {e}')
                print(f'  动作序列{i:04d}: 成功提取{success_count}帧')
                total_sequences += 1
        print(f'成功处理{total_sequences}个FIGANI动作序列')

    def load_fdother_file(self, file_path):
        """分析FDOTHER.DAT文件 - 混合资源"""
        print("分析FDOTHER.DAT文件...")
        with open(file_path, 'rb') as f:
            self.fileDatas = f.read()
        
        # 使用AnalysisOTHER和AnalysisOtherSubs进行文件分析
        self.AnalysisOTHER()
        print(f'FDOTHER分析完成，共{len(self.datablocksOTHER)}个主分类')
        
        # 处理所有子索引
        total_processed = 0
        for subIndex in range(len(self.datablocksOTHER)):
            try:
                self.AnalysisOtherSubs(subIndex)
                self.AnalysisOtherSubsImage(subIndex)
                total_processed += 1
                print(f'处理主分类{subIndex}完成')
            except Exception as e:
                print(f'处理主分类{subIndex}时出错: {e}')
        print(f'成功处理{total_processed}个FDOTHER主分类')

    def load_fdshap_file(self, file_path):
        """分析FDSHAP.DAT文件 - 形状资源"""
        print("分析FDSHAP.DAT文件...")
        with open(file_path, 'rb') as f:
            self.fileDatas = f.read()
            # 设置FDSHAP专用文件数据属性
            self.fileDatasFDSHAP = self.fileDatas
        
        # 使用AnalysisFDSHAP进行文件分析
        self.AnalysisFDSHAP()
        print(f'FDSHAP分析完成，共{len(self.datablocksFDSHAP)}个主分类')
        
        # 处理所有子索引并生成图像
        total_processed = 0
        success_count = 0
        
        # 创建FDSHAP输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        for main_index in range(len(self.datablocksFDSHAP)):
            try:
                if main_index < len(self.subBlockCountsFDSHAP):
                    sub_block_count = self.subBlockCountsFDSHAP[main_index]
                    if sub_block_count > 0:
                        # 为每个主分类创建单独的目录
                        main_class_dir = os.path.join(self.output_dir, f'fdshap_{main_index:03d}')
                        os.makedirs(main_class_dir, exist_ok=True)
                        
                        for sub_index in range(sub_block_count):
                            # 检查数据块是否存在且有效
                            if main_index < len(self.datablocksFDSHAP) and sub_index < len(self.datablocksFDSHAP[main_index]):
                                data_block = self.datablocksFDSHAP[main_index][sub_index]
                                if data_block is not None and isinstance(data_block, DataBlock) and hasattr(data_block, 'length') and data_block.length is not None and data_block.length > 4:
                                    try:
                                        # 使用固定的尺寸24x24，因为FDSHAP通常是固定尺寸的形状资源
                                        width, height = 24, 24
                                        
                                        # 确保尺寸在合理范围内
                                        if 1 <= width <= 1000 and 1 <= height <= 1000:
                                            # 使用makeShapBMP方法处理FDSHAP文件
                                            image = self.bmp_maker.makeShapBMP(
                                                width, height,
                                                self.fileDatas,
                                                data_block.startOffset,
                                                data_block.length,
                                                ColorPanel(1)
                                            )
                                            # 将图像保存到主分类的单独目录中
                                            image_path = os.path.join(main_class_dir, f'fdshap_{main_index:03d}_{sub_index:04d}.png')
                                            image.save(image_path)
                                            
                                            # 将生成的图像存储到shaps数组中，供FDFIELD使用
                                            if sub_index < len(self.shaps):
                                                self.shaps[sub_index] = image
                                            
                                            success_count += 1
                                    except Exception as e:
                                        print(f'FDSHAP主分类{main_index}子索引{sub_index}图像生成失败: {e}')
                total_processed += 1
                print(f'处理主分类{main_index}完成')
            except Exception as e:
                print(f'处理主分类{main_index}时出错: {e}')
        
        # 设置shapsDone标志，表示图块图像已生成完成
        self.shapsDone = True
        print(f'成功处理{total_processed}个FDSHAP主分类，生成{success_count}个图像文件')

    def load_fdfield_file(self, file_path):
        """分析FDFIELD.DAT文件 - 地图资源"""
        print("分析FDFIELD.DAT文件...")
        with open(file_path, 'rb') as f:
            self.fileDatas = f.read()
        
        # 使用AnalysisFDFIELD进行文件分析
        self.AnalysisFDFIELD()
        print(f'FDFIELD分析完成，共{len(self.datablocksFDFIELD)}个主分类')
        
        # 生成地图图像
        success_count = 0
        for i in range(len(self.datablocksFDFIELD)):
            # 检查数据块是否存在且有效
            data_block = self.datablocksFDFIELD[i]
            if data_block is not None and isinstance(data_block, DataBlock) and hasattr(data_block, 'length') and data_block.length is not None and data_block.length > 4:
                try:
                    # 确保在生成地图图像之前已经加载了FDSHAP文件
                    if not self.shapsDone:
                        print("错误: 生成地图图像前需要先分析FDSHAP.DAT文件!")
                        return
                    
                    # 使用makeFieldBMP方法处理FDFIELD文件
                    image = self.bmp_maker.makeFieldBMP(
                        self.fileDatas,
                        i,
                        data_block.startOffset,
                        data_block.length,
                        ColorPanel(1)
                    )
                    image_path = os.path.join(self.output_dir, f'fdfield_{i:05d}.png')
                    image.save(image_path)
                    success_count += 1
                except Exception as e:
                    print(f'地图{i}处理失败: {e}')
        print(f'成功提取{success_count}个地图图像')

    def load_ani_file(self, file_path):
        """分析ANI.DAT文件 - 动画资源"""
        print("分析ANI.DAT文件...")
        with open(file_path, 'rb') as f:
            self.fileDatas = f.read()
        
        # 使用AnalysisANI进行文件分析
        self.AnalysisANI()
        print(f'ANI分析完成，共{len(self.datablocksANI)}个主分段')
        
        # 生成动画图像
        total_sequences = 0
        for i in range(len(self.datablocksANI)):  # 9个主分段
            # 修复变量名不一致的问题
            if i < len(self.subBlockCountsANI):
                sub_block_count = self.subBlockCountsANI[i]
            else:
                sub_block_count = 0
                
            if sub_block_count > 0:
                print(f'处理动画分段{i:02d}，包含{sub_block_count}个子段')
                ani_dir = os.path.join(self.output_dir, f'ani_segment_{i:02d}')
                os.makedirs(ani_dir, exist_ok=True)
                
                success_count = 0
                for j in range(sub_block_count):
                    # 检查数据块是否存在且有效
                    if i < len(self.datablocksANI) and j < len(self.datablocksANI[i]):
                        data_block = self.datablocksANI[i][j]
                        if data_block is not None and isinstance(data_block, DataBlock) and hasattr(data_block, 'length') and data_block.length is not None and data_block.length > 4:
                            try:
                                # 使用新的ANI专用方法生成图像
                                # 传递整个数据块给方法，它会从正确位置读取宽度、高度和数据
                                image = self.bmp_maker.makeANIBMP(
                                    self.fileDatas,
                                    data_block.startOffset,  # 从数据块开始位置
                                    data_block.length,     # 整个数据块长度
                                    ColorPanel(1)
                                )
                                
                                image_path = os.path.join(ani_dir, f'frame_{j:03d}.png')
                                image.save(image_path)
                                success_count += 1
                                
                                # 获取图像尺寸用于显示
                                width, height = image.size
                                print(f'  ANI动画分段{i:02d}帧{j:03d}处理成功: {width}x{height}')
                            except Exception as e:
                                print(f'ANI动画分段{i:02d}帧{j:03d}处理失败: {e}')
                                # 尝试更安全的方式，仅保存原始数据到临时文件
                                try:
                                    # 保存原始数据块以便分析
                                    raw_data_path = os.path.join(ani_dir, f'raw_frame_{j:03d}.bin')
                                    with open(raw_data_path, 'wb') as raw_file:
                                        raw_file.write(self.fileDatas[data_block.startOffset:data_block.startOffset+data_block.length])
                                except:
                                    pass  # 忽略保存原始数据的错误
                print(f'  动画分段{i:02d}: 成功提取{success_count}帧')
                total_sequences += 1
        print(f'成功处理{total_sequences}个ANI动画分段')

def main():

    """主函数，支持命令行参数解析"""
    import argparse
    import os
    import sys
    
    parser = argparse.ArgumentParser(description='炎龙骑士团II资源文件分析器')
    parser.add_argument('file', nargs='?', help='要分析的资源文件路径')
    parser.add_argument('-b', '--batch', help='批量分析目录中的所有支持文件')
    parser.add_argument('-o', '--output', default='output_images', help='输出目录路径')
    
    args = parser.parse_args()
    
    # 创建分析器实例
    analyzer = FD2Analyzer()
    analyzer.output_dir = args.output
    os.makedirs(analyzer.output_dir, exist_ok=True)
    
    if args.batch:
        # 批量分析模式
        if os.path.isdir(args.batch):
            analyzer.batch_analyze(args.batch)
        else:
            print(f"错误: 目录 '{args.batch}' 不存在")
            sys.exit(1)
    elif args.file:
        # 单文件分析模式
        if os.path.isfile(args.file):
            analyzer.analyze_file(args.file)
        else:
            print(f"错误: 文件 '{args.file}' 不存在")
            sys.exit(1)
    else:
        # 显示帮助信息
        parser.print_help()


if __name__ == '__main__':
    main()
