import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta
from datetime import datetime, timedelta
import json
import os
import time

# 페이지 설정
st.set_page_config(
    page_title="🚀 주식 스크리너 (Cloud)",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 캐시된 종목 리스트 로딩
@st.cache_data(ttl=3600)  # 1시간 캐시
def load_stock_lists():
    """종목 리스트를 로드하거나 생성합니다."""
    # 클라우드 환경에서는 파일이 없을 수 있으므로 기본 종목 사용
    default_stocks = {
        "S&P 500": {
            "AAPL": "Apple Inc.",
            "MSFT": "Microsoft Corp.",
            "GOOGL": "Alphabet Inc.",
            "AMZN": "Amazon.com Inc.",
            "TSLA": "Tesla Inc.",
            "META": "Meta Platforms Inc.",
            "NVDA": "NVIDIA Corp.",
            "JPM": "JPMorgan Chase & Co.",
            "JNJ": "Johnson & Johnson",
            "UNH": "UnitedHealth Group Inc.",
            "V": "Visa Inc.",
            "PG": "Procter & Gamble Co.",
            "HD": "Home Depot Inc.",
            "MA": "Mastercard Inc.",
            "BAC": "Bank of America Corp.",
            "DIS": "Walt Disney Co.",
            "ADBE": "Adobe Inc.",
            "CRM": "Salesforce Inc.",
            "NFLX": "Netflix Inc.",
            "XOM": "Exxon Mobil Corp."
        },
        "NASDAQ": {
            "AAPL": "Apple Inc.",
            "MSFT": "Microsoft Corp.",
            "GOOGL": "Alphabet Inc.",
            "AMZN": "Amazon.com Inc.",
            "TSLA": "Tesla Inc.",
            "META": "Meta Platforms Inc.",
            "NVDA": "NVIDIA Corp.",
            "PYPL": "PayPal Holdings Inc.",
            "CMCSA": "Comcast Corp.",
            "INTC": "Intel Corp.",
            "CSCO": "Cisco Systems Inc.",
            "PEP": "PepsiCo Inc.",
            "ADBE": "Adobe Inc.",
            "NFLX": "Netflix Inc.",
            "TXN": "Texas Instruments Inc."
        },
        "KOSPI": {
            "005930.KS": "삼성전자",
            "000660.KS": "SK하이닉스",
            "035420.KS": "NAVER",
            "005490.KS": "POSCO홀딩스",
            "000270.KS": "기아",
            "005380.KS": "현대차",
            "051910.KS": "LG화학",
            "035720.KS": "카카오",
            "006400.KS": "삼성SDI",
            "028260.KS": "삼성물산",
            "068270.KS": "셀트리온",
            "207940.KS": "삼성바이오로직스",
            "066570.KS": "LG전자",
            "323410.KS": "카카오뱅크",
            "003670.KS": "포스코퓨처엠"
        },
        "KOSDAQ": {
            "263750.KQ": "펄어비스",
            "293490.KQ": "카카오게임즈",
            "196170.KQ": "알테오젠",
            "041510.KQ": "에스엠",
            "145020.KQ": "휴젤",
            "112040.KQ": "위메이드",
            "357780.KQ": "솔브레인",
            "086900.KQ": "메디톡스",
            "039030.KQ": "이오테크닉스",
            "058470.KQ": "리노공업",
            "067310.KQ": "하나마이크론",
            "078600.KQ": "대주전자재료",
            "108860.KQ": "셀바스AI",
            "095340.KQ": "ISC",
            "317870.KQ": "엔바이오니아"
        }
    }
    
    return default_stocks

# 기술적 지표 계산
@st.cache_data(ttl=300)  # 5분 캐시
def calculate_technical_indicators(df):
    """기술적 지표를 계산합니다."""
    if len(df) < 50:  # 충분한 데이터가 없으면 계산하지 않음
        return df
    
    # 볼린저 밴드
    bb_period = 20
    bb_std = 2
    df['BB_Middle'] = df['Close'].rolling(window=bb_period).mean()
    rolling_std = df['Close'].rolling(window=bb_period).std()
    df['BB_Upper'] = df['BB_Middle'] + (rolling_std * bb_std)
    df['BB_Lower'] = df['BB_Middle'] - (rolling_std * bb_std)
    
    # RSI
    try:
        df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    except:
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    try:
        macd_ind = ta.trend.MACD(df['Close'])
        df['MACD'] = macd_ind.macd()
        df['MACD_Signal'] = macd_ind.macd_signal()
        df['MACD_Histogram'] = macd_ind.macd_diff()
    except:
        exp1 = df['Close'].ewm(span=12).mean()
        exp2 = df['Close'].ewm(span=26).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
    
    # 이동평균
    df['MA_20'] = df['Close'].rolling(window=20).mean()
    df['MA_50'] = df['Close'].rolling(window=50).mean()
    
    # 거래량 평균
    df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
    
    return df

# 주식 데이터 가져오기
@st.cache_data(ttl=300)  # 5분 캐시
def get_stock_data(symbol, period="3mo"):
    """주식 데이터를 가져옵니다."""
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        
        if df.empty:
            return None
            
        df = calculate_technical_indicators(df)
        return df
    except Exception as e:
        st.error(f"데이터 가져오기 실패 ({symbol}): {str(e)}")
        return None

# 조건 확인 함수들
def check_bb_breakout(df):
    """볼린저 밴드 상단 돌파 확인"""
    if len(df) < 2:
        return False
    latest = df.iloc[-1]
    previous = df.iloc[-2]
    return (latest['Close'] > latest['BB_Upper'] and 
            previous['Close'] <= previous['BB_Upper'])

def check_rsi_condition(df, condition, value):
    """RSI 조건 확인"""
    if len(df) < 1 or pd.isna(df.iloc[-1]['RSI']):
        return False
    latest_rsi = df.iloc[-1]['RSI']
    
    if condition == "초과":
        return latest_rsi > value
    elif condition == "미만":
        return latest_rsi < value
    elif condition == "상향돌파":
        if len(df) < 2:
            return False
        prev_rsi = df.iloc[-2]['RSI']
        return latest_rsi > value and prev_rsi <= value
    elif condition == "하향돌파":
        if len(df) < 2:
            return False
        prev_rsi = df.iloc[-2]['RSI']
        return latest_rsi < value and prev_rsi >= value
    return False

def check_volume_surge(df, multiplier=1.5):
    """거래량 급증 확인"""
    if len(df) < 1:
        return False
    latest = df.iloc[-1]
    return latest['Volume'] > latest['Volume_MA'] * multiplier

# 스크리닝 함수
def screen_stocks(stocks, conditions):
    """주식 스크리닝을 실행합니다."""
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_stocks = len(stocks)
    
    for i, (symbol, name) in enumerate(stocks.items()):
        progress = (i + 1) / total_stocks
        progress_bar.progress(progress)
        status_text.text(f"분석 중: {name} ({symbol}) - {i+1}/{total_stocks}")
        
        df = get_stock_data(symbol)
        if df is None or len(df) < 20:
            continue
        
        # 조건 확인
        conditions_met = []
        
        # BB 상단 돌파 조건
        if "bb_breakout" in conditions:
            if check_bb_breakout(df):
                conditions_met.append("BB상단돌파")
        
        # RSI 조건
        if "rsi_condition" in conditions:
            rsi_condition = conditions["rsi_condition"]
            if check_rsi_condition(df, rsi_condition["type"], rsi_condition["value"]):
                conditions_met.append(f"RSI{rsi_condition['type']}{rsi_condition['value']}")
        
        # 거래량 조건
        if "volume_surge" in conditions:
            if check_volume_surge(df, conditions["volume_surge"]):
                conditions_met.append("거래량급증")
        
        # 결과가 있으면 추가
        if conditions_met:
            latest = df.iloc[-1]
            results.append({
                "Symbol": symbol,
                "Name": name,
                "Price": latest['Close'],
                "Change%": ((latest['Close'] - df.iloc[-2]['Close']) / df.iloc[-2]['Close'] * 100) if len(df) > 1 else 0,
                "RSI": latest['RSI'] if not pd.isna(latest['RSI']) else 0,
                "Volume_Ratio": latest['Volume'] / latest['Volume_MA'] if latest['Volume_MA'] > 0 else 0,
                "Conditions": ", ".join(conditions_met)
            })
    
    progress_bar.empty()
    status_text.empty()
    return results

# 차트 생성
def create_stock_chart(symbol, df):
    """주식 차트를 생성합니다."""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=('Price & Bollinger Bands', 'RSI', 'Volume'),
        row_width=[0.2, 0.2, 0.7]
    )
    
    # 캔들스틱 차트
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Price"
        ),
        row=1, col=1
    )
    
    # 볼린저 밴드
    if 'BB_Upper' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], name='BB Upper', line=dict(color='red', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], name='BB Lower', line=dict(color='red', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Middle'], name='BB Middle', line=dict(color='blue', width=1)), row=1, col=1)
    
    # RSI
    if 'RSI' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    
    # 거래량
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='lightblue'), row=3, col=1)
    if 'Volume_MA' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['Volume_MA'], name='Volume MA', line=dict(color='orange')), row=3, col=1)
    
    fig.update_layout(
        title=f'{symbol} - Stock Analysis',
        xaxis_title='Date',
        height=800,
        showlegend=True
    )
    
    return fig

# 메인 앱
def main():
    st.title("🚀 주식 기술적 분석 스크리너 (Cloud Edition)")
    st.markdown("---")
    
    # 사이드바
    st.sidebar.title("📊 설정")
    
    # 주식 리스트 로드
    try:
        stock_lists = load_stock_lists()
    except Exception as e:
        st.error(f"종목 리스트 로딩 실패: {str(e)}")
        return
    
    # 시장 선택
    market = st.sidebar.selectbox(
        "📈 시장 선택",
        options=list(stock_lists.keys()),
        index=0
    )
    
    selected_stocks = stock_lists[market]
    st.sidebar.write(f"선택된 시장: **{market}** ({len(selected_stocks)}개 종목)")
    
    # 조건 설정
    st.sidebar.subheader("🎯 스크리닝 조건")
    
    conditions = {}
    
    # BB 상단 돌파
    if st.sidebar.checkbox("볼린저 밴드 상단 돌파", value=True):
        conditions["bb_breakout"] = True
    
    # RSI 조건
    if st.sidebar.checkbox("RSI 조건", value=True):
        rsi_type = st.sidebar.selectbox("RSI 조건 타입", ["미만", "초과", "상향돌파", "하향돌파"])
        rsi_value = st.sidebar.number_input("RSI 값", min_value=0, max_value=100, value=70)
        conditions["rsi_condition"] = {"type": rsi_type, "value": rsi_value}
    
    # 거래량 조건
    if st.sidebar.checkbox("거래량 급증", value=False):
        volume_multiplier = st.sidebar.number_input("거래량 배수", min_value=1.0, max_value=5.0, value=1.5, step=0.1)
        conditions["volume_surge"] = volume_multiplier
    
    # 스크리닝 실행
    if st.sidebar.button("🚀 스크리닝 실행", type="primary"):
        if not conditions:
            st.warning("최소 하나의 조건을 선택해주세요!")
            return
        
        st.subheader(f"📊 {market} 스크리닝 결과")
        
        with st.spinner("스크리닝 실행 중..."):
            results = screen_stocks(selected_stocks, conditions)
        
        if not results:
            st.info("조건에 맞는 종목이 없습니다.")
        else:
            st.success(f"🎯 {len(results)}개 종목이 조건을 만족합니다!")
            
            # 결과 테이블
            df_results = pd.DataFrame(results)
            st.dataframe(
                df_results,
                use_container_width=True,
                hide_index=True
            )
            
            # 상세 차트
            st.subheader("📈 상세 차트")
            selected_symbol = st.selectbox(
                "차트를 볼 종목 선택",
                options=[row['Symbol'] for row in results],
                format_func=lambda x: f"{x} - {next(row['Name'] for row in results if row['Symbol'] == x)}"
            )
            
            if selected_symbol:
                with st.spinner("차트 생성 중..."):
                    df_chart = get_stock_data(selected_symbol, period="6mo")
                    if df_chart is not None:
                        fig = create_stock_chart(selected_symbol, df_chart)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("차트 데이터를 가져올 수 없습니다.")
    
    # 정보 섹션
    st.markdown("---")
    st.subheader("ℹ️ 사용 가이드")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📊 지원 시장**
        - S&P 500: 미국 대형주
        - NASDAQ: 미국 기술주
        - KOSPI: 한국 대형주
        - KOSDAQ: 한국 중소형주
        """)
    
    with col2:
        st.markdown("""
        **🎯 스크리닝 조건**
        - BB 상단 돌파: 모멘텀 신호
        - RSI 조건: 과매수/과매도 확인
        - 거래량 급증: 관심도 증가
        """)
    
    st.markdown("""
    ---
    **⚠️ 면책조항**: 이 도구는 교육 및 연구 목적으로 제작되었습니다. 
    실제 투자 결정에 사용하기 전에 반드시 전문가와 상담하시기 바랍니다.
    """)

if __name__ == "__main__":
    main() 