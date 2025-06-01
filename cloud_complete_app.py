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
@st.cache_data(ttl=300, show_spinner=False)  # 캐시 시간 단축
def load_complete_stock_lists():
    """완전한 종목 리스트를 로드합니다."""
    
    # 강제 캐시 클리어 체크
    if st.sidebar.button("🔄 캐시 클리어 & 새로고침"):
        st.cache_data.clear()
        st.rerun()
    
    # GitHub에서 JSON 파일 읽기 시도
    json_file = "complete_stock_lists.json"
    
    # 상세한 파일 시스템 디버깅
    st.subheader("🔍 파일 시스템 디버깅")
    
    # 현재 작업 디렉토리 확인
    current_dir = os.getcwd()
    st.write(f"📂 현재 작업 디렉토리: {current_dir}")
    
    # 디렉토리 내 모든 파일 목록
    try:
        all_files = os.listdir('.')
        st.write(f"📄 전체 파일 목록: {all_files}")
        
        json_files = [f for f in all_files if f.endswith('.json')]
        st.write(f"📊 JSON 파일들: {json_files}")
    except Exception as e:
        st.error(f"디렉토리 읽기 실패: {str(e)}")
    
    # 파일 존재 여부 및 상세 정보
    file_exists = os.path.exists(json_file)
    st.write(f"📁 {json_file} 존재 여부: {file_exists}")
    
    if file_exists:
        try:
            file_size = os.path.getsize(json_file)
            st.write(f"📏 파일 크기: {file_size:,} bytes")
            
            # 파일 읽기 권한 확인
            readable = os.access(json_file, os.R_OK)
            st.write(f"📖 읽기 권한: {readable}")
            
            # 파일 수정 시간
            import datetime
            mtime = os.path.getmtime(json_file)
            mtime_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            st.write(f"🕒 파일 수정 시간: {mtime_str}")
            
        except Exception as e:
            st.error(f"파일 정보 확인 실패: {str(e)}")
    
    # 파일 존재 여부 확인
    if not file_exists:
        st.error(f"❌ {json_file} 파일을 찾을 수 없습니다!")
        
        # 기본 샘플 데이터 사용
        st.warning("⚠️ 기본 샘플 종목 리스트를 사용합니다.")
        return get_fallback_stock_lists()
    
    # 파일 로딩 시도
    st.info(f"🔄 {json_file} 파일 로딩 중...")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            st.write("📖 파일 열기 성공")
            
            # 파일 일부 미리보기
            f.seek(0)
            preview = f.read(200)
            st.write(f"📄 파일 미리보기 (첫 200자):")
            st.code(preview)
            
            # 파일 전체 읽기
            f.seek(0)
            content = f.read()
            st.write(f"📐 전체 파일 크기: {len(content)} 문자")
            
            # JSON 파싱
            f.seek(0)
            stock_lists = json.load(f)
            st.write("✅ JSON 파싱 성공")
        
        # 데이터 유효성 검사
        st.write(f"📊 로드된 데이터 타입: {type(stock_lists)}")
        
        if isinstance(stock_lists, dict):
            st.write(f"📈 시장 개수: {len(stock_lists)}")
            st.write(f"🏢 시장 목록: {list(stock_lists.keys())}")
            
            # 각 시장별 종목 수 미리보기
            for market, stocks in stock_lists.items():
                if isinstance(stocks, dict):
                    st.write(f"🔍 {market}: {len(stocks)}개 종목")
                    # 첫 3개 종목 예시
                    sample_stocks = list(stocks.items())[:3]
                    st.write(f"   예시: {sample_stocks}")
                else:
                    st.error(f"❌ {market} 데이터가 딕셔너리가 아님: {type(stocks)}")
            
            if all(isinstance(v, dict) for v in stock_lists.values()):
                total_stocks = sum(len(stocks) for stocks in stock_lists.values())
                st.success(f"✅ 완전한 종목 리스트 로딩 완료! (총 {total_stocks}개 종목)")
                
                # 각 시장별 종목 수 표시
                st.info("📊 시장별 종목 수:")
                for market, stocks in stock_lists.items():
                    st.write(f"- {market}: {len(stocks)}개")
                
                # 캐시 정보 표시
                st.success("🎯 이 데이터는 정상적으로 로드되었습니다!")
                
                return stock_lists
            else:
                st.error("❌ 일부 시장 데이터가 딕셔너리 형태가 아닙니다.")
        else:
            st.error(f"❌ 루트 데이터가 딕셔너리가 아닙니다: {type(stock_lists)}")
    
    except json.JSONDecodeError as e:
        st.error(f"❌ JSON 파싱 오류: {str(e)}")
        st.error(f"오류 위치: line {e.lineno}, column {e.colno}")
    except UnicodeDecodeError as e:
        st.error(f"❌ 인코딩 오류: {str(e)}")
    except Exception as e:
        st.error(f"❌ 파일 로딩 실패: {str(e)}")
        st.error(f"오류 타입: {type(e).__name__}")
        import traceback
        st.error(f"상세 오류: {traceback.format_exc()}")
    
    # 실패 시 기본 데이터 사용
    st.warning("⚠️ 기본 샘플 종목 리스트를 사용합니다.")
    return get_fallback_stock_lists()

def get_fallback_stock_lists():
    """기본 샘플 종목 리스트 (완전한 버전이 로드되지 않을 때)"""
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
    
    # 상세한 디버깅 정보
    st.info(f"🔍 **DEBUG**: stocks 타입: {type(stocks)}, 길이: {len(stocks) if hasattr(stocks, '__len__') else 'N/A'}")
    
    # 더 엄격한 입력 유효성 검사
    if stocks is None:
        st.error("❌ 종목 데이터가 None입니다.")
        return []
    
    if not isinstance(stocks, dict):
        st.error(f"❌ 종목 데이터 타입 오류: {type(stocks).__name__} (예상: dict)")
        st.error(f"실제 데이터: {str(stocks)[:200]}...")
        return []
    
    if not stocks:
        st.warning("⚠️ 선택된 시장에 종목이 없습니다.")
        return []
    
    # hasattr으로 안전하게 확인
    if not hasattr(stocks, 'items'):
        st.error(f"❌ stocks 객체에 items() 메소드가 없습니다. 타입: {type(stocks)}")
        return []
    
    results = []
    total_stocks = len(stocks)
    processed = 0
    
    st.info(f"📊 총 {total_stocks}개 종목 스크리닝 시작...")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # 더 안전한 items() 호출
        try:
            stock_items = list(stocks.items())
            st.success(f"✅ 종목 리스트 변환 성공: {len(stock_items)}개")
        except Exception as items_error:
            st.error(f"❌ stocks.items() 호출 실패: {str(items_error)}")
            st.error(f"stocks 내용 샘플: {list(stocks.keys())[:5] if hasattr(stocks, 'keys') else 'N/A'}")
            return []
        
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
                        
                except Exception as stock_error:
                    # 개별 종목 에러는 무시하고 계속 진행
                    continue
            
            # 배치 완료 후 잠시 대기 (메모리 정리)
            time.sleep(0.1)
    
    except Exception as e:
        st.error(f"❌ 스크리닝 중 전체 오류 발생: {str(e)}")
        st.error(f"에러 타입: {type(e).__name__}")
        import traceback
        st.error(f"상세 에러: {traceback.format_exc()}")
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
    st.markdown("**완전한 버전 - 최대 851개 종목 지원 (Streamlit Cloud)**")
    
    # 중요 공지
    st.markdown("""
    <div style="background-color: #e6f3ff; padding: 10px; border-radius: 5px; border-left: 5px solid #0066cc;">
    <strong>📢 중요:</strong> 이 앱은 <strong>851개 전체 종목</strong>을 지원합니다!<br>
    • S&P 500: 503개 | NASDAQ: 154개 | KOSPI: 110개 | KOSDAQ: 84개<br>
    • complete_stock_lists.json 파일이 정상 로드되면 전체 종목을 사용할 수 있습니다.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 사이드바
    st.sidebar.title("📊 설정")
    
    # 종목 리스트 로드
    with st.spinner("종목 리스트 로딩 중..."):
        stock_lists = load_complete_stock_lists()
    
    # 더 상세한 데이터 유효성 검사
    st.sidebar.markdown("### 🔍 시스템 상태")
    if not isinstance(stock_lists, dict):
        st.sidebar.error(f"❌ 로드된 데이터 타입: {type(stock_lists)}")
        st.error("❌ 종목 리스트 로딩에 실패했습니다. 페이지를 새로고침해주세요.")
        st.stop()
    
    if not stock_lists:
        st.sidebar.error("❌ 빈 종목 리스트")
        st.error("❌ 종목 리스트가 비어있습니다. 페이지를 새로고침해주세요.")
        st.stop()
    
    st.sidebar.success("✅ 종목 리스트 정상 로드")
    
    # 시장 선택
    market = st.sidebar.selectbox(
        "📈 시장 선택",
        options=list(stock_lists.keys()),
        index=0
    )
    
    # 선택된 시장의 종목 가져오기 (더 안전하게)
    try:
        selected_stocks = stock_lists.get(market, {})
        st.sidebar.info(f"✅ {market} 데이터 타입: {type(selected_stocks)}")
    except Exception as e:
        st.sidebar.error(f"❌ 시장 데이터 로드 실패: {str(e)}")
        st.error(f"❌ {market} 시장 데이터를 가져올 수 없습니다.")
        st.stop()
    
    if not selected_stocks:
        st.error(f"❌ {market} 시장에 종목이 없습니다.")
        st.stop()
    
    if not isinstance(selected_stocks, dict):
        st.error(f"❌ {market} 시장 데이터 타입 오류: {type(selected_stocks)}")
        st.stop()
    
    st.sidebar.write(f"선택된 시장: **{market}** ({len(selected_stocks)}개 종목)")
    
    # 디버깅 정보 (항상 표시)
    with st.sidebar.expander("🔍 디버그 정보", expanded=True):
        st.write(f"**종목 리스트 타입**: {type(selected_stocks)}")
        st.write(f"**종목 수**: {len(selected_stocks) if isinstance(selected_stocks, dict) else 'N/A'}")
        st.write(f"**hasattr items**: {hasattr(selected_stocks, 'items')}")
        if isinstance(selected_stocks, dict) and selected_stocks:
            first_item = list(selected_stocks.items())[0]
            st.write(f"**첫 번째 종목**: {first_item}")
    
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