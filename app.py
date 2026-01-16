import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. 페이지 설정
st.set_page_config(page_title="농수산물 양허세율 조회", layout="wide")

st.title("🌾 국영무역품목 양허세율 대시보드")
st.markdown("---")

# 2. 파일 경로 설정 (정확한 파일명)
# 파일명에 공백이 있으므로 주의해서 입력해야 합니다.
data = "한국농수산식품유통공사_국영무역품목 양허세율_20200925.csv"

@st.cache_data
def load_data(file_path):
    # 파일 존재 여부 확인
    if not os.path.exists(file_path):
        return None
    
    try:
        # 공공데이터 CSV는 주로 'cp949' 인코딩을 사용합니다.
        df = pd.read_csv(file_path, encoding='cp949')
    except:
        # 실패할 경우 utf-8 시도
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        
    # 데이터 전처리: 컬럼명 양끝 공백 제거
    df.columns = df.columns.str.strip()
    
    # 수치 데이터 정제 (콤마 제거 및 형변환)
    numeric_cols = ['저율관세(추천, %)', '고율종가(미추천)', '종량(미추천, 원/kg)']
    for col in numeric_cols:
        if col in df.columns:
            # 콤마 제거 후 숫자로 변환, 오류값은 0으로 채움
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
            
    return df

# 데이터 로드
df = load_data(data)

# 3. 데이터가 정상적으로 불러와졌을 때만 화면 구성
if df is not None:
    # 사이드바 품목 필터
    st.sidebar.header("🔍 필터 설정")
    items = df['품명'].unique()
    selected_items = st.sidebar.multiselect("조회할 품목을 선택하세요", items, default=items)
    
    filtered_df = df[df['품명'].isin(selected_items)]

    # 상단 요약 지표 (KPI)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("총 분석 품목", f"{len(filtered_df)}개")
    with col2:
        if not filtered_df.empty:
            max_rate = filtered_df['고율종가(미추천)'].max()
            st.metric("최고 고율 관세", f"{max_rate}%")
    with col3:
        st.write("💡 **팁**: 저율관세는 추천 시 적용되며, 미추천 시 훨씬 높은 세율이 적용됩니다.")

    # 메인 시각화: 저율 vs 고율 비교
    st.subheader("📊 품목별 관세율 비교 (추천 vs 미추천)")
    
    fig = px.bar(
        filtered_df, 
        x='품명', 
        y=['저율관세(추천, %)', '고율종가(미추천)'],
        barmode='group',
        labels={'value': '세율 (%)', 'variable': '구분'},
        color_discrete_map={'저율관세(추천, %)': '#3498db', '고율종가(미추천)': '#e74c3c'},
        text_auto='.1f'
    )
    st.plotly_chart(fig, use_container_width=True)

    # 하단 상세 데이터
    st.subheader("📋 전체 품목 상세 데이터")
    st.dataframe(filtered_df, use_container_width=True)

else:
    # 파일 로드 실패 시 디버깅 정보 제공
    st.error(f"⚠️ '{data}' 파일을 찾을 수 없습니다.")
    st.info("GitHub 저장소의 파일 이름과 코드 내의 파일 이름이 일치하는지 확인해 주세요.")
    
    # 현재 서버 경로의 파일 목록을 보여주어 수정을 돕습니다.
    st.write("현재 서버 내 파일 목록:", os.listdir('.'))