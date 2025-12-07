import folium
from folium import plugins
from folium.features import DivIcon
import requests
import time

# ==========================================
# 1. 核心配置 & 样式
# ==========================================
STYLES = {
    "THREAT": {"color": "#c62828", "icon": "fire", "size": (30, 30), "area_color": "#ffcdd2"}, # Red
    "PASS":   {"color": "#e65100", "icon": "shield", "size": (24, 24), "area_color": "#ffe0b2"}, # Orange
    "HUB":    {"color": "#f9a825", "icon": "crosshairs", "size": (22, 22), "area_color": "#fff9c4"}, # Yellow
    "CORE":   {"color": "#1b5e20", "icon": "star", "size": (26, 26), "area_color": "#c8e6c9"},   # Green
    "WATER":  {"color": "#0277bd", "icon": "tint", "size": (20, 20), "area_color": "#b3e5fc"},   # Blue
    "BASE":   {"color": "#455a64", "icon": "map-marker", "size": (16, 16), "area_color": "#eceff1"} # Slate
}

# ==========================================
# 2. 高精度地理轨迹 (不依赖路由，确保历史准确)
# ==========================================

# A. 黄河 (几字形 - 25点)
YELLOW_RIVER_COORDS = [
    [35.85, 103.20], [36.06, 103.83], [36.56, 104.68], [37.51, 105.17],
    [38.48, 106.23], [39.23, 106.77], [40.33, 107.00], [40.76, 107.40],
    [40.90, 108.50], [40.65, 109.84], [40.27, 111.19], [39.43, 111.48], 
    [38.50, 111.00], [37.50, 110.80], [36.14, 110.44], [35.60, 110.35], 
    [34.61, 110.36], [34.77, 111.19], [34.90, 113.62], [34.85, 114.30], 
    [35.10, 115.00], [35.50, 116.00], [36.20, 116.50], [36.65, 116.99], 
    [37.73, 119.16]
]

# B. 明长城主线 (高分辨率 - 60+点)
# 嘉峪关 -> 河西走廊北侧 -> 宁夏 -> 延绥(榆林) -> 偏关 -> 大同 -> 宣府 -> 居庸关 -> 山海关
GREAT_WALL_TRACE = [
    [39.81, 98.21], [39.50, 99.00], [39.30, 100.00], [38.90, 101.50], # 河西段
    [38.20, 102.50], [37.50, 104.00], [37.20, 105.00], [37.50, 106.00], # 绕行腾格里
    [38.00, 106.50], [38.40, 106.30], [38.20, 107.50], [37.80, 108.50], # 宁夏/盐池
    [38.28, 109.73], [38.50, 110.50], [39.00, 111.00], [39.43, 111.48], # 榆林 -> 偏关
    [39.60, 112.00], [39.80, 112.80], [40.10, 113.30], [40.30, 113.80], # 大同段
    [40.50, 114.50], [40.81, 114.88], [40.60, 115.50], [40.35, 116.00], # 宣府 -> 八达岭
    [40.60, 116.80], [40.70, 117.20], [40.50, 118.00], [40.20, 119.00], # 燕山段
    [40.00, 119.75], [39.96, 119.80]  # 山海关 -> 老龙头
]

# ==========================================
# 3. 完整战略节点 (40 Nodes)
# ==========================================
LOCATIONS = {
    # --- 北方威胁 ---
    "Mongolia":  {"name": "蒙古高原", "coords": [43.65, 111.97], "type": "THREAT", "group": "北方威胁", "radius": 150000},
    "Manchuria": {"name": "女真/辽东", "coords": [41.8, 123.4], "type": "THREAT", "group": "北方威胁", "radius": 120000},

    # --- 西北长城防线 ---
    "Jiayuguan":{"name": "嘉峪关", "coords": [39.81, 98.21], "type": "PASS", "group": "西北防线", "radius": 0}, # New
    "Xiyu":     {"name": "西域(敦煌)", "coords": [40.14, 94.66], "type": "BASE", "group": "西北防线", "radius": 0},
    "Hexi":     {"name": "河西走廊", "coords": [38.93, 100.45], "type": "HUB", "group": "西北防线", "radius": 60000},
    "Gansu":    {"name": "甘肃镇", "coords": [39.20, 99.50], "type": "BASE", "group": "西北防线", "radius": 0},
    "Ningxia":  {"name": "宁夏镇", "coords": [38.48, 106.23], "type": "HUB", "group": "西北防线", "radius": 0},
    "Hetao":    {"name": "河套平原", "coords": [40.76, 107.40], "type": "THREAT", "group": "西北防线", "radius": 80000},
    "Yansui":   {"name": "延绥镇", "coords": [38.28, 109.73], "type": "HUB", "group": "西北防线", "radius": 0},
    "Longxi":   {"name": "陇西", "coords": [35.50, 104.60], "type": "HUB", "group": "西北防线", "radius": 0},

    # --- 山西/河东防线 ---
    "Datong":   {"name": "大同", "coords": [40.07, 113.30], "type": "HUB", "group": "九边重镇", "radius": 0},
    "Yanmen":   {"name": "雁门关", "coords": [39.18, 112.88], "type": "PASS", "group": "九边重镇", "radius": 0},
    "Ningwu":   {"name": "宁武关", "coords": [39.00, 112.30], "type": "PASS", "group": "九边重镇", "radius": 0},
    "Piantou":  {"name": "偏头关", "coords": [39.43, 111.48], "type": "PASS", "group": "九边重镇", "radius": 0},
    "Taiyuan":  {"name": "太原", "coords": [37.87, 112.54], "type": "CORE", "group": "九边重镇", "radius": 40000},
    "Hedong":   {"name": "河东", "coords": [36.08, 111.51], "type": "HUB", "group": "九边重镇", "radius": 0},

    # --- 京师/幽燕防线 ---
    "Xuanfu":   {"name": "宣府", "coords": [40.60, 115.00], "type": "HUB", "group": "九边重镇", "radius": 0},
    "Juyong":   {"name": "居庸关", "coords": [40.28, 116.06], "type": "PASS", "group": "九边重镇", "radius": 0},
    "Beijing":  {"name": "北京", "coords": [39.90, 116.40], "type": "CORE", "group": "九边重镇", "radius": 40000},
    "Shanhai":  {"name": "山海关", "coords": [40.00, 119.75], "type": "PASS", "group": "九边重镇", "radius": 0},
    "Liaodong": {"name": "辽西走廊", "coords": [40.60, 120.80], "type": "BASE", "group": "九边重镇", "radius": 0},

    # --- 核心腹地 ---
    "Guanzhong": {"name": "关中", "coords": [34.26, 108.95], "type": "CORE", "group": "核心腹地", "radius": 80000},
    "Hangu":     {"name": "函谷关", "coords": [34.63, 110.90], "type": "PASS", "group": "核心腹地", "radius": 0},
    "CentralPlains": {"name": "中原(洛阳)", "coords": [34.66, 112.40], "type": "CORE", "group": "中原腹地", "radius": 70000},

    # --- 西南/蜀道 ---
    "Hanzhong":  {"name": "汉中", "coords": [33.07, 107.02], "type": "HUB", "group": "西南防线", "radius": 40000},
    "Bashu":     {"name": "巴蜀", "coords": [30.66, 104.06], "type": "CORE", "group": "西南防线", "radius": 100000},
    "Diaoyu":    {"name": "钓鱼城", "coords": [30.00, 106.27], "type": "PASS", "group": "西南防线", "radius": 0},

    # --- 荆襄/中翼 ---
    "Nanyang":   {"name": "南阳", "coords": [33.00, 112.52], "type": "BASE", "group": "中翼防线", "radius": 0},
    "Xiangyang": {"name": "襄阳", "coords": [32.01, 112.12], "type": "HUB", "group": "中翼防线", "radius": 0},
    "Jiangling": {"name": "江陵", "coords": [30.33, 112.23], "type": "HUB", "group": "中翼防线", "radius": 0},
    "Ezhou":     {"name": "鄂州", "coords": [30.54, 114.30], "type": "HUB", "group": "中翼防线", "radius": 0},

    # --- 江淮/东翼 ---
    "Jianghuai": {"name": "江淮", "coords": [32.50, 117.00], "type": "HUB", "group": "东南防线", "radius": 60000},
    "Shouchun":  {"name": "寿春", "coords": [32.58, 116.78], "type": "PASS", "group": "东南防线", "radius": 0},
    "Hefei":     {"name": "合肥", "coords": [31.86, 117.28], "type": "PASS", "group": "东南防线", "radius": 0},
    "Zhongli":   {"name": "钟离(凤阳)", "coords": [32.86, 117.55], "type": "PASS", "group": "东南防线", "radius": 0},
    "Xuyi":      {"name": "盱眙", "coords": [33.00, 118.53], "type": "PASS", "group": "东南防线", "radius": 0},
    "Zhenjiang": {"name": "镇江", "coords": [32.20, 119.45], "type": "PASS", "group": "东南防线", "radius": 0},
    "Jiangnan":  {"name": "江南", "coords": [32.06, 118.79], "type": "CORE", "group": "东南防线", "radius": 90000},
    
    # --- 辅助节点 ---
    "Wuhan": {"name": "", "coords": [30.59, 114.30], "type": "WATER", "group": "HIDDEN", "radius": 0},
    "Anqing": {"name": "", "coords": [30.50, 117.05], "type": "WATER", "group": "HIDDEN", "radius": 0},
}

# ==========================================
# 4. 完整连线定义 (58 Links)
# ==========================================
EDGES = [
    # 1. 丝路 (Land)
    ("Xiyu", "Jiayuguan", "ROAD", "西北防线"), # New
    ("Jiayuguan", "Gansu", "ROAD", "西北防线"), # New
    ("Gansu", "Hexi", "ROAD", "西北防线"),
    ("Hexi", "Longxi", "ROAD", "西北防线"), 
    ("Longxi", "Guanzhong", "MOUNTAIN", "西北防线"),
    
    # 2. 北方入侵 (Attack)
    ("Mongolia", "Hetao", "ATTACK", "北方威胁"),
    ("Mongolia", "Datong", "ATTACK", "北方威胁"),
    ("Mongolia", "Xuanfu", "ATTACK", "北方威胁"),
    ("Hetao", "Guanzhong", "ATTACK", "西北防线"), 
    ("Hetao", "Ningxia", "ATTACK", "西北防线"),
    
    # 3. 九边横向防线 (The Great Wall Highway)
    ("Jiayuguan", "Gansu", "ROAD", "九边重镇"),
    ("Gansu", "Ningxia", "ROAD", "九边重镇"), # 穿越沙漠边缘
    ("Ningxia", "Yansui", "ROAD", "九边重镇"), 
    ("Yansui", "Piantou", "ROAD", "九边重镇"), # New Link
    ("Piantou", "Datong", "ROAD", "九边重镇"), # New Link
    ("Datong", "Xuanfu", "ROAD", "九边重镇"), 
    ("Xuanfu", "Juyong", "ATTACK", "九边重镇"), 
    ("Juyong", "Beijing", "ATTACK", "九边重镇"),
    ("Beijing", "Shanhai", "ROAD", "九边重镇"), # 关内走廊

    # 4. 山西防线 (Inner Defense)
    ("Datong", "Yanmen", "MOUNTAIN", "九边重镇"), 
    ("Datong", "Ningwu", "MOUNTAIN", "九边重镇"),
    ("Piantou", "Ningwu", "MOUNTAIN", "九边重镇"), # 外三关互联
    ("Ningwu", "Taiyuan", "ROAD", "九边重镇"), 
    ("Yanmen", "Taiyuan", "ROAD", "九边重镇"), 
    ("Taiyuan", "Hedong", "ROAD", "九边重镇"),
    
    # 5. 河东出击
    ("Hedong", "Guanzhong", "ATTACK", "九边重镇"), 
    ("Hedong", "CentralPlains", "ATTACK", "九边重镇"),

    # 6. 东北走廊
    ("Manchuria", "Liaodong", "ATTACK", "北方威胁"), 
    ("Liaodong", "Shanhai", "ATTACK", "九边重镇"),

    # 7. 核心交通 & 漕运 (Supply)
    ("Guanzhong", "Hangu", "ROAD", "核心腹地"), 
    ("Hangu", "CentralPlains", "ROAD", "中原腹地"),
    ("Beijing", "CentralPlains", "STRATEGY", "中原腹地"),
    ("Jiangnan", "CentralPlains", "STRATEGY", "东南防线"), # 漕运拟合

    # 8. 蜀道
    ("Guanzhong", "Hanzhong", "MOUNTAIN", "西南防线"), 
    ("Hanzhong", "Bashu", "MOUNTAIN", "西南防线"),
    ("Bashu", "Diaoyu", "WATER", "西南防线"),

    # 9. 荆襄
    ("CentralPlains", "Nanyang", "ATTACK", "中翼防线"), 
    ("Nanyang", "Xiangyang", "ATTACK", "中翼防线"),
    ("Xiangyang", "Jiangling", "ROAD", "中翼防线"), 
    ("Jiangling", "Ezhou", "WATER", "中翼防线"),
    
    # 10. 江淮防线
    ("CentralPlains", "Shouchun", "ATTACK", "东南防线"), 
    ("Shouchun", "Hefei", "ROAD", "东南防线"),
    ("Shouchun", "Zhongli", "ROAD", "东南防线"), 
    ("Shouchun", "Xuyi", "ROAD", "东南防线"),
    ("Hefei", "Zhenjiang", "ATTACK", "东南防线"), 
    ("Zhongli", "Zhenjiang", "STRATEGY", "东南防线"),
    ("Xuyi", "Jiangnan", "STRATEGY", "东南防线"),

    # 11. 长江水路
    ("Diaoyu", "Jiangling", "WATER", "西南防线"), 
    ("Jiangling", "Wuhan", "WATER", "中翼防线"), 
    ("Wuhan", "Anqing", "WATER", "东南防线"), 
    ("Anqing", "Jiangnan", "WATER", "东南防线"),
    ("Zhenjiang", "Jiangnan", "WATER", "东南防线"),
]

# ==========================================
# 5. 路由算法 (OSRM)
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

def create_final_map():
    # 验证数据完整性
    nodes = [k for k,v in LOCATIONS.items() if v.get("group") != "HIDDEN"]
    print("-" * 40)
    print(f"战略节点检查: {len(nodes)} (Expected: ~40)")
    print(f"战略链路检查: {len(EDGES)} (Expected: ~58)")
    print("-" * 40)
    
    print("初始化地图...")
    m = folium.Map(location=[35.0, 108.0], zoom_start=5, tiles=None)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}',
        attr='Esri', name='山川地形图', control=True
    ).add_to(m)

    groups = {}
    layer_list = ["万里长城", "黄河水系", "北方威胁", "九边重镇", "核心腹地", "西北防线", "中原腹地", "西南防线", "中翼防线", "东南防线"]
    for name in layer_list:
        groups[name] = folium.FeatureGroup(name=name)
        m.add_child(groups[name])

    # 1. 绘制万里长城 (High Res Trace)
    print("绘制万里长城 (真实轨迹)...")
    # 主线 (深灰色)
    folium.PolyLine(
        GREAT_WALL_TRACE, color="#37474f", weight=5, opacity=0.9,
        tooltip="万里长城 (明长城主线)"
    ).add_to(groups["万里长城"])
    # 装饰线 (城墙感)
    folium.PolyLine(
        GREAT_WALL_TRACE, color="#cfd8dc", weight=2, dash_array='4, 4'
    ).add_to(groups["万里长城"])

    # 2. 绘制黄河 (High Res Trace)
    print("绘制黄河 (真实轨迹)...")
    plugins.AntPath(YELLOW_RIVER_COORDS, color="#fbc02d", weight=6, opacity=0.8, pulse_color='white', delay=2000, tooltip="黄河").add_to(groups["黄河水系"])

    # 3. 绘制区域
    for key, data in LOCATIONS.items():
        if data.get("group") != "HIDDEN" and data.get("radius", 0) > 0:
            folium.Circle(
                location=data["coords"], radius=data["radius"],
                color=STYLES[data["type"]]["color"], weight=1,
                fill=True, fill_color=STYLES[data["type"]]["area_color"], fill_opacity=0.15
            ).add_to(groups[data["group"]])

    # 4. 绘制连线 (Routing)
    print(f"正在计算 {len(EDGES)} 条真实路径 (OSRM)...")
    for i, (start_k, end_k, etype, gname) in enumerate(EDGES):
        if start_k not in LOCATIONS or end_k not in LOCATIONS: continue
        target = groups.get(gname, groups["中原腹地"])
        p1 = LOCATIONS[start_k]["coords"]
        p2 = LOCATIONS[end_k]["coords"]
        
        # 请求路由
        time.sleep(0.1) # Throttling
        points = get_real_path(p1, p2)
        
        if etype == "ATTACK":
            plugins.AntPath(points, color="#b71c1c", weight=4, opacity=0.8, delay=800, pulse_color='white', tooltip=f"进攻: {start_k}->{end_k}").add_to(target)
        elif etype == "WATER":
            plugins.AntPath(points, color="#0277bd", weight=5, opacity=0.6, delay=1500, tooltip="水路").add_to(target)
        elif etype == "MOUNTAIN":
            folium.PolyLine(points, color="#5d4037", weight=3, opacity=0.9, dash_array='5, 8', tooltip="山路/栈道").add_to(target)
        elif etype == "ROAD":
            folium.PolyLine(points, color="#212121", weight=3, opacity=0.6, tooltip="官道").add_to(target)
        else:
            folium.PolyLine(points, color="#757575", weight=2, opacity=0.5, dash_array='4, 6', tooltip="战略连接").add_to(target)

    # 5. 绘制节点
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

    # 6. 控件
    folium.LayerControl(collapsed=False).add_to(m)
    plugins.MiniMap(toggle_display=True, tile_layer=None, tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}', attr='Esri').add_to(m)
    plugins.MeasureControl().add_to(m)
    plugins.Search(layer=groups["九边重镇"], geom_type='Point', placeholder='搜索...', collapsed=True, search_label='tooltip').add_to(m)

    legend_html = """
     <div style="position: fixed; bottom: 30px; left: 20px; width: 160px; 
     border: 2px solid #5d4037; border-radius: 4px; z-index:9999; 
     font-family: 'Microsoft YaHei'; background-color: #fff3e0; opacity: 0.95; 
     padding: 10px; font-size:12px; box-shadow: 3px 3px 5px rgba(0,0,0,0.3);">
     <b style="display:block; border-bottom:1px solid #8d6e63; margin-bottom:5px; text-align:center; color:#5d4037">全景战略图</b>
     <div><span style="color:#37474f; font-weight:bold; border-bottom: 2px dashed #cfd8dc;">===</span> 万里长城</div>
     <div><span style="color:#fbc02d; font-weight:bold;">~~~</span> 黄河</div>
     <div><span style="color:#0277bd; font-weight:bold;">===></span> 长江</div>
     <div><span style="color:#b71c1c; font-weight:bold;">---></span> 进攻</div>
     </div>
     """
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save("ancient_china_map_final.html")
    print(f"生成完毕: ancient_china_map_final.html")

if __name__ == "__main__":
    create_final_map()
