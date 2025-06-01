import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import ta
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
from strategy_builder import (
    StrategyBuilder, PresetStrategies, Condition, ConditionType, 
    Operator, get_strategy_description
)

# 페이지 설정
st.set_page_config(
    page_title="고급 주식 스크리너",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 제목
st.title("🚀 고급 주식 전략 스크리너")
st.markdown("---")

class AdvancedStockScreener:
    def __init__(self):
        self.markets = {
            "KOSPI": self.get_kospi_stocks(),
            "KOSDAQ": self.get_kosdaq_stocks(),
            "NASDAQ": self.get_nasdaq_stocks(),
            "S&P 500": self.get_sp500_stocks()
        }
    
    @st.cache_data(ttl=3600)
    def get_kospi_stocks(_self):
        """KOSPI 주요 종목들"""
        return [
            "005930.KS",  # 삼성전자
            "000660.KS",  # SK하이닉스
            "035420.KS",  # NAVER
            "005380.KS",  # 현대차
            "005490.KS",  # POSCO홀딩스
            "035720.KS",  # 카카오
            "051910.KS",  # LG화학
            "006400.KS",  # 삼성SDI
            "034020.KS",  # 두산에너빌리티
            "028260.KS",  # 삼성물산
            "003550.KS",  # LG
            "068270.KS",  # 셀트리온
            "207940.KS",  # 삼성바이오로직스
            "096770.KS",  # SK이노베이션
            "323410.KS",  # 카카오뱅크
        ]
    
    @st.cache_data(ttl=3600)
    def get_kosdaq_stocks(_self):
        """KOSDAQ 주요 종목들"""
        return [
            "263750.KQ",  # 펄어비스
            "293490.KQ",  # 카카오게임즈
            "041510.KQ",  # SM
            "178920.KQ",  # PI첨단소재
            "086980.KQ",  # 쇼박스
            "053800.KQ",  # 안랩
            "064260.KQ",  # 다날
            "214150.KQ",  # 클래시스
            "039030.KQ",  # 이오테크닉스
            "225570.KQ",  # 넥슨게임즈
            "054620.KQ",  # APS홀딩스
            "196170.KQ",  # 알테오젠
            "145020.KQ",  # 휴젤
            "222080.KQ",  # 씨아이에스
            "357780.KQ",  # 솔브레인
        ]
    
    @st.cache_data(ttl=3600)
    def get_nasdaq_stocks(_self):
        """NASDAQ 주요 종목들"""
        return [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
            "META", "NVDA", "NFLX", "CRM", "ADBE",
            "ORCL", "INTC", "AMD", "QCOM", "CSCO",
            "PYPL", "SPOT", "ZM", "DOCU", "ROKU"
        ]
    
    @st.cache_data(ttl=3600)
    def get_sp500_stocks(_self):
        """S&P 500 주요 종목들"""
        return [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
            "BRK-B", "UNH", "JNJ", "XOM", "JPM",
            "V", "PG", "MA", "HD", "CVX",
            "WMT", "BAC", "ABBV", "PFE", "KO"
        ]
    
    def get_stock_data(self, symbol: str, period: str = "6mo") -> pd.DataFrame:
        """주식 데이터 가져오기"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            if data.empty:
                return None
            return data
        except Exception as e:
            st.error(f"데이터 가져오기 실패 ({symbol}): {str(e)}")
            return None
    
    def get_stock_info(self, symbol: str) -> dict:
        """주식 기본 정보 가져오기"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', 'N/A')),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                'currency': info.get('currency', 'USD'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A')
            }
        except Exception as e:
            return {
                'symbol': symbol,
                'name': 'N/A',
                'market_cap': 0,
                'pe_ratio': 'N/A',
                'price': 0,
                'currency': 'USD',
                'sector': 'N/A',
                'industry': 'N/A'
            }
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """기술적 지표 계산"""
        if data is None or data.empty:
            return None
            
        # 볼린저 밴드
        bb_period = 20
        bb_std = 2
        data['BB_Middle'] = ta.trend.sma_indicator(data['Close'], window=bb_period)
        data['BB_Upper'] = data['BB_Middle'] + (data['Close'].rolling(bb_period).std() * bb_std)
        data['BB_Lower'] = data['BB_Middle'] - (data['Close'].rolling(bb_period).std() * bb_std)
        
        # RSI
        data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
        
        # MACD
        data['MACD'] = ta.trend.macd_diff(data['Close'])
        data['MACD_Signal'] = ta.trend.macd_signal(data['Close'])
        
        # 이동평균
        data['SMA_20'] = ta.trend.sma_indicator(data['Close'], window=20)
        data['SMA_50'] = ta.trend.sma_indicator(data['Close'], window=50)
        data['SMA_200'] = ta.trend.sma_indicator(data['Close'], window=200)
        
        # 거래량 관련
        data['Volume_SMA'] = ta.volume.volume_sma(data['Close'], data['Volume'], window=20)
        
        # Stochastic
        data['Stoch_K'] = ta.momentum.stoch(data['High'], data['Low'], data['Close'])
        data['Stoch_D'] = ta.momentum.stoch_signal(data['High'], data['Low'], data['Close'])
        
        # Williams %R
        data['Williams_R'] = ta.momentum.williams_r(data['High'], data['Low'], data['Close'])
        
        return data

def create_custom_strategy():
    """사용자 정의 전략 생성"""
    st.subheader("🛠️ 사용자 정의 전략 빌더")
    
    strategy = StrategyBuilder()
    
    # 조건 개수 선택
    num_conditions = st.number_input("조건 개수", min_value=1, max_value=10, value=2)
    
    for i in range(num_conditions):
        st.write(f"**조건 {i+1}**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            condition_type = st.selectbox(
                f"지표 선택 {i+1}",
                ["볼린저 밴드", "RSI", "MACD", "이동평균", "거래량", "가격액션"],
                key=f"type_{i}"
            )
        
        with col2:
            if condition_type == "볼린저 밴드":
                operator = st.selectbox(
                    f"조건 {i+1}",
                    ["상단 돌파", "하단 지지", "상단 위", "하단 아래"],
                    key=f"op_{i}"
                )
                value = 0
            elif condition_type == "RSI":
                operator = st.selectbox(
                    f"조건 {i+1}",
                    ["초과", "미만", "상향돌파", "하향돌파"],
                    key=f"op_{i}"
                )
            elif condition_type == "이동평균":
                operator = st.selectbox(
                    f"조건 {i+1}",
                    ["골든크로스", "주가>20일선"],
                    key=f"op_{i}"
                )
                value = 0
            else:
                operator = st.selectbox(
                    f"조건 {i+1}",
                    ["초과", "미만"],
                    key=f"op_{i}"
                )
        
        with col3:
            if condition_type in ["RSI", "거래량", "가격액션"]:
                value = st.number_input(f"값 {i+1}", value=70.0 if condition_type == "RSI" else 1.5, key=f"val_{i}")
            else:
                value = 0
        
        # 조건 객체 생성 및 추가
        condition = create_condition_from_ui(condition_type, operator, value, i)
        if condition:
            strategy.add_condition(condition)
    
    # 조합 방식
    logic = st.radio("조건 조합 방식", ["AND (모든 조건 만족)", "OR (하나라도 만족)"])
    strategy.set_combination_logic("AND" if "AND" in logic else "OR")
    
    return strategy

def create_condition_from_ui(condition_type, operator, value, index):
    """UI 입력으로부터 조건 객체 생성"""
    try:
        # 조건 타입 매핑
        type_mapping = {
            "볼린저 밴드": ConditionType.BOLLINGER_BAND,
            "RSI": ConditionType.RSI,
            "MACD": ConditionType.MACD,
            "이동평균": ConditionType.MOVING_AVERAGE,
            "거래량": ConditionType.VOLUME,
            "가격액션": ConditionType.PRICE_ACTION
        }
        
        # 연산자 매핑
        operator_mapping = {
            "상단 돌파": Operator.BREAKOUT,
            "하단 지지": Operator.SUPPORT,
            "상단 위": Operator.GREATER_THAN,
            "하단 아래": Operator.LESS_THAN,
            "초과": Operator.GREATER_THAN,
            "미만": Operator.LESS_THAN,
            "상향돌파": Operator.CROSS_ABOVE,
            "하향돌파": Operator.CROSS_BELOW,
            "골든크로스": Operator.CROSS_ABOVE,
            "주가>20일선": Operator.GREATER_THAN
        }
        
        condition_obj_type = type_mapping.get(condition_type)
        operator_obj = operator_mapping.get(operator)
        
        if not condition_obj_type or not operator_obj:
            return None
        
        # 파라미터 설정
        parameters = None
        if condition_type == "이동평균":
            if operator == "골든크로스":
                parameters = {'ma_type': 'golden_cross'}
            elif operator == "주가>20일선":
                parameters = {'period': 20}
        elif condition_type == "가격액션":
            parameters = {'type': 'daily_change'}
        
        return Condition(
            name=f"{condition_type} {operator}",
            condition_type=condition_obj_type,
            operator=operator_obj,
            value=value,
            description=f"{condition_type} {operator} {value if value != 0 else ''}",
            parameters=parameters
        )
    except Exception as e:
        st.error(f"조건 생성 오류: {str(e)}")
        return None

def main():
    screener = AdvancedStockScreener()
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["🎯 기본 스크리너", "🛠️ 고급 전략 빌더", "📊 시장 분석"])
    
    with tab1:
        st.header("기본 스크리너")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("설정")
            
            # 시장 선택
            selected_market = st.selectbox(
                "시장 선택",
                ["KOSPI", "KOSDAQ", "NASDAQ", "S&P 500"]
            )
            
            # 사전 정의된 전략 선택
            strategy_type = st.selectbox(
                "전략 선택",
                ["모멘텀 돌파", "과매도 반전", "골든 크로스"]
            )
            
            # 전략 설명
            if strategy_type == "모멘텀 돌파":
                strategy = PresetStrategies.momentum_breakout()
            elif strategy_type == "과매도 반전":
                strategy = PresetStrategies.oversold_reversal()
            else:
                strategy = PresetStrategies.golden_cross()
            
            st.text_area("전략 설명", get_strategy_description(strategy), height=200)
            
            # 스크리닝 실행
            if st.button("🔍 스크리닝 실행", type="primary"):
                st.session_state.run_screening = True
                st.session_state.selected_market = selected_market
                st.session_state.strategy = strategy
        
        with col2:
            if hasattr(st.session_state, 'run_screening') and st.session_state.run_screening:
                st.subheader(f"📊 {st.session_state.selected_market} 스크리닝 결과")
                
                stocks = screener.markets[st.session_state.selected_market]
                
                with st.spinner("주식 데이터를 분석 중입니다..."):
                    results = []
                    progress_bar = st.progress(0)
                    
                    for i, symbol in enumerate(stocks):
                        data = screener.get_stock_data(symbol)
                        if data is not None:
                            data_with_indicators = screener.calculate_technical_indicators(data)
                            if st.session_state.strategy.evaluate_strategy(data_with_indicators):
                                stock_info = screener.get_stock_info(symbol)
                                latest_data = data_with_indicators.iloc[-1]
                                
                                results.append({
                                    '티커': symbol,
                                    '종목명': stock_info['name'][:20] + "..." if len(stock_info['name']) > 20 else stock_info['name'],
                                    '섹터': stock_info['sector'],
                                    '현재가': f"{latest_data['Close']:.2f}",
                                    '시가총액': f"{stock_info['market_cap']:,}" if stock_info['market_cap'] else "N/A",
                                    'PER': f"{stock_info['pe_ratio']:.2f}" if isinstance(stock_info['pe_ratio'], (int, float)) else "N/A",
                                    'RSI': f"{latest_data['RSI']:.1f}",
                                    '볼린저밴드%': f"{((latest_data['Close'] - latest_data['BB_Lower']) / (latest_data['BB_Upper'] - latest_data['BB_Lower']) * 100):.1f}%",
                                    '거래량비율': f"{(latest_data['Volume'] / latest_data['Volume_SMA']):.1f}x" if latest_data['Volume_SMA'] > 0 else "N/A"
                                })
                        
                        progress_bar.progress((i + 1) / len(stocks))
                        time.sleep(0.05)  # API 제한 방지
                
                if results:
                    df_results = pd.DataFrame(results)
                    st.dataframe(df_results, use_container_width=True, height=400)
                    
                    # 상세 차트
                    if len(results) > 0:
                        st.subheader("📈 상세 차트")
                        selected_stock = st.selectbox("차트를 볼 종목 선택", [r['티커'] for r in results])
                        
                        if selected_stock:
                            display_detailed_chart(screener, selected_stock)
                else:
                    st.info("설정한 조건에 맞는 종목이 없습니다.")
    
    with tab2:
        st.header("고급 전략 빌더")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            custom_strategy = create_custom_strategy()
            
            selected_market_custom = st.selectbox(
                "시장 선택",
                ["KOSPI", "KOSDAQ", "NASDAQ", "S&P 500"],
                key="custom_market"
            )
            
            if st.button("🚀 사용자 전략 실행", type="primary"):
                st.session_state.run_custom = True
                st.session_state.custom_strategy = custom_strategy
                st.session_state.custom_market = selected_market_custom
        
        with col2:
            if hasattr(st.session_state, 'run_custom') and st.session_state.run_custom:
                st.subheader("사용자 정의 전략 결과")
                
                # 전략 실행 로직 (기본 스크리너와 동일)
                stocks = screener.markets[st.session_state.custom_market]
                
                with st.spinner("사용자 전략을 실행 중입니다..."):
                    results = []
                    progress_bar = st.progress(0)
                    
                    for i, symbol in enumerate(stocks):
                        data = screener.get_stock_data(symbol)
                        if data is not None:
                            data_with_indicators = screener.calculate_technical_indicators(data)
                            if st.session_state.custom_strategy.evaluate_strategy(data_with_indicators):
                                stock_info = screener.get_stock_info(symbol)
                                latest_data = data_with_indicators.iloc[-1]
                                
                                results.append({
                                    '티커': symbol,
                                    '종목명': stock_info['name'][:15] + "..." if len(stock_info['name']) > 15 else stock_info['name'],
                                    '현재가': f"{latest_data['Close']:.2f}",
                                    'RSI': f"{latest_data['RSI']:.1f}",
                                    'MACD': f"{latest_data['MACD']:.3f}",
                                    '20일선': f"{latest_data['SMA_20']:.2f}",
                                    '거래량': f"{latest_data['Volume']:,}"
                                })
                        
                        progress_bar.progress((i + 1) / len(stocks))
                        time.sleep(0.05)
                
                if results:
                    df_results = pd.DataFrame(results)
                    st.dataframe(df_results, use_container_width=True)
                else:
                    st.info("사용자 정의 조건에 맞는 종목이 없습니다.")
    
    with tab3:
        st.header("시장 분석")
        
        market_analysis = st.selectbox(
            "분석할 시장",
            ["KOSPI", "KOSDAQ", "NASDAQ", "S&P 500"]
        )
        
        if st.button("📊 시장 분석 실행"):
            analyze_market(screener, market_analysis)

def display_detailed_chart(screener, symbol):
    """상세 차트 표시"""
    chart_data = screener.get_stock_data(symbol, "1y")
    chart_data = screener.calculate_technical_indicators(chart_data)
    
    # 메인 차트
    fig = go.Figure()
    
    # 캔들스틱
    fig.add_trace(go.Candlestick(
        x=chart_data.index,
        open=chart_data['Open'],
        high=chart_data['High'],
        low=chart_data['Low'],
        close=chart_data['Close'],
        name="Price"
    ))
    
    # 볼린저 밴드
    fig.add_trace(go.Scatter(
        x=chart_data.index,
        y=chart_data['BB_Upper'],
        line=dict(color='red', width=1),
        name='BB Upper'
    ))
    fig.add_trace(go.Scatter(
        x=chart_data.index,
        y=chart_data['BB_Lower'],
        line=dict(color='red', width=1),
        name='BB Lower',
        fill='tonexty',
        fillcolor='rgba(255,0,0,0.1)'
    ))
    
    # 이동평균선
    fig.add_trace(go.Scatter(
        x=chart_data.index,
        y=chart_data['SMA_20'],
        line=dict(color='blue', width=1),
        name='20일선'
    ))
    fig.add_trace(go.Scatter(
        x=chart_data.index,
        y=chart_data['SMA_50'],
        line=dict(color='orange', width=1),
        name='50일선'
    ))
    
    fig.update_layout(
        title=f"{symbol} 상세 차트",
        yaxis_title="Price",
        height=500,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 보조 지표들
    col1, col2 = st.columns(2)
    
    with col1:
        # RSI 차트
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(
            x=chart_data.index,
            y=chart_data['RSI'],
            line=dict(color='purple'),
            name='RSI'
        ))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
        fig_rsi.update_layout(
            title="RSI",
            yaxis_title="RSI",
            height=250
        )
        st.plotly_chart(fig_rsi, use_container_width=True)
    
    with col2:
        # MACD 차트
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(
            x=chart_data.index,
            y=chart_data['MACD'],
            line=dict(color='blue'),
            name='MACD'
        ))
        fig_macd.add_trace(go.Scatter(
            x=chart_data.index,
            y=chart_data['MACD_Signal'],
            line=dict(color='red'),
            name='Signal'
        ))
        fig_macd.update_layout(
            title="MACD",
            yaxis_title="MACD",
            height=250
        )
        st.plotly_chart(fig_macd, use_container_width=True)

def analyze_market(screener, market):
    """시장 분석"""
    stocks = screener.markets[market]
    
    with st.spinner(f"{market} 시장을 분석 중입니다..."):
        market_data = []
        
        for symbol in stocks[:10]:  # 처음 10개 종목만 분석
            data = screener.get_stock_data(symbol, "3mo")
            if data is not None:
                data = screener.calculate_technical_indicators(data)
                latest = data.iloc[-1]
                
                market_data.append({
                    'Symbol': symbol,
                    'RSI': latest['RSI'],
                    'Price_vs_BB': (latest['Close'] - latest['BB_Lower']) / (latest['BB_Upper'] - latest['BB_Lower']),
                    'Volume_Ratio': latest['Volume'] / latest['Volume_SMA'] if latest['Volume_SMA'] > 0 else 1,
                    'MA_Signal': 1 if latest['Close'] > latest['SMA_20'] else 0
                })
    
    if market_data:
        df = pd.DataFrame(market_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # RSI 분포
            fig_rsi = px.histogram(df, x='RSI', bins=20, title="RSI 분포")
            fig_rsi.add_vline(x=30, line_dash="dash", line_color="green")
            fig_rsi.add_vline(x=70, line_dash="dash", line_color="red")
            st.plotly_chart(fig_rsi, use_container_width=True)
        
        with col2:
            # 볼린저 밴드 위치 분포
            fig_bb = px.histogram(df, x='Price_vs_BB', bins=20, title="볼린저 밴드 내 위치 분포")
            st.plotly_chart(fig_bb, use_container_width=True)
        
        # 시장 요약
        st.subheader("시장 요약")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("과매도 종목", f"{len(df[df['RSI'] < 30])}/{len(df)}")
        with col2:
            st.metric("과매수 종목", f"{len(df[df['RSI'] > 70])}/{len(df)}")
        with col3:
            st.metric("20일선 상위", f"{df['MA_Signal'].sum()}/{len(df)}")
        with col4:
            st.metric("평균 거래량비", f"{df['Volume_Ratio'].mean():.1f}x")

if __name__ == "__main__":
    main() 