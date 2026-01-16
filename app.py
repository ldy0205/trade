import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. 페이지 설정
st.set_page_config(page_title="농수산물 양허세율 대시보드", layout="wide")

st.title("🌾 국영무역품목 양허세율 분석 서비스")
st.markdown("---")

# 2. 파일 경로 설정 (정확한 파일명 사용)
data_path = "한국농수산식품유통공사_국영무역품목 양허세율_20200925.csv"

@st.cache_data
def load_and_clean_data(file_path):
    # 파일 존재 확인
    if not os.path.exists(file_path):
        return None
    
    try:
        # 공공데이터 한글 인코딩(cp949) 우선 시도
        df = pd.read_csv(file_path, encoding='cp949')
    except:
        # 실패 시 utf-8 시도
        df = pd.read_csv(file_path, encoding='utf-8-sig')

    # 컬럼명 정리 (공백 제거)
    df.columns = df.columns.str.strip()
    
    # 숫자 데이터 정제: 콤마(,) 제거 및 수치형 변환
    numeric_cols = ['저율관세(추천, %)', '고율종가(미추천)', '종량(미추천, 원/kg)']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
            
    return df

# 데이터 로드
df = load_and_clean_data(data_path)

# 3. 데이터가 있을 때만 화면 렌더링
if df is not None:
    # --- 사이드바 필터 ---
    st.sidebar.header("🔍 검색 및 필터")
    items = df['품명'].unique()
    selected = st.sidebar.multiselect("분석할 품목을 선택하세요", items, default=items)
    
    filtered_df = df[df['품명'].isin(selected)]

    # --- 메인 지표 ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("총 분석 품목", f"{len(filtered_df)}개")
    with col2:
        if not filtered_df.empty:
            max_duty = filtered_df.loc[filtered_df['고율종가(미추천)'].idxmax()]
            st.metric("최고 고율 품목", max_duty['품명'], f"{max_duty['고율종가(미추천)']}%")
    with col3:
        avg_low = filtered_df['저율관세(추천, %)'].mean()
        st.metric("평균 저율관세", f"{avg_low:.1f}%")

    # --- 시각화 ---
    st.subheader("📊 추천(저율) vs 미추천(고율) 관세율 비교")
    
    # 바 차트 생성
    fig = px.bar(
        filtered_df, 
        x='품명', 
        y=['저율관세(추천, %)', '고율종가(미추천)'],
        barmode='group',
        labels={'value': '세율 (%)', 'variable': '세율 구분'},
        color_discrete_map={'저율관세(추천, %)': '#3498db', '고율종가(미추천)': '#e74c3c'},
        text_auto=True
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- 상세 데이터 ---
    st.subheader("📋 상세 데이터 정보")
    st.dataframe(filtered_df, use_container_width=True)

else:
    # 파일 로드 실패 시 디버깅 안내
    st.error(f"⚠️ '{data_path}' 파일을 읽어올 수 없습니다.")
    st.info("GitHub에 CSV 파일이 업로드되어 있는지, 파일명이 코드와 정확히 일치하는지 확인해 주세요.")
    
    # 현재 서버의 파일 목록 출력 (디버깅용)
    st.write("현재 경로의 파일 목록:", os.listdir('.'))