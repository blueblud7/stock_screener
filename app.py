import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import ta
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
from typing import List, Dict, Any
import time

# 페이지 설정
st.set_page_config(
    page_title="주식 스크리너 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 제목
st.title("📈 주식 기술적 분석 스크리너")
st.markdown("---")

class StockScreener:
    def __init__(self):
        self.markets = {
            "KOSPI": self.get_kospi_stocks(),
            "KOSDAQ": self.get_kosdaq_stocks(),
            "NASDAQ": self.get_nasdaq_stocks(),
            "S&P 500": self.get_sp500_stocks()
        }
    
    @st.cache_data(ttl=3600)
    def get_kospi_stocks(_self):
        """KOSPI 주요 종목들 (예시)"""
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
        ]
    
    @st.cache_data(ttl=3600)
    def get_kosdaq_stocks(_self):
        """KOSDAQ 주요 종목들 (예시)"""
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
        ]
    
    @st.cache_data(ttl=3600)
    def get_nasdaq_stocks(_self):
        """NASDAQ 주요 종목들"""
        return [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
            "META", "NVDA", "NFLX", "CRM", "ADBE",
            "ORCL", "INTC", "AMD", "QCOM", "CSCO"
        ]
    
    @st.cache_data(ttl=3600)
    def get_sp500_stocks(_self):
        """S&P 500 주요 종목들"""
        return [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
            "BRK-B", "UNH", "JNJ", "XOM", "JPM",
            "V", "PG", "MA", "HD", "CVX"
        ]
    
    def get_stock_data(self, symbol: str, period: str = "3mo") -> pd.DataFrame:
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
    
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """주식 기본 정보 가져오기"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return {
                'symbol': symbol,
                'name': info.get('longName', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'price': info.get('currentPrice', 0),
                'currency': info.get('currency', 'USD')
            }
        except Exception as e:
            return {
                'symbol': symbol,
                'name': 'N/A',
                'market_cap': 0,
                'pe_ratio': 'N/A',
                'price': 0,
                'currency': 'USD'
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
        
        # 거래량 관련
        data['Volume_SMA'] = ta.volume.volume_sma(data['Close'], data['Volume'], window=20)
        
        return data
    
    def check_conditions(self, data: pd.DataFrame, conditions: Dict) -> bool:
        """조건식 확인"""
        if data is None or data.empty or len(data) < 2:
            return False
            
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        results = []
        
        # 볼린저 밴드 조건
        if conditions.get('bb_breakout'):
            # 상단 밴드 돌파
            bb_signal = (prev['Close'] <= prev['BB_Upper']) and (latest['Close'] > latest['BB_Upper'])
            results.append(bb_signal)
        
        if conditions.get('bb_support'):
            # 하단 밴드 지지
            bb_support = (prev['Close'] <= prev['BB_Lower']) and (latest['Close'] > latest['BB_Lower'])
            results.append(bb_support)
        
        # RSI 조건
        if conditions.get('rsi_overbought'):
            rsi_signal = latest['RSI'] > conditions.get('rsi_threshold', 70)
            results.append(rsi_signal)
        
        if conditions.get('rsi_oversold'):
            rsi_signal = latest['RSI'] < conditions.get('rsi_threshold_low', 30)
            results.append(rsi_signal)
        
        if conditions.get('rsi_reversal'):
            # RSI 하락 전환
            rsi_reversal = (latest['RSI'] > 70) and (latest['RSI'] < prev['RSI'])
            results.append(rsi_reversal)
        
        # 이동평균 조건
        if conditions.get('sma_golden_cross'):
            # 골든 크로스 (20일선이 50일선 상향 돌파)
            golden_cross = (prev['SMA_20'] <= prev['SMA_50']) and (latest['SMA_20'] > latest['SMA_50'])
            results.append(golden_cross)
        
        if conditions.get('price_above_sma'):
            # 주가가 이동평균선 위에 있음
            above_sma = latest['Close'] > latest['SMA_20']
            results.append(above_sma)
        
        # 거래량 조건
        if conditions.get('volume_spike'):
            # 거래량 급증
            volume_spike = latest['Volume'] > latest['Volume_SMA'] * 1.5
            results.append(volume_spike)
        
        # 조건 조합 방식
        if conditions.get('condition_type') == 'AND':
            return all(results)
        else:  # OR
            return any(results) if results else False

def main():
    screener = StockScreener()
    
    # 사이드바
    st.sidebar.header("🔍 스크리닝 조건 설정")
    
    # 시장 선택
    selected_market = st.sidebar.selectbox(
        "시장 선택",
        ["KOSPI", "KOSDAQ", "NASDAQ", "S&P 500"]
    )
    
    # 조건 설정
    st.sidebar.subheader("기술적 지표 조건")
    
    conditions = {}
    
    # 볼린저 밴드 조건
    st.sidebar.markdown("**볼린저 밴드**")
    conditions['bb_breakout'] = st.sidebar.checkbox("상단 밴드 돌파")
    conditions['bb_support'] = st.sidebar.checkbox("하단 밴드 지지")
    
    # RSI 조건
    st.sidebar.markdown("**RSI**")
    conditions['rsi_overbought'] = st.sidebar.checkbox("RSI 과매수 (>70)")
    conditions['rsi_oversold'] = st.sidebar.checkbox("RSI 과매도 (<30)")
    conditions['rsi_reversal'] = st.sidebar.checkbox("RSI 고점 반전")
    
    if conditions['rsi_overbought']:
        conditions['rsi_threshold'] = st.sidebar.slider("RSI 과매수 임계값", 60, 90, 70)
    if conditions['rsi_oversold']:
        conditions['rsi_threshold_low'] = st.sidebar.slider("RSI 과매도 임계값", 10, 40, 30)
    
    # 이동평균 조건
    st.sidebar.markdown("**이동평균**")
    conditions['sma_golden_cross'] = st.sidebar.checkbox("골든크로스 (20일선 > 50일선)")
    conditions['price_above_sma'] = st.sidebar.checkbox("주가 > 20일 이동평균")
    
    # 거래량 조건
    st.sidebar.markdown("**거래량**")
    conditions['volume_spike'] = st.sidebar.checkbox("거래량 급증 (1.5배 이상)")
    
    # 조건 조합 방식
    conditions['condition_type'] = st.sidebar.radio(
        "조건 조합 방식",
        ["AND (모든 조건 만족)", "OR (하나라도 만족)"]
    )
    conditions['condition_type'] = "AND" if "AND" in conditions['condition_type'] else "OR"
    
    # 스크리닝 실행
    if st.sidebar.button("🔍 스크리닝 실행", type="primary"):
        stocks = screener.markets[selected_market]
        
        with st.spinner("주식 데이터를 분석 중입니다..."):
            results = []
            progress_bar = st.progress(0)
            
            for i, symbol in enumerate(stocks):
                data = screener.get_stock_data(symbol)
                if data is not None:
                    data_with_indicators = screener.calculate_technical_indicators(data)
                    if screener.check_conditions(data_with_indicators, conditions):
                        stock_info = screener.get_stock_info(symbol)
                        latest_data = data_with_indicators.iloc[-1]
                        
                        results.append({
                            '티커': symbol,
                            '종목명': stock_info['name'],
                            '현재가': f"{latest_data['Close']:.2f}",
                            '시가총액': f"{stock_info['market_cap']:,}" if stock_info['market_cap'] else "N/A",
                            'PER': stock_info['pe_ratio'],
                            'RSI': f"{latest_data['RSI']:.2f}",
                            '볼린저밴드': f"{latest_data['Close']:.2f} / {latest_data['BB_Upper']:.2f}",
                            '거래량': f"{latest_data['Volume']:,}",
                        })
                
                progress_bar.progress((i + 1) / len(stocks))
                time.sleep(0.1)  # API 제한 방지
        
        # 결과 표시
        st.subheader(f"📊 {selected_market} 스크리닝 결과")
        
        if results:
            df_results = pd.DataFrame(results)
            st.dataframe(df_results, use_container_width=True)
            
            # 상세 차트
            st.subheader("📈 선택된 종목 상세 차트")
            selected_stock = st.selectbox("차트를 볼 종목 선택", [r['티커'] for r in results])
            
            if selected_stock:
                chart_data = screener.get_stock_data(selected_stock, "6mo")
                chart_data = screener.calculate_technical_indicators(chart_data)
                
                fig = go.Figure()
                
                # 캔들스틱 차트
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
                    fill='tonexty'
                ))
                
                # 이동평균
                fig.add_trace(go.Scatter(
                    x=chart_data.index,
                    y=chart_data['SMA_20'],
                    line=dict(color='blue', width=1),
                    name='SMA 20'
                ))
                
                fig.update_layout(
                    title=f"{selected_stock} 차트",
                    yaxis_title="Price",
                    height=600
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
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
                    title="RSI 지표",
                    yaxis_title="RSI",
                    height=300
                )
                st.plotly_chart(fig_rsi, use_container_width=True)
                
        else:
            st.info("설정한 조건에 맞는 종목이 없습니다.")
    
    # 사용법 안내
    with st.expander("📖 사용법 안내"):
        st.markdown("""
        ### 주요 기능
        
        1. **시장 선택**: KOSPI, KOSDAQ, NASDAQ, S&P 500 중 선택
        2. **조건 설정**: 다양한 기술적 지표 조건을 조합
        3. **실시간 스크리닝**: 설정한 조건에 맞는 종목들을 실시간으로 필터링
        4. **상세 차트**: 선택된 종목의 상세 기술적 분석 차트 제공
        
        ### 지원 지표
        
        - **볼린저 밴드**: 상단/하단 밴드 돌파 및 지지
        - **RSI**: 과매수/과매도 구간 및 반전 신호
        - **이동평균**: 골든크로스, 주가와 이동평균 관계
        - **거래량**: 평균 대비 거래량 급증
        
        ### 조건 조합
        
        - **AND**: 모든 선택된 조건을 만족하는 종목
        - **OR**: 선택된 조건 중 하나라도 만족하는 종목
        """)

if __name__ == "__main__":
    main() 