import folium
from folium import plugins
from folium.features import DivIcon
import requests
import time

# ==========================================
# 1. 核心配置 & 样式
# ==========================================
STYLES = {
    "THREAT": {"color": "#b71c1c", "icon": "fire", "size": (30, 30), "area_color": "#ffcdd2"}, # 威胁 (红)
    "PASS":   {"color": "#e65100", "icon": "shield", "size": (24, 24), "area_color": "#ffe0b2"}, # 关隘 (橙)
    "HUB":    {"color": "#f9a825", "icon": "crosshairs", "size": (22, 22), "area_color": "#fff9c4"}, # 枢纽 (黄)
    "CORE":   {"color": "#1b5e20", "icon": "star", "size": (26, 26), "area_color": "#c8e6c9"},   # 核心 (绿)
    "WATER":  {"color": "#0277bd", "icon": "tint", "size": (20, 20), "area_color": "#b3e5fc"},   # 水路 (蓝)
    "BASE":   {"color": "#616161", "icon": "map-marker", "size": (16, 16), "area_color": "#eeeeee"} # 基地 (灰)
}

# ==========================================
# 2. 完整地理节点 (Restored All Links)
# ==========================================
LOCATIONS = {
    # --- A. 北方威胁源 ---
    "Mongolia":  {"name": "蒙古高原", "coords": [43.65, 111.97], "type": "THREAT", "group": "北方威胁", "radius": 150000},
    "Manchuria": {"name": "女真/辽东", "coords": [41.8, 123.4], "type": "THREAT", "group": "北方威胁", "radius": 120000},

    # --- B. 西北长城线 (九边西段) ---
    "Xiyu":     {"name": "西域(敦煌)", "coords": [40.14, 94.66], "type": "BASE", "group": "西北防线", "radius": 0},
    "Hexi":     {"name": "河西走廊", "coords": [38.93, 100.45], "type": "HUB", "group": "西北防线", "radius": 60000},
    "Gansu":    {"name": "甘肃镇(张掖)", "coords": [38.93, 100.45], "type": "BASE", "group": "西北防线", "radius": 0}, 
    "Ningxia":  {"name": "宁夏镇(银川)", "coords": [38.48, 106.23], "type": "HUB", "group": "西北防线", "radius": 0},
    "Hetao":    {"name": "河套平原", "coords": [40.76, 107.40], "type": "THREAT", "group": "西北防线", "radius": 80000},
    "Yansui":   {"name": "延绥镇(榆林)", "coords": [38.28, 109.73], "type": "HUB", "group": "西北防线", "radius": 0},
    "Longxi":   {"name": "陇西", "coords": [35.5, 104.6], "type": "HUB", "group": "西北防线", "radius": 0},

    # --- C. 山西/河东 (九边中段) ---
    "Datong":   {"name": "大同", "coords": [40.07, 113.3], "type": "HUB", "group": "九边重镇", "radius": 0},
    "Yanmen":   {"name": "雁门关", "coords": [39.18, 112.88], "type": "PASS", "group": "九边重镇", "radius": 0},
    "Ningwu":   {"name": "宁武关", "coords": [39.00, 112.30], "type": "PASS", "group": "九边重镇", "radius": 0},
    "Piantou":  {"name": "偏头关", "coords": [39.43, 111.48], "type": "PASS", "group": "九边重镇", "radius": 0},
    "Taiyuan":  {"name": "太原", "coords": [37.87, 112.54], "type": "CORE", "group": "九边重镇", "radius": 40000},
    "Hedong":   {"name": "河东(临汾)", "coords": [36.08, 111.51], "type": "HUB", "group": "九边重镇", "radius": 0},

    # --- D. 京师/幽燕 (九边东段) ---
    "Xuanfu":   {"name": "宣府", "coords": [40.6, 115.0], "type": "HUB", "group": "九边重镇", "radius": 0},
    "Juyong":   {"name": "居庸关", "coords": [40.28, 116.06], "type": "PASS", "group": "九边重镇", "radius": 0},
    "Beijing":  {"name": "北京", "coords": [39.90, 116.40], "type": "CORE", "group": "九边重镇", "radius": 40000},
    "Shanhai":  {"name": "山海关", "coords": [40.00, 119.75], "type": "PASS", "group": "九边重镇", "radius": 0},
    "Liaodong": {"name": "辽西走廊", "coords": [40.6, 120.8], "type": "BASE", "group": "九边重镇", "radius": 0},

    # --- E. 核心腹地 ---
    "Guanzhong": {"name": "关中(长安)", "coords": [34.26, 108.95], "type": "CORE", "group": "核心腹地", "radius": 80000},
    "Hangu":     {"name": "函谷关", "coords": [34.63, 110.9], "type": "PASS", "group": "核心腹地", "radius": 0},
    "CentralPlains": {"name": "中原(洛阳)", "coords": [34.66, 112.4], "type": "CORE", "group": "中原腹地", "radius": 70000},

    # --- F. 西南 (蜀道) ---
    "Hanzhong":  {"name": "汉中", "coords": [33.07, 107.02], "type": "HUB", "group": "西南防线", "radius": 40000},
    "Bashu":     {"name": "巴蜀(成都)", "coords": [30.66, 104.06], "type": "CORE", "group": "西南防线", "radius": 100000},
    "Diaoyu":    {"name": "钓鱼城", "coords": [30.00, 106.27], "type": "PASS", "group": "西南防线", "radius": 0},

    # --- G. 荆襄 (中翼) ---
    "Nanyang":   {"name": "南阳", "coords": [33.00, 112.52], "type": "BASE", "group": "中翼防线", "radius": 0},
    "Xiangyang": {"name": "襄阳", "coords": [32.01, 112.12], "type": "HUB", "group": "中翼防线", "radius": 0},
    "Jiangling": {"name": "江陵(荆州)", "coords": [30.33, 112.23], "type": "HUB", "group": "中翼防线", "radius": 0},
    "Ezhou":     {"name": "鄂州(武昌)", "coords": [30.54, 114.30], "type": "HUB", "group": "中翼防线", "radius": 0},

    # --- H. 江淮 & 江南 (东翼) ---
    "Jianghuai": {"name": "江淮", "coords": [32.5, 117.0], "type": "HUB", "group": "东南防线", "radius": 60000},
    "Shouchun":  {"name": "寿春", "coords": [32.58, 116.78], "type": "PASS", "group": "东南防线", "radius": 0},
    "Hefei":     {"name": "合肥", "coords": [31.86, 117.28], "type": "PASS", "group": "东南防线", "radius": 0},
    "Zhenjiang": {"name": "镇江(京口)", "coords": [32.20, 119.45], "type": "PASS", "group": "东南防线", "radius": 0},
    "Jiangnan":  {"name": "江南(南京)", "coords": [32.06, 118.79], "type": "CORE", "group": "东南防线", "radius": 90000},
    
    # --- 辅助节点 (用于水路路由生成) ---
    "Wuhan": {"name": "", "coords": [30.59, 114.30], "type": "WATER", "group": "HIDDEN", "radius": 0},
    "Anqing": {"name": "", "coords": [30.50, 117.05], "type": "WATER", "group": "HIDDEN", "radius": 0},
}

# ==========================================
# 3. 完整连线定义 (All Links Restored)
# ==========================================
# (Start, End, Type, Group)
# ATTACK=红, WATER=蓝, MOUNTAIN=棕(虚线), ROAD=黑, STRATEGY=灰(虚线)
EDGES = [
    # --- 1. 丝路与西北 ---
    ("Xiyu", "Hexi", "ROAD", "西北防线"),
    ("Hexi", "Longxi", "ROAD", "西北防线"),
    ("Longxi", "Guanzhong", "MOUNTAIN", "西北防线"), 
    
    # --- 2. 北方入侵 & 九边连接 ---
    ("Mongolia", "Hetao", "ATTACK", "北方威胁"),
    ("Hetao", "Ningxia", "ATTACK", "西北防线"),
    ("Ningxia", "Yansui", "ROAD", "西北防线"),
    ("Yansui", "Datong", "ROAD", "九边重镇"),
    ("Hetao", "Guanzhong", "ATTACK", "西北防线"), # 匈奴入侵线
    ("Hetao", "Yansui", "ATTACK", "西北防线"),
    
    # --- 3. 山西/京师防线 ---
    ("Mongolia", "Datong", "ATTACK", "北方威胁"),
    ("Mongolia", "Xuanfu", "ATTACK", "北方威胁"),
    ("Datong", "Xuanfu", "ROAD", "九边重镇"),
    ("Datong", "Yanmen", "MOUNTAIN", "九边重镇"), # 外三关
    ("Datong", "Ningwu", "MOUNTAIN", "九边重镇"),
    ("Datong", "Piantou", "MOUNTAIN", "九边重镇"),
    ("Yanmen", "Taiyuan", "ROAD", "九边重镇"),
    ("Taiyuan", "Hedong", "ROAD", "九边重镇"),
    ("Hedong", "Guanzhong", "ATTACK", "九边重镇"), # 渡河
    ("Hedong", "CentralPlains", "ATTACK", "九边重镇"), # 太行八陉
    
    # --- 4. 东北走廊 ---
    ("Manchuria", "Liaodong", "ATTACK", "北方威胁"),
    ("Liaodong", "Shanhai", "ATTACK", "九边重镇"), # 辽西走廊
    ("Shanhai", "Beijing", "ROAD", "九边重镇"),
    ("Xuanfu", "Juyong", "ATTACK", "九边重镇"), # 土木堡后防线
    ("Juyong", "Beijing", "ATTACK", "九边重镇"),

    # --- 5. 关中与中原 ---
    ("Guanzhong", "Hangu", "ROAD", "核心腹地"),
    ("Hangu", "CentralPlains", "ROAD", "中原腹地"),
    ("Beijing", "CentralPlains", "STRATEGY", "中原腹地"),

    # --- 6. 蜀道与西南 ---
    ("Guanzhong", "Hanzhong", "MOUNTAIN", "西南防线"), # 秦岭栈道
    ("Hanzhong", "Bashu", "MOUNTAIN", "西南防线"),     # 金牛道
    ("Bashu", "Diaoyu", "WATER", "西南防线"),          # 嘉陵江水路

    # --- 7. 荆襄防线 (铁三角) ---
    ("CentralPlains", "Nanyang", "ATTACK", "中翼防线"),
    ("Nanyang", "Xiangyang", "ATTACK", "中翼防线"),
    ("Xiangyang", "Jiangling", "ROAD", "中翼防线"),    # 汉水陆路
    ("Jiangling", "Ezhou", "WATER", "中翼防线"),       # 长江中游
    ("Ezhou", "Wuhan", "WATER", "中翼防线"),

    # --- 8. 江淮防线 (守江必守淮) ---
    ("CentralPlains", "Shouchun", "ATTACK", "东南防线"),
    ("Shouchun", "Hefei", "ROAD", "东南防线"),
    ("Hefei", "Zhenjiang", "ATTACK", "东南防线"), # 濡须口方向
    ("Shouchun", "Zhenjiang", "STRATEGY", "东南防线"),

    # --- 9. 长江天险 (分段连接以实现曲线) ---
    ("Diaoyu", "Jiangling", "WATER", "西南防线"),
    ("Wuhan", "Anqing", "WATER", "东南防线"),
    ("Anqing", "Jiangnan", "WATER", "东南防线"),
    ("Zhenjiang", "Jiangnan", "WATER", "东南防线"),
]

# ==========================================
# 4. 路由与生成逻辑
# ==========================================
def get_real_path(p1, p2):
    """请求 OSRM 获取真实路径"""
    url = f"http://router.project-osrm.org/route/v1/driving/{p1[1]},{p1[0]};{p2[1]},{p2[0]}?overview=full&geometries=geojson"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data['code'] == 'Ok':
                return [[p[1], p[0]] for p in data['routes'][0]['geometry']['coordinates']]
    except:
        pass
    return [p1, p2]

def create_final_map():
    print("初始化地形图...")
    m = folium.Map(location=[35.5, 108.0], zoom_start=5, tiles=None)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}',
        attr='Esri', name='山川地形图', control=True
    ).add_to(m)

    # 创建分组
    layer_names = ["北方威胁", "西北防线", "九边重镇", "核心腹地", "中原腹地", "西南防线", "中翼防线", "东南防线"]
    groups = {name: folium.FeatureGroup(name=name) for name in layer_names}
    for g in groups.values(): m.add_child(g)

    # 1. 绘制区域势力范围
    for key, data in LOCATIONS.items():
        if data.get("group") != "HIDDEN" and data.get("radius", 0) > 0:
            folium.Circle(
                location=data["coords"], radius=data["radius"],
                color=STYLES[data["type"]]["color"], weight=1,
                fill=True, fill_color=STYLES[data["type"]]["area_color"], fill_opacity=0.15
            ).add_to(groups[data["group"]])

    # 2. 绘制所有连线 (Routing)
    total = len(EDGES)
    print(f"开始计算 {total} 条真实路径 (OSRM)...")
    
    for i, (start_k, end_k, etype, gname) in enumerate(EDGES):
        if gname not in groups: continue
        
        # 进度提示
        print(f"[{i+1}/{total}] Routing: {start_k} -> {end_k}")
        
        p1 = LOCATIONS[start_k]["coords"]
        p2 = LOCATIONS[end_k]["coords"]
        target = groups[gname]
        
        # 获取真实路径 (水路也用Driving模拟沿江公路，效果很好)
        time.sleep(0.15) # 避免API速率限制
        points = get_real_path(p1, p2)
        
        # 样式应用
        if etype == "ATTACK":
            plugins.AntPath(points, color="#d50000", weight=4, opacity=0.8, delay=800, pulse_color='white', tooltip="进攻路线").add_to(target)
        elif etype == "WATER":
            plugins.AntPath(points, color="#0277bd", weight=5, opacity=0.6, delay=1500, tooltip="水路").add_to(target)
        elif etype == "MOUNTAIN":
            folium.PolyLine(points, color="#5d4037", weight=3, opacity=0.9, dash_array='5, 8', tooltip="山路/栈道").add_to(target)
        elif etype == "ROAD":
            folium.PolyLine(points, color="#212121", weight=3, opacity=0.6, tooltip="官道/走廊").add_to(target)
        else:
            folium.PolyLine(points, color="#757575", weight=2, opacity=0.5, dash_array='4, 6', tooltip="战略连接").add_to(target)

    # 3. 绘制节点
    for key, data in LOCATIONS.items():
        if data.get("group") == "HIDDEN": continue
        target = groups.get(data["group"], groups["中原腹地"])
        style = STYLES.get(data["type"], STYLES["BASE"])
        
        # 图标
        folium.Marker(
            location=data["coords"],
            icon=folium.Icon(color="white", icon_color=style["color"], icon=style["icon"], prefix='fa'),
            tooltip=data["name"]
        ).add_to(target)
        
        # 文字
        folium.map.Marker(
            [data["coords"][0] - 0.25, data["coords"][1]],
            icon=DivIcon(
                icon_size=(150,36), icon_anchor=(75,0),
                html=f'''<div style="font-size: 9pt; font-family: 'Microsoft YaHei'; font-weight: 800; color: #212121; text-shadow: 2px 0 #fff, -2px 0 #fff, 0 2px #fff; text-align: center; pointer-events: none;">{data["name"]}</div>''',
            )
        ).add_to(target)

    # 4. 控件与图例
    folium.LayerControl(collapsed=False).add_to(m)
    plugins.MiniMap(toggle_display=True, tile_layer=None, tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}', attr='Esri').add_to(m)
    plugins.MeasureControl().add_to(m)
    plugins.Search(layer=groups["九边重镇"], geom_type='Point', placeholder='搜索地点...', collapsed=True, search_label='tooltip').add_to(m)

    legend_html = """
     <div style="position: fixed; bottom: 30px; left: 20px; width: 160px; 
     border: 2px solid #5d4037; border-radius: 4px; z-index:9999; 
     font-family: 'Microsoft YaHei'; background-color: #fff3e0; opacity: 0.95; 
     padding: 10px; font-size:12px; box-shadow: 3px 3px 5px rgba(0,0,0,0.3);">
     <b style="display:block; border-bottom:1px solid #8d6e63; margin-bottom:5px; text-align:center; color:#5d4037">全景战略图 (真实路径)</b>
     <div><span style="color:#d50000; font-weight:bold;">---></span> 进攻 (红)</div>
     <div><span style="color:#0277bd; font-weight:bold;">===></span> 水路 (蓝)</div>
     <div><span style="color:#5d4037; font-weight:bold;">- - -</span> 山路/栈道 (褐)</div>
     <div><span style="color:#212121; font-weight:bold;">——</span> 走廊/官道 (黑)</div>
     <div style="margin-top:5px; color:#666">* 包含九边、外三关、<br>江淮重镇及完整水路</div>
     </div>
     """
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save("ancient_china_final_connected.html")
    print("最终版生成完毕: ancient_china_final_connected.html")

if __name__ == "__main__":
    create_final_map()
