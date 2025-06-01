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
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 페이지 설정
st.set_page_config(
    page_title="🚀 Ultra Complete 주식 스크리너",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 전체 종목 리스트 로딩
@st.cache_data(ttl=3600)
def load_ultra_complete_stock_lists():
    """완전한 851개 종목 리스트를 로드합니다."""
    
    json_file = "complete_stock_lists.json"
    
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                stock_lists = json.load(f)
            
            # 데이터 유효성 검사
            if isinstance(stock_lists, dict) and all(isinstance(v, dict) for v in stock_lists.values()):
                total_stocks = sum(len(stocks) for stocks in stock_lists.values())
                st.success(f"✅ 완전한 종목 리스트 로딩 완료! (총 {total_stocks}개 종목)")
                return stock_lists
            else:
                st.warning("⚠️ JSON 파일 형식이 올바르지 않습니다.")
        except Exception as e:
            st.warning(f"JSON 파일 로딩 실패: {str(e)}")
    
    # 파일이 없으면 오류 메시지
    st.error("❌ complete_stock_lists.json 파일을 찾을 수 없습니다!")
    st.info("💡 complete_stock_lists.py를 먼저 실행하여 전체 종목 리스트를 생성해주세요.")
    st.stop()

# 멀티스레딩 기술적 지표 계산
def calculate_technical_indicators_fast(df):
    """빠른 기술적 지표 계산"""
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
        return df

# 개별 종목 데이터 가져오기 (멀티스레딩용)
def get_single_stock_data(symbol, period="3mo"):
    """개별 종목 데이터 수집"""
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        
        if df.empty:
            return symbol, None
            
        # 메모리 최적화
        df = df.astype({
            'Open': 'float32',
            'High': 'float32', 
            'Low': 'float32',
            'Close': 'float32',
            'Volume': 'int64'
        })
        
        df = calculate_technical_indicators_fast(df)
        return symbol, df
        
    except Exception as e:
        return symbol, None

# 멀티스레딩 주식 데이터 수집
def get_multiple_stocks_data(symbols, max_workers=20):
    """멀티스레딩으로 여러 종목 데이터 수집"""
    stock_data = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 모든 종목을 동시에 요청
        future_to_symbol = {executor.submit(get_single_stock_data, symbol): symbol for symbol in symbols}
        
        for future in as_completed(future_to_symbol):
            try:
                symbol, df = future.result()
                if df is not None:
                    stock_data[symbol] = df
            except Exception as e:
                continue
    
    return stock_data

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

def check_price_momentum(df):
    """가격 모멘텀 확인 (20일 MA 상향)"""
    if len(df) < 2 or 'MA_20' not in df.columns:
        return False
    latest = df.iloc[-1]
    return latest['Close'] > latest['MA_20']

def check_macd_bullish(df):
    """MACD 상승 신호 확인"""
    if len(df) < 2 or 'MACD' not in df.columns or 'MACD_Signal' not in df.columns:
        return False
    latest = df.iloc[-1]
    previous = df.iloc[-2]
    return (latest['MACD'] > latest['MACD_Signal'] and 
            previous['MACD'] <= previous['MACD_Signal'])

# 울트라 스크리닝 (멀티스레딩)
def ultra_screen_stocks(stocks, conditions, max_workers=20):
    """멀티스레딩으로 초고속 전체 스크리닝"""
    
    if not isinstance(stocks, dict) or not stocks:
        st.error("❌ 종목 데이터 오류")
        return []
    
    total_stocks = len(stocks)
    st.info(f"🚀 {total_stocks}개 종목 울트라 스크리닝 시작... (멀티스레딩 {max_workers}개)")
    
    # 프로그레스 바 설정
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    symbols = list(stocks.keys())
    results = []
    processed = 0
    
    # 배치 크기 설정 (메모리 관리)
    batch_size = 100
    
    try:
        for i in range(0, len(symbols), batch_size):
            batch_symbols = symbols[i:i+batch_size]
            batch_end = min(i + batch_size, len(symbols))
            
            status_text.text(f"배치 {i//batch_size + 1}: {i+1}-{batch_end} 종목 처리 중...")
            
            # 배치 단위로 멀티스레딩 데이터 수집
            stock_data = get_multiple_stocks_data(batch_symbols, max_workers)
            
            # 각 종목별 조건 확인
            for symbol in batch_symbols:
                processed += 1
                progress = processed / total_stocks
                progress_bar.progress(progress)
                
                if symbol not in stock_data:
                    continue
                
                df = stock_data[symbol]
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
                
                # 가격 모멘텀
                if conditions.get("price_momentum") and check_price_momentum(df):
                    conditions_met.append("가격모멘텀")
                
                # MACD 상승 신호
                if conditions.get("macd_bullish") and check_macd_bullish(df):
                    conditions_met.append("MACD상승")
                
                # 결과 추가
                if conditions_met:
                    latest = df.iloc[-1]
                    change_pct = ((latest['Close'] - df.iloc[-2]['Close']) / df.iloc[-2]['Close'] * 100) if len(df) > 1 else 0
                    
                    results.append({
                        "Symbol": symbol,
                        "Name": stocks[symbol],
                        "Price": round(latest['Close'], 2),
                        "Change%": round(change_pct, 2),
                        "RSI": round(latest['RSI'], 1) if not pd.isna(latest['RSI']) else 0,
                        "Volume_Ratio": round(latest['Volume'] / latest['Volume_MA'], 2) if latest['Volume_MA'] > 0 else 0,
                        "BB_Position": round((latest['Close'] - latest['BB_Lower']) / (latest['BB_Upper'] - latest['BB_Lower']) * 100, 1) if 'BB_Upper' in df.columns else 0,
                        "Conditions": ", ".join(conditions_met)
                    })
            
            # 배치 완료 후 잠시 대기
            time.sleep(0.2)
    
    except Exception as e:
        st.error(f"❌ 울트라 스크리닝 중 오류: {str(e)}")
        return []
    
    finally:
        progress_bar.empty()
        status_text.empty()
    
    return results

# 고급 차트 생성
def create_advanced_chart(symbol, df, name):
    """고급 기술적 분석 차트"""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(f'{symbol} - {name}', 'Volume', 'RSI & MACD'),
        row_heights=[0.6, 0.2, 0.2]
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
    
    # 이동평균
    if 'MA_20' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['MA_20'], name='MA 20', line=dict(color='orange', width=2)), row=1, col=1)
    if 'MA_50' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['MA_50'], name='MA 50', line=dict(color='purple', width=2)), row=1, col=1)
    
    # 거래량
    colors = ['red' if row['Close'] >= row['Open'] else 'blue' for _, row in df.iterrows()]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color=colors), row=2, col=1)
    if 'Volume_MA' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['Volume_MA'], name='Volume MA', line=dict(color='yellow', width=2)), row=2, col=1)
    
    # RSI
    if 'RSI' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')), row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    # MACD
    if 'MACD' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='blue')), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], name='Signal', line=dict(color='red')), row=3, col=1)
    
    fig.update_layout(
        height=800,
        showlegend=False,
        xaxis_rangeslider_visible=False,
        title=f"📈 {symbol} - {name} 고급 기술적 분석"
    )
    
    return fig

# 메인 앱
def main():
    st.title("🚀 Ultra Complete 주식 스크리너")
    st.markdown("**완전한 851개 종목 멀티스레딩 울트라 스크리너**")
    st.markdown("---")
    
    # 사이드바
    st.sidebar.title("📊 Ultra 설정")
    
    # 종목 리스트 로드
    with st.spinner("완전한 종목 리스트 로딩 중..."):
        stock_lists = load_ultra_complete_stock_lists()
    
    # 시장 선택
    market_options = list(stock_lists.keys()) + ["🌍 전체 시장"]
    market = st.sidebar.selectbox(
        "📈 시장 선택",
        options=market_options,
        index=len(market_options)-1  # 기본값: 전체 시장
    )
    
    # 선택된 종목 가져오기
    if market == "🌍 전체 시장":
        selected_stocks = {}
        for stocks in stock_lists.values():
            selected_stocks.update(stocks)
        st.sidebar.success(f"✅ 전체 시장 선택: {len(selected_stocks)}개 종목")
    else:
        selected_stocks = stock_lists[market]
        st.sidebar.info(f"✅ {market}: {len(selected_stocks)}개 종목")
    
    # 울트라 설정
    st.sidebar.subheader("⚡ 울트라 설정")
    max_workers = st.sidebar.slider("동시 처리 스레드 수", 10, 50, 25)
    
    # 조건 설정
    st.sidebar.subheader("🎯 스크리닝 조건")
    
    conditions = {}
    
    # 핵심 조건들
    if st.sidebar.checkbox("볼린저 밴드(20,2) 상단 돌파", value=True):
        conditions["bb_breakout"] = True
    
    if st.sidebar.checkbox("RSI 조건", value=True):
        rsi_type = st.sidebar.selectbox("RSI 조건 타입", ["미만", "초과", "상향돌파", "하향돌파"])
        rsi_value = st.sidebar.number_input("RSI 값", min_value=0, max_value=100, value=70)
        conditions["rsi_condition"] = {"type": rsi_type, "value": rsi_value}
    
    if st.sidebar.checkbox("거래량 급증", value=False):
        volume_multiplier = st.sidebar.number_input("거래량 배수", min_value=1.0, max_value=5.0, value=1.5, step=0.1)
        conditions["volume_surge"] = volume_multiplier
    
    # 추가 조건들
    if st.sidebar.checkbox("가격 모멘텀 (20일 MA 상향)", value=False):
        conditions["price_momentum"] = True
    
    if st.sidebar.checkbox("MACD 상승 신호", value=False):
        conditions["macd_bullish"] = True
    
    # 울트라 스크리닝 실행
    if st.sidebar.button("🚀 울트라 스크리닝 실행", type="primary"):
        if not conditions:
            st.warning("최소 하나의 조건을 선택해주세요!")
            return
        
        st.subheader(f"📊 {market} 울트라 스크리닝 결과")
        
        start_time = time.time()
        
        with st.spinner(f"울트라 스크리닝 실행 중... ({len(selected_stocks)}개 종목)"):
            results = ultra_screen_stocks(selected_stocks, conditions, max_workers)
        
        end_time = time.time()
        execution_time = round(end_time - start_time, 2)
        
        if not results:
            st.info("조건에 맞는 종목이 없습니다.")
        else:
            st.success(f"🎯 {len(results)}개 종목이 조건을 만족합니다! (실행시간: {execution_time}초)")
            
            # 결과 정렬 옵션
            sort_options = ["RSI", "Change%", "Volume_Ratio", "BB_Position", "Symbol"]
            sort_by = st.selectbox("정렬 기준", sort_options, index=1)
            ascending = st.checkbox("오름차순", value=False)
            
            # 결과 정렬
            df_results = pd.DataFrame(results)
            df_results = df_results.sort_values(by=sort_by, ascending=ascending)
            
            # 결과 테이블
            st.dataframe(
                df_results,
                use_container_width=True,
                hide_index=True
            )
            
            # CSV 다운로드
            csv = df_results.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 결과 CSV 다운로드",
                data=csv,
                file_name=f"ultra_screening_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
            
            # 상세 차트
            if len(results) > 0:
                st.subheader("📈 고급 차트 분석")
                
                # 차트 선택
                chart_symbol = st.selectbox(
                    "차트를 볼 종목 선택",
                    options=[row['Symbol'] for row in results],
                    format_func=lambda x: f"{x} - {next(row['Name'] for row in results if row['Symbol'] == x)}"
                )
                
                if chart_symbol:
                    with st.spinner("고급 차트 생성 중..."):
                        chart_data = get_single_stock_data(chart_symbol, period="6mo")
                        if chart_data[1] is not None:
                            stock_name = next(row['Name'] for row in results if row['Symbol'] == chart_symbol)
                            fig = create_advanced_chart(chart_symbol, chart_data[1], stock_name)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.error("차트 데이터를 가져올 수 없습니다.")
    
    # 통계 정보
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_stocks = sum(len(stocks) for stocks in stock_lists.values())
        st.metric("📊 전체 종목 수", f"{total_stocks:,}")
    
    with col2:
        st.metric("🏢 지원 시장", len(stock_lists))
    
    with col3:
        st.metric("⚡ 최대 스레드", max_workers)
    
    with col4:
        if market == "🌍 전체 시장":
            st.metric("🎯 선택된 종목", f"{len(selected_stocks):,}")
        else:
            st.metric("🎯 선택된 종목", len(selected_stocks))
    
    # 정보 섹션
    st.markdown("---")
    st.subheader("ℹ️ Ultra Complete 스크리너 정보")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📊 지원 시장 & 종목 수**
        - S&P 500: 503개 종목
        - NASDAQ: 154개 종목  
        - KOSPI: 110개 종목
        - KOSDAQ: 84개 종목
        - **전체: 851개 종목**
        """)
    
    with col2:
        st.markdown("""
        **🚀 Ultra 기능**
        - 멀티스레딩 초고속 분석
        - 전체 시장 동시 스크리닝
        - 고급 기술적 지표
        - CSV 결과 다운로드
        - 실시간 진행률 표시
        """)
    
    st.markdown("""
    ---
    **⚠️ 면책조항**: 이 도구는 교육 및 연구 목적으로 제작되었습니다. 
    실제 투자 결정에 사용하기 전에 반드시 전문가와 상담하시기 바랍니다.
    """)

if __name__ == "__main__":
    main() 