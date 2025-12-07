import folium
from folium import plugins
from folium.features import DivIcon

# ==========================================
# 1. 样式定义 (Styles)
# ==========================================
# 颜色映射：威胁=红, 关隘=橙, 枢纽=黄, 核心=绿, 水系=蓝, 基地=灰
STYLES = {
    "THREAT": {"color": "#d32f2f", "icon": "fire", "size": (30, 30)},       # 红色：威胁源头
    "PASS":   {"color": "#f57c00", "icon": "shield", "size": (25, 25)},     # 橙色：防御关隘
    "HUB":    {"color": "#fbc02d", "icon": "crosshairs", "size": (20, 20)}, # 黄色：战略枢纽
    "CORE":   {"color": "#2e7d32", "icon": "star", "size": (25, 25)},       # 绿色：核心/首都
    "WATER":  {"color": "#0288d1", "icon": "tint", "size": (20, 20)},       # 蓝色：水系防线
    "BASE":   {"color": "gray",    "icon": "map-marker", "size": (15, 15)}  # 灰色：普通重镇
}

# ==========================================
# 2. 地理数据 (中文)
# ==========================================
LOCATIONS = {
    # --- 北方威胁 (Threats) ---
    "Mongolia":  {"name": "蒙古高原/匈奴", "coords": [44.0, 111.0], "type": "THREAT"},
    "Manchuria": {"name": "辽东/女真/后金", "coords": [41.8, 123.4], "type": "THREAT"},
    "Xiyu":      {"name": "西域", "coords": [40.0, 94.0], "type": "THREAT"},

    # --- 西北防线 ---
    "Wuwei":    {"name": "武威", "coords": [37.9, 102.6], "type": "BASE"},
    "Zhangye":  {"name": "张掖", "coords": [38.9, 100.4], "type": "BASE"},
    "Hexi":     {"name": "河西走廊", "coords": [38.5, 101.5], "type": "HUB"},
    "Longxi":   {"name": "陇西", "coords": [35.5, 104.6], "type": "HUB"},
    "Hetao":    {"name": "河套平原", "coords": [40.8, 107.5], "type": "THREAT"}, # 战略跳板

    # --- 山西/京师防线 ---
    "Datong":   {"name": "大同 (云州)", "coords": [40.07, 113.3], "type": "HUB"},
    "Daizhou":  {"name": "代州", "coords": [39.08, 112.95], "type": "BASE"},
    "Yanmen":   {"name": "雁门关", "coords": [39.18, 112.88], "type": "PASS"},
    "Ningwu":   {"name": "宁武关", "coords": [39.00, 112.30], "type": "PASS"},
    "Piantou":  {"name": "偏头关", "coords": [39.43, 111.48], "type": "PASS"},
    "Taiyuan":  {"name": "太原", "coords": [37.87, 112.54], "type": "CORE"},

    "Liaoxi":   {"name": "辽西走廊", "coords": [40.8, 120.5], "type": "HUB"},
    "Xuanfu":   {"name": "宣府", "coords": [40.81, 114.88], "type": "HUB"},
    "Juyong":   {"name": "居庸关", "coords": [40.28, 116.06], "type": "PASS"},
    "Shanhai":  {"name": "山海关", "coords": [40.00, 119.75], "type": "PASS"},
    "LiaodongPlain": {"name": "辽东平原", "coords": [41.2, 122.5], "type": "BASE"},

    # --- 核心屏障 ---
    "Hedong":    {"name": "河东 (表里山河)", "coords": [36.5, 111.5], "type": "HUB"},
    "Guanzhong": {"name": "关中 (四塞之国)", "coords": [34.3, 108.9], "type": "CORE"},
    "NorthMts":  {"name": "北山山脉", "coords": [35.5, 108.5], "type": "PASS"},
    "Hangu":     {"name": "函谷关/潼关", "coords": [34.61, 110.36], "type": "PASS"},
    "Beijing":   {"name": "北京/幽州", "coords": [39.90, 116.40], "type": "CORE"},

    # --- 中原与交通 ---
    "CentralPlains": {"name": "中原", "coords": [34.7, 113.6], "type": "CORE"},
    "Qinling":       {"name": "秦岭/蜀道", "coords": [33.5, 107.5], "type": "PASS"},
    "Hanzhong":      {"name": "汉中", "coords": [33.07, 107.02], "type": "HUB"},

    # --- 南方防线 ---
    "Bashu":     {"name": "巴蜀", "coords": [30.6, 104.0], "type": "CORE"},
    "Diaoyu":    {"name": "钓鱼城", "coords": [30.0, 106.27], "type": "PASS"},
    "Nanyang":   {"name": "南阳", "coords": [33.0, 112.5], "type": "BASE"},
    "Xiangyang": {"name": "襄阳 (腰脊)", "coords": [32.01, 112.12], "type": "HUB"},
    "Jiangling": {"name": "江陵 (荆州)", "coords": [30.35, 112.19], "type": "HUB"},
    "Ezhou":     {"name": "鄂州", "coords": [30.54, 114.30], "type": "BASE"},
    "Jianghuai": {"name": "江淮", "coords": [32.5, 117.0], "type": "HUB"},
    "HuaiRiver": {"name": "淮河防线", "coords": [32.9, 116.0], "type": "WATER"},
    "HuaiForts": {"name": "淮河重镇", "coords": [32.0, 116.8], "type": "BASE"},
    "Zhenjiang": {"name": "镇江 (京口)", "coords": [32.2, 119.45], "type": "PASS"},
    "Yangtze":   {"name": "长江天险", "coords": [30.5, 117.0], "type": "WATER"},
    "Jiangnan":  {"name": "江南/南京", "coords": [31.5, 120.0], "type": "CORE"},
}

# 连线类型:
# ATTACK = 红色, 动画流动 (进攻/南下)
# STRATEGY = 灰色, 静态/虚线 (战略控制/补给)
# WATER = 蓝色, 动画流动 (水路)
EDGES = [
    # 西北线
    ("Xiyu", "Wuwei", "STRATEGY"), ("Wuwei", "Zhangye", "STRATEGY"), ("Zhangye", "Hexi", "STRATEGY"),
    ("Hexi", "Longxi", "ATTACK"), ("Longxi", "Guanzhong", "ATTACK"),
    ("Mongolia", "Hetao", "ATTACK"), ("Hetao", "NorthMts", "ATTACK"), ("NorthMts", "Guanzhong", "ATTACK"),

    # 山西线
    ("Mongolia", "Datong", "ATTACK"), ("Datong", "Daizhou", "ATTACK"),
    ("Daizhou", "Yanmen", "ATTACK"), ("Daizhou", "Ningwu", "ATTACK"), ("Daizhou", "Piantou", "ATTACK"),
    ("Yanmen", "Taiyuan", "STRATEGY"), ("Taiyuan", "Hedong", "STRATEGY"),
    ("Hedong", "Guanzhong", "ATTACK"), ("Hedong", "CentralPlains", "ATTACK"), ("Hedong", "Beijing", "STRATEGY"),

    # 东北线 (辽东-北京)
    ("Manchuria", "LiaodongPlain", "ATTACK"), ("LiaodongPlain", "Liaoxi", "STRATEGY"),
    ("Liaoxi", "Shanhai", "ATTACK"), ("Shanhai", "Beijing", "ATTACK"),
    ("Mongolia", "Xuanfu", "ATTACK"), ("Xuanfu", "Juyong", "ATTACK"), ("Juyong", "Beijing", "ATTACK"),

    # 中原枢纽
    ("Guanzhong", "Hangu", "STRATEGY"), ("Hangu", "CentralPlains", "STRATEGY"), ("Beijing", "CentralPlains", "STRATEGY"),

    # 西翼 (四川)
    ("Guanzhong", "Qinling", "STRATEGY"), ("Qinling", "Hanzhong", "STRATEGY"), ("Hanzhong", "Bashu", "STRATEGY"),
    ("Bashu", "Diaoyu", "STRATEGY"), ("Diaoyu", "Yangtze", "WATER"),

    # 中翼 (荆襄)
    ("CentralPlains", "Nanyang", "ATTACK"), ("Nanyang", "Xiangyang", "ATTACK"),
    ("Xiangyang", "Jiangling", "STRATEGY"), ("Jiangling", "Ezhou", "STRATEGY"), ("Ezhou", "Yangtze", "WATER"),

    # 东翼 (江淮)
    ("CentralPlains", "Jianghuai", "ATTACK"), ("Jianghuai", "HuaiRiver", "STRATEGY"),
    ("HuaiRiver", "HuaiForts", "STRATEGY"), ("HuaiForts", "Zhenjiang", "ATTACK"), ("Zhenjiang", "Yangtze", "WATER"),
    ("Yangtze", "Jiangnan", "STRATEGY")
]

def create_chinese_map():
    # 1. 底图设置 (CartoDB Positron 适合展示文字标签)
    m = folium.Map(location=[36.0, 108.0], zoom_start=5, tiles="CartoDB positron")

    # 2. 添加中文图例 (HTML)
    legend_html = """
     <div style="position: fixed; 
     bottom: 50px; left: 50px; width: 150px; height: 190px; 
     border:2px solid grey; z-index:9999; font-size:14px; font-family: 'Microsoft YaHei', sans-serif;
     background-color:white; opacity:0.9; padding: 10px;">
     <b>兵家必争之地图例</b><br>
     <i class="fa fa-fire" style="color:#d32f2f"></i> 威胁源头 (游牧)<br>
     <i class="fa fa-star" style="color:#2e7d32"></i> 核心/京师<br>
     <i class="fa fa-shield" style="color:#f57c00"></i> 关键关隘<br>
     <i class="fa fa-crosshairs" style="color:#fbc02d"></i> 战略枢纽<br>
     <span style="color:#d32f2f"><b>&rarr; &rarr;</b></span> 进攻/南下路线<br>
     <span style="color:#0288d1"><b>&rarr; &rarr;</b></span> 水路防线<br>
     <span style="color:gray"><b>&mdash;&mdash;</b></span> 战略控制/补给
     </div>
     """
    m.get_root().html.add_child(folium.Element(legend_html))

    # 3. 绘制连线 (AntPath 动画)
    for start, end, etype in EDGES:
        if start in LOCATIONS and end in LOCATIONS:
            p1 = LOCATIONS[start]["coords"]
            p2 = LOCATIONS[end]["coords"]
            
            if etype == "ATTACK":
                # 红色动画虚线：模拟进攻
                plugins.AntPath([p1, p2], color="#d32f2f", weight=4, opacity=0.8, delay=1000, tooltip="进攻/南下路线").add_to(m)
            elif etype == "WATER":
                # 蓝色动画虚线：模拟水流
                plugins.AntPath([p1, p2], color="#0288d1", weight=4, opacity=0.7, delay=1500, tooltip="水路防线").add_to(m)
            else:
                # 灰色静态虚线：战略连接
                folium.PolyLine([p1, p2], color="gray", weight=2, opacity=0.5, dash_array='5, 10', tooltip="战略连接").add_to(m)

    # 4. 绘制节点 (图标 + 中文标签)
    for key, data in LOCATIONS.items():
        l_type = data["type"]
        style = STYLES.get(l_type, STYLES["BASE"])
        
        # A. 图标 (Marker)
        folium.Marker(
            location=data["coords"],
            icon=folium.Icon(color="white", icon_color=style["color"], icon=style["icon"], prefix='fa'),
            tooltip=data["name"] # 鼠标悬停提示
        ).add_to(m)

        # B. 中文文本标签 (DivIcon)
        # 稍微偏移坐标，防止文字遮挡图标
        folium.map.Marker(
            [data["coords"][0] - 0.25, data["coords"][1]], 
            icon=DivIcon(
                icon_size=(150,36),
                icon_anchor=(75,0),
                # 使用微软雅黑字体，白色描边增加可读性
                html=f'''<div style="
                    font-size: 10pt; 
                    font-family: 'Microsoft YaHei', 'SimHei', sans-serif; 
                    font-weight: bold; 
                    color: black; 
                    text-shadow: 2px 0 #fff, -2px 0 #fff, 0 2px #fff, 0 -2px #fff, 1px 1px #fff, -1px -1px #fff, 1px -1px #fff, -1px 1px #fff;
                    text-align: center;
                    white-space: nowrap;
                    ">{data["name"]}</div>''',
            )
        ).add_to(m)

    # 保存文件
    output_file = "ancient_china_map_cn.html"
    m.save(output_file)
    print(f"中文地图已生成: {output_file}")

if __name__ == "__main__":
    create_chinese_map()
