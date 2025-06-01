import yfinance as yf
import time
import requests
from datetime import datetime, timedelta

print("=== yfinance 0.2.61 테스트 ===")
print(f"yfinance 버전: {yf.__version__}")

# 1. 기본 테스트
print("\n1. 기본 다운로드 테스트")
try:
    # 단일 종목 다운로드
    data = yf.download("AAPL", period="5d", interval="1d")
    if not data.empty:
        print(f"✅ AAPL 데이터 성공: {len(data)}일치 데이터")
        print(f"   최근가: ${data['Close'].iloc[-1]:.2f}")
    else:
        print("❌ AAPL 데이터 실패")
except Exception as e:
    print(f"❌ AAPL 오류: {e}")

# 2. 한국 주식 테스트
print("\n2. 한국 주식 테스트")
korean_symbols = ['005930.KS']  # 삼성전자
for symbol in korean_symbols:
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d")
        if not hist.empty:
            print(f"✅ {symbol} 성공: {hist['Close'].iloc[-1]:.0f}원")
        else:
            print(f"❌ {symbol} 데이터 없음")
    except Exception as e:
        print(f"❌ {symbol} 오류: {e}")

# 3. 다양한 방법 테스트
print("\n3. 다양한 접근법 테스트")

# 방법 A: Ticker 객체 사용
try:
    aapl = yf.Ticker("AAPL")
    info = aapl.info
    if info:
        print(f"✅ Ticker.info 성공: {info.get('longName', 'N/A')}")
    else:
        print("❌ Ticker.info 실패")
except Exception as e:
    print(f"❌ Ticker.info 오류: {e}")

# 방법 B: 프록시 사용
print("\n4. 프록시 옵션 테스트")
try:
    data = yf.download("MSFT", period="2d", proxy=None)
    if not data.empty:
        print(f"✅ 프록시 옵션 성공: {len(data)}일치")
    else:
        print("❌ 프록시 옵션 실패")
except Exception as e:
    print(f"❌ 프록시 옵션 오류: {e}")

# 방법 C: 세션 사용
print("\n5. 세션 사용 테스트")
try:
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    ticker = yf.Ticker("GOOGL", session=session)
    hist = ticker.history(period="2d")
    if not hist.empty:
        print(f"✅ 커스텀 세션 성공: ${hist['Close'].iloc[-1]:.2f}")
    else:
        print("❌ 커스텀 세션 실패")
except Exception as e:
    print(f"❌ 커스텀 세션 오류: {e}")

# 6. 대량 다운로드 테스트
print("\n6. 대량 다운로드 테스트")
try:
    symbols = "AAPL MSFT GOOGL"
    data = yf.download(symbols, period="2d", group_by="ticker", threads=True)
    if not data.empty:
        print(f"✅ 대량 다운로드 성공: {data.shape}")
    else:
        print("❌ 대량 다운로드 실패")
except Exception as e:
    print(f"❌ 대량 다운로드 오류: {e}")

print("\n=== 테스트 완료 ===") 