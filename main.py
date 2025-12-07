import folium
from folium import plugins
from folium.features import DivIcon
import requests
import time
import math

# ==========================================
# 1. 核心配置
# ==========================================
STYLES = {
    "THREAT": {"color": "#d50000", "icon": "fire"},
    "PASS":   {"color": "#e65100", "icon": "shield"},
    "HUB":    {"color": "#f9a825", "icon": "crosshairs"},
    "CORE":   {"color": "#1b5e20", "icon": "star"},
    "WATER":  {"color": "#0277bd", "icon": "tint"},
    "BASE":   {"color": "#616161", "icon": "map-marker"}
}

LOCATIONS = {
    # --- 北方 ---
    "Mongolia":  {"coords": [44.0, 111.0], "type": "THREAT", "name": "蒙古高原"},
    "Manchuria": {"coords": [41.8, 123.4], "type": "THREAT", "name": "辽东/女真"},
    "Xiyu":      {"coords": [40.1, 94.6], "type": "BASE", "name": "西域(敦煌)"},
    
    # --- 西北 ---
    "Hexi":      {"coords": [39.0, 100.5], "type": "HUB", "name": "河西走廊"}, # 张掖附近
    "Longxi":    {"coords": [35.5, 104.6], "type": "HUB", "name": "陇西"},
    "Hetao":     {"coords": [40.8, 107.5], "type": "THREAT", "name": "河套平原"},
    
    # --- 核心 ---
    "Guanzhong": {"coords": [34.26, 108.9], "type": "CORE", "name": "关中(长安)"}, # 西安
    "Hangu":     {"coords": [34.63, 110.30], "type": "PASS", "name": "函谷关"},    # 灵宝
    
    # --- 山西/九边 ---
    "Datong":    {"coords": [40.07, 113.3], "type": "HUB", "name": "大同"},
    "Yanmen":    {"coords": [39.18, 112.88], "type": "PASS", "name": "雁门关"},
    "Taiyuan":   {"coords": [37.87, 112.54], "type": "CORE", "name": "太原"},
    "Hedong":    {"coords": [36.10, 111.5], "type": "HUB", "name": "河东(临汾)"}, # 临汾更适合代表河东腹地

    # --- 幽燕 ---
    "Xuanfu":    {"coords": [40.6, 115.0], "type": "HUB", "name": "宣府"},
    "Juyong":    {"coords": [40.28, 116.06], "type": "PASS", "name": "居庸关"},
    "Shanhai":   {"coords": [40.00, 119.75], "type": "PASS", "name": "山海关"},
    "Beijing":   {"coords": [39.90, 116.40], "type": "CORE", "name": "北京"},
    "Liaodong":  {"coords": [41.1, 121.1], "type": "BASE", "name": "辽西走廊"},

    # --- 南方/腹地 ---
    "CentralPlains": {"coords": [34.7, 113.3], "type": "CORE", "name": "中原(洛阳)"}, # 郑州/洛阳
    "Hanzhong":      {"coords": [33.07, 107.02], "type": "HUB", "name": "汉中"},
    "Bashu":         {"coords": [30.6, 104.0], "type": "CORE", "name": "巴蜀(成都)"},
    "Diaoyu":        {"coords": [30.0, 106.27], "type": "PASS", "name": "钓鱼城"},
    "Xiangyang":     {"coords": [32.01, 112.12], "type": "HUB", "name": "襄阳"},
    "Jiangling":     {"coords": [30.35, 112.19], "type": "HUB", "name": "江陵(荆州)"},
    "Jianghuai":     {"coords": [32.5, 117.0], "type": "HUB", "name": "江淮"},
    "Yangtze":       {"coords": [30.5, 117.0], "type": "WATER", "name": "长江防线(安庆)"},
    "Jiangnan":      {"coords": [32.0, 118.8], "type": "CORE", "name": "江南(南京)"}
}

# ==========================================
# 2. 路由算法 (获取真实地理路径)
# ==========================================
def get_real_path(start_coords, end_coords, mode='driving'):
    """
    使用 OSRM 公共 API 获取两点之间的真实路径坐标。
    mode: 'driving' (沿公路/河谷), 'walking' (更直/翻山)
    """
    # OSRM 使用 [lon, lat] 格式
    p1 = f"{start_coords[1]},{start_coords[0]}"
    p2 = f"{end_coords[1]},{end_coords[0]}"
    
    url = f"http://router.project-osrm.org/route/v1/{mode}/{p1};{p2}?overview=full&geometries=geojson"
    
    try:
        r = requests.get(url, timeout=2)
        if r.status_code == 200:
            data = r.json()
            if data['code'] == 'Ok':
                # OSRM 返回的是 [lon, lat]，Folium 需要 [lat, lon]
                coords_lonlat = data['routes'][0]['geometry']['coordinates']
                coords_latlon = [[p[1], p[0]] for p in coords_lonlat]
                return coords_latlon
    except:
        print(f"Routing failed for {p1} to {p2}, using straight line.")
    
    # 失败回退到直线
    return [start_coords, end_coords]

# 长江稍微特殊，汽车不能开在水里，我们手动增加中间点模拟弯曲，或者使用直线
# 为了演示，我们对水路使用直线，对陆路使用路由

# ==========================================
# 3. 连线定义
# ==========================================
# (Start, End, Type)
RAW_EDGES = [
    # 丝路与西北 (地形极其明显，必须路由)
    ("Xiyu", "Hexi", "ROAD"), ("Hexi", "Longxi", "ROAD"), ("Longxi", "Guanzhong", "MOUNTAIN"),
    
    # 关中四塞
    ("Guanzhong", "Hangu", "ROAD"), ("Hangu", "CentralPlains", "ROAD"),
    ("Guanzhong", "Hanzhong", "MOUNTAIN"), ("Hanzhong", "Bashu", "MOUNTAIN"), # 秦岭与金牛道
    
    # 东北走廊
    ("Manchuria", "Liaodong", "ATTACK"), ("Liaodong", "Shanhai", "ROAD"),
    ("Shanhai", "Beijing", "ROAD"), ("Beijing", "CentralPlains", "STRATEGY"),
    
    # 山西脊梁
    ("Mongolia", "Datong", "ATTACK"), ("Datong", "Yanmen", "MOUNTAIN"),
    ("Yanmen", "Taiyuan", "ROAD"), ("Taiyuan", "Hedong", "ROAD"),
    ("Hedong", "Guanzhong", "ATTACK"), # 渡河
    
    # 荆襄与江淮
    ("CentralPlains", "Xiangyang", "ATTACK"), ("Xiangyang", "Jiangling", "ROAD"),
    ("CentralPlains", "Jianghuai", "ATTACK"), ("Jianghuai", "Jiangnan", "STRATEGY"),
    
    # 水路 (单独处理，不走路由)
    ("Bashu", "Diaoyu", "WATER"), ("Diaoyu", "Jiangling", "WATER"),
    ("Jiangling", "Yangtze", "WATER"), ("Yangtze", "Jiangnan", "WATER"),
    
    # 其他威胁
    ("Mongolia", "Hetao", "ATTACK"), ("Hetao", "Guanzhong", "ATTACK"),
    ("Mongolia", "Xuanfu", "ATTACK"), ("Xuanfu", "Juyong", "ATTACK"), ("Juyong", "Beijing", "MOUNTAIN")
]

def create_real_path_map():
    print("正在计算真实地理路径 (Querying OSRM)...")
    
    m = folium.Map(location=[35.5, 108.0], zoom_start=5, tiles=None)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}',
        attr='Esri', name='山川地形图', control=True
    ).add_to(m)

    # 绘制连线
    for start, end, etype in RAW_EDGES:
        if start in LOCATIONS and end in LOCATIONS:
            p1 = LOCATIONS[start]["coords"]
            p2 = LOCATIONS[end]["coords"]
            
            # 1. 决定路径点
            path_points = []
            
            if etype == "WATER":
                # 水路直接连线 (或手动增加弯曲点)，因为路由引擎不懂行船
                path_points = [p1, p2]
            elif etype == "ATTACK" and "Mongolia" in start:
                # 游牧进攻往往跨越荒野，直线更具压迫感
                path_points = [p1, p2]
            else:
                # 陆路 (ROAD/MOUNTAIN) 使用 OSRM 查找真实山谷/公路路径
                # 稍微延迟避免 API 限制
                time.sleep(0.15) 
                path_points = get_real_path(p1, p2, mode='driving')

            # 2. 决定样式
            if etype == "ATTACK":
                plugins.AntPath(path_points, color="#d50000", weight=4, opacity=0.7, delay=800, pulse_color='white', tooltip="进攻路线").add_to(m)
            elif etype == "WATER":
                plugins.AntPath(path_points, color="#0277bd", weight=5, opacity=0.6, delay=2000, tooltip="水路").add_to(m)
            elif etype == "MOUNTAIN":
                folium.PolyLine(path_points, color="#795548", weight=3, opacity=0.8, dash_array='5, 10', tooltip="险峻山路(栈道)").add_to(m)
            elif etype == "ROAD":
                folium.PolyLine(path_points, color="#424242", weight=3, opacity=0.6, tooltip="官道/走廊").add_to(m)
            else:
                folium.PolyLine(path_points, color="gray", weight=2, opacity=0.5, dash_array='2, 5').add_to(m)

    # 绘制节点
    for key, data in LOCATIONS.items():
        style = STYLES.get(data["type"], STYLES["BASE"])
        folium.Marker(
            location=data["coords"],
            icon=folium.Icon(color="white", icon_color=style["color"], icon=style["icon"], prefix='fa'),
            tooltip=data["name"]
        ).add_to(m)
        
        # 标签
        folium.map.Marker(
            [data["coords"][0] - 0.25, data["coords"][1]],
            icon=DivIcon(
                icon_size=(150,36), icon_anchor=(75,0),
                html=f'''<div style="font-size: 10pt; font-family: 'Microsoft YaHei'; font-weight: 800; color: #212121; text-shadow: 2px 0 #fff, -2px 0 #fff, 0 2px #fff; text-align: center; pointer-events: none;">{data["name"]}</div>''',
            )
        ).add_to(m)

    # 添加图例
    legend_html = """
     <div style="position: fixed; bottom: 30px; left: 20px; width: 140px; border: 1px solid #999; background: rgba(255,255,255,0.9); padding: 10px; font-size:12px; z-index:9999;">
     <b>真实地理路径图</b><br>
     <span style="color:#795548">---</span> 沿山脉/公路地形<br>
     <span style="color:#d50000">---></span> 进攻方向<br>
     <span style="color:#0277bd">===></span> 水路
     </div>
     """
    m.get_root().html.add_child(folium.Element(legend_html))

    output_file = "ancient_china_real_paths.html"
    m.save(output_file)
    print(f"真实路径地图已生成: {output_file}")

if __name__ == "__main__":
    create_real_path_map()
