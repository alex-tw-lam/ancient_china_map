import folium
from folium import plugins

# ==========================================
# 1. GEOGRAPHIC DATA (Hardcoded for Historical Accuracy)
# ==========================================
# Colors mapped from your DOT logic:
# Threats = Red (#d32f2f)
# Passes = Orange (#f57c00)
# Hubs = Yellow/Gold (#fbc02d)
# Core/Safe = Green (#388e3c)
# Waterways = Blue (#0288d1)

LOCATIONS = {
    # --- LAYER 1: THREATS (Red) ---
    "Mongolia": {"name": "Mongolia / Xiongnu (Source)", "coords": [44.0, 111.0], "color": "red", "icon": "fire"},
    "Manchuria": {"name": "Manchuria / Liaodong / Jurchen", "coords": [41.8, 123.4], "color": "red", "icon": "fire"},
    "Xiyu": {"name": "Western Regions (Xiyu)", "coords": [40.0, 94.0], "color": "red", "icon": "fire"}, # Near Dunhuang

    # --- LAYER 2: NORTHERN DEFENSE (Yellow/Orange/Green) ---
    "Wuwei": {"name": "Wuwei (Liangzhou)", "coords": [37.9283, 102.6371], "color": "beige"},
    "Zhangye": {"name": "Zhangye (Ganzhou)", "coords": [38.9326, 100.4542], "color": "beige"},
    "Hexi": {"name": "Hexi Corridor", "coords": [38.5, 101.5], "color": "beige"},
    "Longxi": {"name": "Longxi / Longyou", "coords": [35.5, 104.6], "color": "beige"},
    "Hetao": {"name": "Hetao Plain (Springboard)", "coords": [40.8, 107.5], "color": "orange"}, # Ordos Loop

    "Datong": {"name": "Datong (Yunzhou)", "coords": [40.0768, 113.3001], "color": "beige"},
    "Daizhou": {"name": "Daizhou (Hub)", "coords": [39.08, 112.95], "color": "gold"},
    "Yanmen": {"name": "Yanmen Pass", "coords": [39.183, 112.883], "color": "orange", "icon": "shield"},
    "Ningwu": {"name": "Ningwu Pass", "coords": [39.00, 112.30], "color": "orange", "icon": "shield"},
    "Piantou": {"name": "Piantou Pass", "coords": [39.43, 111.48], "color": "orange", "icon": "shield"},
    "Taiyuan": {"name": "Taiyuan (Northern Heart)", "coords": [37.8706, 112.5489], "color": "green"},

    "Liaoxi": {"name": "Liaoxi Corridor", "coords": [40.8, 120.5], "color": "beige"}, # Jinzhou area
    "Xuanfu": {"name": "Xuanfu (Zhangjiakou)", "coords": [40.81, 114.88], "color": "beige"},
    "Juyong": {"name": "Juyong Pass", "coords": [40.288, 116.068], "color": "orange", "icon": "shield"},
    "Shanhai": {"name": "Shanhai Pass", "coords": [40.009, 119.754], "color": "orange", "icon": "shield"},
    "LiaodongPlain": {"name": "Liaodong Plain", "coords": [41.2, 122.5], "color": "beige"},

    # --- LAYER 3: BARRIERS (Yellow/Green) ---
    "Hedong": {"name": "Hedong (Shanxi Highlands)", "coords": [36.5, 111.5], "color": "gold"},
    "Guanzhong": {"name": "Guanzhong Plain (Chang'an)", "coords": [34.3, 108.9], "color": "green", "icon": "star"},
    "NorthMts": {"name": "North Mountains (Ziwuling)", "coords": [35.5, 108.5], "color": "orange"},
    "Hangu": {"name": "Hangu / Tongguan Pass", "coords": [34.61, 110.36], "color": "orange", "icon": "shield"},
    "Beijing": {"name": "Beijing / Youzhou", "coords": [39.9042, 116.4074], "color": "green", "icon": "star"},

    # --- LAYER 4: CENTRAL (Green/Yellow) ---
    "CentralPlains": {"name": "Central Plains (Luoyang/Kaifeng)", "coords": [34.7, 113.6], "color": "green"},
    "Qinling": {"name": "Qinling Mountains / Shu Roads", "coords": [33.5, 107.5], "color": "orange"},
    "Hanzhong": {"name": "Hanzhong Basin", "coords": [33.07, 107.02], "color": "beige"},

    # --- LAYER 5: SOUTH DEFENSE (Blue/Green/Yellow) ---
    "Bashu": {"name": "Bashu (Sichuan)", "coords": [30.6, 104.0], "color": "green"},
    "Diaoyu": {"name": "Diaoyu City (Fortress)", "coords": [30.0, 106.27], "color": "orange", "icon": "shield"},

    "Nanyang": {"name": "Nanyang Basin", "coords": [33.0, 112.5], "color": "beige"},
    "Xiangyang": {"name": "Xiangyang (The Waist)", "coords": [32.01, 112.12], "color": "gold", "icon": "crosshairs"},
    "Jiangling": {"name": "Jiangling (Jingzhou)", "coords": [30.35, 112.19], "color": "beige"},
    "Ezhou": {"name": "Ezhou (Wuchang)", "coords": [30.54, 114.30], "color": "green"},

    "Jianghuai": {"name": "Jianghuai Region", "coords": [32.5, 117.0], "color": "beige"},
    "HuaiRiver": {"name": "Huai River Line", "coords": [32.9, 116.0], "color": "blue", "icon": "tint"},
    "HuaiForts": {"name": "Huai Forts (Shouchun/Hefei)", "coords": [32.0, 116.8], "color": "lightgray"},
    "Zhenjiang": {"name": "Zhenjiang (Jingkou)", "coords": [32.2, 119.45], "color": "orange", "icon": "lock"},
    "Yangtze": {"name": "Yangtze River Line", "coords": [30.5, 117.0], "color": "blue", "icon": "tint"},
    "Jiangnan": {"name": "Jiangnan (Nanjing/Hangzhou)", "coords": [31.5, 120.0], "color": "green", "icon": "star"},
}

# ==========================================
# 2. CONNECTIONS (Edges)
# ==========================================
EDGES = [
    # NW Route
    ("Xiyu", "Wuwei"), ("Wuwei", "Zhangye"), ("Zhangye", "Hexi"),
    ("Hexi", "Longxi"), ("Longxi", "Guanzhong"),
    ("Mongolia", "Hetao"), ("Hetao", "NorthMts"), ("NorthMts", "Guanzhong"),

    # Shanxi Route
    ("Mongolia", "Datong"), ("Datong", "Daizhou"),
    ("Daizhou", "Yanmen"), ("Daizhou", "Ningwu"), ("Daizhou", "Piantou"),
    ("Yanmen", "Taiyuan"), ("Taiyuan", "Hedong"),
    ("Hedong", "Guanzhong"), ("Hedong", "CentralPlains"), ("Hedong", "Beijing"),

    # NE Route
    ("Manchuria", "LiaodongPlain"), ("LiaodongPlain", "Liaoxi"),
    ("Liaoxi", "Shanhai"), ("Shanhai", "Beijing"),
    ("Mongolia", "Xuanfu"), ("Xuanfu", "Juyong"), ("Juyong", "Beijing"),

    # Central
    ("Guanzhong", "Hangu"), ("Hangu", "CentralPlains"), ("Beijing", "CentralPlains"),

    # West Wing
    ("Guanzhong", "Qinling"), ("Qinling", "Hanzhong"), ("Hanzhong", "Bashu"),
    ("Bashu", "Diaoyu"), ("Diaoyu", "Yangtze"),

    # Central Wing
    ("CentralPlains", "Nanyang"), ("Nanyang", "Xiangyang"),
    ("Xiangyang", "Jiangling"), ("Jiangling", "Ezhou"), ("Ezhou", "Yangtze"),

    # East Wing
    ("CentralPlains", "Jianghuai"), ("Jianghuai", "HuaiRiver"),
    ("HuaiRiver", "HuaiForts"), ("HuaiForts", "Zhenjiang"), ("Zhenjiang", "Yangtze"),
    ("Yangtze", "Jiangnan")
]

def create_ancient_map():
    # Initialize Map centered on China
    m = folium.Map(location=[35.0, 108.0], zoom_start=5, tiles="CartoDB positron")

    # Create Feature Groups for Layer Control
    fg_nodes = folium.FeatureGroup(name="Strategic Locations")
    fg_edges = folium.FeatureGroup(name="Invasion/Defense Routes")

    # Add Markers
    for key, data in LOCATIONS.items():
        color = data.get("color", "blue")
        icon_type = data.get("icon", "info-sign")
        
        # Customizing Marker colors
        icon = folium.Icon(color=color, icon=icon_type, prefix='fa')
        
        folium.Marker(
            location=data["coords"],
            popup=folium.Popup(f"<b>{data['name']}</b>", max_width=300),
            tooltip=data["name"],
            icon=icon
        ).add_to(fg_nodes)

    # Add Edges (Arrows)
    for start, end in EDGES:
        if start in LOCATIONS and end in LOCATIONS:
            p1 = LOCATIONS[start]["coords"]
            p2 = LOCATIONS[end]["coords"]
            
            # Draw the line
            folium.PolyLine(
                locations=[p1, p2],
                color="#455a64",
                weight=2,
                opacity=0.7
            ).add_to(fg_edges)
            
            # Add a small circle at the end to simulate an arrow tip (Folium AntPath is complex, simple circle works)
            folium.CircleMarker(
                location=p2,
                radius=3,
                color="red",
                fill=True,
                fill_opacity=1
            ).add_to(fg_edges)

    # Add features to map
    m.add_child(fg_edges)
    m.add_child(fg_nodes)
    
    # Add Layer Control
    folium.LayerControl().add_to(m)

    # Save
    output_file = "ancient_china_strategy_map.html"
    m.save(output_file)
    print(f"Map generated successfully: {output_file}")

if __name__ == "__main__":
    create_ancient_map()
