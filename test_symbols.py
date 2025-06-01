import yfinance as yf
import time

# 한국 주식 테스트
print('=== 한국 주식 테스트 ===')
korean_symbols = ['005930.KS', '373220.KQ', '000660.KS']  # 삼성전자, LG에너지솔루션, SK하이닉스
for symbol in korean_symbols:
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period='5d')
        if not data.empty:
            print(f'{symbol}: 데이터 정상 - 최근가 {data.Close.iloc[-1]:.0f}')
        else:
            print(f'{symbol}: 데이터 없음')
    except Exception as e:
        print(f'{symbol}: 오류 - {str(e)}')
    time.sleep(0.5)

print('\n=== 미국 주식 테스트 ===')
us_symbols = ['AAPL', 'MSFT', 'GOOGL']
for symbol in us_symbols:
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period='5d')
        if not data.empty:
            print(f'{symbol}: 데이터 정상 - 최근가 ${data.Close.iloc[-1]:.2f}')
        else:
            print(f'{symbol}: 데이터 없음')
    except Exception as e:
        print(f'{symbol}: 오류 - {str(e)}')
    time.sleep(0.5) 