import folium
from folium import plugins
from folium.features import DivIcon

# ==========================================
# 1. 核心配置 (Configuration)
# ==========================================

# 颜色与样式配置
STYLES = {
    "THREAT": {"color": "#c62828", "icon": "fire", "size": (30, 30), "area_color": "#ffcdd2"},       # 鲜红
    "PASS":   {"color": "#e65100", "icon": "shield", "size": (24, 24), "area_color": "#ffe0b2"},     # 深橙
    "HUB":    {"color": "#f9a825", "icon": "crosshairs", "size": (22, 22), "area_color": "#fff9c4"}, # 暗黄
    "CORE":   {"color": "#2e7d32", "icon": "star", "size": (26, 26), "area_color": "#c8e6c9"},       # 深绿
    "WATER":  {"color": "#0277bd", "icon": "tint", "size": (20, 20), "area_color": "#b3e5fc"},       # 深蓝
    "BASE":   {"color": "gray",    "icon": "map-marker", "size": (15, 15), "area_color": "#eeeeee"}
}

# ==========================================
# 2. 地理数据 (增强版：包含区域半径)
# ==========================================
# radius: 区域大致半径 (米)，用于绘制势力范围圆圈
LOCATIONS = {
    # --- 威胁源头 ---
    "Mongolia":  {"name": "蒙古高原", "coords": [44.0, 111.0], "type": "THREAT", "group": "北方威胁", "radius": 150000, "desc": "<b>游牧大本营</b><br>匈奴、突厥、蒙古根据地，居高临下俯视中原。"},
    "Manchuria": {"name": "辽东/女真", "coords": [41.8, 123.4], "type": "THREAT", "group": "北方威胁", "radius": 120000, "desc": "<b>东北策源地</b><br>女真、满清龙兴之地，侧翼威胁华北。"},
    
    # --- 核心战略区 (Polygons) ---
    "Guanzhong": {"name": "关中平原", "coords": [34.5, 108.9], "type": "CORE", "group": "核心腹地", "radius": 90000, "desc": "<b>天府之国 (秦)</b><br>四塞以为固。东函谷，南武关，西散关，北萧关。"},
    "Hetao":    {"name": "河套平原", "coords": [40.8, 107.5], "type": "THREAT", "group": "西北防线", "radius": 80000, "desc": "<b>战略跳板</b><br>黄河百害，唯富一套。匈奴南下的前进基地。"},
    "Bashu":     {"name": "四川盆地", "coords": [30.6, 104.5], "type": "CORE", "group": "西南防线", "radius": 110000, "desc": "<b>大后方</b><br>沃野千里，天府之国。南宋抵抗蒙军50年的资本。"},
    "Jiangnan":  {"name": "江南腹地", "coords": [31.2, 120.0], "type": "CORE", "group": "东南防线", "radius": 100000, "desc": "<b>经济命脉</b><br>赋税重地，衣冠南渡后的华夏最后堡垒。"},
    "CentralPlains": {"name": "中原(洛阳)", "coords": [34.7, 113.3], "type": "CORE", "group": "中原腹地", "radius": 70000, "desc": "<b>四战之地</b><br>天下之中，无险可守，兵家必争。"},

    # --- 关键节点 ---
    "Hexi":     {"name": "河西走廊", "coords": [39.0, 100.5], "type": "HUB", "group": "西北防线", "radius": 0, "desc": "<b>丝路咽喉</b><br>断绝则西域失联，夹在沙漠与雪山之间。"},
    "Longxi":   {"name": "陇西", "coords": [35.5, 104.6], "type": "HUB", "group": "西北防线", "radius": 0, "desc": "<b>关中西屏</b><br>防御吐蕃的前线。"},
    "Hangu":     {"name": "函谷关", "coords": [34.61, 110.36], "type": "PASS", "group": "核心腹地", "radius": 0, "desc": "<b>关中东门</b><br>扼守崤函古道，六国攻秦之死地。"},

    "Datong":   {"name": "大同", "coords": [40.07, 113.3], "type": "HUB", "group": "九边重镇", "radius": 0, "desc": "<b>屏翰中原</b><br>明朝九边重镇，直面漠南蒙古。"},
    "Yanmen":   {"name": "雁门关", "coords": [39.18, 112.88], "type": "PASS", "group": "九边重镇", "radius": 0, "desc": "<b>中华第一关</b><br>扼守山西南北通道，杨家将驻守地。"},
    "Taiyuan":  {"name": "太原", "coords": [37.87, 112.54], "type": "CORE", "group": "九边重镇", "radius": 40000, "desc": "<b>河东心脏</b><br>控带山河，踞天下之肩背。"},
    "Hedong":    {"name": "河东高地", "coords": [36.5, 111.5], "type": "HUB", "group": "九边重镇", "radius": 0, "desc": "<b>表里山河</b><br>西渡黄河击关中，南下太行入中原。"},

    "Xuanfu":   {"name": "宣府", "coords": [40.81, 114.88], "type": "HUB", "group": "九边重镇", "radius": 0, "desc": "<b>京师锁钥</b><br>土木堡之变发生地，距北京极近。"},
    "Juyong":   {"name": "居庸关", "coords": [40.28, 116.06], "type": "PASS", "group": "九边重镇", "radius": 0, "desc": "<b>京师门户</b><br>一夫当关，守护北京的最后防线。"},
    "Shanhai":  {"name": "山海关", "coords": [40.00, 119.75], "type": "PASS", "group": "九边重镇", "radius": 0, "desc": "<b>辽东咽喉</b><br>京师屏障，吴三桂开关处。"},
    "Beijing":   {"name": "北京", "coords": [39.90, 116.40], "type": "CORE", "group": "九边重镇", "radius": 30000, "desc": "<b>天子守国门</b><br>幽燕腹地，元明清都城。"},

    "Hanzhong":      {"name": "汉中", "coords": [33.07, 107.02], "type": "HUB", "group": "西南防线", "radius": 40000, "desc": "<b>蜀道咽喉</b><br>秦岭以南关键盆地，得汉中则定巴蜀。"},
    "Diaoyu":    {"name": "钓鱼城", "coords": [30.0, 106.27], "type": "PASS", "group": "西南防线", "radius": 0, "desc": "<b>上帝折鞭处</b><br>蒙哥大汗陨落之地，阻挡蒙军36年。"},

    "Xiangyang": {"name": "襄阳", "coords": [32.01, 112.12], "type": "HUB", "group": "中翼防线", "radius": 0, "desc": "<b>天下腰脊</b><br>南宋防御铁三角之首，失襄阳则长江无险。"},
    "Jiangling": {"name": "江陵(荆州)", "coords": [30.35, 112.19], "type": "HUB", "group": "中翼防线", "radius": 0, "desc": "<b>据上流之势</b><br>东连吴会，西通巴蜀，北接中原。"},
    "Jianghuai": {"name": "江淮", "coords": [32.5, 117.0], "type": "HUB", "group": "东南防线", "radius": 60000, "desc": "<b>守江必守淮</b><br>水网密布，限制北方骑兵发挥。"},
    "Yangtze":   {"name": "长江防线", "coords": [30.5, 117.0], "type": "WATER", "group": "东南防线", "radius": 0, "desc": "<b>黄金水道</b><br>南方政权的最后死线。"},
}

# ==========================================
# 3. 连线逻辑
# ==========================================
EDGES = [
    # 北方攻势
    ("Mongolia", "Hetao", "ATTACK", "北方威胁"), ("Hetao", "Guanzhong", "ATTACK", "西北防线"),
    ("Mongolia", "Datong", "ATTACK", "九边重镇"), ("Datong", "Yanmen", "ATTACK", "九边重镇"),
    ("Mongolia", "Xuanfu", "ATTACK", "九边重镇"), ("Xuanfu", "Juyong", "ATTACK", "九边重镇"),
    ("Manchuria", "Shanhai", "ATTACK", "九边重镇"), ("Shanhai", "Beijing", "ATTACK", "九边重镇"),
    
    # 战略连接
    ("Hedong", "CentralPlains", "ATTACK", "中原腹地"),
    ("Guanzhong", "Hangu", "STRATEGY", "核心腹地"), ("Hangu", "CentralPlains", "STRATEGY", "中原腹地"),
    ("Yanmen", "Taiyuan", "STRATEGY", "九边重镇"), ("Taiyuan", "Hedong", "STRATEGY", "九边重镇"),
    
    # 南方防御
    ("Guanzhong", "Hanzhong", "STRATEGY", "西南防线"), ("Hanzhong", "Bashu", "STRATEGY", "西南防线"),
    ("CentralPlains", "Xiangyang", "ATTACK", "中翼防线"), ("Xiangyang", "Jiangling", "STRATEGY", "中翼防线"),
    ("CentralPlains", "Jianghuai", "ATTACK", "东南防线"), ("Jianghuai", "Jiangnan", "STRATEGY", "东南防线"),
    
    # 水路
    ("Bashu", "Diaoyu", "WATER", "西南防线"), ("Diaoyu", "Jiangling", "WATER", "中翼防线"),
    ("Jiangling", "Yangtze", "WATER", "东南防线"), ("Yangtze", "Jiangnan", "WATER", "东南防线")
]

def create_enriched_map():
    # 1. 物理地形底图
    # 使用自定义名称 '山川地形图' 解决 LayerControl 乱码/URL问题
    m = folium.Map(location=[35.5, 108.0], zoom_start=5, tiles=None)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}',
        attr='Tiles &copy; Esri',
        name='山川地形图', # 关键：这里命名，LayerControl就不会显示URL了
        overlay=False,
        control=True
    ).add_to(m)

    # 2. 初始化功能组 (Feature Groups)
    # 我们按战略区域分组，而不是按类型分组，这样更有逻辑
    groups = {
        "北方威胁": folium.FeatureGroup(name="<span style='color:#c62828'><b>北方威胁 (游牧)</b></span>"),
        "核心腹地": folium.FeatureGroup(name="<span style='color:#2e7d32'><b>关中核心 (秦)</b></span>"),
        "九边重镇": folium.FeatureGroup(name="<b>九边防御 (明)</b>"),
        "西北防线": folium.FeatureGroup(name="西北防线 (汉/唐)"),
        "中原腹地": folium.FeatureGroup(name="中原腹地"),
        "西南防线": folium.FeatureGroup(name="西翼 (巴蜀/汉中)"),
        "中翼防线": folium.FeatureGroup(name="中翼 (荆襄)"),
        "东南防线": folium.FeatureGroup(name="<span style='color:#0277bd'><b>东翼 (江淮/江南)</b></span>"),
    }
    for g in groups.values():
        m.add_child(g)

    # 3. 绘制区域 (Circles) - 填充空白，显示势力范围
    for key, data in LOCATIONS.items():
        if data.get("radius", 0) > 0 and data["group"] in groups:
            target_group = groups[data["group"]]
            style = STYLES.get(data["type"], STYLES["BASE"])
            
            folium.Circle(
                location=data["coords"],
                radius=data["radius"],
                color=style["color"],
                weight=1,
                fill=True,
                fill_color=style["area_color"],
                fill_opacity=0.2, # 低透明度，不遮挡地形
                popup=data["name"] + " 势力范围",
                tooltip=data["name"] + " 区域"
            ).add_to(target_group)

    # 4. 绘制连线
    for start, end, etype, gname in EDGES:
        if start in LOCATIONS and end in LOCATIONS and gname in groups:
            p1 = LOCATIONS[start]["coords"]
            p2 = LOCATIONS[end]["coords"]
            target_group = groups[gname]
            
            if etype == "ATTACK":
                plugins.AntPath([p1, p2], color="#c62828", weight=4, opacity=0.8, delay=800, pulse_color='white', tooltip="进攻/威胁").add_to(target_group)
            elif etype == "WATER":
                plugins.AntPath([p1, p2], color="#0277bd", weight=5, opacity=0.6, delay=1500, tooltip="长江/水路").add_to(target_group)
            else:
                folium.PolyLine([p1, p2], color="#616161", weight=2, opacity=0.6, dash_array='5, 10').add_to(target_group)

    # 5. 绘制节点与标签
    for key, data in LOCATIONS.items():
        if data["group"] in groups:
            target_group = groups[data["group"]]
            l_type = data["type"]
            style = STYLES.get(l_type, STYLES["BASE"])
            
            # HTML Popup 内容
            popup_content = f"""
            <div style="font-family:'Microsoft YaHei'; min-width:180px;">
                <h4 style="color:{style['color']}; margin:0 0 8px 0; border-bottom:1px solid #ccc; padding-bottom:5px;">
                    <i class="fa fa-{style['icon']}"></i> {data['name']}
                </h4>
                <div style="font-size:13px; color:#333; line-height:1.4;">
                    {data.get('desc', '重要战略地点')}
                </div>
            </div>
            """

            # 图标
            folium.Marker(
                location=data["coords"],
                icon=folium.Icon(color="white", icon_color=style["color"], icon=style["icon"], prefix='fa'),
                popup=folium.Popup(popup_content, max_width=250),
                tooltip=data["name"]
            ).add_to(target_group)

            # 永久文字标签
            folium.map.Marker(
                [data["coords"][0] - 0.25, data["coords"][1]],
                icon=DivIcon(
                    icon_size=(150,36),
                    icon_anchor=(75,0),
                    html=f'''<div style="
                        font-size: 10pt; font-family: 'Microsoft YaHei'; font-weight: 800; color: #212121;
                        text-shadow: 2px 0 #fff, -2px 0 #fff, 0 2px #fff, 0 -2px #fff, 1px 1px #fff;
                        text-align: center; white-space: nowrap; pointer-events: none;
                        ">{data["name"]}</div>''',
                )
            ).add_to(target_group)

    # 6. 添加高级控件 (Enrichment)
    
    # A. 图层控制器 (右上角，现在干净了)
    folium.LayerControl(collapsed=False).add_to(m)
    
    # B. 搜索栏 (左上角) - 允许搜索地点
    search = plugins.Search(
        layer=groups["九边重镇"], # 必须绑定到一个图层，这里绑定点最多的
        geom_type='Point',
        placeholder='搜索地点 (如: 北京)',
        collapsed=True,
        search_label='tooltip' # 搜索 tooltip 字段
    ).add_to(m)
    
    # C. 测距工具 (右上角)
    plugins.MeasureControl(
        position='topright', 
        primary_length_unit='kilometers', 
        secondary_length_unit='miles', 
        primary_area_unit='sqmeters'
    ).add_to(m)
    
    # D. 迷你地图 (右下角)
    plugins.MiniMap(toggle_display=True, tile_layer='CartoDB positron', width=150, height=150).add_to(m)

    # 7. 紧凑型图例 (左下角)
    legend_html = """
     <div style="
     position: fixed; bottom: 30px; left: 20px; width: 140px; 
     border: 1px solid #999; border-radius: 4px; z-index:9999; 
     font-family: 'Microsoft YaHei'; background-color: rgba(255,255,255,0.9); 
     padding: 10px; font-size:12px; box-shadow: 2px 2px 4px rgba(0,0,0,0.2);">
     <b style="display:block; border-bottom:1px solid #ccc; margin-bottom:5px; text-align:center;">战略图例</b>
     <div><i class="fa fa-fire" style="color:#c62828; width:15px;"></i> 威胁 / 进攻</div>
     <div><i class="fa fa-star" style="color:#2e7d32; width:15px;"></i> 核心 / 帝都</div>
     <div><i class="fa fa-shield" style="color:#e65100; width:15px;"></i> 关隘 / 防线</div>
     <div><i class="fa fa-crosshairs" style="color:#f9a825; width:15px;"></i> 必争枢纽</div>
     <div><i class="fa fa-tint" style="color:#0277bd; width:15px;"></i> 江河水路</div>
     <div style="margin-top:5px; color:#666;">* 点击图标查看详情</div>
     </div>
     """
    m.get_root().html.add_child(folium.Element(legend_html))

    output_file = "ancient_china_map_enriched.html"
    m.save(output_file)
    print(f"增强版地图已生成: {output_file}")

if __name__ == "__main__":
    create_enriched_map()
