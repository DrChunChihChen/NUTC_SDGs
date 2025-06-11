import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO
import base64
import os
from pathlib import Path
import logging


# =============================================================================
# Setup Logging
# =============================================================================
def setup_logging():
    """Setup logging to file for debug information."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('streamlit_debug.log', encoding='utf-8'),
            logging.StreamHandler()  # Also log to console if needed
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()

# =============================================================================
# Page Configuration
# =============================================================================
st.set_page_config(
    page_title="校園碳盤查",
    page_icon="🌍",
    layout="wide"
)


# =============================================================================
# Helper function to encode images
# =============================================================================
def get_image_as_base64(file_path):
    """Reads a file and returns its base64 encoded string with logging."""
    try:
        path = Path(file_path)

        logger.info(f"嘗試載入圖片: {file_path}")
        logger.info(f"絕對路徑: {path.absolute()}")
        logger.info(f"當前工作目錄: {Path.cwd()}")

        if not path.exists():
            logger.error(f"圖片檔案不存在: {file_path}")
            return None

        if not path.is_file():
            logger.error(f"路徑不是檔案: {file_path}")
            return None

        file_size = path.stat().st_size
        logger.info(f"檔案大小: {file_size:,} bytes")

        if file_size == 0:
            logger.error("圖片檔案為空")
            return None

        if file_size > 10 * 1024 * 1024:  # 10MB limit
            logger.warning("圖片檔案過大 (>10MB)，可能影響載入效能")

        with open(path, "rb") as f:
            data = f.read()

        encoded = base64.b64encode(data).decode()
        logger.info(f"圖片載入成功！Base64 長度: {len(encoded)}")
        return encoded

    except PermissionError:
        logger.error(f"沒有權限讀取檔案: {file_path}")
        return None
    except Exception as e:
        logger.error(f"讀取圖片時發生錯誤: {str(e)}")
        return None


def get_image_mime_type(file_path):
    """Determines the MIME type based on file extension."""
    extension = Path(file_path).suffix.lower()
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml',
        '.bmp': 'image/bmp'
    }
    return mime_types.get(extension, 'image/jpeg')  # Default to jpeg for jpg files


# =============================================================================
# Reusable Components
# =============================================================================
def set_background(file_path):
    """
    Sets a background image for the Streamlit app with logging.
    Args:
    file_path (str): The path to the image file.
    """
    logger.info("開始設定背景圖片...")

    base64_img = get_image_as_base64(file_path)
    if base64_img:
        mime_type = get_image_mime_type(file_path)
        logger.info(f"偵測到的圖片格式: {mime_type}")

        # Enhanced CSS with multiple fallback selectors
        page_bg_img = f"""
        <style>
        /* Main app container - Multiple selectors for compatibility */
        .stApp {{
            background-image: url("data:{mime_type};base64,{base64_img}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}

        /* Alternative selectors for different Streamlit versions */
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:{mime_type};base64,{base64_img}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}

        [data-testid="stAppViewContainer"] > .main {{
            background-image: url("data:{mime_type};base64,{base64_img}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}

        .main {{
            background-image: url("data:{mime_type};base64,{base64_img}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}

        /* Make header transparent */
        [data-testid="stHeader"] {{
            background: rgba(0,0,0,0) !important;
        }}

        header[data-testid="stHeader"] {{
            background: rgba(0,0,0,0) !important;
        }}

        /* Style forms and containers for better readability */
        .stForm {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            padding: 2rem !important;
            border-radius: 0.5rem !important;
            backdrop-filter: blur(10px) !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        }}

        div[data-testid="stForm"] {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            padding: 2rem !important;
            border-radius: 0.5rem !important;
            backdrop-filter: blur(10px) !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        }}

        /* Legacy selector fallback */
        div.st-emotion-cache-1xw8zd {{
            background-color: rgba(255, 255, 255, 0.85) !important;
            padding: 2rem !important;
            border-radius: 0.5rem !important;
        }}
        </style>
        """

        st.markdown(page_bg_img, unsafe_allow_html=True)
        logger.info("背景 CSS 已套用成功")
        return True
    else:
        logger.error(f"無法載入背景圖片：{file_path}")
        return False


def display_footer():
    """Displays the contact information footer."""
    st.divider()

    # Use relative path or check if file exists
    logo_path = "OFFICE_NUTC.png"

    # Try different possible paths
    possible_paths = [
        logo_path,
        f"images/{logo_path}",
        f"assets/{logo_path}",
        "OFFICE_NUTC.png"  # Original absolute path as fallback
    ]

    logo_loaded = False
    for path in possible_paths:
        if os.path.exists(path):
            try:
                st.image(path, width=200)
                logo_loaded = True
                break
            except Exception as e:
                st.warning(f"無法載入 logo: {path} - {e}")
                continue

    if not logo_loaded:
        st.info("Logo 未找到，請將 OFFICE_NUTC.jpg 放在程式資料夾中")

    st.caption("""
    國立臺中科技大學 永續辦公室  
    地址 : 404 台中市北區三民路三段129號行政大樓4樓1401室  
    電話 : 04 - 2219 - 6479  
    傳真 : 04 - 2219 - 5003  
    信箱 : sdgsnutc2024@gmail.com
    Copyright © 2025 NUTC. All rights reserved
    """)


# =============================================================================
# User Authentication
# =============================================================================
USERS = {
    "Elvis": "0000",
    "Nutc1": "0001",
    "Nutc2": "0002",
    "Nutc3": "0003"
}


def login_page():
    """Renders the login page with a background image."""
    # Log file system information
    current_dir = os.getcwd()
    logger.info(f"當前工作目錄: {current_dir}")

    try:
        files = os.listdir('.')
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'))]
        logger.info(f"找到 {len(image_files)} 個圖片檔案: {image_files}")
        logger.info(f"目錄中共有 {len(files)} 個檔案")
    except Exception as e:
        logger.error(f"無法讀取目錄: {e}")

    # Try to load background image (silently)
    possible_bg_paths = [
        "img1.jpg",
        "images/img1.jpg",
        "assets/img1.jpg",
        "background_for_login.png",
        "background.jpg",
        "img1.jpg"
    ]

    background_loaded = False
    for bg_path in possible_bg_paths:
        logger.info(f"嘗試載入背景圖片: {bg_path}")
        if os.path.exists(bg_path):
            logger.info(f"找到檔案: {bg_path}")
            if set_background(bg_path):
                background_loaded = True
                logger.info(f"背景圖片載入成功: {bg_path}")
                break
        else:
            logger.warning(f"檔案不存在: {bg_path}")

    if not background_loaded:
        logger.error("無法載入任何背景圖片")

    # Clean login UI
    st.title("校園碳盤查系統")
    st.write("請使用您的帳號密碼登入")

    # Login form
    with st.form("login_form"):
        username = st.text_input("帳號 (Username)")
        password = st.text_input("密碼 (Password)", type="password")
        submitted = st.form_submit_button("登入")

        if submitted:
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("登入成功！")
                logger.info(f"用戶 {username} 登入成功")
                st.rerun()
            else:
                st.error("帳號或密碼錯誤")
                logger.warning(f"登入失敗 - 用戶名: {username}")

    display_footer()


# =============================================================================
# Helper Functions & Data Initialization
# =============================================================================
def get_ar_initial_data(prefix):
    """
    Initializes session state with default values for a given AR version (AR5 or AR6).
    This function creates keys with a specific prefix to keep data separate.
    """
    # --- State flags ---
    if f"show_dashboard_{prefix}" not in st.session_state:
        st.session_state[f"show_dashboard_{prefix}"] = False

    # --- Inventory Year ---
    if f"inventory_year_{prefix}" not in st.session_state:
        years = range(datetime.now().year + 25, 2019, -1)
        st.session_state[f"inventory_year_{prefix}"] = datetime.now().year if datetime.now().year in years else years[0]

    # --- Data Dictionaries ---
    # The data for AR5 and AR6 will be identical initially as requested.
    if f"s1_data_{prefix}" not in st.session_state:
        st.session_state[f"s1_data_{prefix}"] = {
            '燃料油': {'usage': 100, 'unit': '公升/年', 'factor': 0.002567},
            '天然氣(NG)': {'usage': 100, 'unit': '度/年', 'factor': 0.001881},
            '液化石油氣(LPG)': {'usage': 100, 'unit': '公升/年', 'factor': 0.001754},
            '汽油': {'usage': 100, 'unit': '公升/年', 'factor': 0.002271},
            '柴油': {'usage': 100, 'unit': '公升/年', 'factor': 0.002615},
            '潤滑油': {'usage': 100, 'unit': '公升/年', 'factor': 0.002956},
        }
    if f"s2_data_{prefix}" not in st.session_state:
        st.session_state[f"s2_data_{prefix}"] = {
            '車用汽油': {'usage': 100, 'unit': '公升/年', 'factor': 0.002298},
            '車用柴油': {'usage': 100, 'unit': '公升/年', 'factor': 0.002722},
            '煤油': {'usage': 100, 'unit': '公升/年', 'factor': 0.002567},
            '潤滑油_mobile': {'name': '潤滑油', 'usage': 100, 'unit': '公升/年', 'factor': 0.002956},
            '液化石油氣(LPG)_mobile': {'name': '液化石油氣(LPG)', 'usage': 100, 'unit': '公升/年', 'factor': 0.001803},
            '液化天然氣(LNG)': {'usage': 100, 'unit': '度/年', 'factor': 0.002241},
        }
    if f"s3_septic_system_{prefix}" not in st.session_state:
        st.session_state[f"s3_septic_system_{prefix}"] = '否 (使用化糞池)'
    if f"s3_data_{prefix}" not in st.session_state:
        st.session_state[f"s3_data_{prefix}"] = {
            '平日日間使用學生': {'usage': 100, 'factor': 0.0021},
            '平日夜間使用學生': {'usage': 10, 'factor': 0.0005},
            '假日使用學生': {'usage': 0, 'factor': 0.0},
            '住宿人員': {'usage': 0, 'factor': 0.0},
            '平日日間使用員工': {'usage': 50, 'factor': 0.0021},
            '平日夜間使用員工': {'usage': 5, 'factor': 0.0005},
            '假日使用員工': {'usage': 0, 'factor': 0.0},
        }
    if f"s4_data_{prefix}" not in st.session_state:
        st.session_state[f"s4_data_{prefix}"] = {
            '二氧化碳滅火器': {'usage': 1, 'gwp': 1, 'factor': None},
            'FM-200': {'usage': 1, 'gwp': 3350, 'factor': None},
            'BC型乾粉滅火器': {'usage': 1, 'gwp': None, 'factor': 0.0003},
            'KBC型乾粉滅火器': {'usage': 1, 'gwp': None, 'factor': 0.0002},
        }
    if f"s5_data_{prefix}" not in st.session_state:
        st.session_state[f"s5_data_{prefix}"] = {
            'HFC-23/R-23': {'usage': 0.5, 'gwp': 12400}, 'HFC-32/R-32': {'usage': 0.1, 'gwp': 677},
            'HFC-41': {'usage': 0.0, 'gwp': 116}, 'HFC-134': {'usage': 0.0, 'gwp': 1120},
            'HFC-134a/R-134a': {'usage': 0.0, 'gwp': 1300}, 'HFC-143': {'usage': 0.0, 'gwp': 328},
            'HFC-143a/R-143a': {'usage': 0.0, 'gwp': 4800}, 'HFC-152': {'usage': 0.0, 'gwp': 16},
            'HFC-152a/R-152a': {'usage': 0.0, 'gwp': 138}, 'R401a': {'usage': 0.0, 'gwp': 1130},
            'R401B': {'usage': 0.0, 'gwp': 1236}, 'R404A': {'usage': 0.5, 'gwp': 3943},
            'R407A': {'usage': 0.0, 'gwp': 1923}, 'R407B': {'usage': 0.0, 'gwp': 2547},
            'R407C': {'usage': 0.0, 'gwp': 1624}, 'R408A': {'usage': 0.0, 'gwp': 3257},
            'R410A': {'usage': 0.0, 'gwp': 1924}, 'R413A': {'usage': 0.0, 'gwp': 1945},
            'R417A': {'usage': 0.0, 'gwp': 2127}, 'R507A': {'usage': 0.0, 'gwp': 3985}
        }
    if f"s6_data_{prefix}" not in st.session_state:
        st.session_state[f"s6_data_{prefix}"] = {
            '汽車-汽油': {'distance': 100, 'factor': 0.104}, '汽車-電動車': {'distance': 100, 'factor': 0.04},
            '機車-一般機車': {'distance': 100, 'factor': 0.079}, '機車-電動機車': {'distance': 100, 'factor': 0.017},
            '公車/客運': {'distance': 100, 'factor': 0.078}, '捷運': {'distance': 100, 'factor': 0.04},
            '火車': {'distance': 0, 'factor': 0.04}, '高鐵': {'distance': 0, 'factor': 0.028}
        }
    if f"s7_electricity_{prefix}" not in st.session_state:
        months = ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
        st.session_state[f"s7_electricity_{prefix}"] = {m: 10000 for m in months}
    if f"s7_water_{prefix}" not in st.session_state:
        months = ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
        st.session_state[f"s7_water_{prefix}"] = {m: 100 for m in months}
    if f"s7_water_source_{prefix}" not in st.session_state:
        st.session_state[f"s7_water_source_{prefix}"] = '台灣自來水營業事業處'
    if f"water_factors_{prefix}" not in st.session_state:
        st.session_state[f"water_factors_{prefix}"] = {'台灣自來水營業事業處': 0.1872, '臺北自來水營業事業處': 0.0666}


def get_campus_initial_data():
    """Initializes session state with default values for the campus carbon negative page."""
    if 'campus_inventory_year' not in st.session_state:
        years = range(datetime.now().year + 25, 2019, -1)
        st.session_state.campus_inventory_year = datetime.now().year if datetime.now().year in years else years[0]

    if 'campus_renewable_self_use' not in st.session_state:
        st.session_state.campus_renewable_self_use = [
            {"類別": "太陽能光電", "每年實際發電度數": 1000, "單位": "度電(kWh)"},
            {"類別": "風力發電", "每年實際發電度數": 0, "單位": "度電(kWh)"}
        ]
    if 'campus_renewable_sold' not in st.session_state:
        st.session_state.campus_renewable_sold = [
            {"類別": "太陽能光電", "每年實際發電度數": 1000, "單位": "度電(kWh)"},
            {"類別": "風力發電", "每年實際發電度數": 0, "單位": "度電(kWh)"}
        ]
    if 'campus_tree_sink' not in st.session_state:
        st.session_state.campus_tree_sink = [
            {"樹木類別": "針葉樹", "植物固碳當量(kgCO2e)": 1000},
            {"樹木類別": "闊葉樹", "植物固碳當量(kgCO2e)": 500},
            {"樹木類別": "棕梠科", "植物固碳當量(kgCO2e)": 20}
        ]


def initialize_state():
    """Initializes session state for all pages."""
    if 'page' not in st.session_state:
        st.session_state.page = "AR5"

    get_ar_initial_data('ar5')
    get_ar_initial_data('ar6')
    get_campus_initial_data()


# =============================================================================
# Excel Export Function
# =============================================================================
def to_excel(prefix):
    """
    Serializes all input data from session state for a specific AR version into a multi-sheet Excel file.
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Sheet 1: 固定源
        df1 = pd.DataFrame.from_dict(st.session_state[f's1_data_{prefix}'], orient='index')
        df1['排放量(tCO2e)'] = df1['usage'] * df1['factor']
        df1.index.name = '燃料類別'
        df1.reset_index(inplace=True)
        df1.rename(columns={'usage': '使用量', 'unit': '單位', 'factor': '排放係數'}, inplace=True)
        df1.to_excel(writer, sheet_name='固定源', index=False)

        # Sheet 2: 移動源
        df2_data = []
        for key, val in st.session_state[f's2_data_{prefix}'].items():
            row = val.copy()
            row['燃料類別'] = val.get('name', key)
            row['排放量(tCO2e)'] = row['usage'] * row['factor']
            df2_data.append(row)
        df2 = pd.DataFrame(df2_data)
        df2 = df2[['燃料類別', 'usage', 'unit', 'factor', '排放量(tCO2e)']]  # Reorder
        df2.rename(columns={'usage': '使用量', 'unit': '單位', 'factor': '排放係數'}, inplace=True)
        df2.to_excel(writer, sheet_name='移動源', index=False)

        # Sheet 3: 汙水
        if st.session_state[f's3_septic_system_{prefix}'] == '否 (使用化糞池)':
            df3 = pd.DataFrame.from_dict(st.session_state[f's3_data_{prefix}'], orient='index')
            df3['排放量(tCO2e)'] = df3['usage'] * df3['factor'] * 28  # GWP for CH4
            df3.index.name = '人員類別'
            df3.reset_index(inplace=True)
            df3.rename(columns={'usage': '人數', 'factor': '排放係數(CH4)'}, inplace=True)
            df3.to_excel(writer, sheet_name='汙水', index=False)

        # Sheet 4: 滅火器
        df4 = pd.DataFrame.from_dict(st.session_state[f's4_data_{prefix}'], orient='index')
        df4['排放量(tCO2e)'] = 0  # Initialize column
        df4.loc[df4['gwp'].notna(), '排放量(tCO2e)'] = (df4['usage'] * df4['gwp']) / 1000
        df4.loc[df4['factor'].notna(), '排放量(tCO2e)'] = df4['usage'] * df4['factor']
        df4.index.name = '類別'
        df4.reset_index(inplace=True)
        df4.rename(columns={'usage': '每年填充/使用量(公斤/年)', 'gwp': 'GWP係數', 'factor': '排放係數'}, inplace=True)
        df4.to_excel(writer, sheet_name='滅火器', index=False)

        # Sheet 5: 冷媒
        df5 = pd.DataFrame.from_dict(st.session_state[f's5_data_{prefix}'], orient='index')
        df5['排放量(tCO2e)'] = (df5['usage'] * df5['gwp']) / 1000
        df5.index.name = '冷媒種類'
        df5.reset_index(inplace=True)
        df5.rename(columns={'usage': '每年填充量(公斤/年)', 'gwp': 'GWP係數'}, inplace=True)
        df5.to_excel(writer, sheet_name='冷媒', index=False)

        # Sheet 6: 員工通勤
        df6 = pd.DataFrame.from_dict(st.session_state[f's6_data_{prefix}'], orient='index')
        df6['排放量(tCO2e)'] = (df6['distance'] * df6['factor']) / 1000
        df6.index.name = '交通工具'
        df6.reset_index(inplace=True)
        df6.rename(columns={'distance': '總通勤距離(公里/年)', 'factor': '排放係數(KgCO2e/pkm)'}, inplace=True)
        df6.to_excel(writer, sheet_name='員工通勤', index=False)

        # Sheet 7: 外購電力
        df7_elec = pd.DataFrame(st.session_state[f's7_electricity_{prefix}'].items(), columns=['月份', '用電量(度)'])
        df7_elec['排放量(tCO2e)'] = (df7_elec['用電量(度)'] * 0.474) / 1000
        df7_elec.to_excel(writer, sheet_name='外購電力', index=False)

        # Sheet 8: 外購水力
        water_factor = st.session_state[f'water_factors_{prefix}'][st.session_state[f's7_water_source_{prefix}']]
        df7_water = pd.DataFrame(st.session_state[f's7_water_{prefix}'].items(), columns=['月份', '用水量(度)'])
        df7_water['排放量(tCO2e)'] = (df7_water['用水量(度)'] * water_factor) / 1000
        df7_water.to_excel(writer, sheet_name='外購水力', index=False)
        worksheet = writer.sheets['外購水力']
        worksheet.write_string('E1', f'供水單位: {st.session_state[f"s7_water_source_{prefix}"]}')
        worksheet.write_string('E2', f'排放係數: {water_factor}')

    processed_data = output.getvalue()
    return processed_data


# =============================================================================
# Calculation Functions
# =============================================================================
def calculate_totals(prefix):
    """Calculate all emission totals for a given AR version and store them in session_state."""
    totals = {}
    gwp_ch4 = 28

    # Step 1
    totals['s1'] = sum(v['usage'] * v['factor'] for k, v in st.session_state[f's1_data_{prefix}'].items())
    # Step 2
    totals['s2'] = sum(v.get('usage', 0) * v.get('factor', 0) for k, v in st.session_state[f's2_data_{prefix}'].items())
    # Step 3
    is_septic_used = st.session_state[f's3_septic_system_{prefix}'] == '否 (使用化糞池)'
    totals['s3'] = sum(v['usage'] * v['factor'] * gwp_ch4 for k, v in
                       st.session_state[f's3_data_{prefix}'].items()) if is_septic_used else 0
    # Step 4
    s4_total = 0
    for k, v in st.session_state[f's4_data_{prefix}'].items():
        if v.get('gwp') is not None:
            s4_total += (v['usage'] * v['gwp']) / 1000
        elif v.get('factor') is not None:
            s4_total += v['usage'] * v['factor']
    totals['s4'] = s4_total
    # Step 5
    totals['s5'] = sum((v['usage'] * v['gwp']) / 1000 for k, v in st.session_state[f's5_data_{prefix}'].items())
    # Step 6
    totals['s6'] = sum((v['distance'] * v['factor']) / 1000 for k, v in st.session_state[f's6_data_{prefix}'].items())
    # Step 7
    total_electricity_usage = sum(st.session_state[f's7_electricity_{prefix}'].values())
    totals['s7_electricity'] = (total_electricity_usage * 0.474) / 1000
    total_water_usage = sum(st.session_state[f's7_water_{prefix}'].values())
    water_factor = st.session_state[f'water_factors_{prefix}'][st.session_state[f's7_water_source_{prefix}']]
    totals['s7_water'] = (total_water_usage * water_factor) / 1000

    st.session_state[f'totals_{prefix}'] = totals

    # Scope Totals
    scope1 = totals['s1'] + totals['s2'] + totals['s3'] + totals['s4'] + totals['s5']
    scope2 = totals['s7_electricity']
    scope3 = totals['s6'] + totals['s7_water']
    st.session_state[f'scope_totals_{prefix}'] = {
        'Scope 1': scope1, 'Scope 2': scope2, 'Scope 3': scope3, 'Grand Total': scope1 + scope2 + scope3
    }
    st.session_state[f'emission_breakdown_{prefix}'] = {
        '固定源': totals.get('s1', 0), '移動源': totals.get('s2', 0),
        '汙水': totals.get('s3', 0), '滅火器': totals.get('s4', 0),
        '冷媒': totals.get('s5', 0), '員工通勤': totals.get('s6', 0),
        '外購電力': totals.get('s7_electricity', 0), '外購水力': totals.get('s7_water', 0),
    }


# =============================================================================
# UI Components
# =============================================================================
def main_app():
    """Renders the main application with sidebar navigation."""
    with st.sidebar:
        st.write(f"歡迎, {st.session_state.username}!")
        st.title("導覽選單")

        if st.button("AR5-溫室氣體盤查資料", use_container_width=True,
                     type="primary" if st.session_state.page == "AR5" else "secondary"):
            st.session_state.page = "AR5"
            st.rerun()

        if st.button("AR6-溫室氣體盤查資料", use_container_width=True,
                     type="primary" if st.session_state.page == "AR6" else "secondary"):
            st.session_state.page = "AR6"
            st.rerun()

        if st.button("校園負碳", use_container_width=True,
                     type="primary" if st.session_state.page == "Campus" else "secondary"):
            st.session_state.page = "Campus"
            st.rerun()

        st.divider()
        if st.button("登出"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        # Add a spacer to push the footer to the bottom
        st.markdown("<div style='flex: 1;'></div>", unsafe_allow_html=True)
        display_footer()

    # --- Page Routing ---
    page = st.session_state.get("page", "AR5")

    if page == "AR5":
        if st.session_state.get("show_dashboard_ar5", False):
            create_dashboard('ar5', "AR5")
        else:
            create_input_form('ar5', "AR5")
    elif page == "AR6":
        if st.session_state.get("show_dashboard_ar6", False):
            create_dashboard('ar6', "AR6")
        else:
            create_input_form('ar6', "AR6")
    elif page == "Campus":
        show_campus_carbon_negative_page()


def create_dashboard(prefix, title):
    """Renders the main dashboard view for a given AR version."""
    st.title(f"{title} - {st.session_state[f'inventory_year_{prefix}']} 年度溫室氣體盤查儀表板")
    if st.button("⬅️ 返回編輯資料"):
        st.session_state[f'show_dashboard_{prefix}'] = False
        st.rerun()

    scope = st.session_state[f'scope_totals_{prefix}']

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("總碳排放量 (tCO2e)", f"{scope['Grand Total']:.2f}")
    col2.metric("範疇一 Scope 1", f"{scope['Scope 1']:.2f}")
    col3.metric("範疇二 Scope 2", f"{scope['Scope 2']:.2f}")
    col4.metric("範疇三 Scope 3", f"{scope['Scope 3']:.2f}")

    st.divider()

    # --- Top Row Charts ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("各類別排放佔比")
        emissions = st.session_state[f'emission_breakdown_{prefix}']
        filtered_emissions = {k: v for k, v in emissions.items() if v > 0}

        if filtered_emissions:
            fig = go.Figure(data=[go.Pie(
                labels=list(filtered_emissions.keys()), values=list(filtered_emissions.values()),
                hole=.4, textinfo='label+percent', insidetextorientation='radial'
            )])
            fig.update_layout(showlegend=False, height=400, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("目前沒有可顯示的排放數據。")

    with col2:
        st.subheader("各範疇排放比較 (tCO2e)")
        scope_df = pd.DataFrame({
            '範疇': ['Scope 1', 'Scope 2', 'Scope 3'],
            '排放量': [scope['Scope 1'], scope['Scope 2'], scope['Scope 3']]
        })
        fig = go.Figure(go.Bar(
            x=scope_df['排放量'], y=scope_df['範疇'], orientation='h',
            text=scope_df['排放量'].apply(lambda x: f'{x:.2f}'),
            textposition='auto', marker_color=['#10B981', '#F59E0B', '#8B5CF6']
        ))
        fig.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("各類別排放細項 (tCO2e)")

    def create_breakdown_chart(data, y_col, x_col, title):
        if data.empty or data[x_col].sum() == 0:
            st.write(f"{title}: 無排放數據")
            return
        max_val = data[x_col].max()
        colors = ['#FF4136' if v == max_val else '#1f77b4' for v in data[x_col]]
        fig = go.Figure(go.Bar(
            x=data[x_col], y=data[y_col], orientation='h', text=data[x_col].apply(lambda x: f'{x:.4f}'),
            marker_color=colors
        ))
        fig.update_layout(title_text=title, height=350, margin=dict(l=10, r=10, t=30, b=10),
                          yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        s1_df = pd.DataFrame.from_dict(st.session_state[f's1_data_{prefix}'], orient='index')
        s1_df['emission'] = s1_df['usage'] * s1_df['factor']
        s1_df = s1_df[s1_df['emission'] > 0].reset_index().rename(columns={'index': '燃料類別'})
        create_breakdown_chart(s1_df, '燃料類別', 'emission', '固定源排放')

        s4_items = []
        for item, values in st.session_state[f's4_data_{prefix}'].items():
            emission = 0
            if values.get('gwp') is not None:
                emission = (values['usage'] * values['gwp']) / 1000
            elif values.get('factor') is not None:
                emission = values['usage'] * values['factor']
            if emission > 0: s4_items.append({'類別': item, 'emission': emission})
        s4_df = pd.DataFrame(s4_items)
        create_breakdown_chart(s4_df, '類別', 'emission', '滅火器排放')
    with col2:
        s2_items = []
        for key, values in st.session_state[f's2_data_{prefix}'].items():
            emission = values['usage'] * values['factor']
            if emission > 0: s2_items.append({'燃料類別': values.get('name', key), 'emission': emission})
        s2_df = pd.DataFrame(s2_items)
        create_breakdown_chart(s2_df, '燃料類別', 'emission', '移動源排放')

        s6_df = pd.DataFrame.from_dict(st.session_state[f's6_data_{prefix}'], orient='index')
        s6_df['emission'] = (s6_df['distance'] * s6_df['factor']) / 1000
        s6_df = s6_df[s6_df['emission'] > 0].reset_index().rename(columns={'index': '交通工具'})
        create_breakdown_chart(s6_df, '交通工具', 'emission', '員工通勤排放')

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        s7_elec_df = pd.DataFrame(st.session_state[f's7_electricity_{prefix}'].items(), columns=['月份', '用電量(度)'])
        s7_elec_df['emission'] = (s7_elec_df['用電量(度)'] * 0.474) / 1000
        s7_elec_df = s7_elec_df[s7_elec_df['emission'] > 0]
        if not s7_elec_df.empty:
            max_val = s7_elec_df['emission'].max()
            colors = ['#FF4136' if v == max_val else '#1E90FF' for v in s7_elec_df['emission']]
            elec_fig = go.Figure(go.Bar(
                x=s7_elec_df['月份'], y=s7_elec_df['emission'], text=s7_elec_df['emission'].apply(lambda x: f'{x:.4f}'),
                textposition='auto', marker_color=colors
            ))
            elec_fig.update_layout(
                title_text='每月外購電力排放 (tCO2e)', xaxis_title="月份", yaxis_title="排放量(tCO2e)", height=400,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(elec_fig, use_container_width=True)
        else:
            st.write("外購電力: 無排放數據")

    with col2:
        water_factor = st.session_state[f'water_factors_{prefix}'][st.session_state[f's7_water_source_{prefix}']]
        s7_water_df = pd.DataFrame(st.session_state[f's7_water_{prefix}'].items(), columns=['月份', '用水量(度)'])
        s7_water_df['emission'] = (s7_water_df['用水量(度)'] * water_factor) / 1000
        s7_water_df = s7_water_df[s7_water_df['emission'] > 0]
        if not s7_water_df.empty:
            max_val = s7_water_df['emission'].max()
            colors = ['#FF4136' if v == max_val else '#1E90FF' for v in s7_water_df['emission']]
            water_fig = go.Figure(go.Bar(
                x=s7_water_df['月份'], y=s7_water_df['emission'],
                text=s7_water_df['emission'].apply(lambda x: f'{x:.4f}'),
                textposition='auto', marker_color=colors
            ))
            water_fig.update_layout(
                title_text='每月外購水力排放 (tCO2e)', xaxis_title="月份", yaxis_title="排放量(tCO2e)", height=400,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(water_fig, use_container_width=True)
        else:
            st.write("外購水力: 無排放數據")


def create_input_form(prefix, title):
    """Renders the multi-tab data input form for a given AR version."""
    st.title(f"{title}-溫室氣體盤查資料輸入")

    # --- Year Selector ---
    years_options = list(range(datetime.now().year + 25, 2019, -1))
    try:
        index = years_options.index(st.session_state[f'inventory_year_{prefix}'])
    except (KeyError, ValueError):
        index = years_options.index(datetime.now().year) if datetime.now().year in years_options else 0

    st.session_state[f'inventory_year_{prefix}'] = st.selectbox(
        "盤查年度:", years_options, index=index, key=f'year_selector_{prefix}'
    )

    st.info("請填寫以下各類別的活動數據，系統將自動計算排放量。")
    st.divider()

    # --- TABS FOR NAVIGATION ---
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "1. 固定源", "2. 移動源", "3. 汙水", "4. 滅火器",
        "5. 冷媒", "6. 員工通勤", "7. 電力/水力"
    ])

    # --- Tab 1: Stationary Sources ---
    with tab1:
        cols = st.columns([2, 2, 1])
        cols[0].markdown("**燃料類別**")
        cols[1].markdown("**使用量**")
        cols[2].markdown("**排放量計算 (tCO2e)**")
        data = st.session_state[f's1_data_{prefix}']
        total = 0
        for item, values in data.items():
            cols = st.columns([2, 2, 1])
            cols[0].write(f"{item} ({values['unit']})")
            values['usage'] = cols[1].number_input(" ", key=f"s1_{item}_{prefix}", value=values['usage'],
                                                   label_visibility="collapsed")
            emission = values['usage'] * values['factor']
            cols[2].text_input(" ", f"{emission:.4f}", key=f"s1_{item}_out_{prefix}", disabled=True,
                               label_visibility="collapsed")
            total += emission
        st.metric("固定源碳排放當量 (tCO2e)", f"{total:.4f}")

    # --- Tab 2: Mobile Sources ---
    with tab2:
        cols = st.columns([2, 2, 1])
        cols[0].markdown("**燃料類別**")
        cols[1].markdown("**使用量**")
        cols[2].markdown("**排放量計算 (tCO2e)**")
        data = st.session_state[f's2_data_{prefix}']
        total = 0
        for item, values in data.items():
            cols = st.columns([2, 2, 1])
            name = values.get('name', item)
            cols[0].write(f"{name} ({values['unit']})")
            values['usage'] = cols[1].number_input(" ", key=f"s2_{item}_{prefix}", value=values['usage'],
                                                   label_visibility="collapsed")
            emission = values['usage'] * values['factor']
            cols[2].text_input(" ", f"{emission:.4f}", key=f"s2_{item}_out_{prefix}", disabled=True,
                               label_visibility="collapsed")
            total += emission
        st.metric("移動源碳排放當量 (tCO2e)", f"{total:.4f}")

    # --- Tab 3: Wastewater ---
    with tab3:
        st.selectbox("學校汙水是否有納入汙水下水道系統？", ['否 (使用化糞池)', '是 (無化糞池逸散)'],
                     key=f's3_septic_system_{prefix}')
        total = 0
        if st.session_state[f's3_septic_system_{prefix}'] == '否 (使用化糞池)':
            cols = st.columns([2, 2, 1])
            cols[0].markdown("**人員類別**")
            cols[1].markdown("**人數**")
            cols[2].markdown("**排放量計算 (tCO2e)**")
            data = st.session_state[f's3_data_{prefix}']
            for item, values in data.items():
                cols = st.columns([2, 2, 1])
                cols[0].write(f"{item}")
                values['usage'] = cols[1].number_input(" ", key=f"s3_{item}_{prefix}", value=values['usage'],
                                                       label_visibility="collapsed")
                emission = values['usage'] * values['factor'] * 28
                cols[2].text_input(" ", f"{emission:.4f}", key=f"s3_{item}_out_{prefix}", disabled=True,
                                   label_visibility="collapsed")
                total += emission
        st.metric("汙水排放碳排放當量 (tCO2e)", f"{total:.4f}")

    # --- Tab 4: Fire Extinguishers ---
    with tab4:
        cols = st.columns([2, 2, 1])
        cols[0].markdown("**類別**")
        cols[1].markdown("**每年填充/使用量 (公斤/年)**")
        cols[2].markdown("**排放量計算 (tCO2e)**")
        data = st.session_state[f's4_data_{prefix}']
        total = 0
        for item, values in data.items():
            cols = st.columns([2, 2, 1])
            cols[0].write(f"{item}")
            values['usage'] = cols[1].number_input(" ", key=f"s4_{item}_{prefix}", value=values['usage'],
                                                   label_visibility="collapsed")
            emission = 0
            if values.get('gwp') is not None:
                emission = (values['usage'] * values['gwp']) / 1000
            elif values.get('factor') is not None:
                emission = values['usage'] * values['factor']
            cols[2].text_input(" ", f"{emission:.4f}", key=f"s4_{item}_out_{prefix}", disabled=True,
                               label_visibility="collapsed")
            total += emission
        st.metric("滅火器使用碳排放當量 (tCO2e)", f"{total:.4f}")

    # --- Tab 5: Refrigerants ---
    with tab5:
        cols = st.columns([2, 2, 1, 1])
        cols[0].markdown("**冷媒種類**")
        cols[1].markdown("**每年填充量 (公斤/年)**")
        cols[2].markdown("**GWP係數**")
        cols[3].markdown("**排放量 (tCO2e)**")
        data = st.session_state[f's5_data_{prefix}']
        total = 0
        for item, values in data.items():
            cols = st.columns([2, 2, 1, 1])
            cols[0].write(f"{item}")
            values['usage'] = cols[1].number_input(" ", key=f"s5_{item}_{prefix}", value=values['usage'], step=0.1,
                                                   format="%.1f", label_visibility="collapsed")
            cols[2].text_input(" ", value=values['gwp'], key=f"s5_gwp_{item}_{prefix}", disabled=True,
                               label_visibility="collapsed")
            emission = (values['usage'] * values['gwp']) / 1000
            cols[3].text_input(" ", f"{emission:.4f}", key=f"s5_{item}_out_{prefix}", disabled=True,
                               label_visibility="collapsed")
            total += emission
        st.metric("填充冷媒碳排放當量 (tCO2e)", f"{total:.4f}")

    # --- Tab 6: Commuting ---
    with tab6:
        cols = st.columns([2, 2, 1, 1])
        cols[0].markdown("**交通工具**")
        cols[1].markdown("**總通勤距離 (公里/年)**")
        cols[2].markdown("**排放係數 (KgCO2e/pkm)**")
        cols[3].markdown("**排放量 (tCO2e)**")
        data = st.session_state[f's6_data_{prefix}']
        total = 0
        for item, values in data.items():
            cols = st.columns([2, 2, 1, 1])
            cols[0].write(f"{item}")
            values['distance'] = cols[1].number_input(" ", key=f"s6_{item}_{prefix}", value=values['distance'],
                                                      label_visibility="collapsed")
            cols[2].text_input(" ", value=values['factor'], key=f"s6_factor_{item}_{prefix}", disabled=True,
                               label_visibility="collapsed")
            emission = (values['distance'] * values['factor']) / 1000
            cols[3].text_input(" ", f"{emission:.4f}", key=f"s6_{item}_out_{prefix}", disabled=True,
                               label_visibility="collapsed")
            total += emission
        st.metric("員工通勤碳排放當量 (tCO2e)", f"{total:.4f}")

    # --- Tab 7: Utilities ---
    with tab7:
        st.subheader("外購電力 (度)")
        data_elec = st.session_state[f's7_electricity_{prefix}']
        cols = st.columns(4)
        for i, month in enumerate(data_elec.keys()):
            data_elec[month] = cols[i % 4].number_input(month, key=f"s7_elec_{month}_{prefix}", value=data_elec[month])
        total_usage_elec = sum(data_elec.values())
        total_emission_elec = (total_usage_elec * 0.474) / 1000
        st.metric("總用電度數", f"{total_usage_elec:,}")
        st.metric("外購電力碳排放當量 (tCO2e)", f"{total_emission_elec:.4f}")

        st.divider()
        st.subheader("外購水力 (度)")
        st.selectbox("請選擇供水單位", options=list(st.session_state[f'water_factors_{prefix}'].keys()),
                     key=f's7_water_source_{prefix}')
        data_water = st.session_state[f's7_water_{prefix}']
        cols = st.columns(4)
        for i, month in enumerate(data_water.keys()):
            data_water[month] = cols[i % 4].number_input(month, key=f"s7_water_{month}_{prefix}",
                                                         value=data_water[month])
        total_usage_water = sum(data_water.values())
        water_factor = st.session_state[f'water_factors_{prefix}'][st.session_state[f's7_water_source_{prefix}']]
        total_emission_water = (total_usage_water * water_factor) / 1000
        st.metric("總用水度數", f"{total_usage_water:,}")
        st.metric("外購水力碳排放當量 (tCO2e)", f"{total_emission_water:.4f}")

    st.divider()

    # --- Action Buttons ---
    col1, col2 = st.columns([1, 3])
    with col1:
        excel_data = to_excel(prefix)
        st.download_button(
            label="📥 下載Excel資料", data=excel_data,
            file_name=f"{title}_GHG盤查資料_{st.session_state[f'inventory_year_{prefix}']}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True
        )
    with col2:
        if st.button("✅ 計算並查看儀表板", use_container_width=True, type="primary", key=f'view_dashboard_{prefix}'):
            calculate_totals(prefix)
            st.session_state[f'show_dashboard_{prefix}'] = True
            st.rerun()


def show_campus_carbon_negative_page():
    """Renders the interactive page for Campus Carbon Negative projects."""
    st.title("校園負碳")

    # Add the year selector
    years_options = list(range(datetime.now().year + 25, 2019, -1))
    st.session_state.campus_inventory_year = st.selectbox(
        "盤查年度:", years_options,
        index=years_options.index(st.session_state.campus_inventory_year),
        key='campus_year_selector'
    )

    st.info("請在此頁面輸入或編輯校園的減碳活動數據，系統將自動計算總減碳量。")

    total_reduction = 0

    # --- Section 1: Renewable Energy (Self-use) ---
    st.subheader("再生能源(自發自用)")
    with st.expander("查看減碳量計算公式"):
        st.latex(r'''
        \text{減碳量 (公噸CO2e/年)} = \frac{\text{每年實際發電度數} \times 0.474}{1000}
        ''')
        st.caption("其中 0.474 (kgCO2e/度) 是電力排放係數。")

    df_self_use = pd.DataFrame(st.session_state.campus_renewable_self_use)
    df_self_use['減碳量(公噸CO2e/年)'] = df_self_use['每年實際發電度數'] * 0.474 / 1000

    edited_df_self_use = st.data_editor(
        df_self_use,
        key="editor_self_use",
        use_container_width=True,
        column_config={
            "類別": st.column_config.TextColumn("類別", disabled=True),
            "每年實際發電度數": st.column_config.NumberColumn("每年實際發電度數", min_value=0, format="%d"),
            "單位": st.column_config.TextColumn("單位", disabled=True),
            "減碳量(公噸CO2e/年)": st.column_config.NumberColumn("減碳量(公噸CO2e/年)", disabled=True, format="%.4f"),
        },
        hide_index=True,
    )
    st.session_state.campus_renewable_self_use = edited_df_self_use.to_dict('records')
    total_self_use = edited_df_self_use['減碳量(公噸CO2e/年)'].sum()
    total_reduction += total_self_use
    st.metric("再生能源(自發自用)總減碳量 (tCO2e)", f"{total_self_use:.4f}")

    st.divider()

    # --- Section 2: Renewable Energy (Sold) ---
    st.subheader("再生能源(售電予廠商)")
    with st.expander("查看減碳量計算公式"):
        st.latex(r'''
        \text{減碳量 (公噸CO2e/年)} = \frac{\text{每年實際發電度數} \times 0.474}{1000}
        ''')
        st.caption("其中 0.474 (kgCO2e/度) 是電力排放係數。")

    df_sold = pd.DataFrame(st.session_state.campus_renewable_sold)
    df_sold['減碳量(公噸CO2e/年)'] = df_sold['每年實際發電度數'] * 0.474 / 1000

    edited_df_sold = st.data_editor(
        df_sold,
        key="editor_sold",
        use_container_width=True,
        column_config={
            "類別": st.column_config.TextColumn("類別", disabled=True),
            "每年實際發電度數": st.column_config.NumberColumn("每年實際發電度數", min_value=0, format="%d"),
            "單位": st.column_config.TextColumn("單位", disabled=True),
            "減碳量(公噸CO2e/年)": st.column_config.NumberColumn("減碳量(公噸CO2e/年)", disabled=True, format="%.4f"),
        },
        hide_index=True,
    )
    st.session_state.campus_renewable_sold = edited_df_sold.to_dict('records')
    total_sold = edited_df_sold['減碳量(公噸CO2e/年)'].sum()
    total_reduction += total_sold
    st.metric("再生能源(售電予廠商)總減碳量 (tCO2e)", f"{total_sold:.4f}")

    st.divider()

    # --- Section 3: Tree Carbon Sink ---
    st.subheader("樹木碳匯(結合校園樹木資訊平台-碳匯計算機)")
    with st.expander("查看固碳量計算公式"):
        st.latex(r'''
        \text{固碳量 (公噸CO2e/年)} = \frac{\text{植物固碳當量 (kgCO2e)}}{1000}
        ''')

    df_trees = pd.DataFrame(st.session_state.campus_tree_sink)
    df_trees['固碳量(公噸CO2e/年)'] = df_trees['植物固碳當量(kgCO2e)'] / 1000

    edited_df_trees = st.data_editor(
        df_trees,
        key="editor_trees",
        use_container_width=True,
        column_config={
            "樹木類別": st.column_config.TextColumn("樹木類別", disabled=True),
            "植物固碳當量(kgCO2e)": st.column_config.NumberColumn("植物固碳當量(kgCO2e)", min_value=0, format="%d"),
            "固碳量(公噸CO2e/年)": st.column_config.NumberColumn("固碳量(公噸CO2e/年)", disabled=True, format="%.4f"),
        },
        hide_index=True,
    )
    st.session_state.campus_tree_sink = edited_df_trees.to_dict('records')
    total_trees = edited_df_trees['固碳量(公噸CO2e/年)'].sum()
    total_reduction += total_trees
    st.metric("樹木碳匯總固碳量 (tCO2e)", f"{total_trees:.4f}")

    st.divider()

    # --- Grand Total ---
    st.header(f"{st.session_state.campus_inventory_year} 年度校園總減碳量")
    st.metric("總減碳量 (公噸CO2e/年)", f"{total_reduction:.4f}")


# =============================================================================
# Main App Logic
# =============================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    initialize_state()
    main_app()
else:
    login_page()
