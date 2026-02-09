import streamlit as st
import pandas as pd
from check_restaurants import OpenRiceChecker
import time
import os

st.set_page_config(
    page_title="OpenRice 餐厅要素检查",
    page_icon="🍽️",
    layout="wide"
)

st.title("🍽️ OpenRice 餐厅要素检查程序")
st.markdown("---")

# 侧边栏说明
with st.sidebar:
    st.header("📋 使用说明")
    st.markdown("""
    ### 检查项目
    1. ✅ 餐厅名称（中文与英文）
    2. ✅ 门面照片
    3. ✅ 菜单
    4. ✅ 餐点照片
    5. ✅ 相关影片
    
    ### Excel文件格式
    - 必须包含 **餐厅名称** 列
    - 必须包含 **URL** 列（或 網址、网址）
    
    ### 使用步骤
    1. 上传Excel文件
    2. 点击"开始检查"
    3. 等待检查完成
    4. 下载检查报告
    """)
    
    st.markdown("---")
    st.markdown("**注意**: 检查过程可能需要一些时间，请耐心等待")

# 文件上传
st.header("📁 步骤1: 上传Excel文件")
uploaded_file = st.file_uploader(
    "选择包含餐厅清单的Excel文件",
    type=['xlsx', 'xls'],
    help="Excel文件应包含'餐厅名称'和'URL'列"
)

# 检查设置
if uploaded_file is not None:
    st.success(f"✅ 已上传文件: {uploaded_file.name}")
    
    # 预览Excel文件
    try:
        df = pd.read_excel(uploaded_file)
        st.subheader("📊 文件预览")
        st.dataframe(df.head(), use_container_width=True)
        st.info(f"共 {len(df)} 间餐厅")
        
        # 检查必要的列
        has_name = '餐厅名称' in df.columns or '餐廳名稱' in df.columns or '名称' in df.columns
        has_url = 'URL' in df.columns or '網址' in df.columns or '网址' in df.columns
        
        if not has_name or not has_url:
            st.warning("⚠️ 请确保Excel文件包含'餐厅名称'和'URL'列")
        else:
            st.success("✅ Excel文件格式正确")
    except Exception as e:
        st.error(f"读取Excel文件时出错: {e}")
        uploaded_file = None

# 开始检查按钮
st.markdown("---")
st.header("🚀 步骤2: 开始检查")

if uploaded_file is not None:
    if st.button("开始检查", type="primary", use_container_width=True):
        # 保存上传的文件到临时位置
        temp_file = "temp_restaurants.xlsx"
        with open(temp_file, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # 创建检查器
        checker = OpenRiceChecker(temp_file, use_selenium=False)
        
        # 进度条
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.container()
        
        # 运行检查
        total_restaurants = len(pd.read_excel(temp_file))
        results_list = []
        
        try:
            df = pd.read_excel(temp_file)
            
            # 检查必要的列
            if 'URL' not in df.columns:
                possible_url_cols = ['網址', '网址', 'url', '链接', '連結']
                for col in possible_url_cols:
                    if col in df.columns:
                        df['URL'] = df[col]
                        break
            
            if '餐厅名称' not in df.columns:
                possible_name_cols = ['餐廳名稱', '餐厅名称', '名稱', '名称', 'name', 'Name']
                for col in possible_name_cols:
                    if col in df.columns:
                        df['餐厅名称'] = df[col]
                        break
            
            for idx, row in df.iterrows():
                restaurant_name = row['餐厅名称']
                url = row['URL']
                
                # 更新进度
                progress = (idx + 1) / total_restaurants
                progress_bar.progress(progress)
                status_text.text(f"正在检查: {restaurant_name} ({idx + 1}/{total_restaurants})")
                
                # 检查餐厅
                result = checker.check_restaurant(url, restaurant_name)
                results_list.append(result)
                
                # 延迟
                time.sleep(1)
            
            # 完成
            progress_bar.progress(1.0)
            status_text.text("✅ 检查完成！")
            
            # 显示结果
            st.markdown("---")
            st.header("📊 检查结果")
            
            df_results = pd.DataFrame(results_list)
            
            # 统计
            total = len(df_results)
            passed = len(df_results[df_results['状态'] == '合格'])
            failed = total - passed
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总餐厅数", total)
            with col2:
                st.metric("合格餐厅", passed, delta=f"{passed/total*100:.1f}%")
            with col3:
                st.metric("不合格餐厅", failed, delta=f"{failed/total*100:.1f}%")
            
            # 显示结果表格
            st.subheader("详细结果")
            st.dataframe(df_results, use_container_width=True)
            
            # 不合格餐厅清单
            failed_restaurants = df_results[df_results['状态'] != '合格']
            if len(failed_restaurants) > 0:
                st.subheader("❌ 不合格餐厅清单")
                st.dataframe(failed_restaurants[['餐厅名称', 'URL', '状态', '通过率']], use_container_width=True)
            
            # 生成报告文件
            output_file = 'restaurant_check_report.xlsx'
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                df_results.to_excel(writer, sheet_name='完整报告', index=False)
                if len(failed_restaurants) > 0:
                    failed_restaurants.to_excel(writer, sheet_name='不合格餐厅', index=False)
            
            # 下载按钮
            st.markdown("---")
            st.header("📥 步骤3: 下载报告")
            with open(output_file, "rb") as f:
                st.download_button(
                    label="下载Excel报告",
                    data=f.read(),
                    file_name=output_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            # 清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
        except Exception as e:
            st.error(f"检查过程中出错: {e}")
            import traceback
            st.code(traceback.format_exc())
else:
    st.info("👆 请先上传Excel文件")

# 页脚
st.markdown("---")
st.markdown("💡 **提示**: 如果遇到问题，请检查Excel文件格式和网络连接")
