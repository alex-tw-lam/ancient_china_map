import folium
from folium import plugins
from folium.features import DivIcon

# ==========================================
# 1. 核心配置 (Configuration)
# ==========================================

# 颜色与样式配置
STYLES = {
    "THREAT": {"color": "#d50000", "icon": "fire", "size": (30, 30), "area_color": "#ffcdd2"},       # 鲜红
    "PASS":   {"color": "#e65100", "icon": "shield", "size": (24, 24), "area_color": "#ffe0b2"},     # 深橙
    "HUB":    {"color": "#f9a825", "icon": "crosshairs", "size": (22, 22), "area_color": "#fff9c4"}, # 暗黄
    "CORE":   {"color": "#1b5e20", "icon": "star", "size": (28, 28), "area_color": "#c8e6c9"},       # 深绿
    "WATER":  {"color": "#0277bd", "icon": "tint", "size": (20, 20), "area_color": "#b3e5fc"},       # 深蓝
    "BASE":   {"color": "#616161", "icon": "map-marker", "size": (16, 16), "area_color": "#eeeeee"}
}

# ==========================================
# 2. 地理数据 (补全缺失节点)
# ==========================================
LOCATIONS = {
    # --- 1. 北方威胁源 ---
    "Mongolia":  {"name": "蒙古高原", "coords": [44.0, 111.0], "type": "THREAT", "group": "北方威胁", "radius": 150000, "desc": "<b>游牧大本营</b><br>匈奴、突厥、蒙古、瓦剌的根据地。"},
    "Manchuria": {"name": "女真/辽东", "coords": [41.8, 124.0], "type": "THREAT", "group": "北方威胁", "radius": 120000, "desc": "<b>东北策源地</b><br>满清龙兴之地。"},
    "Xiyu":      {"name": "西域(敦煌)", "coords": [40.1, 94.6], "type": "BASE", "group": "西北走廊", "radius": 0, "desc": "<b>丝绸之路起点</b><br>通往中亚的门户。"},

    # --- 2. 西北走廊 ---
    "Hexi":     {"name": "河西走廊", "coords": [39.0, 100.5], "type": "HUB", "group": "西北走廊", "radius": 70000, "desc": "<b>咽喉要道</b><br>汉唐断匈奴臂膀之地。"},
    "Longxi":   {"name": "陇西", "coords": [35.5, 104.6], "type": "HUB", "group": "西北走廊", "radius": 0, "desc": "<b>关中西屏</b><br>抵御吐蕃与羌人的前线。"},
    "Hetao":    {"name": "河套平原", "coords": [40.8, 107.5], "type": "THREAT", "group": "西北走廊", "radius": 80000, "desc": "<b>由于在此</b><br>黄河百害，唯富一套。"},

    # --- 3. 关中核心 ---
    "Guanzhong": {"name": "关中(长安)", "coords": [34.3, 108.9], "type": "CORE", "group": "核心腹地", "radius": 80000, "desc": "<b>帝王之都</b><br>周秦汉唐定都之地。"},
    "Hangu":     {"name": "函谷关", "coords": [34.61, 110.36], "type": "PASS", "group": "核心腹地", "radius": 0, "desc": "<b>关中东门</b><br>扼守崤函古道。"},
    
    # --- 4. 山西/九边 ---
    "Datong":   {"name": "大同", "coords": [40.07, 113.3], "type": "HUB", "group": "九边重镇", "radius": 0, "desc": "<b>北门锁钥</b><br>直面漠南蒙古。"},
    "Yanmen":   {"name": "雁门关", "coords": [39.18, 112.88], "type": "PASS", "group": "九边重镇", "radius": 0, "desc": "<b>中华第一关</b><br>杨家将驻守地。"},
    "Taiyuan":  {"name": "太原", "coords": [37.87, 112.54], "type": "CORE", "group": "九边重镇", "radius": 35000, "desc": "<b>河东心脏</b><br>金军攻宋突破口。"},
    "Hedong":    {"name": "河东高地", "coords": [36.5, 111.5], "type": "HUB", "group": "九边重镇", "radius": 0, "desc": "<b>表里山河</b><br>对关中和中原形成高屋建瓴之势。"},

    # --- 5. 京师/幽燕 ---
    "Xuanfu":   {"name": "宣府", "coords": [40.81, 114.88], "type": "HUB", "group": "九边重镇", "radius": 0, "desc": "<b>京师外屏</b><br>土木堡之变发生地。"},
    "Juyong":   {"name": "居庸关", "coords": [40.28, 116.06], "type": "PASS", "group": "九边重镇", "radius": 0, "desc": "<b>京师门户</b><br>最后一道防线。"},
    "Liaodong": {"name": "辽东走廊", "coords": [41.1, 121.1], "type": "BASE", "group": "九边重镇", "radius": 0, "desc": "<b>入关通道</b>"},
    "Shanhai":  {"name": "山海关", "coords": [40.00, 119.75], "type": "PASS", "group": "九边重镇", "radius": 0, "desc": "<b>天下第一关</b><br>扼守咽喉。"},
    "Beijing":   {"name": "北京", "coords": [39.90, 116.40], "type": "CORE", "group": "九边重镇", "radius": 40000, "desc": "<b>元明清都城</b><br>天子守国门。"},

    # --- 6. 腹地与南方 ---
    "CentralPlains": {"name": "中原(洛阳)", "coords": [34.7, 113.3], "type": "CORE", "group": "中原腹地", "radius": 70000, "desc": "<b>天下之中</b><br>四战之地。"},
    "Hanzhong":      {"name": "汉中", "coords": [33.07, 107.02], "type": "HUB", "group": "西南防线", "radius": 40000, "desc": "<b>蜀之门户</b><br>得汉中则定巴蜀。"},
    "Bashu":     {"name": "巴蜀", "coords": [30.6, 104.0], "type": "CORE", "group": "西南防线", "radius": 100000, "desc": "<b>天府粮仓</b>"},
    "Diaoyu":    {"name": "钓鱼城", "coords": [30.0, 106.27], "type": "PASS", "group": "西南防线", "radius": 0, "desc": "<b>上帝折鞭处</b>"},

    "Xiangyang": {"name": "襄阳", "coords": [32.01, 112.12], "type": "HUB", "group": "中翼防线", "radius": 0, "desc": "<b>天下腰脊</b>"},
    "Jiangling": {"name": "江陵(荆州)", "coords": [30.35, 112.19], "type": "HUB", "group": "中翼防线", "radius": 0, "desc": "<b>据上流之势</b>"},
    "Jianghuai": {"name": "江淮", "coords": [32.5, 117.0], "type": "HUB", "group": "东南防线", "radius": 60000, "desc": "<b>水网密布</b>"},
    "Yangtze":   {"name": "长江防线", "coords": [30.5, 117.0], "type": "WATER", "group": "东南防线", "radius": 0, "desc": "<b>黄金水道</b>"},
    "Jiangnan":  {"name": "江南(南京)", "coords": [31.5, 119.5], "type": "CORE", "group": "东南防线", "radius": 90000, "desc": "<b>经济命脉</b>"}
}

# ==========================================
# 3. 连线逻辑 (补全缺失链路)
# ==========================================
# 格式: (起点, 终点, 类型, 所属图层组)
# 类型: ATTACK (红), WATER (蓝), ROAD (褐/实线), MOUNTAIN (褐/虚线), STRATEGY (灰)

EDGES = [
    # --- A. 丝绸之路与西北 ---
    ("Xiyu", "Hexi", "ROAD", "西北走廊"),       # 补全: 西域入河西
    ("Hexi", "Longxi", "ROAD", "西北走廊"),     # 河西入陇右
    ("Longxi", "Guanzhong", "MOUNTAIN", "西北走廊"), # 陇坂高地入关中
    
    # --- B. 北方游牧攻势 ---
    ("Mongolia", "Hetao", "ATTACK", "北方威胁"),
    ("Hetao", "Guanzhong", "ATTACK", "西北走廊"), # 匈奴入寇
    ("Hetao", "Datong", "ATTACK", "九边重镇"),    # 侧翼包抄
    ("Mongolia", "Datong", "ATTACK", "九边重镇"),
    ("Mongolia", "Xuanfu", "ATTACK", "九边重镇"),
    
    # --- C. 山西脊梁 ---
    ("Datong", "Yanmen", "MOUNTAIN", "九边重镇"), # 翻越雁门
    ("Yanmen", "Taiyuan", "ROAD", "九边重镇"),
    ("Taiyuan", "Hedong", "ROAD", "九边重镇"),
    ("Hedong", "CentralPlains", "ATTACK", "九边重镇"), # 太行八陉下河南
    ("Hedong", "Guanzhong", "ATTACK", "九边重镇"),     # 渡河攻关中 (如李渊)

    # --- D. 东北走廊 ---
    ("Manchuria", "Liaodong", "ATTACK", "北方威胁"),
    ("Liaodong", "Shanhai", "ATTACK", "九边重镇"),  # 辽西走廊
    ("Shanhai", "Beijing", "ROAD", "九边重镇"),     # 关宁锦防线
    ("Xuanfu", "Juyong", "ATTACK", "九边重镇"),
    ("Juyong", "Beijing", "MOUNTAIN", "九边重镇"),

    # --- E. 内部交通网 ---
    ("Guanzhong", "Hangu", "ROAD", "核心腹地"),     # 崤函古道
    ("Hangu", "CentralPlains", "ROAD", "中原腹地"),
    ("Beijing", "CentralPlains", "STRATEGY", "中原腹地"), # 补全: 京师控中原

    # --- F. 西南蜀道 ---
    ("Guanzhong", "Hanzhong", "MOUNTAIN", "西南防线"), # 补全: 秦岭栈道
    ("Hanzhong", "Bashu", "MOUNTAIN", "西南防线"),     # 金牛道
    ("Bashu", "Diaoyu", "WATER", "西南防线"),

    # --- G. 南方防线 ---
    ("CentralPlains", "Xiangyang", "ATTACK", "中翼防线"),
    ("Xiangyang", "Jiangling", "ROAD", "中翼防线"),
    ("Jiangling", "Yangtze", "WATER", "中翼防线"),
    ("CentralPlains", "Jianghuai", "ATTACK", "东南防线"),
    ("Jianghuai", "Yangtze", "STRATEGY", "东南防线"), # 守江必守淮
    ("Yangtze", "Jiangnan", "WATER", "东南防线")
]

def create_complete_map():
    m = folium.Map(location=[35.5, 108.0], zoom_start=5, tiles=None)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}',
        attr='Tiles &copy; Esri',
        name='山川地形图',
        overlay=False,
        control=True
    ).add_to(m)

    # 分组
    groups = {
        "北方威胁": folium.FeatureGroup(name="<span style='color:#d50000'><b>北方威胁</b></span>"),
        "核心腹地": folium.FeatureGroup(name="<span style='color:#1b5e20'><b>关中核心</b></span>"),
        "九边重镇": folium.FeatureGroup(name="九边/山西防线"),
        "西北走廊": folium.FeatureGroup(name="西北/丝绸之路"),
        "中原腹地": folium.FeatureGroup(name="中原腹地"),
        "西南防线": folium.FeatureGroup(name="西翼 (蜀道)"),
        "中翼防线": folium.FeatureGroup(name="中翼 (荆襄)"),
        "东南防线": folium.FeatureGroup(name="<span style='color:#0277bd'><b>东翼 (江淮)</b></span>"),
    }
    for g in groups.values():
        m.add_child(g)

    # 绘制区域
    for key, data in LOCATIONS.items():
        if data.get("radius", 0) > 0 and data["group"] in groups:
            folium.Circle(
                location=data["coords"],
                radius=data["radius"],
                color=STYLES[data["type"]]["color"],
                weight=1,
                fill=True,
                fill_color=STYLES[data["type"]]["area_color"],
                fill_opacity=0.15,
                popup=data["name"] + " 区域"
            ).add_to(groups[data["group"]])

    # 绘制连线
    for start, end, etype, gname in EDGES:
        if start in LOCATIONS and end in LOCATIONS and gname in groups:
            p1 = LOCATIONS[start]["coords"]
            p2 = LOCATIONS[end]["coords"]
            target = groups[gname]
            
            # 根据类型定制线条样式
            if etype == "ATTACK":
                # 红色脉冲，模拟进攻压力
                plugins.AntPath([p1, p2], color="#d50000", weight=4, opacity=0.8, delay=800, pulse_color='white', tooltip="进攻/威胁").add_to(target)
            elif etype == "WATER":
                # 蓝色流动，模拟水路
                plugins.AntPath([p1, p2], color="#0277bd", weight=5, opacity=0.6, delay=2000, tooltip="水路/长江").add_to(target)
            elif etype == "MOUNTAIN":
                # 棕色虚线，模拟艰难的山路/栈道
                folium.PolyLine([p1, p2], color="#795548", weight=3, opacity=0.8, dash_array='5, 10', tooltip="山脉/栈道").add_to(target)
            elif etype == "ROAD":
                # 黑色实线，模拟官道
                folium.PolyLine([p1, p2], color="#424242", weight=3, opacity=0.7, tooltip="官道/走廊").add_to(target)
            else:
                # 灰色细虚线，模拟战略联系
                folium.PolyLine([p1, p2], color="#9e9e9e", weight=2, opacity=0.5, dash_array='2, 5', tooltip="战略连接").add_to(target)

    # 绘制节点
    for key, data in LOCATIONS.items():
        if data["group"] in groups:
            target = groups[data["group"]]
            style = STYLES.get(data["type"], STYLES["BASE"])
            
            popup_html = f"""<div style="font-family:'Microsoft YaHei'; width:180px;">
                <h4 style="margin:0; border-bottom:1px solid #ccc; padding-bottom:5px; color:{style['color']}">{data['name']}</h4>
                <p style="font-size:12px; margin-top:5px;">{data.get('desc','')}</p></div>"""

            folium.Marker(
                location=data["coords"],
                icon=folium.Icon(color="white", icon_color=style["color"], icon=style["icon"], prefix='fa'),
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=data["name"]
            ).add_to(target)

            folium.map.Marker(
                [data["coords"][0] - 0.25, data["coords"][1]],
                icon=DivIcon(
                    icon_size=(150,36),
                    icon_anchor=(75,0),
                    html=f'''<div style="font-size: 10pt; font-family: 'Microsoft YaHei'; font-weight: 800; color: #212121; text-shadow: 2px 0 #fff, -2px 0 #fff, 0 2px #fff, 0 -2px #fff, 1px 1px #fff; text-align: center; white-space: nowrap; pointer-events: none;">{data["name"]}</div>''',
                )
            ).add_to(target)

    # 控件
    folium.LayerControl(collapsed=False).add_to(m)
    plugins.MiniMap(toggle_display=True, tile_layer=None, tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}', attr='Esri').add_to(m)
    
    # 搜索
    plugins.Search(layer=groups["九边重镇"], geom_type='Point', placeholder='搜索地点...', collapsed=True, search_label='tooltip').add_to(m)

    # 图例
    legend_html = """
     <div style="position: fixed; bottom: 30px; left: 20px; width: 160px; 
     border: 1px solid #8d6e63; border-radius: 4px; z-index:9999; 
     font-family: 'Microsoft YaHei'; background-color: #fff8e1; opacity: 0.95; 
     padding: 10px; font-size:12px; box-shadow: 3px 3px 5px rgba(0,0,0,0.3);">
     <b style="display:block; border-bottom:1px solid #8d6e63; margin-bottom:5px; text-align:center; color:#5d4037">战略图例</b>
     <div><i class="fa fa-fire" style="color:#d50000; width:15px;"></i> 威胁 / 进攻</div>
     <div><i class="fa fa-star" style="color:#1b5e20; width:15px;"></i> 核心 / 帝都</div>
     <div><i class="fa fa-shield" style="color:#e65100; width:15px;"></i> 关隘 / 防线</div>
     <hr style="border:0; border-top:1px dashed #ccc; margin:5px 0;">
     <div><span style="color:#d50000; font-weight:bold;">---></span> 进攻 (红)</div>
     <div><span style="color:#0277bd; font-weight:bold;">===></span> 水路 (蓝)</div>
     <div><span style="color:#795548; font-weight:bold;">- - -</span> 栈道/山路 (褐)</div>
     <div><span style="color:#424242; font-weight:bold;">——</span> 官道/走廊 (黑)</div>
     </div>
     """
    m.get_root().html.add_child(folium.Element(legend_html))

    output_file = "ancient_china_map_complete.html"
    m.save(output_file)
    print(f"完整版地图已生成: {output_file}")

if __name__ == "__main__":
    create_complete_map()
