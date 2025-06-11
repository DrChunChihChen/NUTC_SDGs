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
    # This is a simplified version of your function for brevity.
    # The full data initialization is assumed to be the same as in your original code.
    if f"show_dashboard_{prefix}" not in st.session_state:
        st.session_state[f"show_dashboard_{prefix}"] = False
    if f"inventory_year_{prefix}" not in st.session_state:
        years = range(datetime.now().year + 25, 2019, -1)
        st.session_state[f"inventory_year_{prefix}"] = datetime.now().year
    # ... (all other data initializations s1_data, s2_data, etc., remain the same)
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

def initialize_state():
    """Initializes session state for all pages."""
    if 'page' not in st.session_state:
        st.session_state.page = "AR5"
    get_ar_initial_data('ar5')
    get_ar_initial_data('ar6')
    # get_campus_initial_data() # This can be called when navigating to the campus page


# =============================================================================
# Excel Export & Import Functions
# =============================================================================
def to_excel(prefix):
    """Serializes all input data from session state into a multi-sheet Excel file."""
    # This function remains the same as your original code
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
        df2_data = [{'燃料類別': v.get('name', k), **v} for k, v in st.session_state[f's2_data_{prefix}'].items()]
        df2 = pd.DataFrame(df2_data)
        df2['排放量(tCO2e)'] = df2['usage'] * df2['factor']
        df2.rename(columns={'usage': '使用量', 'unit': '單位', 'factor': '排放係數'}, inplace=True)
        df2 = df2[['燃料類別', '使用量', '單位', '排放係數', '排放量(tCO2e)']]
        df2.to_excel(writer, sheet_name='移動源', index=False)
        
        # ... (rest of the sheets) ...
    return output.getvalue()


def handle_excel_upload(uploaded_file, prefix):
    """Parses an uploaded Excel file and updates the session state."""
    # This function remains the same as the previous version
    try:
        xls = pd.ExcelFile(uploaded_file)
        
        def get_sheet(sheet_name):
            return pd.read_excel(xls, sheet_name=sheet_name) if sheet_name in xls.sheet_names else None

        if (df := get_sheet('固定源')) is not None:
            for _, row in df.iterrows():
                if row['燃料類別'] in st.session_state[f's1_data_{prefix}']:
                    st.session_state[f's1_data_{prefix}'][row['燃料類別']]['usage'] = row['使用量']
        
        # ... (rest of the upload handling logic) ...
        return True
    except Exception as e:
        st.error(f"檔案解析失敗: {e}")
        return False


# =============================================================================
# Calculation Functions
# =============================================================================
def calculate_totals(prefix):
    """Calculate all emission totals for a given AR version and store them in session_state."""
    # This function remains the same as your original code
    totals = {}
    gwp_ch4 = 28
    totals['s1'] = sum(v['usage'] * v['factor'] for v in st.session_state[f's1_data_{prefix}'].values())
    totals['s2'] = sum(v['usage'] * v['factor'] for v in st.session_state[f's2_data_{prefix}'].values())
    is_septic = st.session_state[f's3_septic_system_{prefix}'] == '否 (使用化糞池)'
    totals['s3'] = sum(v['usage'] * v['factor'] * gwp_ch4 for v in st.session_state[f's3_data_{prefix}'].values()) if is_septic else 0
    s4_total = 0
    for v in st.session_state[f's4_data_{prefix}'].values():
        if v.get('gwp') is not None: s4_total += (v['usage'] * v['gwp']) / 1000
        elif v.get('factor') is not None: s4_total += v['usage'] * v['factor']
    totals['s4'] = s4_total
    totals['s5'] = sum((v['usage'] * v['gwp']) / 1000 for v in st.session_state[f's5_data_{prefix}'].values())
    totals['s6'] = sum((v['distance'] * v['factor']) / 1000 for v in st.session_state[f's6_data_{prefix}'].values())
    total_electricity = sum(st.session_state[f's7_electricity_{prefix}'].values())
    totals['s7_electricity'] = (total_electricity * 0.474) / 1000
    total_water = sum(st.session_state[f's7_water_{prefix}'].values())
    water_factor = st.session_state[f'water_factors_{prefix}'][st.session_state[f's7_water_source_{prefix}']]
    totals['s7_water'] = (total_water * water_factor) / 1000
    st.session_state[f'totals_{prefix}'] = totals
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
        # Navigation buttons remain the same
        if st.button("AR5-溫室氣體盤查資料", use_container_width=True, type="primary" if st.session_state.page == "AR5" else "secondary"):
            st.session_state.page = "AR5"; st.rerun()
        if st.button("AR6-溫室氣體盤查資料", use_container_width=True, type="primary" if st.session_state.page == "AR6" else "secondary"):
            st.session_state.page = "AR6"; st.rerun()
        if st.button("校園負碳", use_container_width=True, type="primary" if st.session_state.page == "Campus" else "secondary"):
            st.session_state.page = "Campus"; st.rerun()
        st.divider()
        # Excel upload section remains the same
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
    prefix, title = ('ar5', "AR5") if page == "AR5" else (('ar6', "AR6") if page == "AR6" else ('campus', "Campus"))
    if page in ["AR5", "AR6"]:
        if st.session_state.get(f"show_dashboard_{prefix}", False):
            create_dashboard(prefix, title)
        else:
            create_input_form(prefix, title)
    elif page == "Campus":
        show_campus_carbon_negative_page()


def create_dashboard(prefix, title):
    """Renders the main dashboard view for a given AR version."""
    st.title(f"{title} - {st.session_state[f'inventory_year_{prefix}']} 年度溫室氣體盤查儀表板")
    if st.button("⬅️ 返回編輯資料"):
        st.session_state[f'show_dashboard_{prefix}'] = False
        st.rerun()

    scope = st.session_state[f'scope_totals_{prefix}']
    emissions = st.session_state[f'emission_breakdown_{prefix}']

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("總碳排放量 (tCO2e)", f"{scope['Grand Total']:.2f}")
    col2.metric("範疇一 Scope 1", f"{scope['Scope 1']:.2f}")
    col3.metric("範疇二 Scope 2", f"{scope['Scope 2']:.2f}")
    col4.metric("範疇三 Scope 3", f"{scope['Scope 3']:.2f}")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("各類別排放佔比")
        filtered_emissions = {k: v for k, v in emissions.items() if v > 0}
        if filtered_emissions:
            fig = go.Figure(data=[go.Pie(labels=list(filtered_emissions.keys()), values=list(filtered_emissions.values()), hole=.4, textinfo='label+percent')])
            fig.update_layout(showlegend=False, height=400, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("無排放數據可顯示。")

    with col2:
        st.subheader("各範疇排放比較 (tCO2e)")
        scope_df = pd.DataFrame({'範疇': ['Scope 1', 'Scope 2', 'Scope 3'], '排放量': [scope['Scope 1'], scope['Scope 2'], scope['Scope 3']]})
        fig = go.Figure(go.Bar(x=scope_df['排放量'], y=scope_df['範疇'], orientation='h', text=scope_df['排放量'].apply(lambda x: f'{x:.2f}'), textposition='auto', marker_color=['#10B981', '#F59E0B', '#8B5CF6']))
        fig.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    st.subheader("各類別排放細項 (tCO2e)")

    def create_breakdown_chart(data, y_col, x_col, title):
        if data.empty or data[x_col].sum() == 0:
            st.write(f"{title}: 無排放數據")
            return
        fig = go.Figure(go.Bar(x=data[x_col], y=data[y_col], orientation='h', text=data[x_col].apply(lambda x: f'{x:.4f}')))
        fig.update_layout(title_text=title, height=350, margin=dict(l=10, r=10, t=30, b=10), yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        s1_df = pd.DataFrame.from_dict(st.session_state[f's1_data_{prefix}'], orient='index')
        s1_df['emission'] = s1_df['usage'] * s1_df['factor']
        create_breakdown_chart(s1_df[s1_df.emission > 0].reset_index().rename(columns={'index':'類別'}), '類別', 'emission', '固定源排放')
        
        s4_items = []
        for item, values in st.session_state[f's4_data_{prefix}'].items():
            emission = (values['usage'] * values['gwp']) / 1000 if values.get('gwp') else values['usage'] * values.get('factor', 0)
            if emission > 0: s4_items.append({'類別': item, 'emission': emission})
        create_breakdown_chart(pd.DataFrame(s4_items), '類別', 'emission', '滅火器排放')

    with col2:
        s2_items = []
        for key, values in st.session_state[f's2_data_{prefix}'].items():
            emission = values['usage'] * values['factor']
            if emission > 0: s2_items.append({'燃料類別': values.get('name', key), 'emission': emission})
        create_breakdown_chart(pd.DataFrame(s2_items), '燃料類別', 'emission', '移動源排放')

        s6_df = pd.DataFrame.from_dict(st.session_state[f's6_data_{prefix}'], orient='index')
        s6_df['emission'] = (s6_df['distance'] * s6_df['factor']) / 1000
        create_breakdown_chart(s6_df[s6_df.emission > 0].reset_index().rename(columns={'index':'交通工具'}), '交通工具', 'emission', '員工通勤排放')

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        s7_elec_df = pd.DataFrame(st.session_state[f's7_electricity_{prefix}'].items(), columns=['月份', '用電量(度)'])
        s7_elec_df['emission'] = (s7_elec_df['用電量(度)'] * 0.474) / 1000
        if not s7_elec_df[s7_elec_df.emission > 0].empty:
            elec_fig = go.Figure(go.Bar(x=s7_elec_df['月份'], y=s7_elec_df['emission'], text=s7_elec_df['emission'].apply(lambda x: f'{x:.4f}')))
            elec_fig.update_layout(title_text='每月外購電力排放 (tCO2e)', height=400)
            st.plotly_chart(elec_fig, use_container_width=True)

    with col2:
        water_factor = st.session_state[f'water_factors_{prefix}'][st.session_state[f's7_water_source_{prefix}']]
        s7_water_df = pd.DataFrame(st.session_state[f's7_water_{prefix}'].items(), columns=['月份', '用水量(度)'])
        s7_water_df['emission'] = (s7_water_df['用水量(度)'] * water_factor) / 1000
        if not s7_water_df[s7_water_df.emission > 0].empty:
            water_fig = go.Figure(go.Bar(x=s7_water_df['月份'], y=s7_water_df['emission'], text=s7_water_df['emission'].apply(lambda x: f'{x:.4f}')))
            water_fig.update_layout(title_text='每月外購水力排放 (tCO2e)', height=400)
            st.plotly_chart(water_fig, use_container_width=True)


def create_input_form(prefix, title):
    """Renders the multi-tab data input form."""
    st.title(f"{title}-溫室氣體盤查資料輸入")
    # This function remains largely the same, showing input fields.
    # For brevity, only showing a small part of it.
    years_opts = list(range(datetime.now().year + 25, 2019, -1))
    st.selectbox("盤查年度:", years_opts, key=f'inventory_year_{prefix}')
    st.info("請填寫以下各類別的活動數據，系統將自動計算排放量。")
    st.divider()
    # ... (Tabs for data input) ...
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
    # ... (Implementation of this page remains the same) ...


# =============================================================================
# Main App Logic
# =============================================================================
if not st.session_state.get("logged_in", False):
    login_page()
else:
    initialize_state()
    main_app()
