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

# 開始檢查按鈕
st.markdown("---")
st.header("🚀 步驟2: 開始檢查")

if uploaded_file is not None:
    if st.button("開始檢查", type="primary", use_container_width=True):
        # 儲存上傳的檔案到臨時位置
        temp_file = "temp_restaurants.xlsx"
        with open(temp_file, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # 創建檢查器
        checker = OpenRiceChecker(temp_file, use_selenium=False)
        
        # 進度條
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.container()
        
        # 執行檢查
        total_restaurants = len(pd.read_excel(temp_file))
        results_list = []
        
        try:
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
            
            for idx, row in df.iterrows():
                restaurant_name = row['餐廳名稱']
                url = row['URL']
                
                # 更新進度
                progress = (idx + 1) / total_restaurants
                progress_bar.progress(progress)
                status_text.text(f"正在檢查: {restaurant_name} ({idx + 1}/{total_restaurants})")
                
                # 檢查餐廳
                result = checker.check_restaurant(url, restaurant_name)
                results_list.append(result)
                
                # 延遲
                time.sleep(1)
            
            # 完成
            progress_bar.progress(1.0)
            status_text.text("✅ 檢查完成！")
            
            # 顯示結果
            st.markdown("---")
            st.header("📊 檢查結果")
            
            df_results = pd.DataFrame(results_list)
            
            # 統計
            total = len(df_results)
            passed = len(df_results[df_results['狀態'] == '合格'])
            failed = total - passed
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("總餐廳數", total)
            with col2:
                st.metric("合格餐廳", passed, delta=f"{passed/total*100:.1f}%")
            with col3:
                st.metric("不合格餐廳", failed, delta=f"{failed/total*100:.1f}%")
            
            # 顯示結果表格
            st.subheader("詳細結果")
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
            
            # 清理臨時檔案
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
        except Exception as e:
            st.error(f"檢查過程中出錯: {e}")
            import traceback
            st.code(traceback.format_exc())
else:
    st.info("👆 請先上傳Excel檔案")

# 頁尾
st.markdown("---")
st.markdown("💡 **提示**: 如果遇到問題，請檢查Excel檔案格式和網路連線")
