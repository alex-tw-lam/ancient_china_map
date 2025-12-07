import folium
from folium import plugins
from folium.features import DivIcon
import requests
import time

# ==========================================
# 1. 核心样式配置
# ==========================================
STYLES = {
    "THREAT": {"color": "#b71c1c", "icon": "fire", "size": (30, 30), "area_color": "#ffcdd2"},
    "PASS":   {"color": "#e65100", "icon": "shield", "size": (24, 24), "area_color": "#ffe0b2"},
    "HUB":    {"color": "#f9a825", "icon": "crosshairs", "size": (22, 22), "area_color": "#fff9c4"},
    "CORE":   {"color": "#1b5e20", "icon": "star", "size": (26, 26), "area_color": "#c8e6c9"},
    "WATER":  {"color": "#0277bd", "icon": "tint", "size": (20, 20), "area_color": "#b3e5fc"},
    "BASE":   {"color": "#616161", "icon": "map-marker", "size": (16, 16), "area_color": "#eeeeee"}
}

# ==========================================
# 2. 地理节点 (坐标微调以匹配路网)
# ==========================================
LOCATIONS = {
    # --- 北方威胁 ---
    # 调整坐标到路网可达处 (如二连浩特附近代表蒙古入口)
    "Mongolia":  {"name": "蒙古高原", "coords": [43.65, 111.97], "type": "THREAT", "group": "北方威胁", "radius": 150000},
    "Manchuria": {"name": "女真/辽东", "coords": [41.8, 123.4], "type": "THREAT", "group": "北方威胁", "radius": 120000},
    
    # --- 核心区 ---
    "Guanzhong": {"name": "关中(长安)", "coords": [34.26, 108.95], "type": "CORE", "group": "核心腹地", "radius": 80000},
    "Hangu":     {"name": "函谷关", "coords": [34.63, 110.9], "type": "PASS", "group": "核心腹地", "radius": 0},
    "CentralPlains": {"name": "中原(洛阳)", "coords": [34.66, 112.4], "type": "CORE", "group": "中原腹地", "radius": 70000},

    # --- 西北 ---
    "Xiyu":     {"name": "西域(敦煌)", "coords": [40.14, 94.66], "type": "BASE", "group": "西北走廊", "radius": 0},
    "Hexi":     {"name": "河西走廊", "coords": [38.93, 100.45], "type": "HUB", "group": "西北走廊", "radius": 60000},
    "Longxi":   {"name": "陇西", "coords": [35.5, 104.6], "type": "HUB", "group": "西北走廊", "radius": 0},
    "Hetao":    {"name": "河套平原", "coords": [40.8, 107.5], "type": "THREAT", "group": "西北走廊", "radius": 80000},

    # --- 山西/九边 ---
    "Datong":   {"name": "大同", "coords": [40.07, 113.3], "type": "HUB", "group": "九边重镇", "radius": 0},
    "Yanmen":   {"name": "雁门关", "coords": [39.18, 112.88], "type": "PASS", "group": "九边重镇", "radius": 0},
    "Taiyuan":  {"name": "太原", "coords": [37.87, 112.54], "type": "CORE", "group": "九边重镇", "radius": 40000},
    "Hedong":   {"name": "河东高地", "coords": [36.08, 111.51], "type": "HUB", "group": "九边重镇", "radius": 0},

    # --- 京师/东北 ---
    "Xuanfu":   {"name": "宣府", "coords": [40.6, 115.0], "type": "HUB", "group": "九边重镇", "radius": 0},
    "Juyong":   {"name": "居庸关", "coords": [40.28, 116.06], "type": "PASS", "group": "九边重镇", "radius": 0},
    "Shanhai":  {"name": "山海关", "coords": [40.00, 119.75], "type": "PASS", "group": "九边重镇", "radius": 0},
    "Liaodong": {"name": "辽西走廊", "coords": [40.6, 120.8], "type": "BASE", "group": "九边重镇", "radius": 0},
    "Beijing":  {"name": "北京", "coords": [39.90, 116.40], "type": "CORE", "group": "九边重镇", "radius": 40000},

    # --- 南方关键点 ---
    "Hanzhong":  {"name": "汉中", "coords": [33.07, 107.02], "type": "HUB", "group": "西南防线", "radius": 40000},
    "Bashu":     {"name": "巴蜀(成都)", "coords": [30.66, 104.06], "type": "CORE", "group": "西南防线", "radius": 100000},
    "Diaoyu":    {"name": "钓鱼城", "coords": [30.00, 106.27], "type": "PASS", "group": "西南防线", "radius": 0},
    
    "Xiangyang": {"name": "襄阳", "coords": [32.01, 112.12], "type": "HUB", "group": "中翼防线", "radius": 0},
    "Jiangling": {"name": "江陵(荆州)", "coords": [30.33, 112.23], "type": "HUB", "group": "中翼防线", "radius": 0},
    "Jianghuai": {"name": "江淮(合肥)", "coords": [31.86, 117.28], "type": "HUB", "group": "东南防线", "radius": 60000},
    "Jiangnan":  {"name": "江南(南京)", "coords": [32.06, 118.79], "type": "CORE", "group": "东南防线", "radius": 90000},

    # --- 辅助水路节点 (不显示图标，仅用于生成弯曲路径) ---
    "Wuhan":     {"name": "武汉(水路点)", "coords": [30.59, 114.30], "type": "WATER", "group": "HIDDEN", "radius": 0},
    "Jiujiang":  {"name": "九江(水路点)", "coords": [29.70, 115.99], "type": "WATER", "group": "HIDDEN", "radius": 0},
}

# ==========================================
# 3. 路由算法 (OSRM)
# ==========================================
def get_route_points(p1_coords, p2_coords):
    """
    通过 OSRM 获取两点间真实地形路径
    """
    start = f"{p1_coords[1]},{p1_coords[0]}"
    end = f"{p2_coords[1]},{p2_coords[0]}"
    url = f"http://router.project-osrm.org/route/v1/driving/{start};{end}?overview=full&geometries=geojson"
    
    try:
        # 添加 User-Agent 防止被某些防火墙拦截
        headers = {'User-Agent': 'AncientChinaMapGenerator/1.0'}
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data['code'] == 'Ok':
                # GeoJSON returns [lon, lat], folium needs [lat, lon]
                return [[p[1], p[0]] for p in data['routes'][0]['geometry']['coordinates']]
    except Exception as e:
        print(f"路由获取失败: {e}")
    
    # 降级方案：直线
    return [p1_coords, p2_coords]

# ==========================================
# 4. 连线定义 (全覆盖)
# ==========================================
# 逻辑: (起点, 终点, 类型, 分组)
EDGES = [
    # --- 1. 丝绸之路 (山谷走廊) ---
    ("Xiyu", "Hexi", "ROAD", "西北走廊"),
    ("Hexi", "Longxi", "ROAD", "西北走廊"),
    ("Longxi", "Guanzhong", "MOUNTAIN", "西北走廊"), # 翻越陇坂

    # --- 2. 北方入侵 (骑兵路线) ---
    # 蒙古 -> 大同 (翻越阴山余脉)
    ("Mongolia", "Datong", "ATTACK", "北方威胁"),
    # 蒙古 -> 宣府 -> 居庸关 -> 北京 (直逼京师)
    ("Mongolia", "Xuanfu", "ATTACK", "北方威胁"),
    ("Xuanfu", "Juyong", "ATTACK", "九边重镇"),
    ("Juyong", "Beijing", "ATTACK", "九边重镇"),
    # 河套 -> 关中 (秦直道方向)
    ("Hetao", "Guanzhong", "ATTACK", "西北走廊"),
    
    # --- 3. 东北走廊 (辽西走廊) ---
    ("Manchuria", "Liaodong", "ATTACK", "北方威胁"),
    ("Liaodong", "Shanhai", "ATTACK", "九边重镇"), # 紧贴海岸线
    ("Shanhai", "Beijing", "ROAD", "九边重镇"),

    # --- 4. 山西脊梁 ---
    ("Datong", "Yanmen", "MOUNTAIN", "九边重镇"),
    ("Yanmen", "Taiyuan", "ROAD", "九边重镇"),
    ("Taiyuan", "Hedong", "ROAD", "九边重镇"),
    ("Hedong", "Guanzhong", "ATTACK", "九边重镇"), # 渡河
    ("Hedong", "CentralPlains", "ATTACK", "九边重镇"), # 太行八陉

    # --- 5. 内部交通 (崤函古道) ---
    ("Guanzhong", "Hangu", "ROAD", "核心腹地"),
    ("Hangu", "CentralPlains", "ROAD", "核心腹地"),
    ("Beijing", "CentralPlains", "STRATEGY", "中原腹地"),

    # --- 6. 蜀道难 (秦岭穿越) ---
    ("Guanzhong", "Hanzhong", "MOUNTAIN", "西南防线"), # 穿越秦岭
    ("Hanzhong", "Bashu", "MOUNTAIN", "西南防线"),     # 金牛道

    # --- 7. 长江水路 (分段拟合) ---
    # 巴蜀 -> 钓鱼城 -> 江陵 -> 武汉 -> 九江 -> 南京
    ("Bashu", "Diaoyu", "WATER", "西南防线"), # 嘉陵江/长江
    ("Diaoyu", "Jiangling", "WATER", "中翼防线"),
    ("Jiangling", "Wuhan", "WATER", "中翼防线"), # 增加中间点以获得曲线
    ("Wuhan", "Jiujiang", "WATER", "东南防线"),
    ("Jiujiang", "Jiangnan", "WATER", "东南防线"),

    # --- 8. 南方陆路防线 ---
    ("CentralPlains", "Xiangyang", "ATTACK", "中翼防线"),
    ("Xiangyang", "Jiangling", "ROAD", "中翼防线"),
    ("CentralPlains", "Jianghuai", "ATTACK", "东南防线"),
    ("Jianghuai", "Jiangnan", "STRATEGY", "东南防线"),
]

def create_real_terrain_map():
    print("正在初始化地图...")
    m = folium.Map(location=[35.5, 108.0], zoom_start=5, tiles=None)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}',
        attr='Esri', name='山川地形图', control=True
    ).add_to(m)

    # 建立图层组
    groups = {}
    for name in ["北方威胁", "核心腹地", "九边重镇", "西北走廊", "中原腹地", "西南防线", "中翼防线", "东南防线"]:
        groups[name] = folium.FeatureGroup(name=name)
        m.add_child(groups[name])

    # 1. 绘制区域 (Circles)
    for key, data in LOCATIONS.items():
        if data.get("group") != "HIDDEN" and data.get("radius", 0) > 0:
            folium.Circle(
                location=data["coords"], radius=data["radius"],
                color=STYLES[data["type"]]["color"], weight=1,
                fill=True, fill_color=STYLES[data["type"]]["area_color"], fill_opacity=0.15
            ).add_to(groups[data["group"]])

    # 2. 计算并绘制路径 (核心步骤)
    print(f"正在计算 {len(EDGES)} 条真实地理路径 (OSRM)...")
    
    for start_key, end_key, etype, gname in EDGES:
        if gname not in groups: continue
        
        p1 = LOCATIONS[start_key]["coords"]
        p2 = LOCATIONS[end_key]["coords"]
        target_layer = groups[gname]

        # 核心逻辑：所有类型都尝试获取真实地形路径
        # 对于水路，我们通过连接沿江城市并使用 OSRM (驾车模式通常沿江公路) 来模拟河流弯曲
        time.sleep(0.1) # 礼貌延迟
        points = get_route_points(p1, p2)
        
        # 样式应用
        if etype == "ATTACK":
            # 红色流光 (进攻)
            plugins.AntPath(points, color="#d50000", weight=4, opacity=0.8, delay=800, pulse_color='white', tooltip=f"进攻: {start_key}->{end_key}").add_to(target_layer)
        elif etype == "WATER":
            # 蓝色流光 (水路) - 宽线
            plugins.AntPath(points, color="#0277bd", weight=5, opacity=0.6, delay=1500, reverse=False, tooltip="长江水道").add_to(target_layer)
        elif etype == "MOUNTAIN":
            # 棕色虚线 (栈道/翻山)
            folium.PolyLine(points, color="#5d4037", weight=3, opacity=0.9, dash_array='5, 8', tooltip="险峻山路").add_to(target_layer)
        elif etype == "ROAD":
            # 黑色实线 (官道/走廊)
            folium.PolyLine(points, color="#212121", weight=3, opacity=0.6, tooltip="主要通道").add_to(target_layer)
        else:
            # 灰色虚线 (战略联系)
            folium.PolyLine(points, color="#757575", weight=2, opacity=0.5, dash_array='4, 6').add_to(target_layer)

    # 3. 绘制节点与标签
    for key, data in LOCATIONS.items():
        if data.get("group") == "HIDDEN": continue
        
        target_layer = groups.get(data["group"], groups["中原腹地"])
        style = STYLES.get(data["type"], STYLES["BASE"])
        
        # 图标
        folium.Marker(
            location=data["coords"],
            icon=folium.Icon(color="white", icon_color=style["color"], icon=style["icon"], prefix='fa'),
            tooltip=data["name"]
        ).add_to(target_layer)
        
        # 文字
        folium.map.Marker(
            [data["coords"][0] - 0.25, data["coords"][1]],
            icon=DivIcon(
                icon_size=(150,36), icon_anchor=(75,0),
                html=f'''<div style="font-size: 10pt; font-family: 'Microsoft YaHei'; font-weight: 800; color: #212121; text-shadow: 2px 0 #fff, -2px 0 #fff, 0 2px #fff; text-align: center; pointer-events: none;">{data["name"]}</div>''',
            )
        ).add_to(target_layer)

    # 4. 控件
    folium.LayerControl(collapsed=False).add_to(m)
    plugins.MiniMap(toggle_display=True, tile_layer=None, tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}', attr='Esri').add_to(m)
    plugins.MeasureControl().add_to(m)

    # 5. 图例
    legend_html = """
     <div style="position: fixed; bottom: 30px; left: 20px; width: 150px; 
     border: 2px solid #5d4037; border-radius: 4px; z-index:9999; 
     font-family: 'Microsoft YaHei'; background-color: #fff3e0; opacity: 0.95; 
     padding: 10px; font-size:12px; box-shadow: 3px 3px 5px rgba(0,0,0,0.3);">
     <b style="display:block; border-bottom:1px solid #8d6e63; margin-bottom:5px; text-align:center; color:#5d4037">真实地形战略图</b>
     <div><span style="color:#d50000; font-weight:bold;">---></span> 真实进攻路线</div>
     <div><span style="color:#0277bd; font-weight:bold;">===></span> 长江拟合水路</div>
     <div><span style="color:#5d4037; font-weight:bold;">- - -</span> 翻山/栈道</div>
     <div><span style="color:#212121; font-weight:bold;">——</span> 走廊/官道</div>
     <div style="margin-top:5px; color:#666">* 所有路线均基于<br>真实地形/路网计算</div>
     </div>
     """
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save("ancient_china_real_terrain.html")
    print("生成完成: ancient_china_real_terrain.html")

if __name__ == "__main__":
    create_real_terrain_map()
