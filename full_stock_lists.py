import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import json

def get_sp500_list():
    """S&P 500 전체 종목 리스트 가져오기"""
    try:
        # 위키피디아에서 S&P 500 리스트 가져오기
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 테이블 찾기
        table = soup.find('table', {'id': 'constituents'})
        if table:
            df = pd.read_html(str(table))[0]
            stocks = []
            for _, row in df.iterrows():
                stocks.append({
                    'symbol': row['Symbol'],
                    'name': row['Security'],
                    'sector': row['GICS Sector']
                })
            print(f"✅ S&P 500: {len(stocks)}개 종목 수집 성공")
            return stocks
        else:
            print("❌ S&P 500 테이블을 찾을 수 없습니다.")
            return []
    except Exception as e:
        print(f"❌ S&P 500 오류: {e}")
        return []

def get_nasdaq_list():
    """NASDAQ 주요 종목들 가져오기 (샘플)"""
    # NASDAQ 전체 리스트는 매우 크므로 주요 종목들만
    major_nasdaq = [
        {"symbol": "AAPL", "name": "Apple Inc", "sector": "Technology"},
        {"symbol": "MSFT", "name": "Microsoft Corp", "sector": "Technology"},
        {"symbol": "GOOGL", "name": "Alphabet Inc Class A", "sector": "Technology"},
        {"symbol": "GOOG", "name": "Alphabet Inc Class C", "sector": "Technology"},
        {"symbol": "AMZN", "name": "Amazon.com Inc", "sector": "Consumer Discretionary"},
        {"symbol": "TSLA", "name": "Tesla Inc", "sector": "Consumer Discretionary"},
        {"symbol": "META", "name": "Meta Platforms Inc", "sector": "Technology"},
        {"symbol": "NVDA", "name": "NVIDIA Corp", "sector": "Technology"},
        {"symbol": "NFLX", "name": "Netflix Inc", "sector": "Communication Services"},
        {"symbol": "ADBE", "name": "Adobe Inc", "sector": "Technology"},
        {"symbol": "CRM", "name": "Salesforce Inc", "sector": "Technology"},
        {"symbol": "ORCL", "name": "Oracle Corp", "sector": "Technology"},
        {"symbol": "INTC", "name": "Intel Corp", "sector": "Technology"},
        {"symbol": "AMD", "name": "Advanced Micro Devices", "sector": "Technology"},
        {"symbol": "QCOM", "name": "Qualcomm Inc", "sector": "Technology"},
        {"symbol": "CSCO", "name": "Cisco Systems Inc", "sector": "Technology"},
        {"symbol": "AVGO", "name": "Broadcom Inc", "sector": "Technology"},
        {"symbol": "TXN", "name": "Texas Instruments", "sector": "Technology"},
        {"symbol": "COST", "name": "Costco Wholesale", "sector": "Consumer Staples"},
        {"symbol": "CMCSA", "name": "Comcast Corp", "sector": "Communication Services"},
        {"symbol": "PEP", "name": "PepsiCo Inc", "sector": "Consumer Staples"},
        {"symbol": "TMUS", "name": "T-Mobile US Inc", "sector": "Communication Services"},
        {"symbol": "AMAT", "name": "Applied Materials", "sector": "Technology"},
        {"symbol": "INTU", "name": "Intuit Inc", "sector": "Technology"},
        {"symbol": "BKNG", "name": "Booking Holdings", "sector": "Consumer Discretionary"},
        {"symbol": "ISRG", "name": "Intuitive Surgical", "sector": "Healthcare"},
        {"symbol": "AMGN", "name": "Amgen Inc", "sector": "Healthcare"},
        {"symbol": "HON", "name": "Honeywell Intl", "sector": "Industrials"},
        {"symbol": "VRTX", "name": "Vertex Pharmaceuticals", "sector": "Healthcare"},
        {"symbol": "ADP", "name": "Automatic Data Processing", "sector": "Technology"},
        {"symbol": "GILD", "name": "Gilead Sciences", "sector": "Healthcare"},
        {"symbol": "SBUX", "name": "Starbucks Corp", "sector": "Consumer Discretionary"},
        {"symbol": "MU", "name": "Micron Technology", "sector": "Technology"},
        {"symbol": "ADI", "name": "Analog Devices", "sector": "Technology"},
        {"symbol": "PYPL", "name": "PayPal Holdings", "sector": "Technology"},
        {"symbol": "MDLZ", "name": "Mondelez International", "sector": "Consumer Staples"},
        {"symbol": "REGN", "name": "Regeneron Pharmaceuticals", "sector": "Healthcare"},
        {"symbol": "CSX", "name": "CSX Corp", "sector": "Industrials"},
        {"symbol": "NXPI", "name": "NXP Semiconductors", "sector": "Technology"},
        {"symbol": "ATVI", "name": "Activision Blizzard", "sector": "Technology"},
    ]
    
    print(f"✅ NASDAQ 주요 종목: {len(major_nasdaq)}개 종목")
    return major_nasdaq

def get_korean_stocks():
    """한국 주식 리스트 (KOSPI + KOSDAQ 주요 종목들)"""
    
    # KOSPI 주요 종목들
    kospi_stocks = [
        {"symbol": "005930.KS", "name": "삼성전자", "sector": "기술하드웨어와장비", "market": "KOSPI"},
        {"symbol": "000660.KS", "name": "SK하이닉스", "sector": "반도체와반도체장비", "market": "KOSPI"},
        {"symbol": "035420.KS", "name": "NAVER", "sector": "소프트웨어와서비스", "market": "KOSPI"},
        {"symbol": "005380.KS", "name": "현대차", "sector": "자동차와부품", "market": "KOSPI"},
        {"symbol": "035720.KS", "name": "카카오", "sector": "소프트웨어와서비스", "market": "KOSPI"},
        {"symbol": "051910.KS", "name": "LG화학", "sector": "소재", "market": "KOSPI"},
        {"symbol": "006400.KS", "name": "삼성SDI", "sector": "기술하드웨어와장비", "market": "KOSPI"},
        {"symbol": "028260.KS", "name": "삼성물산", "sector": "건설과건설자재", "market": "KOSPI"},
        {"symbol": "012330.KS", "name": "현대모비스", "sector": "자동차와부품", "market": "KOSPI"},
        {"symbol": "068270.KS", "name": "셀트리온", "sector": "제약바이오와생명과학", "market": "KOSPI"},
        {"symbol": "207940.KS", "name": "삼성바이오로직스", "sector": "제약바이오와생명과학", "market": "KOSPI"},
        {"symbol": "086790.KS", "name": "하나금융지주", "sector": "은행", "market": "KOSPI"},
        {"symbol": "055550.KS", "name": "신한지주", "sector": "은행", "market": "KOSPI"},
        {"symbol": "105560.KS", "name": "KB금융", "sector": "은행", "market": "KOSPI"},
        {"symbol": "096770.KS", "name": "SK이노베이션", "sector": "에너지", "market": "KOSPI"},
        {"symbol": "017670.KS", "name": "SK텔레콤", "sector": "전기통신서비스", "market": "KOSPI"},
        {"symbol": "000270.KS", "name": "기아", "sector": "자동차와부품", "market": "KOSPI"},
        {"symbol": "003550.KS", "name": "LG", "sector": "기술하드웨어와장비", "market": "KOSPI"},
        {"symbol": "373220.KS", "name": "LG에너지솔루션", "sector": "기술하드웨어와장비", "market": "KOSPI"},
        {"symbol": "018260.KS", "name": "삼성에스디에스", "sector": "소프트웨어와서비스", "market": "KOSPI"},
        {"symbol": "032830.KS", "name": "삼성생명", "sector": "보험", "market": "KOSPI"},
        {"symbol": "066570.KS", "name": "LG전자", "sector": "기술하드웨어와장비", "market": "KOSPI"},
        {"symbol": "015760.KS", "name": "한국전력", "sector": "유틸리티", "market": "KOSPI"},
        {"symbol": "034730.KS", "name": "SK", "sector": "다양한사업", "market": "KOSPI"},
        {"symbol": "030200.KS", "name": "KT", "sector": "전기통신서비스", "market": "KOSPI"},
        {"symbol": "003670.KS", "name": "포스코홀딩스", "sector": "소재", "market": "KOSPI"},
        {"symbol": "090430.KS", "name": "아모레퍼시픽", "sector": "생활용품과의류", "market": "KOSPI"},
        {"symbol": "010130.KS", "name": "고려아연", "sector": "소재", "market": "KOSPI"},
        {"symbol": "011200.KS", "name": "HMM", "sector": "운송", "market": "KOSPI"},
        {"symbol": "161390.KS", "name": "한국타이어앤테크놀로지", "sector": "자동차와부품", "market": "KOSPI"},
    ]
    
    # KOSDAQ 주요 종목들
    kosdaq_stocks = [
        {"symbol": "263750.KQ", "name": "펄어비스", "sector": "소프트웨어와서비스", "market": "KOSDAQ"},
        {"symbol": "293490.KQ", "name": "카카오게임즈", "sector": "소프트웨어와서비스", "market": "KOSDAQ"},
        {"symbol": "196170.KQ", "name": "알테오젠", "sector": "제약바이오와생명과학", "market": "KOSDAQ"},
        {"symbol": "145020.KQ", "name": "휴젤", "sector": "제약바이오와생명과학", "market": "KOSDAQ"},
        {"symbol": "067310.KQ", "name": "하림지주", "sector": "식품과음료", "market": "KOSDAQ"},
        {"symbol": "086520.KQ", "name": "에코프로", "sector": "소재", "market": "KOSDAQ"},
        {"symbol": "247540.KQ", "name": "에코프로비엠", "sector": "소재", "market": "KOSDAQ"},
        {"symbol": "357780.KQ", "name": "솔브레인", "sector": "소재", "market": "KOSDAQ"},
        {"symbol": "066970.KQ", "name": "엘앤에프", "sector": "소재", "market": "KOSDAQ"},
        {"symbol": "112040.KQ", "name": "위메이드", "sector": "소프트웨어와서비스", "market": "KOSDAQ"},
        {"symbol": "251270.KQ", "name": "넷마블", "sector": "소프트웨어와서비스", "market": "KOSDAQ"},
        {"symbol": "036570.KQ", "name": "엔씨소프트", "sector": "소프트웨어와서비스", "market": "KOSDAQ"},
        {"symbol": "053800.KQ", "name": "안랩", "sector": "소프트웨어와서비스", "market": "KOSDAQ"},
        {"symbol": "095340.KQ", "name": "ISC", "sector": "소프트웨어와서비스", "market": "KOSDAQ"},
        {"symbol": "064760.KQ", "name": "티씨케이", "sector": "기술하드웨어와장비", "market": "KOSDAQ"},
        {"symbol": "041510.KQ", "name": "에스엠", "sector": "미디어와엔터테인먼트", "market": "KOSDAQ"},
        {"symbol": "122870.KQ", "name": "와이지엔터테인먼트", "sector": "미디어와엔터테인먼트", "market": "KOSDAQ"},
        {"symbol": "035900.KQ", "name": "JYP Ent.", "sector": "미디어와엔터테인먼트", "market": "KOSDAQ"},
        {"symbol": "214150.KQ", "name": "클래시스", "sector": "제약바이오와생명과학", "market": "KOSDAQ"},
        {"symbol": "226400.KQ", "name": "오스테오닉", "sector": "헬스케어장비와서비스", "market": "KOSDAQ"},
    ]
    
    print(f"✅ KOSPI 주요 종목: {len(kospi_stocks)}개")
    print(f"✅ KOSDAQ 주요 종목: {len(kosdaq_stocks)}개")
    
    return {
        "KOSPI": kospi_stocks,
        "KOSDAQ": kosdaq_stocks
    }

def save_stock_lists():
    """모든 주식 리스트를 JSON 파일로 저장"""
    print("=== 전체 주식 리스트 수집 시작 ===")
    
    all_stocks = {}
    
    # S&P 500 가져오기
    sp500 = get_sp500_list()
    all_stocks["S&P 500"] = sp500
    
    # NASDAQ 가져오기
    nasdaq = get_nasdaq_list()
    all_stocks["NASDAQ"] = nasdaq
    
    # 한국 주식 가져오기
    korean_stocks = get_korean_stocks()
    all_stocks.update(korean_stocks)
    
    # JSON 파일로 저장
    with open('stock_lists.json', 'w', encoding='utf-8') as f:
        json.dump(all_stocks, f, ensure_ascii=False, indent=2)
    
    print("\n=== 수집 결과 요약 ===")
    for market, stocks in all_stocks.items():
        print(f"{market}: {len(stocks)}개 종목")
    
    print(f"\n✅ 전체 주식 리스트가 'stock_lists.json' 파일로 저장되었습니다!")
    
    return all_stocks

def test_stock_data_availability():
    """저장된 주식들이 실제로 데이터가 있는지 테스트"""
    print("\n=== 주식 데이터 가용성 테스트 ===")
    
    # 각 시장에서 몇 개씩 샘플 테스트
    test_symbols = {
        "S&P 500": ["AAPL", "MSFT", "GOOGL"],
        "NASDAQ": ["TSLA", "NFLX", "AMZN"],
        "KOSPI": ["005930.KS", "000660.KS", "035420.KS"],
        "KOSDAQ": ["263750.KQ", "293490.KQ", "196170.KQ"]
    }
    
    for market, symbols in test_symbols.items():
        print(f"\n{market} 테스트:")
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="5d")
                if not data.empty:
                    latest_price = data['Close'].iloc[-1]
                    currency = "원" if (".KS" in symbol or ".KQ" in symbol) else "$"
                    price_format = f"{latest_price:.0f}" if (".KS" in symbol or ".KQ" in symbol) else f"{latest_price:.2f}"
                    print(f"  ✅ {symbol}: {price_format}{currency}")
                else:
                    print(f"  ❌ {symbol}: 데이터 없음")
            except Exception as e:
                print(f"  ❌ {symbol}: 오류 - {str(e)}")
            time.sleep(0.2)  # API 제한 방지

if __name__ == "__main__":
    # 전체 주식 리스트 수집 및 저장
    all_stocks = save_stock_lists()
    
    # 데이터 가용성 테스트
    test_stock_data_availability() 