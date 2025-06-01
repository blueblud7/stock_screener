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
import json
import os
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="완전한 주식 스크리너 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 제목
st.title("📈 완전한 주식 기술적 분석 스크리너")
st.markdown("---")

class CompleteStockScreener:
    def __init__(self):
        self.load_complete_stock_lists()
        
    def load_complete_stock_lists(self):
        """완전한 주식 리스트 로드"""
        try:
            if os.path.exists('complete_stock_lists.json'):
                with open('complete_stock_lists.json', 'r', encoding='utf-8') as f:
                    self.markets = json.load(f)
                st.success(f"✅ 총 {sum(len(stocks) for stocks in self.markets.values())}개 종목 로드 완료!")
            else:
                st.error("❌ complete_stock_lists.json 파일이 없습니다. python complete_stock_lists.py를 먼저 실행해주세요.")
                self.markets = {}
        except Exception as e:
            st.error(f"❌ 종목 리스트 로드 오류: {e}")
            self.markets = {}
    
    def get_stock_data(self, symbol: str, period: str = "3mo") -> pd.DataFrame:
        """주식 데이터 가져오기"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            if data.empty:
                return None
            return data
        except Exception as e:
            st.warning(f"데이터 로드 실패 - {symbol}: {str(e)}")
            return None
    
    def calculate_bollinger_bands(self, data: pd.DataFrame, window: int = 20, std_dev: int = 2) -> Dict:
        """볼린저 밴드 계산"""
        sma = data['Close'].rolling(window=window).mean()
        std = data['Close'].rolling(window=window).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            'sma': sma,
            'upper': upper_band,
            'lower': lower_band,
            'current_price': data['Close'].iloc[-1],
            'upper_current': upper_band.iloc[-1],
            'lower_current': lower_band.iloc[-1]
        }
    
    def calculate_rsi(self, data: pd.DataFrame, window: int = 14) -> pd.Series:
        """RSI 계산"""
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, data: pd.DataFrame) -> Dict:
        """MACD 계산"""
        exp1 = data['Close'].ewm(span=12).mean()
        exp2 = data['Close'].ewm(span=26).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=9).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def calculate_moving_averages(self, data: pd.DataFrame) -> Dict:
        """이동평균 계산"""
        return {
            'ma5': data['Close'].rolling(window=5).mean(),
            'ma20': data['Close'].rolling(window=20).mean(),
            'ma60': data['Close'].rolling(window=60).mean()
        }
    
    def analyze_stock(self, symbol: str, stock_info: Dict) -> Dict:
        """개별 주식 분석"""
        data = self.get_stock_data(symbol)
        if data is None or len(data) < 60:
            return None
        
        # 기술적 지표 계산
        bb = self.calculate_bollinger_bands(data)
        rsi = self.calculate_rsi(data)
        macd = self.calculate_macd(data)
        ma = self.calculate_moving_averages(data)
        
        # 조건 분석
        current_price = data['Close'].iloc[-1]
        current_rsi = rsi.iloc[-1]
        volume_avg = data['Volume'].rolling(window=20).mean().iloc[-1]
        current_volume = data['Volume'].iloc[-1]
        
        # BB 상단 돌파 조건
        bb_breakout = current_price > bb['upper_current']
        
        # RSI 과매수 조건
        rsi_overbought = current_rsi > 70
        
        # 거래량 증가 조건
        volume_surge = current_volume > volume_avg * 1.5
        
        # 상승 추세 조건
        uptrend = (current_price > ma['ma5'].iloc[-1] and 
                  ma['ma5'].iloc[-1] > ma['ma20'].iloc[-1])
        
        return {
            'symbol': symbol,
            'name': stock_info.get('name', symbol),
            'sector': stock_info.get('sector', 'Unknown'),
            'current_price': current_price,
            'rsi': current_rsi,
            'bb_upper': bb['upper_current'],
            'bb_lower': bb['lower_current'],
            'volume_ratio': current_volume / volume_avg if volume_avg > 0 else 0,
            'macd_signal': macd['macd'].iloc[-1] - macd['signal'].iloc[-1],
            
            # 조건 만족 여부
            'bb_breakout': bb_breakout,
            'rsi_overbought': rsi_overbought,
            'volume_surge': volume_surge,
            'uptrend': uptrend,
            
            # 종합 점수
            'score': sum([bb_breakout, rsi_overbought, volume_surge, uptrend])
        }
    
    def screen_stocks(self, selected_markets: List[str], conditions: Dict) -> pd.DataFrame:
        """주식 스크리닝"""
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_stocks = sum(len(self.markets.get(market, [])) for market in selected_markets)
        current_count = 0
        
        for market in selected_markets:
            if market not in self.markets:
                continue
                
            st.write(f"### 🔍 {market} 분석 중...")
            
            for stock in self.markets[market]:
                current_count += 1
                progress = current_count / total_stocks
                progress_bar.progress(progress)
                status_text.text(f"분석 중: {stock['symbol']} ({current_count}/{total_stocks})")
                
                analysis = self.analyze_stock(stock['symbol'], stock)
                if analysis:
                    # 조건 필터링
                    if self.meets_conditions(analysis, conditions):
                        results.append(analysis)
                
                # API 제한 방지
                time.sleep(0.1)
        
        progress_bar.empty()
        status_text.empty()
        
        if results:
            df = pd.DataFrame(results)
            df = df.sort_values('score', ascending=False)
            return df
        else:
            return pd.DataFrame()
    
    def meets_conditions(self, analysis: Dict, conditions: Dict) -> bool:
        """조건 만족 여부 확인"""
        if conditions['bb_breakout'] and not analysis['bb_breakout']:
            return False
        if conditions['rsi_filter'] and not (conditions['rsi_min'] <= analysis['rsi'] <= conditions['rsi_max']):
            return False
        if conditions['volume_surge'] and not analysis['volume_surge']:
            return False
        if conditions['uptrend'] and not analysis['uptrend']:
            return False
        return True
    
    def create_chart(self, symbol: str) -> go.Figure:
        """주식 차트 생성"""
        data = self.get_stock_data(symbol, "6mo")
        if data is None:
            return None
        
        # 기술적 지표 계산
        bb = self.calculate_bollinger_bands(data)
        rsi = self.calculate_rsi(data)
        ma = self.calculate_moving_averages(data)
        
        # 서브플롯 생성
        from plotly.subplots import make_subplots
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=[f'{symbol} 주가 차트', 'RSI'],
            row_heights=[0.7, 0.3]
        )
        
        # 캔들스틱 차트
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="주가"
            ),
            row=1, col=1
        )
        
        # 볼린저 밴드
        fig.add_trace(
            go.Scatter(x=data.index, y=bb['upper'], name="BB 상단", line=dict(color='red', dash='dash')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=data.index, y=bb['sma'], name="BB 중간", line=dict(color='blue')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=data.index, y=bb['lower'], name="BB 하단", line=dict(color='red', dash='dash')),
            row=1, col=1
        )
        
        # 이동평균
        fig.add_trace(
            go.Scatter(x=data.index, y=ma['ma20'], name="MA20", line=dict(color='orange')),
            row=1, col=1
        )
        
        # RSI
        fig.add_trace(
            go.Scatter(x=data.index, y=rsi, name="RSI", line=dict(color='purple')),
            row=2, col=1
        )
        
        # RSI 기준선
        fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="과매수(70)", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="과매도(30)", row=2, col=1)
        
        fig.update_layout(
            title=f"{symbol} 기술적 분석",
            xaxis_title="날짜",
            height=600,
            showlegend=True
        )
        
        return fig

def main():
    screener = CompleteStockScreener()
    
    if not screener.markets:
        st.stop()
    
    # 사이드바 설정
    st.sidebar.header("🔧 스크리닝 설정")
    
    # 시장 선택
    available_markets = list(screener.markets.keys())
    selected_markets = st.sidebar.multiselect(
        "시장 선택",
        available_markets,
        default=available_markets
    )
    
    # 시장별 종목 수 표시
    st.sidebar.markdown("### 📊 시장별 종목 수")
    for market in available_markets:
        count = len(screener.markets[market])
        st.sidebar.write(f"**{market}**: {count}개")
    
    st.sidebar.markdown("---")
    
    # 조건 설정
    st.sidebar.header("📋 스크리닝 조건")
    
    conditions = {
        'bb_breakout': st.sidebar.checkbox("📈 볼린저 밴드 상단 돌파", value=True),
        'rsi_filter': st.sidebar.checkbox("🎯 RSI 범위 필터"),
        'volume_surge': st.sidebar.checkbox("📊 거래량 급증 (1.5배)", value=False),
        'uptrend': st.sidebar.checkbox("⬆️ 상승 추세", value=False)
    }
    
    if conditions['rsi_filter']:
        rsi_range = st.sidebar.slider("RSI 범위", 0, 100, (30, 70))
        conditions['rsi_min'] = rsi_range[0]
        conditions['rsi_max'] = rsi_range[1]
    else:
        conditions['rsi_min'] = 0
        conditions['rsi_max'] = 100
    
    # 스크리닝 실행
    if st.sidebar.button("🚀 스크리닝 시작", type="primary"):
        if selected_markets:
            with st.spinner("주식 분석 중... 잠시만 기다려주세요."):
                results_df = screener.screen_stocks(selected_markets, conditions)
            
            if not results_df.empty:
                st.success(f"✅ {len(results_df)}개 종목이 조건을 만족합니다!")
                
                # 결과 표시
                st.header("🎯 스크리닝 결과")
                
                # 상위 종목들
                display_cols = ['symbol', 'name', 'sector', 'current_price', 'rsi', 'volume_ratio', 'score']
                col_names = ['심볼', '종목명', '섹터', '현재가', 'RSI', '거래량비율', '점수']
                
                display_df = results_df[display_cols].copy()
                display_df.columns = col_names
                
                # 숫자 포맷팅
                display_df['현재가'] = display_df['현재가'].round(2)
                display_df['RSI'] = display_df['RSI'].round(1)
                display_df['거래량비율'] = display_df['거래량비율'].round(2)
                
                st.dataframe(display_df, use_container_width=True)
                
                # 상세 분석
                st.header("📊 상세 분석")
                selected_symbol = st.selectbox(
                    "분석할 종목 선택",
                    results_df['symbol'].tolist()
                )
                
                if selected_symbol:
                    chart = screener.create_chart(selected_symbol)
                    if chart:
                        st.plotly_chart(chart, use_container_width=True)
                    
                    # 종목 정보
                    stock_info = results_df[results_df['symbol'] == selected_symbol].iloc[0]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("현재가", f"{stock_info['current_price']:.2f}")
                    with col2:
                        st.metric("RSI", f"{stock_info['rsi']:.1f}")
                    with col3:
                        st.metric("거래량 비율", f"{stock_info['volume_ratio']:.2f}x")
                    
                    # 조건 만족 상태
                    st.subheader("조건 만족 상태")
                    conditions_status = {
                        "볼린저 밴드 돌파": stock_info['bb_breakout'],
                        "RSI 과매수": stock_info['rsi_overbought'], 
                        "거래량 급증": stock_info['volume_surge'],
                        "상승 추세": stock_info['uptrend']
                    }
                    
                    for condition, status in conditions_status.items():
                        st.write(f"{'✅' if status else '❌'} {condition}")
                
            else:
                st.warning("😅 조건을 만족하는 종목이 없습니다. 조건을 조정해보세요.")
        else:
            st.warning("⚠️ 최소 하나의 시장을 선택해주세요.")
    
    # 정보 표시
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ 도움말")
    st.sidebar.markdown("""
    **볼린저 밴드 돌파**: 주가가 상단 밴드를 돌파한 상태
    
    **RSI**: 상대강도지수 (0-100)
    - 70 이상: 과매수
    - 30 이하: 과매도
    
    **거래량 급증**: 평균 거래량의 1.5배 이상
    
    **상승 추세**: MA5 > MA20 상태
    """)

if __name__ == "__main__":
    main() 