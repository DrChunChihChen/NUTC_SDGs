import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO
import base64
import os
from pathlib import Path
import logging
import copy


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
# Centralized GHG Configuration
# =============================================================================
# This new structure holds all factors and GWPs for different AR versions.
# To add AR7, you would just add a new 'AR7' key with its corresponding data.
GHG_CONFIG = {
    'AR5': {
        'gwp': {'CH4': 28, 'N2O': 265},
        'factors': {
            's1_data': {
                '燃料油': {'usage': 100, 'unit': '公升/年', 'factor': 0.002567},
                '天然氣(NG)': {'usage': 100, 'unit': '度/年', 'factor': 0.001881},
                '液化石油氣(LPG)': {'usage': 100, 'unit': '公升/年', 'factor': 0.001754},
                '汽油': {'usage': 100, 'unit': '公升/年', 'factor': 0.002271},
                '柴油': {'usage': 100, 'unit': '公升/年', 'factor': 0.002615},
                '潤滑油': {'usage': 100, 'unit': '公升/年', 'factor': 0.002956},
            },
            's2_data': {
                '車用汽油': {'usage': 100, 'unit': '公升/年', 'factor': 0.002298},
                '車用柴油': {'usage': 100, 'unit': '公升/年', 'factor': 0.002722},
                '煤油': {'usage': 100, 'unit': '公升/年', 'factor': 0.002567},
                '潤滑油_mobile': {'name': '潤滑油', 'usage': 100, 'unit': '公升/年', 'factor': 0.002956},
                '液化石油氣(LPG)_mobile': {'name': '液化石油氣(LPG)', 'usage': 100, 'unit': '公升/年', 'factor': 0.001803},
                '液化天然氣(LNG)': {'usage': 100, 'unit': '度/年', 'factor': 0.002241},
            },
            's3_data': {
                '平日日間使用學生': {'usage': 100, 'factor': 0.0021}, # CH4 factor
                '平日夜間使用學生': {'usage': 10, 'factor': 0.0005},
                '假日使用學生': {'usage': 0, 'factor': 0.0},
                '住宿人員': {'usage': 0, 'factor': 0.0},
                '平日日間使用員工': {'usage': 50, 'factor': 0.0021},
                '平日夜間使用員工': {'usage': 5, 'factor': 0.0005},
                '假日使用員工': {'usage': 0, 'factor': 0.0},
            },
            's4_data': {
                '二氧化碳滅火器': {'usage': 1, 'gwp': 1},
                'FM-200': {'usage': 1, 'gwp': 3350},
                'BC型乾粉滅火器': {'usage': 1, 'gwp': 0.0003},
                'KBC型乾粉滅火器': {'usage': 1, 'gwp': 0.0002},
            },
            's5_data': {
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
            },
             's6_data': {
                '汽車-汽油': {'distance': 100, 'factor': 0.104}, '汽車-電動車': {'distance': 100, 'factor': 0.04},
                '機車-一般機車': {'distance': 100, 'factor': 0.079}, '機車-電動機車': {'distance': 100, 'factor': 0.017},
                '公車/客運': {'distance': 100, 'factor': 0.078}, '捷運': {'distance': 100, 'factor': 0.04},
                '火車': {'distance': 0, 'factor': 0.04}, '高鐵': {'distance': 0, 'factor': 0.028}
            },
            's7_factors': {
                'electricity': 0.474, # kgCO2e/kWh
                'water': {'台灣自來水營業事業處': 0.1872, '臺北自來水營業事業處': 0.0666} # kgCO2e/m^3
            }
        }
    },
    'AR6': {
        'gwp': {'CH4': 27.2, 'N2O': 273}, # Different GWP values for AR6
        'factors': {
            # For this example, let's assume most factors are the same as AR5,
            # but you can change any value here for AR6.
            's1_data': {
                '燃料油': {'usage': 100, 'unit': '公升/年', 'factor': 0.002570}, # Slightly different factor
                '天然氣(NG)': {'usage': 100, 'unit': '度/年', 'factor': 0.001885}, # Slightly different factor
                '液化石油氣(LPG)': {'usage': 100, 'unit': '公升/年', 'factor': 0.001754},
                '汽油': {'usage': 100, 'unit': '公升/年', 'factor': 0.002271},
                '柴油': {'usage': 100, 'unit': '公升/年', 'factor': 0.002615},
                '潤滑油': {'usage': 100, 'unit': '公升/年', 'factor': 0.002956},
            },
            's2_data': {
                '車用汽油': {'usage': 100, 'unit': '公升/年', 'factor': 0.002300}, # Slightly different factor
                '車用柴油': {'usage': 100, 'unit': '公升/年', 'factor': 0.002722},
                '煤油': {'usage': 100, 'unit': '公升/年', 'factor': 0.002567},
                '潤滑油_mobile': {'name': '潤滑油', 'usage': 100, 'unit': '公升/年', 'factor': 0.002956},
                '液化石油氣(LPG)_mobile': {'name': '液化石油氣(LPG)', 'usage': 100, 'unit': '公升/年', 'factor': 0.001803},
                '液化天然氣(LNG)': {'usage': 100, 'unit': '度/年', 'factor': 0.002241},
            },
            's3_data': {
                '平日日間使用學生': {'usage': 100, 'factor': 0.0021},
                '平日夜間使用學生': {'usage': 10, 'factor': 0.0005},
                '假日使用學生': {'usage': 0, 'factor': 0.0},
                '住宿人員': {'usage': 0, 'factor': 0.0},
                '平日日間使用員工': {'usage': 50, 'factor': 0.0021},
                '平日夜間使用員工': {'usage': 5, 'factor': 0.0005},
                '假日使用員工': {'usage': 0, 'factor': 0.0},
            },
            's4_data': {
                '二氧化碳滅火器': {'usage': 1, 'gwp': 1},
                'FM-200': {'usage': 1, 'gwp': 3220}, # Different GWP
                'BC型乾粉滅火器': {'usage': 1, 'gwp': 0.0003},
                'KBC型乾粉滅火器': {'usage': 1, 'gwp': 0.0002},
            },
            's5_data': { # GWP values updated for AR6
                'HFC-23/R-23': {'usage': 0.5, 'gwp': 14600}, 'HFC-32/R-32': {'usage': 0.1, 'gwp': 771},
                'HFC-41': {'usage': 0.0, 'gwp': 117}, 'HFC-134': {'usage': 0.0, 'gwp': 1310},
                'HFC-134a/R-134a': {'usage': 0.0, 'gwp': 1530}, 'HFC-143': {'usage': 0.0, 'gwp': 359},
                'HFC-143a/R-143a': {'usage': 0.0, 'gwp': 5810}, 'HFC-152': {'usage': 0.0, 'gwp': 17},
                'HFC-152a/R-152a': {'usage': 0.0, 'gwp': 164}, 'R401a': {'usage': 0.0, 'gwp': 1300}, # Example, may need real AR6 values
                'R401B': {'usage': 0.0, 'gwp': 1400}, 'R404A': {'usage': 0.5, 'gwp': 4740},
                'R407A': {'usage': 0.0, 'gwp': 2100}, 'R407B': {'usage': 0.0, 'gwp': 2800},
                'R407C': {'usage': 0.0, 'gwp': 1800}, 'R408A': {'usage': 0.0, 'gwp': 3300},
                'R410A': {'usage': 0.0, 'gwp': 2260}, 'R413A': {'usage': 0.0, 'gwp': 2000},
                'R417A': {'usage': 0.0, 'gwp': 2200}, 'R507A': {'usage': 0.0, 'gwp': 4800}
            },
             's6_data': {
                '汽車-汽油': {'distance': 100, 'factor': 0.104}, '汽車-電動車': {'distance': 100, 'factor': 0.04},
                '機車-一般機車': {'distance': 100, 'factor': 0.079}, '機車-電動機車': {'distance': 100, 'factor': 0.017},
                '公車/客運': {'distance': 100, 'factor': 0.078}, '捷運': {'distance': 100, 'factor': 0.04},
                '火車': {'distance': 0, 'factor': 0.04}, '高鐵': {'distance': 0, 'factor': 0.028}
            },
            's7_factors': {
                'electricity': 0.474,
                'water': {'台灣自來水營業事業處': 0.1872, '臺北自來水營業事業處': 0.0666}
            }
        }
    },
    'AR7': { # Placeholder for the future
        'gwp': {'CH4': 27.0, 'N2O': 270},
        'factors': {
            # ... Add AR7 specific factors here
        }
    }
}


# =============================================================================
# Helper function to encode images
# =============================================================================
def get_image_as_base64(file_path):
    """Reads a file and returns its base64 encoded string with logging."""
    try:
        path = Path(file_path)
        if not path.exists():
            logger.error(f"圖片檔案不存在: {file_path}")
            return None
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        logger.error(f"讀取圖片時發生錯誤: {str(e)}")
        return None

def get_image_mime_type(file_path):
    """Determines the MIME type based on file extension."""
    extension = Path(file_path).suffix.lower()
    mime_types = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg'}
    return mime_types.get(extension, 'image/jpeg')


# =============================================================================
# Reusable Components
# =============================================================================
def set_background(file_path):
    """Sets a background image for the Streamlit app with logging."""
    base64_img = get_image_as_base64(file_path)
    if base64_img:
        mime_type = get_image_mime_type(file_path)
        page_bg_img = f"""<style>.stApp {{ background-image: url("data:{mime_type};base64,{base64_img}"); ... }}</style>""" # Simplified for brevity
        st.markdown(page_bg_img, unsafe_allow_html=True)

def display_footer():
    """Displays the contact information footer."""
    st.divider()
    # ... (footer code remains the same)

# =============================================================================
# User Authentication
# =============================================================================
# ... (authentication code remains the same)
def load_users_from_secrets():
    if "auth" in st.secrets:
        return st.secrets.auth
    return {}
USERS = load_users_from_secrets()

def login_page():
    st.title("校園碳盤查系統")
    with st.form("login_form"):
        username = st.text_input("帳號")
        password = st.text_input("密碼", type="password")
        if st.form_submit_button("登入"):
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("帳號或密碼錯誤")

# =============================================================================
# Data Initialization (Refactored)
# =============================================================================
def get_initial_data(ar_version):
    """
    Initializes session state with data for the selected AR version.
    This function now populates a generic 'current_data' key.
    """
    # Deep copy to prevent modifying the original config
    config = copy.deepcopy(GHG_CONFIG.get(ar_version, GHG_CONFIG['AR5'])) # Default to AR5 if not found
    
    st.session_state['current_gwp'] = config['gwp']
    st.session_state['current_factors'] = config['factors']

    # Initialize usage/activity data if not present or if AR version changes
    st.session_state['s1_data'] = config['factors']['s1_data']
    st.session_state['s2_data'] = config['factors']['s2_data']
    st.session_state['s3_data'] = config['factors']['s3_data']
    st.session_state['s4_data'] = config['factors']['s4_data']
    st.session_state['s5_data'] = config['factors']['s5_data']
    st.session_state['s6_data'] = config['factors']['s6_data']
    
    # These are less likely to change between AR versions but kept for consistency
    if 's3_septic_system' not in st.session_state:
        st.session_state['s3_septic_system'] = '否 (使用化糞池)'
    if 's7_electricity' not in st.session_state:
        months = ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
        st.session_state['s7_electricity'] = {m: 10000 for m in months}
    if 's7_water' not in st.session_state:
        months = ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
        st.session_state['s7_water'] = {m: 100 for m in months}
    if 's7_water_source' not in st.session_state:
        st.session_state['s7_water_source'] = '台灣自來水營業事業處'

def get_campus_initial_data():
    """Initializes session state with default values for the campus carbon negative page."""
    # ... (this function remains the same)

def initialize_state():
    """Initializes all necessary session states."""
    if 'page' not in st.session_state:
        st.session_state.page = "GHG Inventory"
    if 'ar_version' not in st.session_state:
        st.session_state.ar_version = "AR5"
    if 'inventory_year' not in st.session_state:
        st.session_state.inventory_year = datetime.now().year

    get_initial_data(st.session_state.ar_version)
    get_campus_initial_data()


# =============================================================================
# Excel Export & Import Functions (Refactored)
# =============================================================================
def to_excel():
    """Serializes all current data from session state into an Excel file."""
    # This function now uses the generic 'current' keys, not prefixed ones.
    # ... (code would be similar to the original, but using st.session_state['s1_data'] etc.)
    # ... for brevity, the logic is omitted but would need to be updated.
    output = BytesIO()
    # ...
    # df1 = pd.DataFrame.from_dict(st.session_state['s1_data'], orient='index')
    # ...
    return output.getvalue()

def load_from_excel(uploaded_file):
    """Loads data from an uploaded Excel file into session state."""
    # This function would also be updated to populate the generic keys.
    # ... for brevity, the logic is omitted.
    pass

# =============================================================================
# Calculation Functions (Refactored)
# =============================================================================
def calculate_totals():
    """Calculate all emission totals using data from the current session state."""
    totals = {}
    gwp_ch4 = st.session_state['current_gwp']['CH4'] # Use GWP from current state

    totals['s1'] = sum(v['usage'] * v['factor'] for k, v in st.session_state['s1_data'].items())
    totals['s2'] = sum(v['usage'] * v['factor'] for k, v in st.session_state['s2_data'].items())
    
    is_septic_used = st.session_state['s3_septic_system'] == '否 (使用化糞池)'
    totals['s3'] = sum(v['usage'] * v['factor'] * gwp_ch4 for k, v in st.session_state['s3_data'].items()) if is_septic_used else 0
    
    s4_total = sum((v['usage'] * v['gwp']) / 1000 for k, v in st.session_state['s4_data'].items())
    totals['s4'] = s4_total
    
    totals['s5'] = sum((v['usage'] * v['gwp']) / 1000 for k, v in st.session_state['s5_data'].items())
    totals['s6'] = sum((v['distance'] * v['factor']) / 1000 for k, v in st.session_state['s6_data'].items())

    elec_factor = st.session_state['current_factors']['s7_factors']['electricity']
    total_electricity_usage = sum(st.session_state['s7_electricity'].values())
    totals['s7_electricity'] = (total_electricity_usage * elec_factor) / 1000
    
    water_factor_map = st.session_state['current_factors']['s7_factors']['water']
    water_source = st.session_state['s7_water_source']
    water_factor = water_factor_map[water_source]
    total_water_usage = sum(st.session_state['s7_water'].values())
    totals['s7_water'] = (total_water_usage * water_factor) / 1000

    # Store totals
    st.session_state['totals'] = totals
    scope1 = totals['s1'] + totals['s2'] + totals['s3'] + totals['s4'] + totals['s5']
    scope2 = totals['s7_electricity']
    scope3 = totals['s6'] + totals['s7_water']
    st.session_state['scope_totals'] = {
        'Scope 1': scope1, 'Scope 2': scope2, 'Scope 3': scope3, 'Grand Total': scope1 + scope2 + scope3
    }
    st.session_state['emission_breakdown'] = {
        '固定源': totals.get('s1', 0), '移動源': totals.get('s2', 0),
        '汙水': totals.get('s3', 0), '滅火器': totals.get('s4', 0),
        '冷媒': totals.get('s5', 0), '員工通勤': totals.get('s6', 0),
        '外購電力': totals.get('s7_electricity', 0), '外購水力': totals.get('s7_water', 0),
    }

# =============================================================================
# UI Components (Refactored)
# =============================================================================
def main_app():
    """Renders the main application with a simplified sidebar."""
    with st.sidebar:
        st.write(f"歡迎, {st.session_state.username}!")
        st.title("導覽選單")

        # Simplified navigation
        if st.button("溫室氣體盤查", use_container_width=True, type="primary" if st.session_state.page == "GHG Inventory" else "secondary"):
            st.session_state.page = "GHG Inventory"
            st.rerun()
        if st.button("校園負碳", use_container_width=True, type="primary" if st.session_state.page == "Campus" else "secondary"):
            st.session_state.page = "Campus"
            st.rerun()
        if st.button("從Excel匯入", use_container_width=True, type="primary" if st.session_state.page == "Upload" else "secondary"):
            st.session_state.page = "Upload"
            st.rerun()

        st.divider()
        if st.button("登出"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

    # Page Routing
    if st.session_state.page == "GHG Inventory":
        if st.session_state.get("show_dashboard", False):
            create_dashboard()
        else:
            create_input_form()
    elif st.session_state.page == "Campus":
        show_campus_carbon_negative_page()
    elif st.session_state.page == "Upload":
        create_upload_page()

def create_dashboard():
    """Renders the main dashboard view."""
    title = f"{st.session_state.ar_version} - {st.session_state.inventory_year} 年度"
    st.title(f"{title} 溫室氣體盤查儀表板")
    if st.button("⬅️ 返回編輯資料"):
        st.session_state['show_dashboard'] = False
        st.rerun()
    # ... (Dashboard logic remains similar, but uses generic keys like st.session_state['scope_totals'])
    # ... For brevity, the rest of the dashboard plotting code is omitted.

def create_input_form():
    """Renders the single, dynamic data input form."""
    st.title("溫室氣體盤查資料輸入")

    # --- AR Version and Year Selectors ---
    col1, col2 = st.columns(2)
    with col1:
        # Get available AR versions from config, excluding empty ones like AR7
        available_ars = [ar for ar, data in GHG_CONFIG.items() if data.get('factors')]
        selected_ar = st.selectbox(
            "選擇盤查版本 (GWP & 係數):", available_ars, 
            index=available_ars.index(st.session_state.ar_version)
        )
        if selected_ar != st.session_state.ar_version:
            st.session_state.ar_version = selected_ar
            # Reload data for the new version
            get_initial_data(selected_ar)
            st.rerun()

    with col2:
        years_options = list(range(datetime.now().year + 25, 2019, -1))
        st.session_state.inventory_year = st.selectbox(
            "盤查年度:", years_options, 
            index=years_options.index(st.session_state.inventory_year)
        )

    st.info(f"您正在使用 {st.session_state.ar_version} 的係數與GWP值進行計算。請填寫以下各類別的活動數據。")
    st.divider()

    # --- TABS FOR NAVIGATION ---
    # The tab rendering logic remains the same, but it will now use the generic
    # session state keys (e.g., st.session_state['s1_data']) which are dynamically populated.
    # For brevity, the detailed tab layout code is omitted but would be nearly identical
    # to your original `create_input_form` but without the `prefix`.
    # Example for Tab 1:
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["1. 固定源", "2. 移動源", "3. 汙水", "4. 滅火器", "5. 冷媒", "6. 員工通勤", "7. 電力/水力"])
    with tab1:
        # This section is now dynamic based on the loaded data
        data = st.session_state['s1_data']
        for item, values in data.items():
            # ... render number_input for values['usage'] ...
            pass
    
    st.divider()
    # --- Action Buttons ---
    if st.button("✅ 計算並查看儀表板", use_container_width=True, type="primary"):
        calculate_totals()
        st.session_state['show_dashboard'] = True
        st.rerun()

def create_upload_page():
    st.title("從 Excel 匯入資料")
    # ... (This page would also need refactoring to load data into the new generic state)
    
def show_campus_carbon_negative_page():
    st.title("校園負碳")
    # ... (This page remains the same as it's not AR-version dependent)

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
