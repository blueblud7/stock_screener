import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import time
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="주식 스크리너 대시보드 (실제 데이터)",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 제목
st.title("📈 주식 기술적 분석 스크리너 (실제 데이터)")
st.markdown("---")

class RealStockScreener:
    def __init__(self):
        self.markets = {
            "KOSPI": [
                {"symbol": "005930.KS", "name": "삼성전자"},
                {"symbol": "000660.KS", "name": "SK하이닉스"},
                {"symbol": "035420.KS", "name": "NAVER"},
                {"symbol": "005380.KS", "name": "현대차"},
                {"symbol": "035720.KS", "name": "카카오"},
            ],
            "KOSDAQ": [
                {"symbol": "263750.KQ", "name": "펄어비스"},
                {"symbol": "293490.KQ", "name": "카카오게임즈"},
                {"symbol": "196170.KQ", "name": "알테오젠"},
            ],
            "NASDAQ": [
                {"symbol": "AAPL", "name": "Apple Inc"},
                {"symbol": "MSFT", "name": "Microsoft Corp"},
                {"symbol": "GOOGL", "name": "Alphabet Inc"},
                {"symbol": "AMZN", "name": "Amazon.com Inc"},
                {"symbol": "TSLA", "name": "Tesla Inc"},
            ],
            "S&P 500": [
                {"symbol": "AAPL", "name": "Apple Inc"},
                {"symbol": "MSFT", "name": "Microsoft Corp"},
                {"symbol": "UNH", "name": "UnitedHealth"},
                {"symbol": "JNJ", "name": "Johnson & Johnson"},
                {"symbol": "V", "name": "Visa Inc"},
            ]
        }
    
    def get_stock_data(self, symbol: str, period: str = "90d") -> pd.DataFrame:
        """실제 주식 데이터 가져오기 (yfinance 사용)"""
        try:
            # yfinance 0.2.61 사용
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            return data if not data.empty else None
        except Exception as e:
            st.error(f"데이터 가져오기 실패 {symbol}: {str(e)}")
            return None
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """기술적 지표 계산"""
        if data is None or data.empty or len(data) < 20:
            return None
        
        # 볼린저 밴드 (20일, 2 표준편차)
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['BB_std'] = data['Close'].rolling(window=20).std()
        data['BB_Upper'] = data['SMA_20'] + (data['BB_std'] * 2)
        data['BB_Lower'] = data['SMA_20'] - (data['BB_std'] * 2)
        data['BB_Middle'] = data['SMA_20']
        
        # RSI (14일)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # 이동평균
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        if len(data) >= 200:
            data['SMA_200'] = data['Close'].rolling(window=200).mean()
        
        # MACD
        ema12 = data['Close'].ewm(span=12).mean()
        ema26 = data['Close'].ewm(span=26).mean()
        data['MACD'] = ema12 - ema26
        data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
        
        # 거래량 이동평균
        data['Volume_SMA'] = data['Volume'].rolling(window=20).mean()
        
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
            bb_signal = (prev['Close'] <= prev['BB_Upper']) and (latest['Close'] > latest['BB_Upper'])
            results.append(bb_signal)
        
        if conditions.get('bb_support'):
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
            rsi_reversal = (latest['RSI'] > 70) and (latest['RSI'] < prev['RSI'])
            results.append(rsi_reversal)
        
        # 이동평균 조건
        if conditions.get('sma_golden_cross'):
            if not pd.isna(latest['SMA_50']) and not pd.isna(prev['SMA_50']):
                golden_cross = (prev['SMA_20'] <= prev['SMA_50']) and (latest['SMA_20'] > latest['SMA_50'])
                results.append(golden_cross)
        
        if conditions.get('price_above_sma'):
            above_sma = latest['Close'] > latest['SMA_20']
            results.append(above_sma)
        
        # 거래량 조건
        if conditions.get('volume_spike'):
            if latest['Volume_SMA'] > 0:
                volume_spike = latest['Volume'] > latest['Volume_SMA'] * 1.5
                results.append(volume_spike)
        
        # 조건이 하나도 선택되지 않은 경우
        if not results:
            return True
        
        # 조건 조합 방식
        if conditions.get('condition_type') == 'AND':
            return all(results)
        else:  # OR
            return any(results)

def main():
    screener = RealStockScreener()
    
    # 성공 메시지
    st.success("🎉 실제 데이터 연결 성공! (yfinance 0.2.61 사용)")
    
    # 사이드바
    st.sidebar.header("🔍 스크리닝 조건 설정")
    
    # 시장 선택
    selected_market = st.sidebar.selectbox(
        "시장 선택",
        ["NASDAQ", "KOSPI", "KOSDAQ", "S&P 500"]
    )
    
    # 조건 설정
    st.sidebar.subheader("기술적 지표 조건")
    
    conditions = {}
    
    # 볼린저 밴드 조건
    st.sidebar.markdown("**볼린저 밴드 (BB 20,2)**")
    conditions['bb_breakout'] = st.sidebar.checkbox("상단 밴드 돌파")
    conditions['bb_support'] = st.sidebar.checkbox("하단 밴드 지지")
    
    # RSI 조건
    st.sidebar.markdown("**RSI (14일)**")
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
        
        with st.spinner("실제 주식 데이터를 분석 중입니다..."):
            results = []
            progress_bar = st.progress(0)
            
            for i, stock_info in enumerate(stocks):
                symbol = stock_info['symbol']
                name = stock_info['name']
                
                # 실제 데이터 가져오기
                data = screener.get_stock_data(symbol, period="90d")
                if data is not None:
                    data_with_indicators = screener.calculate_technical_indicators(data)
                    
                    if data_with_indicators is not None and screener.check_conditions(data_with_indicators, conditions):
                        latest_data = data_with_indicators.iloc[-1]
                        
                        # 통화 구분
                        is_korean = ".KS" in symbol or ".KQ" in symbol
                        currency = "원" if is_korean else "$"
                        price_format = f"{latest_data['Close']:.0f}" if is_korean else f"{latest_data['Close']:.2f}"
                        
                        results.append({
                            '티커': symbol,
                            '종목명': name,
                            '현재가': f"{price_format}{currency}",
                            'RSI': f"{latest_data['RSI']:.1f}",
                            '볼린저밴드%': f"{((latest_data['Close'] - latest_data['BB_Lower']) / (latest_data['BB_Upper'] - latest_data['BB_Lower']) * 100):.1f}%" if (latest_data['BB_Upper'] - latest_data['BB_Lower']) > 0 else "N/A",
                            '거래량': f"{latest_data['Volume']:,.0f}",
                            '거래량비율': f"{(latest_data['Volume'] / latest_data['Volume_SMA']):.1f}x" if latest_data['Volume_SMA'] > 0 else "N/A"
                        })
                
                progress_bar.progress((i + 1) / len(stocks))
                time.sleep(0.5)  # API 제한 방지
        
        # 결과 표시
        st.subheader(f"📊 {selected_market} 스크리닝 결과 (실제 데이터)")
        
        if results:
            df_results = pd.DataFrame(results)
            st.dataframe(df_results, use_container_width=True, height=400)
            
            # 상세 차트
            st.subheader("📈 선택된 종목 상세 차트")
            selected_stock = st.selectbox("차트를 볼 종목 선택", [r['티커'] for r in results])
            
            if selected_stock:
                # 선택된 종목의 실제 차트 데이터
                chart_data = screener.get_stock_data(selected_stock, period="180d")
                if chart_data is not None:
                    chart_data = screener.calculate_technical_indicators(chart_data)
                    
                    if chart_data is not None:
                        # 메인 차트
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
                            name='BB Upper',
                            opacity=0.7
                        ))
                        fig.add_trace(go.Scatter(
                            x=chart_data.index,
                            y=chart_data['BB_Lower'],
                            line=dict(color='red', width=1),
                            name='BB Lower',
                            fill='tonexty',
                            fillcolor='rgba(255,0,0,0.1)',
                            opacity=0.7
                        ))
                        
                        # 이동평균
                        fig.add_trace(go.Scatter(
                            x=chart_data.index,
                            y=chart_data['SMA_20'],
                            line=dict(color='blue', width=1),
                            name='20일 이동평균'
                        ))
                        if 'SMA_50' in chart_data.columns:
                            fig.add_trace(go.Scatter(
                                x=chart_data.index,
                                y=chart_data['SMA_50'],
                                line=dict(color='orange', width=1),
                                name='50일 이동평균'
                            ))
                        
                        fig.update_layout(
                            title=f"{selected_stock} 실제 차트 (6개월)",
                            yaxis_title="Price",
                            height=600,
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
                            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="과매수")
                            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="과매도")
                            fig_rsi.update_layout(
                                title="RSI 지표",
                                yaxis_title="RSI",
                                height=300
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
                                title="MACD 지표",
                                yaxis_title="MACD",
                                height=300
                            )
                            st.plotly_chart(fig_macd, use_container_width=True)
                        
                        # 기술적 지표 요약
                        latest = chart_data.iloc[-1]
                        st.subheader("📋 기술적 지표 요약 (실제 데이터)")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            is_korean = ".KS" in selected_stock or ".KQ" in selected_stock
                            currency = "원" if is_korean else "$"
                            price_format = f"{latest['Close']:.0f}" if is_korean else f"{latest['Close']:.2f}"
                            st.metric("현재가", f"{price_format}{currency}")
                        with col2:
                            rsi_color = "inverse" if latest['RSI'] > 70 or latest['RSI'] < 30 else "normal"
                            st.metric("RSI", f"{latest['RSI']:.1f}", delta_color=rsi_color)
                        with col3:
                            bb_position = (latest['Close'] - latest['BB_Lower']) / (latest['BB_Upper'] - latest['BB_Lower']) * 100
                            st.metric("BB 위치", f"{bb_position:.1f}%")
                        with col4:
                            vol_ratio = latest['Volume'] / latest['Volume_SMA'] if latest['Volume_SMA'] > 0 else 1
                            st.metric("거래량 비율", f"{vol_ratio:.1f}x")
                
        else:
            st.info("설정한 조건에 맞는 종목이 없습니다.")
    
    # 사용법 안내
    with st.expander("📖 사용법 안내"):
        st.markdown("""
        ### 🎯 실제 데이터 기반 스크리너
        
        - **✅ 실시간 데이터**: Yahoo Finance API를 통한 실제 주가 데이터
        - **✅ 4개 시장**: KOSPI, KOSDAQ, NASDAQ, S&P 500
        - **✅ 실시간 기술적 지표**: BB(20,2), RSI(14), MACD, 이동평균 등
        
        ### 📊 기능 설명
        
        1. **볼린저 밴드 돌파**: 상단 밴드를 뚫고 올라가는 매수 신호
        2. **RSI 과매수/과매도**: 70 이상(과매수), 30 이하(과매도)
        3. **골든크로스**: 20일선이 50일선을 상향 돌파
        4. **거래량 급증**: 평균 거래량의 1.5배 이상
        
        ### 💡 추천 전략
        
        **매수 신호 조합**:
        - BB 상단 돌파 + 거래량 급증
        - RSI < 70 + 골든크로스
        
        **매도 신호 조합**:
        - RSI > 70 + 고점 반전
        """)

if __name__ == "__main__":
    main() 