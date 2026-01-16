import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 페이지 설정
st.set_page_config(page_title="농수산물 양허세율 조회", layout="wide")

st.title("🌾 국영무역품목 양허세율 대시보드")

# 1. 파일 경로 설정 (정확한 파일명 사용)
data = "한국농수산식품유통공사_국영무역품목 양허세율_20200925.csv"

@st.cache_data
def load_data(file_path):
    # 파일 존재 여부 확인
    if not os.path.exists(file_path):
        st.error(f"파일을 찾을 수 없습니다: {file_path}")
        return pd.DataFrame()
    
    try:
        # 한국어 파일 특성상 cp949 또는 utf-8-sig 인코딩 시도
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='cp949')
    
    # 데이터 클렌징: 숫자 컬럼에 혹시 있을지 모를 콤마(,) 제거 및 수치화
    cols_to_fix = ['저율관세(추천, %)', '고율종가(미추천)', '종량(미추천, 원/kg)']
    for col in cols_to_fix:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    
    return df

# 데이터 로드
df = load_data(data)

if not df.empty:
    # --- 사이드바 ---
    st.sidebar.header("🔍 필터 설정")
    selected_items = st.sidebar.multiselect("품목 선택", df['품명'].unique(), default=df['품명'].unique())
    
    # 데이터 필터링
    filtered_df = df[df['품명'].isin(selected_items)]

    # --- 메인 화면 ---
    # 1. 시각화 (품목별 관세율 비교)
    st.subheader("📊 품목별 관세율 현황")
    
    # 막대 그래프 생성
    fig = px.bar(
        filtered_df, 
        x='품명', 
        y=['저율관세(추천, %)', '고율종가(미추천)'],
        barmode='group',
        labels={'value': '세율 (%)', 'variable': '구분'},
        title="추천(저율) vs 미추천(고율) 세율 비교"
    )
    st.plotly_chart(fig, use_container_width=True)

    # 2. 상세 데이터 테이블
    st.subheader("📋 상세 데이터 확인")
    st.table(filtered_df)

    # 3. 추가 분석 (종량세)
    st.divider()
    st.subheader("💰 미추천 시 종량세 (원/kg)")
    weight_df = filtered_df[filtered_df['종량(미추천, 원/kg)'] > 0]
    if not weight_df.empty:
        fig2 = px.line(weight_df, x='품명', y='종량(미추천, 원/kg)', markers=True)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.write("해당하는 종량세 데이터가 없습니다.")

else:
    st.info("현재 경로에 CSV 파일이 있는지 확인해 주세요.")
    st.code(f"파일명 확인: {data}")