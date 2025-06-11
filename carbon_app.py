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
        if not path.is_file():
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
    mime_types = {
        '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
        '.gif': 'image/gif', '.webp': 'image/webp', '.svg': 'image/svg+xml',
        '.bmp': 'image/bmp'
    }
    return mime_types.get(extension, 'image/jpeg')


# =============================================================================
# Reusable Components
# =============================================================================
def set_background(file_path):
    """Sets a background image for the Streamlit app."""
    base64_img = get_image_as_base64(file_path)
    if base64_img:
        mime_type = get_image_mime_type(file_path)
        page_bg_img = f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:{mime_type};base64,{base64_img}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        [data-testid="stHeader"] {{
            background: rgba(0,0,0,0);
        }}
        .stForm, div[data-testid="stForm"] {{
            background-color: rgba(255, 255, 255, 0.9);
            padding: 2rem;
            border-radius: 0.5rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)


def display_footer():
    """Displays the contact information footer with a sharp logo."""
    st.divider()
    logo_path = "OFFICE_NUTC.png"
    logo_base64 = get_image_as_base64(logo_path)
    if logo_base64:
        st.markdown(f'<img src="data:image/png;base64,{logo_base64}" width="200">', unsafe_allow_html=True)
    elif os.path.exists(logo_path):
        st.image(logo_path, width=200)
    else:
        st.info("Logo not found. Please place OFFICE_NUTC.png in the program folder.")

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
USERS = {"Elvis": "0000", "Nutc1": "0001", "Nutc2": "0002", "Nutc3": "0003"}


def login_page():
    """Renders the login page."""
    set_background("img1.jpg")
    st.title("校園碳盤查系統")
    st.write("請使用您的帳號密碼登入")
    with st.form("login_form"):
        username = st.text_input("帳號 (Username)")
        password = st.text_input("密碼 (Password)", type="password")
        if st.form_submit_button("登入"):
            if USERS.get(username) == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("登入成功！")
                st.rerun()
            else:
                st.error("帳號或密碼錯誤")
    display_footer()


# =============================================================================
# Data Initialization & State Management
# =============================================================================
def get_ar_initial_data(prefix):
    """Initializes session state with default data for AR5/AR6."""
    if f"show_dashboard_{prefix}" not in st.session_state:
        st.session_state[f"show_dashboard_{prefix}"] = False
    if f"inventory_year_{prefix}" not in st.session_state:
        years = range(datetime.now().year + 25, 2019, -1)
        st.session_state[f"inventory_year_{prefix}"] = datetime.now().year
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
            '平日日間使用學生': {'usage': 100, 'factor': 0.0021}, '平日夜間使用學生': {'usage': 10, 'factor': 0.0005},
            '假日使用學生': {'usage': 0, 'factor': 0.0}, '住宿人員': {'usage': 0, 'factor': 0.0},
            '平日日間使用員工': {'usage': 50, 'factor': 0.0021}, '平日夜間使用員工': {'usage': 5, 'factor': 0.0005},
            '假日使用員工': {'usage': 0, 'factor': 0.0},
        }
    if f"s4_data_{prefix}" not in st.session_state:
        st.session_state[f"s4_data_{prefix}"] = {
            '二氧化碳滅火器': {'usage': 1, 'gwp': 1, 'factor': None}, 'FM-200': {'usage': 1, 'gwp': 3350, 'factor': None},
            'BC型乾粉滅火器': {'usage': 1, 'gwp': None, 'factor': 0.0003}, 'KBC型乾粉滅火器': {'usage': 1, 'gwp': None, 'factor': 0.0002},
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
    months = ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
    if f"s7_electricity_{prefix}" not in st.session_state:
        st.session_state[f"s7_electricity_{prefix}"] = {m: 10000 for m in months}
    if f"s7_water_{prefix}" not in st.session_state:
        st.session_state[f"s7_water_{prefix}"] = {m: 100 for m in months}
    if f"s7_water_source_{prefix}" not in st.session_state:
        st.session_state[f"s7_water_source_{prefix}"] = '台灣自來水營業事業處'
    if f"water_factors_{prefix}" not in st.session_state:
        st.session_state[f"water_factors_{prefix}"] = {'台灣自來水營業事業處': 0.1872, '臺北自來水營業事業處': 0.0666}

def get_campus_initial_data():
    """Initializes session state for the campus carbon negative page."""
    if 'campus_inventory_year' not in st.session_state:
        st.session_state.campus_inventory_year = datetime.now().year
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
# Excel Export & Import Functions
# =============================================================================
def to_excel(prefix):
    """Serializes all input data from session state into a multi-sheet Excel file."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df1 = pd.DataFrame.from_dict(st.session_state[f's1_data_{prefix}'], orient='index')
        df1['排放量(tCO2e)'] = df1['usage'] * df1['factor']
        df1.reset_index().rename(columns={'index':'燃料類別', 'usage': '使用量', 'unit': '單位', 'factor': '排放係數'}).to_excel(writer, sheet_name='固定源', index=False)

        df2_data = [{'燃料類別': v.get('name', k), **v} for k, v in st.session_state[f's2_data_{prefix}'].items()]
        df2 = pd.DataFrame(df2_data)
        df2['排放量(tCO2e)'] = df2['usage'] * df2['factor']
        df2.rename(columns={'usage': '使用量', 'unit': '單位', 'factor': '排放係數'})[['燃料類別', '使用量', '單位', '排放係數', '排放量(tCO2e)']].to_excel(writer, sheet_name='移動源', index=False)
        
        if st.session_state[f's3_septic_system_{prefix}'] == '否 (使用化糞池)':
            df3 = pd.DataFrame.from_dict(st.session_state[f's3_data_{prefix}'], orient='index')
            df3['排放量(tCO2e)'] = df3['usage'] * df3['factor'] * 28
            df3.reset_index().rename(columns={'index':'人員類別', 'usage': '人數', 'factor': '排放係數(CH4)'}).to_excel(writer, sheet_name='汙水', index=False)
            
        df4 = pd.DataFrame.from_dict(st.session_state[f's4_data_{prefix}'], orient='index')
        df4['排放量(tCO2e)'] = 0
        df4.loc[df4['gwp'].notna(), '排放量(tCO2e)'] = (df4['usage'] * df4['gwp']) / 1000
        df4.loc[df4['factor'].notna(), '排放量(tCO2e)'] = df4['usage'] * df4['factor']
        df4.reset_index().rename(columns={'index':'類別', 'usage': '每年填充/使用量(公斤/年)', 'gwp': 'GWP係數', 'factor': '排放係數'}).to_excel(writer, sheet_name='滅火器', index=False)
        
        df5 = pd.DataFrame.from_dict(st.session_state[f's5_data_{prefix}'], orient='index')
        df5['排放量(tCO2e)'] = (df5['usage'] * df5['gwp']) / 1000
        df5.reset_index().rename(columns={'index':'冷媒種類', 'usage': '每年填充量(公斤/年)', 'gwp': 'GWP係數'}).to_excel(writer, sheet_name='冷媒', index=False)
        
        df6 = pd.DataFrame.from_dict(st.session_state[f's6_data_{prefix}'], orient='index')
        df6['排放量(tCO2e)'] = (df6['distance'] * df6['factor']) / 1000
        df6.reset_index().rename(columns={'index':'交通工具', 'distance': '總通勤距離(公里/年)', 'factor': '排放係數(KgCO2e/pkm)'}).to_excel(writer, sheet_name='員工通勤', index=False)

        df7_elec = pd.DataFrame(st.session_state[f's7_electricity_{prefix}'].items(), columns=['月份', '用電量(度)'])
        df7_elec['排放量(tCO2e)'] = (df7_elec['用電量(度)'] * 0.474) / 1000
        df7_elec.to_excel(writer, sheet_name='外購電力', index=False)

        water_factor = st.session_state[f'water_factors_{prefix}'][st.session_state[f's7_water_source_{prefix}']]
        df7_water = pd.DataFrame(st.session_state[f's7_water_{prefix}'].items(), columns=['月份', '用水量(度)'])
        df7_water['排放量(tCO2e)'] = (df7_water['用水量(度)'] * water_factor) / 1000
        df7_water.to_excel(writer, sheet_name='外購水力', index=False)
        worksheet = writer.sheets['外購水力']
        worksheet.write_string('E1', f'供水單位: {st.session_state[f"s7_water_source_{prefix}"]}')
        worksheet.write_string('E2', f'排放係數: {water_factor}')
    return output.getvalue()


def handle_excel_upload(uploaded_file, prefix):
    """Parses an uploaded Excel file and updates the session state."""
    try:
        xls = pd.ExcelFile(uploaded_file)
        def get_sheet(name): return pd.read_excel(xls, sheet_name=name) if name in xls.sheet_names else None
        if (df := get_sheet('固定源')) is not None:
            for _, r in df.iterrows(): st.session_state[f's1_data_{prefix}'][r['燃料類別']]['usage'] = r['使用量']
        if (df := get_sheet('移動源')) is not None:
            for _, r in df.iterrows():
                for k, v in st.session_state[f's2_data_{prefix}'].items():
                    if v.get('name', k) == r['燃料類別']: st.session_state[f's2_data_{prefix}'][k]['usage'] = r['使用量']; break
        if (df := get_sheet('汙水')) is not None:
            st.session_state[f's3_septic_system_{prefix}'] = '否 (使用化糞池)'
            for _, r in df.iterrows(): st.session_state[f's3_data_{prefix}'][r['人員類別']]['usage'] = r['人數']
        else: st.session_state[f's3_septic_system_{prefix}'] = '是 (無化糞池逸散)'
        if (df := get_sheet('滅火器')) is not None:
            for _, r in df.iterrows(): st.session_state[f's4_data_{prefix}'][r['類別']]['usage'] = r['每年填充/使用量(公斤/年)']
        if (df := get_sheet('冷媒')) is not None:
            for _, r in df.iterrows(): st.session_state[f's5_data_{prefix}'][r['冷媒種類']]['usage'] = r['每年填充量(公斤/年)']
        if (df := get_sheet('員工通勤')) is not None:
            for _, r in df.iterrows(): st.session_state[f's6_data_{prefix}'][r['交通工具']]['distance'] = r['總通勤距離(公里/年)']
        if (df := get_sheet('外購電力')) is not None:
            for _, r in df.iterrows(): st.session_state[f's7_electricity_{prefix}'][r['月份']] = r['用電量(度)']
        if (df := get_sheet('外購水力')) is not None:
            for _, r in df.iterrows(): st.session_state[f's7_water_{prefix}'][r['月份']] = r['用水量(度)']
        return True
    except Exception as e:
        st.error(f"檔案解析失敗: {e}"); return False


# =============================================================================
# Calculation Functions
# =============================================================================
def calculate_totals(prefix):
    """Calculate all emission totals and scopes for a given AR version."""
    totals = {}
    gwp_ch4 = 28
    totals['s1'] = sum(v['usage'] * v['factor'] for v in st.session_state[f's1_data_{prefix}'].values())
    totals['s2'] = sum(v['usage'] * v['factor'] for v in st.session_state[f's2_data_{prefix}'].values())
    is_septic = st.session_state[f's3_septic_system_{prefix}'] == '否 (使用化糞池)'
    totals['s3'] = sum(v['usage'] * v['factor'] * gwp_ch4 for v in st.session_state[f's3_data_{prefix}'].values()) if is_septic else 0
    s4_total = sum((v['usage'] * v.get('gwp',0)) / 1000 if v.get('gwp') is not None else v['usage'] * v.get('factor', 0) for v in st.session_state[f's4_data_{prefix}'].values())
    totals['s4'] = s4_total
    totals['s5'] = sum((v['usage'] * v['gwp']) / 1000 for v in st.session_state[f's5_data_{prefix}'].values())
    totals['s6'] = sum((v['distance'] * v['factor']) / 1000 for v in st.session_state[f's6_data_{prefix}'].values())
    totals['s7_electricity'] = (sum(st.session_state[f's7_electricity_{prefix}'].values()) * 0.474) / 1000
    water_factor = st.session_state[f'water_factors_{prefix}'][st.session_state[f's7_water_source_{prefix}']]
    totals['s7_water'] = (sum(st.session_state[f's7_water_{prefix}'].values()) * water_factor) / 1000
    
    scope1 = sum(totals[k] for k in ['s1', 's2', 's3', 's4', 's5'])
    scope2 = totals['s7_electricity']
    scope3 = totals['s6'] + totals['s7_water']
    st.session_state[f'scope_totals_{prefix}'] = {'Scope 1': scope1, 'Scope 2': scope2, 'Scope 3': scope3, 'Grand Total': scope1 + scope2 + scope3}
    st.session_state[f'emission_breakdown_{prefix}'] = {
        '固定源': totals['s1'], '移動源': totals['s2'], '汙水': totals['s3'], 
        '滅火器': totals['s4'], '冷媒': totals['s5'], '員工通勤': totals['s6'],
        '外購電力': totals['s7_electricity'], '外購水力': totals['s7_water'],
    }


# =============================================================================
# UI Components
# =============================================================================
def main_app():
    """Renders the main application with sidebar navigation."""
    with st.sidebar:
        st.write(f"歡迎, {st.session_state.username}!")
        st.title("導覽選單")
        if st.button("AR5-溫室氣體盤查資料", use_container_width=True, type="primary" if st.session_state.page == "AR5" else "secondary"):
            st.session_state.page = "AR5"; st.rerun()
        if st.button("AR6-溫室氣體盤查資料", use_container_width=True, type="primary" if st.session_state.page == "AR6" else "secondary"):
            st.session_state.page = "AR6"; st.rerun()
        if st.button("校園負碳", use_container_width=True, type="primary" if st.session_state.page == "Campus" else "secondary"):
            st.session_state.page = "Campus"; st.rerun()
        st.divider()
        st.subheader("手動上傳Excel")
        uploaded_file = st.file_uploader("選擇一個與下載格式相同的Excel檔案", type="xlsx")
        if uploaded_file:
            if st.button("讀取資料並顯示圖表", use_container_width=True):
                prefix = 'ar5' if st.session_state.page == 'AR5' else 'ar6'
                if handle_excel_upload(uploaded_file, prefix):
                    st.success("上傳成功！")
                    calculate_totals(prefix)
                    st.session_state[f'show_dashboard_{prefix}'] = True
                    st.rerun()
        st.divider()
        if st.button("登出"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()
        st.markdown("<div style='flex: 1;'></div>", unsafe_allow_html=True)
        display_footer()

    page = st.session_state.get("page", "AR5")
    prefix = 'ar5' if page == "AR5" else ('ar6' if page == "AR6" else 'campus')
    title = page

    if page in ["AR5", "AR6"]:
        if st.session_state.get(f"show_dashboard_{prefix}", False):
            create_dashboard(prefix, title)
        else:
            create_input_form(prefix, title)
    elif page == "Campus":
        show_campus_carbon_negative_page()


def create_dashboard(prefix, title):
    """Renders the main dashboard view."""
    st.title(f"{title} - {st.session_state[f'inventory_year_{prefix}']} 年度溫室氣體盤查儀表板")
    if st.button("⬅️ 返回編輯資料"):
        st.session_state[f'show_dashboard_{prefix}'] = False; st.rerun()
    
    scope = st.session_state[f'scope_totals_{prefix}']
    emissions = st.session_state[f'emission_breakdown_{prefix}']

    cols = st.columns(4)
    cols[0].metric("總碳排放量 (tCO2e)", f"{scope['Grand Total']:.2f}")
    cols[1].metric("範疇一 Scope 1", f"{scope['Scope 1']:.2f}")
    cols[2].metric("範疇二 Scope 2", f"{scope['Scope 2']:.2f}")
    cols[3].metric("範疇三 Scope 3", f"{scope['Scope 3']:.2f}")
    st.divider()

    cols = st.columns(2)
    with cols[0]:
        st.subheader("各類別排放佔比")
        fig = go.Figure(data=[go.Pie(labels=list(emissions.keys()), values=list(emissions.values()), hole=.4)])
        fig.update_layout(showlegend=False, height=400, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)
    with cols[1]:
        st.subheader("各範疇排放比較 (tCO2e)")
        scope_df = pd.DataFrame.from_dict(scope, orient='index').drop('Grand Total').reset_index()
        scope_df.columns = ['範疇', '排放量']
        fig = go.Figure(go.Bar(x=scope_df['排放量'], y=scope_df['範疇'], orientation='h', text=scope_df['排放量'].apply(lambda x: f'{x:.2f}')))
        fig.update_layout(height=400, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    st.subheader("各類別排放細項 (tCO2e)")
    def create_breakdown_chart(data, y_col, x_col, title):
        if not data.empty and data[x_col].sum() > 0:
            fig = go.Figure(go.Bar(x=data[x_col], y=data[y_col], orientation='h', text=data[x_col].apply(lambda x: f'{x:.4f}')))
            fig.update_layout(title_text=title, height=350, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)
    
    cols = st.columns(2)
    with cols[0]:
        df1 = pd.DataFrame.from_dict(st.session_state[f's1_data_{prefix}'], orient='index')
        df1['emission'] = df1['usage'] * df1['factor']
        create_breakdown_chart(df1, df1.index, 'emission', '固定源排放')
    with cols[1]:
        df2_items = [{'name': v.get('name', k), 'e': v['usage'] * v['factor']} for k, v in st.session_state[f's2_data_{prefix}'].items()]
        create_breakdown_chart(pd.DataFrame(df2_items), 'name', 'e', '移動源排放')

    st.divider()
    cols = st.columns(2)
    with cols[0]:
        df_elec = pd.DataFrame(st.session_state[f's7_electricity_{prefix}'].items(), columns=['月', 'e'])
        df_elec['e'] = (df_elec['e'] * 0.474) / 1000
        fig = go.Figure(go.Bar(x=df_elec['月'], y=df_elec['e'], text=df_elec['e'].apply(lambda x: f'{x:.4f}')))
        fig.update_layout(title_text='每月外購電力排放 (tCO2e)', height=400)
        st.plotly_chart(fig, use_container_width=True)
    with cols[1]:
        wf = st.session_state[f'water_factors_{prefix}'][st.session_state[f's7_water_source_{prefix}']]
        df_water = pd.DataFrame(st.session_state[f's7_water_{prefix}'].items(), columns=['月', 'e'])
        df_water['e'] = (df_water['e'] * wf) / 1000
        fig = go.Figure(go.Bar(x=df_water['月'], y=df_water['e'], text=df_water['e'].apply(lambda x: f'{x:.4f}')))
        fig.update_layout(title_text='每月外購水力排放 (tCO2e)', height=400)
        st.plotly_chart(fig, use_container_width=True)


def create_input_form(prefix, title):
    """Renders the multi-tab data input form."""
    st.title(f"{title}-溫室氣體盤查資料輸入")
    years_opts = list(range(datetime.now().year + 25, 2019, -1))
    st.selectbox("盤查年度:", years_opts, key=f'inventory_year_{prefix}')
    st.info("請填寫以下各類別的活動數據，系統將自動計算排放量。")
    st.divider()
    
    tab_names = ["1. 固定源", "2. 移動源", "3. 汙水", "4. 滅火器", "5. 冷媒", "6. 員工通勤", "7. 電力/水力"]
    tabs = st.tabs(tab_names)

    with tabs[0]:
        st.header("固定源")
        data = st.session_state[f's1_data_{prefix}']
        for item, values in data.items():
            cols = st.columns([2,2,1])
            cols[0].write(f"{item} ({values['unit']})")
            values['usage'] = cols[1].number_input(" ", key=f"s1_{item}_{prefix}", value=values['usage'], label_visibility="collapsed")
            cols[2].text_input(" ", f"{values['usage'] * values['factor']:.4f}", disabled=True, label_visibility="collapsed")

    with tabs[1]:
        st.header("移動源")
        data = st.session_state[f's2_data_{prefix}']
        for item, values in data.items():
            cols = st.columns([2,2,1])
            cols[0].write(f"{values.get('name', item)} ({values['unit']})")
            values['usage'] = cols[1].number_input(" ", key=f"s2_{item}_{prefix}", value=values['usage'], label_visibility="collapsed")
            cols[2].text_input(" ", f"{values['usage'] * values['factor']:.4f}", disabled=True, label_visibility="collapsed")

    with tabs[2]:
        st.header("汙水")
        st.selectbox("學校汙水是否有納入汙水下水道系統？", ['否 (使用化糞池)', '是 (無化糞池逸散)'], key=f's3_septic_system_{prefix}')
        if st.session_state[f's3_septic_system_{prefix}'] == '否 (使用化糞池)':
            data = st.session_state[f's3_data_{prefix}']
            for item, values in data.items():
                cols = st.columns([2,2,1])
                cols[0].write(item)
                values['usage'] = cols[1].number_input(" ", key=f"s3_{item}_{prefix}", value=values['usage'], label_visibility="collapsed")
                cols[2].text_input(" ", f"{values['usage'] * values['factor'] * 28:.4f}", disabled=True, label_visibility="collapsed")

    with tabs[3]:
        st.header("滅火器")
        data = st.session_state[f's4_data_{prefix}']
        for item, values in data.items():
            cols = st.columns([2,2,1])
            cols[0].write(item)
            values['usage'] = cols[1].number_input(" ", key=f"s4_{item}_{prefix}", value=values['usage'], label_visibility="collapsed")
            emission = (values['usage'] * values['gwp']) / 1000 if values.get('gwp') else values['usage'] * values.get('factor', 0)
            cols[2].text_input(" ", f"{emission:.4f}", disabled=True, label_visibility="collapsed")
            
    with tabs[4]:
        st.header("冷媒")
        data = st.session_state[f's5_data_{prefix}']
        for item, values in data.items():
            cols = st.columns([2, 2, 1, 1])
            cols[0].write(item)
            values['usage'] = cols[1].number_input(" ", key=f"s5_{item}_{prefix}", value=values['usage'], step=0.1, format="%.1f", label_visibility="collapsed")
            cols[2].text_input(" ", value=values['gwp'], disabled=True, label_visibility="collapsed")
            cols[3].text_input(" ", f"{(values['usage'] * values['gwp']) / 1000:.4f}", disabled=True, label_visibility="collapsed")

    with tabs[5]:
        st.header("員工通勤")
        data = st.session_state[f's6_data_{prefix}']
        for item, values in data.items():
            cols = st.columns([2, 2, 1, 1])
            cols[0].write(item)
            values['distance'] = cols[1].number_input(" ", key=f"s6_{item}_{prefix}", value=values['distance'], label_visibility="collapsed")
            cols[2].text_input(" ", value=values['factor'], disabled=True, label_visibility="collapsed")
            cols[3].text_input(" ", f"{(values['distance'] * values['factor']) / 1000:.4f}", disabled=True, label_visibility="collapsed")

    with tabs[6]:
        st.header("外購電力與水力")
        st.subheader("外購電力 (度)")
        data_elec = st.session_state[f's7_electricity_{prefix}']
        cols = st.columns(4)
        for i, month in enumerate(data_elec.keys()):
            data_elec[month] = cols[i % 4].number_input(month, key=f"s7_elec_{month}_{prefix}", value=data_elec[month])
        st.divider()
        st.subheader("外購水力 (度)")
        st.selectbox("請選擇供水單位", list(st.session_state[f'water_factors_{prefix}'].keys()), key=f's7_water_source_{prefix}')
        data_water = st.session_state[f's7_water_{prefix}']
        cols = st.columns(4)
        for i, month in enumerate(data_water.keys()):
            data_water[month] = cols[i % 4].number_input(month, key=f"s7_water_{month}_{prefix}", value=data_water[month])

    st.divider()
    col1, col2 = st.columns([1, 3])
    with col1:
        st.download_button(label="📥 下載Excel資料", data=to_excel(prefix), file_name=f"{title}_GHG_Data.xlsx", use_container_width=True)
    with col2:
        if st.button("✅ 計算並查看儀表板", use_container_width=True, type="primary"):
            calculate_totals(prefix)
            st.session_state[f'show_dashboard_{prefix}'] = True
            st.rerun()


def show_campus_carbon_negative_page():
    """Renders the page for Campus Carbon Negative projects."""
    st.title("校園負碳")
    get_campus_initial_data()
    years_options = list(range(datetime.now().year + 25, 2019, -1))
    st.selectbox("盤查年度:", years_options, key='campus_inventory_year')
    st.info("請在此頁面輸入或編輯校園的減碳活動數據。")

    total_reduction = 0
    st.subheader("再生能源(自發自用)")
    df_self_use = pd.DataFrame(st.session_state.campus_renewable_self_use)
    df_self_use['減碳量(公噸CO2e/年)'] = df_self_use['每年實際發電度數'] * 0.474 / 1000
    edited_df_self_use = st.data_editor(df_self_use, key="editor_self_use", hide_index=True)
    total_reduction += edited_df_self_use['減碳量(公噸CO2e/年)'].sum()

    st.subheader("再生能源(售電予廠商)")
    df_sold = pd.DataFrame(st.session_state.campus_renewable_sold)
    df_sold['減碳量(公噸CO2e/年)'] = df_sold['每年實際發電度數'] * 0.474 / 1000
    edited_df_sold = st.data_editor(df_sold, key="editor_sold", hide_index=True)
    total_reduction += edited_df_sold['減碳量(公噸CO2e/年)'].sum()
    
    st.subheader("樹木碳匯")
    df_trees = pd.DataFrame(st.session_state.campus_tree_sink)
    df_trees['固碳量(公噸CO2e/年)'] = df_trees['植物固碳當量(kgCO2e)'] / 1000
    edited_df_trees = st.data_editor(df_trees, key="editor_trees", hide_index=True)
    total_reduction += edited_df_trees['固碳量(公噸CO2e/年)'].sum()
    
    st.divider()
    st.header(f"年度校園總減碳量")
    st.metric("總減碳量 (公噸CO2e/年)", f"{total_reduction:.4f}")


# =============================================================================
# Main App Logic
# =============================================================================
if not st.session_state.get("logged_in", False):
    login_page()
else:
    initialize_state()
    main_app()
