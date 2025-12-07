import folium
from folium import plugins
from folium.features import DivIcon

# ==========================================
# 1. 配置与样式 (Configuration)
# ==========================================

# 样式映射
STYLES = {
    "THREAT": {"color": "#b71c1c", "icon": "fire", "size": (30, 30)},       # 深红
    "PASS":   {"color": "#e65100", "icon": "shield", "size": (25, 25)},     # 深橙
    "HUB":    {"color": "#f9a825", "icon": "crosshairs", "size": (20, 20)}, # 暗黄
    "CORE":   {"color": "#1b5e20", "icon": "star", "size": (25, 25)},       # 深绿
    "WATER":  {"color": "#01579b", "icon": "tint", "size": (20, 20)},       # 深蓝
    "BASE":   {"color": "gray",    "icon": "map-marker", "size": (15, 15)}
}

# ==========================================
# 2. 增强版地理数据 (包含历史描述)
# ==========================================
LOCATIONS = {
    # --- 威胁源头 ---
    "Mongolia":  {"name": "蒙古高原", "coords": [44.0, 111.0], "type": "THREAT", "group": "Threats", "desc": "<b>游牧源头</b><br>匈奴、突厥、蒙古、瓦剌的根据地。"},
    "Manchuria": {"name": "辽东/女真", "coords": [41.8, 123.4], "type": "THREAT", "group": "Threats", "desc": "<b>东北威胁</b><br>女真、满清龙兴之地，窥视山海关。"},
    
    # --- 西北与关中 ---
    "Hexi":     {"name": "河西走廊", "coords": [39.0, 100.5], "type": "HUB", "group": "Northwest", "desc": "<b>丝路咽喉</b><br>断绝则西域失联，夹在沙漠与雪山之间。"},
    "Hetao":    {"name": "河套平原", "coords": [40.8, 107.5], "type": "THREAT", "group": "Northwest", "desc": "<b>游牧跳板</b><br>水草丰美，匈奴南下的前哨基地。"},
    "Longxi":   {"name": "陇西", "coords": [35.5, 104.6], "type": "HUB", "group": "Northwest", "desc": "<b>关中西屏</b><br>防御吐蕃的前线，风起陇西。"},
    "Guanzhong": {"name": "关中平原", "coords": [34.3, 108.9], "type": "CORE", "group": "Core", "desc": "<b>四塞之国</b><br>秦汉隋唐建都之地，沃野千里，易守难攻。"},
    "Hangu":     {"name": "函谷关", "coords": [34.61, 110.36], "type": "PASS", "group": "Core", "desc": "<b>关中东门</b><br>一夫当关，万夫莫开。六国攻秦之死地。"},

    # --- 山西/九边 ---
    "Datong":   {"name": "大同", "coords": [40.07, 113.3], "type": "HUB", "group": "NorthDefense", "desc": "<b>九边重镇</b><br>直面蒙古，明朝防御核心。"},
    "Yanmen":   {"name": "雁门关", "coords": [39.18, 112.88], "type": "PASS", "group": "NorthDefense", "desc": "<b>天下九塞之首</b><br>中华第一关，杨家将驻守地，扼守山西中路。"},
    "Taiyuan":  {"name": "太原", "coords": [37.87, 112.54], "type": "CORE", "group": "NorthDefense", "desc": "<b>河东心脏</b><br>表里山河，控带山河，完颜宗翰攻宋突破口。"},
    "Hedong":    {"name": "河东 (吕梁)", "coords": [36.5, 111.5], "type": "HUB", "group": "NorthDefense", "desc": "<b>居高临下</b><br>西渡黄河击关中，南下太行入中原。"},

    # --- 京师/幽燕 ---
    "Xuanfu":   {"name": "宣府", "coords": [40.81, 114.88], "type": "HUB", "group": "JingDefense", "desc": "<b>京师锁钥</b><br>土木堡之变发生地，距北京极近。"},
    "Juyong":   {"name": "居庸关", "coords": [40.28, 116.06], "type": "PASS", "group": "JingDefense", "desc": "<b>最后防线</b><br>天下第一雄关，守卫北京的最后一道大门。"},
    "Shanhai":  {"name": "山海关", "coords": [40.00, 119.75], "type": "PASS", "group": "JingDefense", "desc": "<b>辽东咽喉</b><br>明清易代关键点，吴三桂开关处。"},
    "Beijing":   {"name": "北京", "coords": [39.90, 116.40], "type": "CORE", "group": "JingDefense", "desc": "<b>幽燕腹地</b><br>元明清都城，天子守国门。"},

    # --- 中原/巴蜀 ---
    "CentralPlains": {"name": "中原(洛阳)", "coords": [34.7, 113.6], "type": "CORE", "group": "Central", "desc": "<b>四战之地</b><br>无险可守，得中原者得天下。"},
    "Hanzhong":      {"name": "汉中", "coords": [33.07, 107.02], "type": "HUB", "group": "WestWing", "desc": "<b>巴蜀咽喉</b><br>秦岭以南关键盆地，蜀汉北伐基地。"},
    "Bashu":     {"name": "巴蜀", "coords": [30.6, 104.0], "type": "CORE", "group": "WestWing", "desc": "<b>天府之国</b><br>大后方粮仓，易守难攻。"},
    "Diaoyu":    {"name": "钓鱼城", "coords": [30.0, 106.27], "type": "PASS", "group": "WestWing", "desc": "<b>上帝折鞭处</b><br>蒙哥大汗陨落之地，阻挡蒙军36年。"},

    # --- 荆襄/江淮/江南 ---
    "Xiangyang": {"name": "襄阳", "coords": [32.01, 112.12], "type": "HUB", "group": "CentralWing", "desc": "<b>天下腰脊</b><br>南宋防御铁三角之首，失襄阳则长江无险。"},
    "Jiangling": {"name": "江陵(荆州)", "coords": [30.35, 112.19], "type": "HUB", "group": "CentralWing", "desc": "<b>据上流之势</b><br>东连吴会，西通巴蜀，北接中原。"},
    "Jianghuai": {"name": "江淮", "coords": [32.5, 117.0], "type": "HUB", "group": "EastWing", "desc": "<b>守江必守淮</b><br>南方政权的缓冲区，也是北方骑兵的泥潭。"},
    "Yangtze":   {"name": "长江天险", "coords": [30.5, 117.0], "type": "WATER", "group": "SouthCore", "desc": "<b>黄金水道</b><br>南方政权的最后死线。"},
    "Jiangnan":  {"name": "江南(南京)", "coords": [31.5, 119.5], "type": "CORE", "group": "SouthCore", "desc": "<b>经济命脉</b><br>赋税重地，偏安政权核心。"},
}

# ==========================================
# 3. 连线定义 (包含层级)
# ==========================================
EDGES = [
    # 进攻线 (红色)
    ("Mongolia", "Hetao", "ATTACK", "Threats"), ("Hetao", "Guanzhong", "ATTACK", "Northwest"),
    ("Mongolia", "Datong", "ATTACK", "NorthDefense"), ("Datong", "Yanmen", "ATTACK", "NorthDefense"),
    ("Mongolia", "Xuanfu", "ATTACK", "JingDefense"), ("Xuanfu", "Juyong", "ATTACK", "JingDefense"),
    ("Manchuria", "Shanhai", "ATTACK", "JingDefense"), ("Shanhai", "Beijing", "ATTACK", "JingDefense"),
    ("Hedong", "CentralPlains", "ATTACK", "NorthDefense"),
    ("CentralPlains", "Xiangyang", "ATTACK", "CentralWing"),
    ("CentralPlains", "Jianghuai", "ATTACK", "EastWing"),
    
    # 战略线 (灰色)
    ("Hexi", "Longxi", "STRATEGY", "Northwest"), ("Longxi", "Guanzhong", "STRATEGY", "Northwest"),
    ("Yanmen", "Taiyuan", "STRATEGY", "NorthDefense"), ("Taiyuan", "Hedong", "STRATEGY", "NorthDefense"),
    ("Guanzhong", "Hangu", "STRATEGY", "Core"), ("Hangu", "CentralPlains", "STRATEGY", "Central"),
    ("Guanzhong", "Hanzhong", "STRATEGY", "WestWing"), ("Hanzhong", "Bashu", "STRATEGY", "WestWing"),
    ("Xiangyang", "Jiangling", "STRATEGY", "CentralWing"),
    ("Jianghuai", "Jiangnan", "STRATEGY", "EastWing"),
    
    # 水路 (蓝色)
    ("Bashu", "Diaoyu", "WATER", "WestWing"), ("Diaoyu", "Jiangling", "WATER", "SouthCore"),
    ("Jiangling", "Yangtze", "WATER", "SouthCore"), ("Yangtze", "Jiangnan", "WATER", "SouthCore")
]

def create_ultimate_map():
    # 1. 物理地形底图 (Esri WorldPhysical) - 突显山脉地形
    attr = 'Tiles &copy; Esri &mdash; Source: US National Park Service'
    tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}'
    
    m = folium.Map(location=[35.5, 108.0], zoom_start=5, tiles=tiles, attr=attr)

    # 2. 创建图层组 (Layer Groups) 用于交互开关
    layers = {
        "Threats": folium.FeatureGroup(name="<span style='color:red'>北方威胁 (游牧/女真)</span>", show=True),
        "Core": folium.FeatureGroup(name="<b>关中核心 (秦)</b>", show=True),
        "Northwest": folium.FeatureGroup(name="西北防线 (汉/唐)", show=True),
        "NorthDefense": folium.FeatureGroup(name="山西防线 (宋)", show=True),
        "JingDefense": folium.FeatureGroup(name="京师九边 (明)", show=True),
        "Central": folium.FeatureGroup(name="中原腹地", show=True),
        "WestWing": folium.FeatureGroup(name="西翼 (巴蜀/汉中)", show=True),
        "CentralWing": folium.FeatureGroup(name="中翼 (荆襄防御)", show=True),
        "EastWing": folium.FeatureGroup(name="东翼 (江淮防御)", show=True),
        "SouthCore": folium.FeatureGroup(name="<span style='color:blue'>江南核心 (水路)</span>", show=True),
    }

    # 将图层添加到地图
    for layer in layers.values():
        m.add_child(layer)

    # 3. 绘制连线
    for start, end, etype, group_key in EDGES:
        if start in LOCATIONS and end in LOCATIONS and group_key in layers:
            p1 = LOCATIONS[start]["coords"]
            p2 = LOCATIONS[end]["coords"]
            target_layer = layers[group_key]
            
            if etype == "ATTACK":
                plugins.AntPath([p1, p2], color="#b71c1c", weight=4, opacity=0.8, delay=800, pulse_color='#ffcdd2', tooltip="进攻路线").add_to(target_layer)
            elif etype == "WATER":
                plugins.AntPath([p1, p2], color="#01579b", weight=5, opacity=0.6, delay=1500, pulse_color='white', tooltip="长江水路").add_to(target_layer)
            else:
                folium.PolyLine([p1, p2], color="#424242", weight=2, opacity=0.6, dash_array='5, 10').add_to(target_layer)

    # 4. 绘制节点
    for key, data in LOCATIONS.items():
        group_key = data.get("group", "Central")
        if group_key in layers:
            l_type = data["type"]
            style = STYLES.get(l_type, STYLES["BASE"])
            target_layer = layers[group_key]

            # A. 交互式 Popup (点击显示详细历史)
            popup_html = f"""
            <div style="font-family:'Microsoft YaHei'; width:200px;">
                <h4 style="margin-bottom:5px; border-bottom:1px solid #ccc; padding-bottom:5px;">{data['name']}</h4>
                <p style="font-size:13px;">{data.get('desc', '')}</p>
            </div>
            """
            
            # B. 图标
            folium.Marker(
                location=data["coords"],
                icon=folium.Icon(color="white", icon_color=style["color"], icon=style["icon"], prefix='fa'),
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=data["name"]
            ).add_to(target_layer)

            # C. 永久显示文字 (带白色描边，适应地形图背景)
            folium.map.Marker(
                [data["coords"][0] - 0.3, data["coords"][1]], 
                icon=DivIcon(
                    icon_size=(150,36),
                    icon_anchor=(75,0),
                    html=f'''<div style="
                        font-size: 10pt; 
                        font-family: 'Microsoft YaHei', sans-serif; 
                        font-weight: 900; 
                        color: #212121; 
                        text-shadow: 2px 0 #fff, -2px 0 #fff, 0 2px #fff, 0 -2px #fff, 1px 1px #fff;
                        text-align: center;
                        white-space: nowrap;
                        pointer-events: none;
                        ">{data["name"]}</div>''',
                )
            ).add_to(target_layer)

    # 5. 添加控制控件
    # 图层控制器
    folium.LayerControl(collapsed=False).add_to(m)
    
    # 全屏插件
    plugins.Fullscreen().add_to(m)
    
    # 迷你导航图
    plugins.MiniMap(toggle_display=True).add_to(m)

    # 6. 古风图例
    legend_html = """
     <div style="
     position: fixed; 
     bottom: 30px; left: 30px; width: 180px; 
     border: 2px solid #5d4037; border-radius: 5px;
     z-index:9999; 
     font-family: 'Microsoft YaHei', sans-serif;
     background-color: #fff3e0; opacity: 0.95; 
     padding: 15px;
     box-shadow: 3px 3px 5px rgba(0,0,0,0.3);
     ">
     <h4 style="margin-top:0; text-align:center; color:#5d4037; border-bottom:1px solid #8d6e63; padding-bottom:5px;">战略图例</h4>
     <div style="font-size:13px; color:#3e2723;">
         <div style="margin-bottom:5px;"><i class="fa fa-fire" style="color:#b71c1c; width:20px;"></i> 北方威胁 (游牧)</div>
         <div style="margin-bottom:5px;"><i class="fa fa-star" style="color:#1b5e20; width:20px;"></i> 核心/帝都</div>
         <div style="margin-bottom:5px;"><i class="fa fa-shield" style="color:#e65100; width:20px;"></i> 雄关/险隘</div>
         <div style="margin-bottom:5px;"><i class="fa fa-crosshairs" style="color:#f9a825; width:20px;"></i> 必争枢纽</div>
         <hr style="border-top: 1px dashed #8d6e63;">
         <div style="margin-bottom:5px;"><span style="color:#b71c1c; font-weight:bold;">--- ></span> 进攻路线 (动画)</div>
         <div style="margin-bottom:5px;"><span style="color:#01579b; font-weight:bold;">=== ></span> 长江/水路 (动画)</div>
         <div style="margin-bottom:5px;"><span style="color:#424242;">- - -</span> 战略补给/控制</div>
     </div>
     </div>
     """
    m.get_root().html.add_child(folium.Element(legend_html))

    # 保存
    output_file = "ancient_china_map_ultimate.html"
    m.save(output_file)
    print(f"终极版战略地图已生成: {output_file}")

if __name__ == "__main__":
    create_ultimate_map()
