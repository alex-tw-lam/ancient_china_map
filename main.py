import folium
from folium import plugins
from folium.features import DivIcon
import requests
import time

# ==========================================
# 1. 核心配置 (Styles)
# ==========================================
STYLES = {
    "THREAT": {"color": "#b71c1c", "icon": "fire", "size": (30, 30), "area_color": "#ffcdd2"}, # Red
    "PASS":   {"color": "#e65100", "icon": "shield", "size": (24, 24), "area_color": "#ffe0b2"}, # Orange
    "HUB":    {"color": "#f9a825", "icon": "crosshairs", "size": (22, 22), "area_color": "#fff9c4"}, # Yellow
    "CORE":   {"color": "#1b5e20", "icon": "star", "size": (26, 26), "area_color": "#c8e6c9"},   # Green
    "WATER":  {"color": "#0277bd", "icon": "tint", "size": (20, 20), "area_color": "#b3e5fc"},   # Blue
    "BASE":   {"color": "#616161", "icon": "map-marker", "size": (16, 16), "area_color": "#eeeeee"} # Gray
}

# ==========================================
# 2. 黄河 (几字形) 坐标
# ==========================================
YELLOW_RIVER_COORDS = [
    [35.85, 103.20], [36.06, 103.83], [36.56, 104.68], [37.51, 105.17],
    [38.48, 106.23], [39.23, 106.77], [40.33, 107.00], [40.76, 107.40],
    [40.65, 109.84], [40.27, 111.19], [39.43, 111.48], [36.14, 110.44],
    [35.60, 110.35], [34.61, 110.36], [34.77, 111.19], [34.90, 113.62],
    [34.85, 114.30], [35.50, 116.00], [36.65, 116.99], [37.73, 119.16]
]

# ==========================================
# 3. 完整地理节点 (All Nodes Restored)
# ==========================================
LOCATIONS = {
    # --- A. 北方威胁 ---
    "Mongolia":  {"name": "蒙古高原", "coords": [43.65, 111.97], "type": "THREAT", "group": "北方威胁", "radius": 150000},
    "Manchuria": {"name": "女真/辽东", "coords": [41.8, 123.4], "type": "THREAT", "group": "北方威胁", "radius": 120000},

    # --- B. 西北防线 (The Northwest) ---
    "Xiyu":     {"name": "西域(敦煌)", "coords": [40.14, 94.66], "type": "BASE", "group": "西北防线", "radius": 0},
    "Hexi":     {"name": "河西走廊", "coords": [38.93, 100.45], "type": "HUB", "group": "西北防线", "radius": 60000},
    "Gansu":    {"name": "甘肃镇", "coords": [39.20, 99.50], "type": "BASE", "group": "西北防线", "radius": 0},
    "Ningxia":  {"name": "宁夏镇", "coords": [38.48, 106.23], "type": "HUB", "group": "西北防线", "radius": 0},
    "Hetao":    {"name": "河套平原", "coords": [40.76, 107.40], "type": "THREAT", "group": "西北防线", "radius": 80000},
    "Yansui":   {"name": "延绥镇", "coords": [38.28, 109.73], "type": "HUB", "group": "西北防线", "radius": 0},
    "Longxi":   {"name": "陇西", "coords": [35.50, 104.60], "type": "HUB", "group": "西北防线", "radius": 0},

    # --- C. 山西 (The Spine) ---
    "Datong":   {"name": "大同", "coords": [40.07, 113.30], "type": "HUB", "group": "九边重镇", "radius": 0},
    "Yanmen":   {"name": "雁门关", "coords": [39.18, 112.88], "type": "PASS", "group": "九边重镇", "radius": 0},
    "Ningwu":   {"name": "宁武关", "coords": [39.00, 112.30], "type": "PASS", "group": "九边重镇", "radius": 0},
    "Piantou":  {"name": "偏头关", "coords": [39.43, 111.48], "type": "PASS", "group": "九边重镇", "radius": 0},
    "Taiyuan":  {"name": "太原", "coords": [37.87, 112.54], "type": "CORE", "group": "九边重镇", "radius": 40000},
    "Hedong":   {"name": "河东", "coords": [36.08, 111.51], "type": "HUB", "group": "九边重镇", "radius": 0},

    # --- D. 幽燕 (The Capital) ---
    "Xuanfu":   {"name": "宣府", "coords": [40.60, 115.00], "type": "HUB", "group": "九边重镇", "radius": 0},
    "Juyong":   {"name": "居庸关", "coords": [40.28, 116.06], "type": "PASS", "group": "九边重镇", "radius": 0},
    "Beijing":  {"name": "北京", "coords": [39.90, 116.40], "type": "CORE", "group": "九边重镇", "radius": 40000},
    "Shanhai":  {"name": "山海关", "coords": [40.00, 119.75], "type": "PASS", "group": "九边重镇", "radius": 0},
    "Liaodong": {"name": "辽西走廊", "coords": [40.60, 120.80], "type": "BASE", "group": "九边重镇", "radius": 0},

    # --- E. 关中 (The Fortress) ---
    "Guanzhong": {"name": "关中", "coords": [34.26, 108.95], "type": "CORE", "group": "核心腹地", "radius": 80000},
    "Hangu":     {"name": "函谷关", "coords": [34.63, 110.90], "type": "PASS", "group": "核心腹地", "radius": 0},
    "CentralPlains": {"name": "中原(洛阳)", "coords": [34.66, 112.40], "type": "CORE", "group": "中原腹地", "radius": 70000},

    # --- F. 西南 (The West Wing) ---
    "Hanzhong":  {"name": "汉中", "coords": [33.07, 107.02], "type": "HUB", "group": "西南防线", "radius": 40000},
    "Bashu":     {"name": "巴蜀", "coords": [30.66, 104.06], "type": "CORE", "group": "西南防线", "radius": 100000},
    "Diaoyu":    {"name": "钓鱼城", "coords": [30.00, 106.27], "type": "PASS", "group": "西南防线", "radius": 0},

    # --- G. 荆襄 (The Center Wing) ---
    "Nanyang":   {"name": "南阳", "coords": [33.00, 112.52], "type": "BASE", "group": "中翼防线", "radius": 0},
    "Xiangyang": {"name": "襄阳", "coords": [32.01, 112.12], "type": "HUB", "group": "中翼防线", "radius": 0},
    "Jiangling": {"name": "江陵", "coords": [30.33, 112.23], "type": "HUB", "group": "中翼防线", "radius": 0},
    "Ezhou":     {"name": "鄂州", "coords": [30.54, 114.30], "type": "HUB", "group": "中翼防线", "radius": 0},

    # --- H. 江淮 (The East Wing) ---
    "Jianghuai": {"name": "江淮", "coords": [32.50, 117.00], "type": "HUB", "group": "东南防线", "radius": 60000},
    "Shouchun":  {"name": "寿春", "coords": [32.58, 116.78], "type": "PASS", "group": "东南防线", "radius": 0},
    "Hefei":     {"name": "合肥", "coords": [31.86, 117.28], "type": "PASS", "group": "东南防线", "radius": 0},
    "Zhongli":   {"name": "钟离(凤阳)", "coords": [32.86, 117.55], "type": "PASS", "group": "东南防线", "radius": 0}, # Restored
    "Xuyi":      {"name": "盱眙", "coords": [33.00, 118.53], "type": "PASS", "group": "东南防线", "radius": 0}, # Restored
    "Zhenjiang": {"name": "镇江", "coords": [32.20, 119.45], "type": "PASS", "group": "东南防线", "radius": 0},
    "Jiangnan":  {"name": "江南", "coords": [32.06, 118.79], "type": "CORE", "group": "东南防线", "radius": 90000},
    
    # --- Hidden Nodes for Routing ---
    "Wuhan": {"name": "", "coords": [30.59, 114.30], "type": "WATER", "group": "HIDDEN", "radius": 0},
    "Anqing": {"name": "", "coords": [30.50, 117.05], "type": "WATER", "group": "HIDDEN", "radius": 0},
}

# ==========================================
# 4. 路由逻辑
# ==========================================
def get_real_path(p1, p2):
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

# ==========================================
# 5. 完整连线定义 (Exhaustive List)
# ==========================================
EDGES = [
    # --- 1. 丝绸之路 (Land) ---
    ("Xiyu", "Hexi", "ROAD", "西北防线"),
    ("Hexi", "Gansu", "ROAD", "西北防线"),
    ("Gansu", "Longxi", "ROAD", "西北防线"),
    ("Longxi", "Guanzhong", "MOUNTAIN", "西北防线"), # 陇坂
    
    # --- 2. 北方入侵 (Attack) ---
    ("Mongolia", "Hetao", "ATTACK", "北方威胁"),
    ("Mongolia", "Datong", "ATTACK", "北方威胁"),
    ("Mongolia", "Xuanfu", "ATTACK", "北方威胁"),
    ("Hetao", "Guanzhong", "ATTACK", "西北防线"), # 匈奴线
    ("Hetao", "Ningxia", "ATTACK", "西北防线"),
    
    # --- 3. 九边横向连接 (Strategic Road) ---
    ("Ningxia", "Yansui", "ROAD", "西北防线"),
    ("Yansui", "Datong", "ROAD", "九边重镇"),
    ("Datong", "Xuanfu", "ROAD", "九边重镇"),
    ("Xuanfu", "Juyong", "ATTACK", "九边重镇"), # 也是入侵线
    ("Juyong", "Beijing", "ATTACK", "九边重镇"),

    # --- 4. 山西外三关 (Mountain Defense) ---
    ("Datong", "Yanmen", "MOUNTAIN", "九边重镇"),
    ("Datong", "Ningwu", "MOUNTAIN", "九边重镇"),
    ("Datong", "Piantou", "MOUNTAIN", "九边重镇"),
    ("Yanmen", "Taiyuan", "ROAD", "九边重镇"),
    ("Ningwu", "Taiyuan", "ROAD", "九边重镇"), # 辅助连接
    ("Taiyuan", "Hedong", "ROAD", "九边重镇"),
    
    # --- 5. 河东(山西)出击 (Attack) ---
    ("Hedong", "Guanzhong", "ATTACK", "九边重镇"), # 渡河攻关中 (李渊)
    ("Hedong", "CentralPlains", "ATTACK", "九边重镇"), # 太行八陉

    # --- 6. 东北走廊 (Corridor) ---
    ("Manchuria", "Liaodong", "ATTACK", "北方威胁"),
    ("Liaodong", "Shanhai", "ATTACK", "九边重镇"),
    ("Shanhai", "Beijing", "ROAD", "九边重镇"),

    # --- 7. 核心交通 (Imperial Roads) ---
    ("Guanzhong", "Hangu", "ROAD", "核心腹地"),
    ("Hangu", "CentralPlains", "ROAD", "中原腹地"),
    ("Beijing", "CentralPlains", "STRATEGY", "中原腹地"), # 大运河/官道方向

    # --- 8. 蜀道 (Mountain) ---
    ("Guanzhong", "Hanzhong", "MOUNTAIN", "西南防线"), # 秦岭
    ("Hanzhong", "Bashu", "MOUNTAIN", "西南防线"),     # 金牛道
    ("Bashu", "Diaoyu", "WATER", "西南防线"),

    # --- 9. 荆襄防线 (Central Wing) ---
    ("CentralPlains", "Nanyang", "ATTACK", "中翼防线"),
    ("Nanyang", "Xiangyang", "ATTACK", "中翼防线"),
    ("Xiangyang", "Jiangling", "ROAD", "中翼防线"),
    ("Jiangling", "Ezhou", "WATER", "中翼防线"),
    
    # --- 10. 江淮防线 (East Wing - The Web) ---
    ("CentralPlains", "Shouchun", "ATTACK", "东南防线"),
    ("Shouchun", "Hefei", "ROAD", "东南防线"),
    ("Shouchun", "Zhongli", "ROAD", "东南防线"), # New Link
    ("Shouchun", "Xuyi", "ROAD", "东南防线"),    # New Link
    ("Hefei", "Zhenjiang", "ATTACK", "东南防线"), # 濡须口
    ("Zhongli", "Zhenjiang", "STRATEGY", "东南防线"),
    ("Xuyi", "Jiangnan", "STRATEGY", "东南防线"), # 运河线

    # --- 11. 长江水路 (Water) ---
    ("Diaoyu", "Jiangling", "WATER", "西南防线"),
    ("Jiangling", "Wuhan", "WATER", "中翼防线"), # 补全中游
    ("Wuhan", "Anqing", "WATER", "东南防线"),
    ("Anqing", "Jiangnan", "WATER", "东南防线"),
    ("Zhenjiang", "Jiangnan", "WATER", "东南防线"),
]

def create_all_links_map():
    print("初始化地图...")
    m = folium.Map(location=[35.5, 108.0], zoom_start=5, tiles=None)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}',
        attr='Esri', name='山川地形图', control=True
    ).add_to(m)

    groups = {}
    layer_list = ["北方威胁", "黄河水系", "核心腹地", "九边重镇", "西北防线", "中原腹地", "西南防线", "中翼防线", "东南防线"]
    for name in layer_list:
        groups[name] = folium.FeatureGroup(name=name)
        m.add_child(groups[name])

    # 1. 绘制黄河
    print("绘制黄河...")
    plugins.AntPath(YELLOW_RIVER_COORDS, color="#fbc02d", weight=6, opacity=0.8, pulse_color='white', delay=2000, tooltip="黄河").add_to(groups["黄河水系"])

    # 2. 绘制区域
    for key, data in LOCATIONS.items():
        if data.get("group") != "HIDDEN" and data.get("radius", 0) > 0:
            folium.Circle(
                location=data["coords"], radius=data["radius"],
                color=STYLES[data["type"]]["color"], weight=1,
                fill=True, fill_color=STYLES[data["type"]]["area_color"], fill_opacity=0.15
            ).add_to(groups[data["group"]])

    # 3. 绘制连线 (Routing)
    total = len(EDGES)
    print(f"正在计算 {total} 条真实路径 (预计耗时45-60秒)...")
    
    for i, (start_k, end_k, etype, gname) in enumerate(EDGES):
        # Error Checking
        if start_k not in LOCATIONS: print(f"Missing: {start_k}"); continue
        if end_k not in LOCATIONS: print(f"Missing: {end_k}"); continue
        
        target = groups[gname]
        p1 = LOCATIONS[start_k]["coords"]
        p2 = LOCATIONS[end_k]["coords"]
        
        # 请求路由
        time.sleep(0.15) # 稍微延迟，确保OSRM不拒绝请求
        points = get_real_path(p1, p2)
        
        if etype == "ATTACK":
            plugins.AntPath(points, color="#b71c1c", weight=4, opacity=0.8, delay=800, pulse_color='white', tooltip=f"进攻: {start_k}->{end_k}").add_to(target)
        elif etype == "WATER":
            plugins.AntPath(points, color="#0277bd", weight=5, opacity=0.6, delay=1500, tooltip="水路").add_to(target)
        elif etype == "MOUNTAIN":
            folium.PolyLine(points, color="#5d4037", weight=3, opacity=0.9, dash_array='5, 8', tooltip="山路").add_to(target)
        elif etype == "ROAD":
            folium.PolyLine(points, color="#212121", weight=3, opacity=0.6, tooltip="官道").add_to(target)
        else:
            folium.PolyLine(points, color="#757575", weight=2, opacity=0.5, dash_array='4, 6', tooltip="战略连接").add_to(target)

    # 4. 绘制节点
    for key, data in LOCATIONS.items():
        if data.get("group") == "HIDDEN": continue
        target = groups.get(data["group"], groups["中原腹地"])
        style = STYLES.get(data["type"], STYLES["BASE"])
        
        folium.Marker(
            location=data["coords"],
            icon=folium.Icon(color="white", icon_color=style["color"], icon=style["icon"], prefix='fa'),
            tooltip=data["name"]
        ).add_to(target)
        
        folium.map.Marker(
            [data["coords"][0] - 0.25, data["coords"][1]],
            icon=DivIcon(
                icon_size=(150,36), icon_anchor=(75,0),
                html=f'''<div style="font-size: 9pt; font-family: 'Microsoft YaHei'; font-weight: 800; color: #212121; text-shadow: 2px 0 #fff, -2px 0 #fff, 0 2px #fff; text-align: center; pointer-events: none;">{data["name"]}</div>''',
            )
        ).add_to(target)

    # 5. 控件
    folium.LayerControl(collapsed=False).add_to(m)
    plugins.MiniMap(toggle_display=True, tile_layer=None, tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}', attr='Esri').add_to(m)
    plugins.MeasureControl().add_to(m)
    plugins.Search(layer=groups["九边重镇"], geom_type='Point', placeholder='搜索...', collapsed=True, search_label='tooltip').add_to(m)

    legend_html = """
     <div style="position: fixed; bottom: 30px; left: 20px; width: 150px; 
     border: 2px solid #5d4037; border-radius: 4px; z-index:9999; 
     font-family: 'Microsoft YaHei'; background-color: #fff3e0; opacity: 0.95; 
     padding: 10px; font-size:12px; box-shadow: 3px 3px 5px rgba(0,0,0,0.3);">
     <b style="display:block; border-bottom:1px solid #8d6e63; margin-bottom:5px; text-align:center; color:#5d4037">终极战略全图</b>
     <div><span style="color:#fbc02d; font-weight:bold;">~~~</span> 黄河</div>
     <div><span style="color:#0277bd; font-weight:bold;">===></span> 长江水路</div>
     <div><span style="color:#b71c1c; font-weight:bold;">---></span> 进攻路线</div>
     <div><span style="color:#5d4037; font-weight:bold;">- - -</span> 翻山/栈道</div>
     <div><span style="color:#212121; font-weight:bold;">——</span> 走廊/官道</div>
     </div>
     """
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save("ancient_china_map_all_links.html")
    print("生成完毕: ancient_china_map_all_links.html")

if __name__ == "__main__":
    create_all_links_map()
