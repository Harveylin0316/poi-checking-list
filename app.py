import streamlit as st
import pandas as pd
from check_restaurants import OpenRiceChecker
import time
import os

st.set_page_config(
    page_title="OpenRice 餐廳要素檢查",
    page_icon="🍽️",
    layout="wide"
)

st.title("🍽️ OpenRice 餐廳要素檢查程式")
st.markdown("---")

# 側邊欄說明
with st.sidebar:
    st.header("📋 使用說明")
    st.markdown("""
    ### 檢查項目
    1. ✅ 餐廳名稱（中文與英文）
    2. ✅ 門面照片
    3. ✅ 菜單
    4. ✅ 餐點照片
    5. ✅ 相關影片
    
    ### Excel檔案格式
    - 必須包含 **餐廳名稱** 欄位
    - 必須包含 **URL** 欄位（或 網址、網址）
    
    ### 使用步驟
    1. 上傳Excel檔案
    2. 點擊"開始檢查"
    3. 等待檢查完成
    4. 下載檢查報告
    """)
    
    st.markdown("---")
    st.markdown("**注意**: 檢查過程可能需要一些時間，請耐心等待")

# 檔案上傳
st.header("📁 步驟1: 上傳Excel檔案")
uploaded_file = st.file_uploader(
    "選擇包含餐廳清單的Excel檔案",
    type=['xlsx', 'xls'],
    help="Excel檔案應包含'餐廳名稱'和'URL'欄位"
)

# 檢查設定
if uploaded_file is not None:
    st.success(f"✅ 已上傳檔案: {uploaded_file.name}")
    
    # 預覽Excel檔案
    try:
        df = pd.read_excel(uploaded_file)
        st.subheader("📊 檔案預覽")
        st.dataframe(df.head(), use_container_width=True)
        st.info(f"共 {len(df)} 間餐廳")
        
        # 檢查必要的欄位
        has_name = '餐廳名稱' in df.columns or '餐廳名稱' in df.columns or '名稱' in df.columns
        has_url = 'URL' in df.columns or '網址' in df.columns or '網址' in df.columns
        
        if not has_name or not has_url:
            st.warning("⚠️ 請確保Excel檔案包含'餐廳名稱'和'URL'欄位")
        else:
            st.success("✅ Excel檔案格式正確")
    except Exception as e:
        st.error(f"讀取Excel檔案時出錯: {e}")
        uploaded_file = None

# 初始化session state
if 'checking' not in st.session_state:
    st.session_state.checking = False
if 'should_stop' not in st.session_state:
    st.session_state.should_stop = False
if 'results' not in st.session_state:
    st.session_state.results = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'total_restaurants' not in st.session_state:
    st.session_state.total_restaurants = 0
if 'temp_file' not in st.session_state:
    st.session_state.temp_file = None
if 'df_restaurants' not in st.session_state:
    st.session_state.df_restaurants = None
if 'checker' not in st.session_state:
    st.session_state.checker = None
if 'checker_initialized' not in st.session_state:
    st.session_state.checker_initialized = False

# 開始檢查按鈕
st.markdown("---")
st.header("🚀 步驟2: 開始檢查")

if uploaded_file is not None:
    # 顯示停止按鈕（如果正在檢查）
    if st.session_state.checking:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("🔄 檢查進行中...")
        with col2:
            if st.button("⏹️ 停止檢查", type="secondary", use_container_width=True):
                st.session_state.should_stop = True
                st.session_state.checking = False
                st.rerun()
    
    # 開始檢查按鈕
    if not st.session_state.checking:
        if st.button("開始檢查", type="primary", use_container_width=True):
            # 重置狀態
            st.session_state.checking = True
            st.session_state.should_stop = False
            st.session_state.results = []
            st.session_state.current_index = 0
            
            # 儲存上傳的檔案到臨時位置
            temp_file = "temp_restaurants.xlsx"
            with open(temp_file, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.session_state.temp_file = temp_file
            
            # 讀取並處理Excel
            df = pd.read_excel(temp_file)
            
            # 檢查必要的欄位
            if 'URL' not in df.columns:
                possible_url_cols = ['網址', '網址', 'url', '連結', '連結']
                for col in possible_url_cols:
                    if col in df.columns:
                        df['URL'] = df[col]
                        break
            
            if '餐廳名稱' not in df.columns:
                possible_name_cols = ['餐廳名稱', '餐厅名称', '名稱', '名称', 'name', 'Name']
                for col in possible_name_cols:
                    if col in df.columns:
                        df['餐廳名稱'] = df[col]
                        break
            
            st.session_state.total_restaurants = len(df)
            st.session_state.df_restaurants = df
            
            # 初始化checker（只創建一次，復用）
            if not st.session_state.checker_initialized:
                st.session_state.checker = OpenRiceChecker(temp_file, use_selenium=False)
                st.session_state.checker_initialized = True
            
            st.rerun()
    
    # 如果正在檢查，執行檢查邏輯
    if st.session_state.checking and st.session_state.df_restaurants is not None:
        df = st.session_state.df_restaurants
        current_idx = st.session_state.current_index
        total = st.session_state.total_restaurants
        
        # 進度條
        progress_bar = st.progress(current_idx / total if total > 0 else 0)
        
        # 檢查是否應該停止
        if st.session_state.should_stop:
            st.session_state.checking = False
            st.warning("⚠️ 檢查已中斷")
        elif current_idx < total:
            # 檢查當前餐廳
            row = df.iloc[current_idx]
            restaurant_name = row['餐廳名稱']
            url = row['URL']
            
            status_text = st.empty()
            status_text.text(f"正在檢查: {restaurant_name} ({current_idx + 1}/{total})")
            
            try:
                # 使用已創建的checker（復用，避免重複創建）
                # 如果checker未初始化，先初始化
                if st.session_state.checker is None:
                    st.session_state.checker = OpenRiceChecker(st.session_state.temp_file, use_selenium=False)
                    st.session_state.checker_initialized = True
                
                checker = st.session_state.checker
                
                # 檢查餐廳
                result = checker.check_restaurant(url, restaurant_name)
                
                # 顯示調試信息（如果有錯誤）
                if result.get('狀態') == '錯誤':
                    st.warning(f"⚠️ {restaurant_name}: {result.get('錯誤資訊', '未知錯誤')}")
                elif result.get('狀態') == '不合格':
                    # 顯示詳細的檢查結果
                    failed_items = []
                    for key in ['中文名稱', '英文名稱', '門面照片', '菜單', '餐點照片', '相關影片']:
                        if result.get(key) == '✗':
                            failed_items.append(key)
                    if failed_items:
                        st.caption(f"❌ 缺少: {', '.join(failed_items)}")
                
                st.session_state.results.append(result)
                
                # 更新索引
                st.session_state.current_index += 1
                
                # 減少延遲（從0.5秒減少到0.1秒，或完全移除）
                # 因為我們已經有session復用，不需要太多延遲
                time.sleep(0.1)
                
                # 繼續下一個
                st.rerun()
                
            except Exception as e:
                st.error(f"檢查 {restaurant_name} 時出錯: {e}")
                st.session_state.current_index += 1
                # 即使出錯也繼續下一個
                if st.session_state.current_index < total:
                    st.rerun()
                else:
                    st.session_state.checking = False
        else:
            # 檢查完成
            st.session_state.checking = False
            progress_bar.progress(1.0)
            st.success("✅ 檢查完成！")
            
            # 清理checker
            st.session_state.checker = None
            st.session_state.checker_initialized = False
        
        # 顯示當前進度
        if len(st.session_state.results) > 0:
            st.info(f"已完成 {len(st.session_state.results)}/{total} 間餐廳")
    
    # 顯示結果（如果有結果且不在檢查中）
    if len(st.session_state.results) > 0 and not st.session_state.checking:
        st.markdown("---")
        st.header("📊 檢查結果")
        
        df_results = pd.DataFrame(st.session_state.results)
        
        # 統計
        total = len(df_results)
        passed = len(df_results[df_results['狀態'] == '合格'])
        failed = total - passed
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("已檢查餐廳數", total)
        with col2:
            st.metric("合格餐廳", passed, delta=f"{passed/total*100:.1f}%" if total > 0 else "0%")
        with col3:
            st.metric("不合格餐廳", failed, delta=f"{failed/total*100:.1f}%" if total > 0 else "0%")
        
        if st.session_state.should_stop:
            st.info(f"💡 共 {st.session_state.total_restaurants} 間餐廳，已檢查 {total} 間")
        
        # 顯示結果表格
        st.subheader("詳細結果")
        
        # 如果有錯誤，顯示錯誤詳情
        error_results = df_results[df_results['狀態'] == '錯誤']
        if len(error_results) > 0:
            st.warning(f"⚠️ {len(error_results)} 間餐廳檢查時發生錯誤")
            with st.expander("查看錯誤詳情"):
                error_cols = ['餐廳名稱', 'URL']
                if '錯誤資訊' in error_results.columns:
                    error_cols.append('錯誤資訊')
                st.dataframe(error_results[error_cols], use_container_width=True)
        
        st.dataframe(df_results, use_container_width=True)
        
        # 不合格餐廳清單
        failed_restaurants = df_results[df_results['狀態'] != '合格']
        if len(failed_restaurants) > 0:
            st.subheader("❌ 不合格餐廳清單")
            st.dataframe(failed_restaurants[['餐廳名稱', 'URL', '狀態', '通過率']], use_container_width=True)
        
        # 產生報告檔案
        output_file = 'restaurant_check_report.xlsx'
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df_results.to_excel(writer, sheet_name='完整報告', index=False)
            if len(failed_restaurants) > 0:
                failed_restaurants.to_excel(writer, sheet_name='不合格餐廳', index=False)
        
        # 下載按鈕
        st.markdown("---")
        st.header("📥 步驟3: 下載報告")
        with open(output_file, "rb") as f:
            st.download_button(
                label="下載Excel報告",
                data=f.read(),
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        # 重置按鈕
        if st.button("🔄 重新開始檢查", use_container_width=True):
            st.session_state.checking = False
            st.session_state.should_stop = False
            st.session_state.results = []
            st.session_state.current_index = 0
            st.session_state.df_restaurants = None
            st.session_state.checker = None
            st.session_state.checker_initialized = False
            if st.session_state.temp_file and os.path.exists(st.session_state.temp_file):
                os.remove(st.session_state.temp_file)
            st.session_state.temp_file = None
            st.rerun()
        
        # 清理臨時檔案（在顯示結果後）
        if st.session_state.temp_file and os.path.exists(st.session_state.temp_file):
            # 延遲清理，讓用戶有時間下載報告
            pass
else:
    st.info("👆 請先上傳Excel檔案")

# 頁尾
st.markdown("---")
st.markdown("💡 **提示**: 如果遇到問題，請檢查Excel檔案格式和網路連線")
