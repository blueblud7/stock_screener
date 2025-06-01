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
    page_title="🚀 주식 스크리너 (Complete Cloud)",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 메모리 최적화된 종목 리스트 로딩
@st.cache_data(ttl=3600)
def load_complete_stock_lists():
    """완전한 종목 리스트를 로드합니다."""
    
    # GitHub에서 JSON 파일 읽기 시도
    json_file = "complete_stock_lists.json"
    
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                stock_lists = json.load(f)
            
            # 데이터 유효성 검사
            if isinstance(stock_lists, dict) and all(isinstance(v, dict) for v in stock_lists.values()):
                st.success(f"✅ 완전한 종목 리스트 로딩 완료! (총 {sum(len(stocks) for stocks in stock_lists.values())}개 종목)")
                return stock_lists
            else:
                st.warning("⚠️ JSON 파일 형식이 올바르지 않습니다.")
        except Exception as e:
            st.warning(f"JSON 파일 로딩 실패: {str(e)}")
    
    # 파일이 없거나 로딩 실패 시 기본 종목 사용
    st.info("ℹ️ 기본 주요 종목 리스트를 사용합니다.")
    
    return {
        "S&P 500": {
            "AAPL": "Apple Inc.", "MSFT": "Microsoft Corp.", "GOOGL": "Alphabet Inc.",
            "AMZN": "Amazon.com Inc.", "TSLA": "Tesla Inc.", "META": "Meta Platforms Inc.",
            "NVDA": "NVIDIA Corp.", "JPM": "JPMorgan Chase & Co.", "JNJ": "Johnson & Johnson",
            "UNH": "UnitedHealth Group Inc.", "V": "Visa Inc.", "PG": "Procter & Gamble Co.",
            "HD": "Home Depot Inc.", "MA": "Mastercard Inc.", "BAC": "Bank of America Corp.",
            "DIS": "Walt Disney Co.", "ADBE": "Adobe Inc.", "CRM": "Salesforce Inc.",
            "NFLX": "Netflix Inc.", "XOM": "Exxon Mobil Corp.", "WMT": "Walmart Inc.",
            "PFE": "Pfizer Inc.", "KO": "Coca-Cola Co.", "INTC": "Intel Corp.",
            "CSCO": "Cisco Systems Inc.", "VZ": "Verizon Communications Inc.",
            "TMO": "Thermo Fisher Scientific Inc.", "ACN": "Accenture PLC",
            "ABBV": "AbbVie Inc.", "NKE": "Nike Inc."
        },
        "NASDAQ": {
            "AAPL": "Apple Inc.", "MSFT": "Microsoft Corp.", "GOOGL": "Alphabet Inc.",
            "AMZN": "Amazon.com Inc.", "TSLA": "Tesla Inc.", "META": "Meta Platforms Inc.",
            "NVDA": "NVIDIA Corp.", "PYPL": "PayPal Holdings Inc.", "CMCSA": "Comcast Corp.",
            "INTC": "Intel Corp.", "CSCO": "Cisco Systems Inc.", "PEP": "PepsiCo Inc.",
            "ADBE": "Adobe Inc.", "NFLX": "Netflix Inc.", "TXN": "Texas Instruments Inc.",
            "QCOM": "QUALCOMM Inc.", "COST": "Costco Wholesale Corp.", "AVGO": "Broadcom Inc.",
            "SBUX": "Starbucks Corp.", "GILD": "Gilead Sciences Inc."
        },
        "KOSPI": {
            "005930.KS": "삼성전자", "000660.KS": "SK하이닉스", "035420.KS": "NAVER",
            "005490.KS": "POSCO홀딩스", "000270.KS": "기아", "005380.KS": "현대차",
            "051910.KS": "LG화학", "035720.KS": "카카오", "006400.KS": "삼성SDI",
            "028260.KS": "삼성물산", "068270.KS": "셀트리온", "207940.KS": "삼성바이오로직스",
            "066570.KS": "LG전자", "323410.KS": "카카오뱅크", "003670.KS": "포스코퓨처엠",
            "096770.KS": "SK이노베이션", "009150.KS": "삼성전기", "000810.KS": "삼성화재",
            "017670.KS": "SK텔레콤", "030200.KS": "KT", "034730.KS": "SK", "018260.KS": "삼성에스디에스",
            "015760.KS": "한국전력", "010950.KS": "S-Oil", "011170.KS": "롯데케미칼"
        },
        "KOSDAQ": {
            "263750.KQ": "펄어비스", "293490.KQ": "카카오게임즈", "196170.KQ": "알테오젠",
            "041510.KQ": "에스엠", "145020.KQ": "휴젤", "112040.KQ": "위메이드",
            "357780.KQ": "솔브레인", "086900.KQ": "메디톡스", "039030.KQ": "이오테크닉스",
            "058470.KQ": "리노공업", "067310.KQ": "하나마이크론", "078600.KQ": "대주전자재료",
            "108860.KQ": "셀바스AI", "095340.KQ": "ISC", "317870.KQ": "엔바이오니아",
            "122870.KQ": "와이지엔터테인먼트", "240810.KQ": "원익피앤이", "253450.KQ": "스튜디오드래곤",
            "376300.KQ": "디어유", "200130.KQ": "콜마비앤에이치"
        }
    }

# 캐시된 기술적 지표 계산
@st.cache_data(ttl=600)  # 10분 캐시
def calculate_technical_indicators(df):
    """메모리 효율적인 기술적 지표 계산"""
    try:
        if len(df) < 50:
            return df
        
        # 볼린저 밴드 (20, 2)
        bb_period = 20
        bb_std = 2
        df['BB_Middle'] = df['Close'].rolling(window=bb_period).mean()
        rolling_std = df['Close'].rolling(window=bb_period).std()
        df['BB_Upper'] = df['BB_Middle'] + (rolling_std * bb_std)
        df['BB_Lower'] = df['BB_Middle'] - (rolling_std * bb_std)
        
        # RSI (14일)
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
        except:
            exp1 = df['Close'].ewm(span=12).mean()
            exp2 = df['Close'].ewm(span=26).mean()
            df['MACD'] = exp1 - exp2
            df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        
        # 이동평균
        df['MA_20'] = df['Close'].rolling(window=20).mean()
        df['MA_50'] = df['Close'].rolling(window=50).mean()
        
        # 거래량 평균
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        
        return df
        
    except Exception as e:
        st.error(f"기술적 지표 계산 오류: {str(e)}")
        return df

# 메모리 효율적인 주식 데이터 가져오기
@st.cache_data(ttl=300)  # 5분 캐시
def get_stock_data_optimized(symbol, period="3mo"):
    """메모리 최적화된 주식 데이터 수집"""
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        
        if df.empty:
            return None
            
        # 메모리 사용량 최소화
        df = df.astype({
            'Open': 'float32',
            'High': 'float32', 
            'Low': 'float32',
            'Close': 'float32',
            'Volume': 'int64'
        })
        
        df = calculate_technical_indicators(df)
        return df
        
    except Exception as e:
        return None

# 조건 확인 함수들
def check_bb_breakout(df):
    """볼린저 밴드 상단 돌파 확인"""
    if len(df) < 2 or 'BB_Upper' not in df.columns:
        return False
    latest = df.iloc[-1]
    previous = df.iloc[-2]
    return (latest['Close'] > latest['BB_Upper'] and 
            previous['Close'] <= previous['BB_Upper'])

def check_rsi_condition(df, condition, value):
    """RSI 조건 확인"""
    if len(df) < 1 or 'RSI' not in df.columns or pd.isna(df.iloc[-1]['RSI']):
        return False
    
    latest_rsi = df.iloc[-1]['RSI']
    
    if condition == "초과":
        return latest_rsi > value
    elif condition == "미만":
        return latest_rsi < value
    elif condition == "상향돌파":
        if len(df) < 2 or pd.isna(df.iloc[-2]['RSI']):
            return False
        prev_rsi = df.iloc[-2]['RSI']
        return latest_rsi > value and prev_rsi <= value
    elif condition == "하향돌파":
        if len(df) < 2 or pd.isna(df.iloc[-2]['RSI']):
            return False
        prev_rsi = df.iloc[-2]['RSI']
        return latest_rsi < value and prev_rsi >= value
    return False

def check_volume_surge(df, multiplier=1.5):
    """거래량 급증 확인"""
    if len(df) < 1 or 'Volume_MA' not in df.columns:
        return False
    latest = df.iloc[-1]
    return latest['Volume'] > latest['Volume_MA'] * multiplier

# 배치 스크리닝 (메모리 효율적)
def screen_stocks_batch(stocks, conditions, batch_size=20):
    """배치 단위로 메모리 효율적 스크리닝"""
    
    # 입력 유효성 검사
    if not isinstance(stocks, dict):
        st.error(f"❌ 종목 데이터 오류: 예상된 딕셔너리가 아닙니다. 실제 타입: {type(stocks)}")
        return []
    
    if not stocks:
        st.warning("⚠️ 선택된 시장에 종목이 없습니다.")
        return []
    
    results = []
    total_stocks = len(stocks)
    processed = 0
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        stock_items = list(stocks.items())
        
        # 배치 단위로 처리
        for i in range(0, total_stocks, batch_size):
            batch = stock_items[i:i+batch_size]
            
            for symbol, name in batch:
                processed += 1
                progress = processed / total_stocks
                progress_bar.progress(progress)
                status_text.text(f"분석 중: {name} ({symbol}) - {processed}/{total_stocks}")
                
                try:
                    df = get_stock_data_optimized(symbol)
                    if df is None or len(df) < 20:
                        continue
                    
                    # 조건 확인
                    conditions_met = []
                    
                    # BB 상단 돌파
                    if conditions.get("bb_breakout") and check_bb_breakout(df):
                        conditions_met.append("BB상단돌파")
                    
                    # RSI 조건
                    if "rsi_condition" in conditions:
                        rsi_cond = conditions["rsi_condition"]
                        if check_rsi_condition(df, rsi_cond["type"], rsi_cond["value"]):
                            conditions_met.append(f"RSI{rsi_cond['type']}{rsi_cond['value']}")
                    
                    # 거래량 조건
                    if "volume_surge" in conditions:
                        if check_volume_surge(df, conditions["volume_surge"]):
                            conditions_met.append("거래량급증")
                    
                    # 결과 추가
                    if conditions_met:
                        latest = df.iloc[-1]
                        change_pct = ((latest['Close'] - df.iloc[-2]['Close']) / df.iloc[-2]['Close'] * 100) if len(df) > 1 else 0
                        
                        results.append({
                            "Symbol": symbol,
                            "Name": name,
                            "Price": round(latest['Close'], 2),
                            "Change%": round(change_pct, 2),
                            "RSI": round(latest['RSI'], 1) if not pd.isna(latest['RSI']) else 0,
                            "Volume_Ratio": round(latest['Volume'] / latest['Volume_MA'], 2) if latest['Volume_MA'] > 0 else 0,
                            "Conditions": ", ".join(conditions_met)
                        })
                        
                except Exception as e:
                    # 개별 종목 에러는 무시하고 계속 진행
                    continue
            
            # 배치 완료 후 잠시 대기 (메모리 정리)
            time.sleep(0.1)
    
    except Exception as e:
        st.error(f"❌ 스크리닝 중 오류 발생: {str(e)}")
        return []
    
    finally:
        progress_bar.empty()
        status_text.empty()
    
    return results

# 간단한 차트 생성
def create_simple_chart(symbol, df):
    """메모리 효율적인 간단한 차트"""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(f'{symbol} - Price & Bollinger Bands', 'RSI'),
        row_heights=[0.7, 0.3]
    )
    
    # 캔들스틱
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
    
    fig.update_layout(
        height=600,
        showlegend=False,
        xaxis_rangeslider_visible=False
    )
    
    return fig

# 메인 앱
def main():
    st.title("🚀 주식 기술적 분석 스크리너 (Complete Cloud Edition)")
    st.markdown("**완전한 버전 - 최대 851개 종목 지원**")
    st.markdown("---")
    
    # 사이드바
    st.sidebar.title("📊 설정")
    
    # 종목 리스트 로드
    with st.spinner("종목 리스트 로딩 중..."):
        stock_lists = load_complete_stock_lists()
    
    # 데이터 유효성 재확인
    if not isinstance(stock_lists, dict) or not stock_lists:
        st.error("❌ 종목 리스트 로딩에 실패했습니다. 페이지를 새로고침해주세요.")
        st.stop()
    
    # 시장 선택
    market = st.sidebar.selectbox(
        "📈 시장 선택",
        options=list(stock_lists.keys()),
        index=0
    )
    
    # 선택된 시장의 종목 가져오기
    selected_stocks = stock_lists.get(market, {})
    
    if not selected_stocks:
        st.error(f"❌ {market} 시장에 종목이 없습니다.")
        st.stop()
    
    st.sidebar.write(f"선택된 시장: **{market}** ({len(selected_stocks)}개 종목)")
    
    # 디버깅 정보 (개발 시에만 표시)
    with st.sidebar.expander("🔍 디버그 정보", expanded=False):
        st.write(f"종목 리스트 타입: {type(selected_stocks)}")
        st.write(f"종목 수: {len(selected_stocks) if isinstance(selected_stocks, dict) else 'N/A'}")
        if isinstance(selected_stocks, dict) and selected_stocks:
            st.write(f"첫 번째 종목: {list(selected_stocks.items())[0]}")
    
    # 조건 설정
    st.sidebar.subheader("🎯 스크리닝 조건")
    
    conditions = {}
    
    # BB 상단 돌파
    if st.sidebar.checkbox("볼린저 밴드(20,2) 상단 돌파", value=True):
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
        
        with st.spinner("배치 스크리닝 실행 중..."):
            results = screen_stocks_batch(selected_stocks, conditions, batch_size=15)
        
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
            if len(results) > 0:
                st.subheader("📈 상세 차트")
                selected_symbol = st.selectbox(
                    "차트를 볼 종목 선택",
                    options=[row['Symbol'] for row in results],
                    format_func=lambda x: f"{x} - {next(row['Name'] for row in results if row['Symbol'] == x)}"
                )
                
                if selected_symbol:
                    with st.spinner("차트 생성 중..."):
                        df_chart = get_stock_data_optimized(selected_symbol, period="6mo")
                        if df_chart is not None:
                            fig = create_simple_chart(selected_symbol, df_chart)
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
        **🎯 핵심 기능**
        - BB(20,2) 상단 돌파 스크리닝
        - RSI 과매수/과매도 확인
        - 거래량 급증 감지
        - 배치 처리로 안정적 분석
        """)
    
    st.markdown("""
    ---
    **⚠️ 면책조항**: 이 도구는 교육 및 연구 목적으로 제작되었습니다. 
    실제 투자 결정에 사용하기 전에 반드시 전문가와 상담하시기 바랍니다.
    """)

if __name__ == "__main__":
    main() 