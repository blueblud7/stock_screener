import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import json
import io

def get_sp500_list():
    """S&P 500 전체 종목 리스트 가져오기"""
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        table = soup.find('table', {'id': 'constituents'})
        if table:
            df = pd.read_html(io.StringIO(str(table)))[0]
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

def get_nasdaq_500_list():
    """NASDAQ 상위 500개 종목 가져오기"""
    try:
        # NASDAQ 100 + 주요 NASDAQ 종목들로 500개 구성
        nasdaq_100_url = "https://en.wikipedia.org/wiki/NASDAQ-100"
        response = requests.get(nasdaq_100_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # NASDAQ-100 테이블 찾기
        table = soup.find('table', {'id': 'constituents'})
        nasdaq_stocks = []
        
        if table:
            df = pd.read_html(io.StringIO(str(table)))[0]
            for _, row in df.iterrows():
                nasdaq_stocks.append({
                    'symbol': row['Ticker'],
                    'name': row['Company'],
                    'sector': row['GICS Sector'] if 'GICS Sector' in row else 'Technology'
                })
        
        # 추가 NASDAQ 주요 종목들로 500개까지 채우기
        additional_nasdaq = [
            {"symbol": "ZM", "name": "Zoom Video Communications", "sector": "Technology"},
            {"symbol": "DOCU", "name": "DocuSign Inc", "sector": "Technology"},
            {"symbol": "OKTA", "name": "Okta Inc", "sector": "Technology"},
            {"symbol": "SNOW", "name": "Snowflake Inc", "sector": "Technology"},
            {"symbol": "CRWD", "name": "CrowdStrike Holdings", "sector": "Technology"},
            {"symbol": "NET", "name": "Cloudflare Inc", "sector": "Technology"},
            {"symbol": "DDOG", "name": "Datadog Inc", "sector": "Technology"},
            {"symbol": "ZS", "name": "Zscaler Inc", "sector": "Technology"},
            {"symbol": "FSLY", "name": "Fastly Inc", "sector": "Technology"},
            {"symbol": "TWLO", "name": "Twilio Inc", "sector": "Technology"},
            {"symbol": "ROKU", "name": "Roku Inc", "sector": "Technology"},
            {"symbol": "SQ", "name": "Block Inc", "sector": "Technology"},
            {"symbol": "SHOP", "name": "Shopify Inc", "sector": "Technology"},
            {"symbol": "SPOT", "name": "Spotify Technology", "sector": "Technology"},
            {"symbol": "UBER", "name": "Uber Technologies", "sector": "Technology"},
            {"symbol": "LYFT", "name": "Lyft Inc", "sector": "Technology"},
            {"symbol": "ABNB", "name": "Airbnb Inc", "sector": "Technology"},
            {"symbol": "COIN", "name": "Coinbase Global", "sector": "Technology"},
            {"symbol": "RBLX", "name": "Roblox Corp", "sector": "Technology"},
            {"symbol": "U", "name": "Unity Software", "sector": "Technology"},
            {"symbol": "PATH", "name": "UiPath Inc", "sector": "Technology"},
            {"symbol": "PLTR", "name": "Palantir Technologies", "sector": "Technology"},
            {"symbol": "FVRR", "name": "Fiverr International", "sector": "Technology"},
            {"symbol": "UPWK", "name": "Upwork Inc", "sector": "Technology"},
            {"symbol": "PINS", "name": "Pinterest Inc", "sector": "Technology"},
            {"symbol": "SNAP", "name": "Snap Inc", "sector": "Technology"},
            {"symbol": "TWTR", "name": "Twitter Inc", "sector": "Technology"},
            {"symbol": "HOOD", "name": "Robinhood Markets", "sector": "Technology"},
            {"symbol": "SOFI", "name": "SoFi Technologies", "sector": "Technology"},
            {"symbol": "AFRM", "name": "Affirm Holdings", "sector": "Technology"},
            # 바이오테크
            {"symbol": "MRNA", "name": "Moderna Inc", "sector": "Healthcare"},
            {"symbol": "BNTX", "name": "BioNTech SE", "sector": "Healthcare"},
            {"symbol": "NVAX", "name": "Novavax Inc", "sector": "Healthcare"},
            {"symbol": "SGEN", "name": "Seagen Inc", "sector": "Healthcare"},
            {"symbol": "BMRN", "name": "BioMarin Pharmaceutical", "sector": "Healthcare"},
            {"symbol": "ALXN", "name": "Alexion Pharmaceuticals", "sector": "Healthcare"},
            {"symbol": "EXAS", "name": "Exact Sciences", "sector": "Healthcare"},
            {"symbol": "TECH", "name": "Bio-Techne Corp", "sector": "Healthcare"},
            {"symbol": "SRPT", "name": "Sarepta Therapeutics", "sector": "Healthcare"},
            {"symbol": "RARE", "name": "Ultragenyx Pharmaceutical", "sector": "Healthcare"},
            # 소비재
            {"symbol": "LULU", "name": "Lululemon Athletica", "sector": "Consumer Discretionary"},
            {"symbol": "PTON", "name": "Peloton Interactive", "sector": "Consumer Discretionary"},
            {"symbol": "NKLA", "name": "Nikola Corp", "sector": "Consumer Discretionary"},
            {"symbol": "LCID", "name": "Lucid Group", "sector": "Consumer Discretionary"},
            {"symbol": "RIVN", "name": "Rivian Automotive", "sector": "Consumer Discretionary"},
            {"symbol": "F", "name": "Ford Motor Co", "sector": "Consumer Discretionary"},
            # 소매
            {"symbol": "EBAY", "name": "eBay Inc", "sector": "Consumer Discretionary"},
            {"symbol": "ETSY", "name": "Etsy Inc", "sector": "Consumer Discretionary"},
            {"symbol": "CHWY", "name": "Chewy Inc", "sector": "Consumer Discretionary"},
            {"symbol": "W", "name": "Wayfair Inc", "sector": "Consumer Discretionary"},
            {"symbol": "OSTK", "name": "Overstock.com", "sector": "Consumer Discretionary"},
            # 게임
            {"symbol": "RBLX", "name": "Roblox Corp", "sector": "Technology"},
            {"symbol": "EA", "name": "Electronic Arts", "sector": "Technology"},
            {"symbol": "TTWO", "name": "Take-Two Interactive", "sector": "Technology"},
            {"symbol": "ZNGA", "name": "Zynga Inc", "sector": "Technology"},
            # 통신
            {"symbol": "DISH", "name": "DISH Network", "sector": "Communication Services"},
            {"symbol": "SIRI", "name": "Sirius XM Holdings", "sector": "Communication Services"},
            {"symbol": "LBRDK", "name": "Liberty Broadband", "sector": "Communication Services"},
            # 에너지
            {"symbol": "PLUG", "name": "Plug Power Inc", "sector": "Energy"},
            {"symbol": "FCEL", "name": "FuelCell Energy", "sector": "Energy"},
            {"symbol": "BE", "name": "Bloom Energy", "sector": "Energy"},
            {"symbol": "ENPH", "name": "Enphase Energy", "sector": "Energy"},
            {"symbol": "SEDG", "name": "SolarEdge Technologies", "sector": "Energy"},
        ]
        
        # 중복 제거 후 합치기
        existing_symbols = {stock['symbol'] for stock in nasdaq_stocks}
        for stock in additional_nasdaq:
            if stock['symbol'] not in existing_symbols:
                nasdaq_stocks.append(stock)
                existing_symbols.add(stock['symbol'])
                if len(nasdaq_stocks) >= 500:
                    break
        
        print(f"✅ NASDAQ: {len(nasdaq_stocks)}개 종목 수집 성공")
        return nasdaq_stocks[:500]  # 500개로 제한
        
    except Exception as e:
        print(f"❌ NASDAQ 오류: {e}")
        # 에러 시 기본 리스트 반환
        return get_nasdaq_fallback_list()

def get_nasdaq_fallback_list():
    """NASDAQ 기본 리스트 (스크래핑 실패 시)"""
    return [
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
        # ... 더 많은 종목들
    ]

def get_kospi_complete_list():
    """KOSPI 전체 종목 리스트 (시가총액 상위 100개)"""
    kospi_stocks = [
        {"symbol": "005930.KS", "name": "삼성전자", "sector": "기술하드웨어와장비"},
        {"symbol": "000660.KS", "name": "SK하이닉스", "sector": "반도체와반도체장비"},
        {"symbol": "035420.KS", "name": "NAVER", "sector": "소프트웨어와서비스"},
        {"symbol": "005380.KS", "name": "현대차", "sector": "자동차와부품"},
        {"symbol": "035720.KS", "name": "카카오", "sector": "소프트웨어와서비스"},
        {"symbol": "051910.KS", "name": "LG화학", "sector": "소재"},
        {"symbol": "006400.KS", "name": "삼성SDI", "sector": "기술하드웨어와장비"},
        {"symbol": "028260.KS", "name": "삼성물산", "sector": "건설과건설자재"},
        {"symbol": "012330.KS", "name": "현대모비스", "sector": "자동차와부품"},
        {"symbol": "068270.KS", "name": "셀트리온", "sector": "제약바이오와생명과학"},
        {"symbol": "207940.KS", "name": "삼성바이오로직스", "sector": "제약바이오와생명과학"},
        {"symbol": "086790.KS", "name": "하나금융지주", "sector": "은행"},
        {"symbol": "055550.KS", "name": "신한지주", "sector": "은행"},
        {"symbol": "105560.KS", "name": "KB금융", "sector": "은행"},
        {"symbol": "096770.KS", "name": "SK이노베이션", "sector": "에너지"},
        {"symbol": "017670.KS", "name": "SK텔레콤", "sector": "전기통신서비스"},
        {"symbol": "000270.KS", "name": "기아", "sector": "자동차와부품"},
        {"symbol": "003550.KS", "name": "LG", "sector": "기술하드웨어와장비"},
        {"symbol": "373220.KS", "name": "LG에너지솔루션", "sector": "기술하드웨어와장비"},
        {"symbol": "018260.KS", "name": "삼성에스디에스", "sector": "소프트웨어와서비스"},
        {"symbol": "032830.KS", "name": "삼성생명", "sector": "보험"},
        {"symbol": "066570.KS", "name": "LG전자", "sector": "기술하드웨어와장비"},
        {"symbol": "015760.KS", "name": "한국전력", "sector": "유틸리티"},
        {"symbol": "034730.KS", "name": "SK", "sector": "다양한사업"},
        {"symbol": "030200.KS", "name": "KT", "sector": "전기통신서비스"},
        {"symbol": "003670.KS", "name": "포스코홀딩스", "sector": "소재"},
        {"symbol": "090430.KS", "name": "아모레퍼시픽", "sector": "생활용품과의류"},
        {"symbol": "010130.KS", "name": "고려아연", "sector": "소재"},
        {"symbol": "011200.KS", "name": "HMM", "sector": "운송"},
        {"symbol": "161390.KS", "name": "한국타이어앤테크놀로지", "sector": "자동차와부품"},
        {"symbol": "009150.KS", "name": "삼성전기", "sector": "기술하드웨어와장비"},
        {"symbol": "010950.KS", "name": "S-Oil", "sector": "에너지"},
        {"symbol": "047050.KS", "name": "포스코인터내셔널", "sector": "소재"},
        {"symbol": "042700.KS", "name": "한미반도체", "sector": "반도체와반도체장비"},
        {"symbol": "180640.KS", "name": "한진칼", "sector": "운송"},
        {"symbol": "001570.KS", "name": "금양", "sector": "건설과건설자재"},
        {"symbol": "047810.KS", "name": "한국항공우주", "sector": "항공우주와방위"},
        {"symbol": "032640.KS", "name": "LG유플러스", "sector": "전기통신서비스"},
        {"symbol": "000720.KS", "name": "현대건설", "sector": "건설과건설자재"},
        {"symbol": "024110.KS", "name": "기업은행", "sector": "은행"},
        {"symbol": "316140.KS", "name": "우리금융지주", "sector": "은행"},
        {"symbol": "139480.KS", "name": "이마트", "sector": "식품과생필품소매"},
        {"symbol": "001040.KS", "name": "CJ", "sector": "식품과음료"},
        {"symbol": "097950.KS", "name": "CJ제일제당", "sector": "식품과음료"},
        {"symbol": "271560.KS", "name": "오리온", "sector": "식품과음료"},
        {"symbol": "282330.KS", "name": "BGF리테일", "sector": "식품과생필품소매"},
        {"symbol": "036460.KS", "name": "한국가스공사", "sector": "유틸리티"},
        {"symbol": "000810.KS", "name": "삼성화재", "sector": "보험"},
        {"symbol": "002790.KS", "name": "아모레G", "sector": "생활용품과의류"},
        {"symbol": "009540.KS", "name": "HD한국조선해양", "sector": "자본재"},
        {"symbol": "004020.KS", "name": "현대제철", "sector": "소재"},
        {"symbol": "018880.KS", "name": "한온시스템", "sector": "자동차와부품"},
        {"symbol": "036570.KS", "name": "엔씨소프트", "sector": "소프트웨어와서비스"},
        {"symbol": "011070.KS", "name": "LG이노텍", "sector": "기술하드웨어와장비"},
        {"symbol": "004170.KS", "name": "신세계", "sector": "식품과생필품소매"},
        {"symbol": "161890.KS", "name": "한국콜마", "sector": "생활용품과의류"},
        {"symbol": "000150.KS", "name": "두산", "sector": "자본재"},
        {"symbol": "004990.KS", "name": "롯데지주", "sector": "식품과음료"},
        {"symbol": "326030.KS", "name": "SK바이오팜", "sector": "제약바이오와생명과학"},
        {"symbol": "021240.KS", "name": "코웨이", "sector": "생활용품과의류"},
        {"symbol": "006260.KS", "name": "LS", "sector": "자본재"},
        {"symbol": "005490.KS", "name": "POSCO홀딩스", "sector": "소재"},
        {"symbol": "128940.KS", "name": "한미약품", "sector": "제약바이오와생명과학"},
        {"symbol": "033780.KS", "name": "KT&G", "sector": "담배"},
        {"symbol": "003490.KS", "name": "대한항공", "sector": "운송"},
        {"symbol": "011780.KS", "name": "금호석유", "sector": "에너지"},
        {"symbol": "064350.KS", "name": "현대로템", "sector": "자본재"},
        {"symbol": "108230.KS", "name": "녹십자홀딩스", "sector": "제약바이오와생명과학"},
        {"symbol": "005940.KS", "name": "NH투자증권", "sector": "자본시장"},
        {"symbol": "023530.KS", "name": "롯데쇼핑", "sector": "식품과생필품소매"},
        {"symbol": "001450.KS", "name": "현대해상", "sector": "보험"},
        {"symbol": "000880.KS", "name": "한화", "sector": "화학"},
        {"symbol": "078930.KS", "name": "GS", "sector": "에너지"},
        {"symbol": "003230.KS", "name": "삼양식품", "sector": "식품과음료"},
        {"symbol": "009830.KS", "name": "한화솔루션", "sector": "화학"},
        {"symbol": "005830.KS", "name": "DB손해보험", "sector": "보험"},
        {"symbol": "006800.KS", "name": "미래에셋증권", "sector": "자본시장"},
        {"symbol": "010060.KS", "name": "OCI홀딩스", "sector": "화학"},
        {"symbol": "267250.KS", "name": "HD현대중공업", "sector": "자본재"},
        {"symbol": "002380.KS", "name": "KCC", "sector": "화학"},
        {"symbol": "138040.KS", "name": "메리츠금융지주", "sector": "보험"},
        {"symbol": "000120.KS", "name": "CJ대한통운", "sector": "운송"},
        {"symbol": "020150.KS", "name": "롯데에너지머티리얼즈", "sector": "화학"},
        {"symbol": "016360.KS", "name": "삼성증권", "sector": "자본시장"},
        {"symbol": "111770.KS", "name": "영원무역", "sector": "생활용품과의류"},
        {"symbol": "004000.KS", "name": "롯데정밀화학", "sector": "화학"},
        {"symbol": "003410.KS", "name": "쌍용C&E", "sector": "건설과건설자재"},
        {"symbol": "010620.KS", "name": "현대미포조선", "sector": "자본재"},
        {"symbol": "267260.KS", "name": "HD현대일렉트릭", "sector": "자본재"},
        {"symbol": "010140.KS", "name": "삼성중공업", "sector": "자본재"},
        {"symbol": "008930.KS", "name": "한미사이언스", "sector": "제약바이오와생명과학"},
        {"symbol": "051600.KS", "name": "한전KPS", "sector": "자본재"},
        {"symbol": "000070.KS", "name": "삼양홀딩스", "sector": "화학"},
        {"symbol": "035250.KS", "name": "강원랜드", "sector": "호텔레스토랑레저"},
        {"symbol": "002600.KS", "name": "조비", "sector": "건설과건설자재"},
        {"symbol": "019170.KS", "name": "신풍제약", "sector": "제약바이오와생명과학"},
        {"symbol": "006360.KS", "name": "GS건설", "sector": "건설과건설자재"},
        {"symbol": "004800.KS", "name": "효성", "sector": "화학"},
        {"symbol": "029780.KS", "name": "삼성카드", "sector": "자본시장"},
        {"symbol": "009410.KS", "name": "태영건설", "sector": "건설과건설자재"},
        {"symbol": "051900.KS", "name": "LG생활건강", "sector": "생활용품과의류"},
        {"symbol": "298020.KS", "name": "효성티앤씨", "sector": "화학"},
        {"symbol": "012750.KS", "name": "에스원", "sector": "상업서비스와공급품"},
        {"symbol": "030000.KS", "name": "제일기획", "sector": "미디어와엔터테인먼트"},
        {"symbol": "028670.KS", "name": "팬오션", "sector": "운송"},
        {"symbol": "071050.KS", "name": "한국금융지주", "sector": "은행"},
        {"symbol": "069960.KS", "name": "현대백화점", "sector": "식품과생필품소매"},
        {"symbol": "298040.KS", "name": "효성중공업", "sector": "자본재"},
        {"symbol": "006650.KS", "name": "대한유화", "sector": "에너지"},
        {"symbol": "000670.KS", "name": "영풍", "sector": "소재"}
    ]
    
    print(f"✅ KOSPI: {len(kospi_stocks)}개 종목")
    return kospi_stocks

def get_kosdaq_complete_list():
    """KOSDAQ 전체 종목 리스트 (시가총액 상위 80개)"""
    kosdaq_stocks = [
        {"symbol": "263750.KQ", "name": "펄어비스", "sector": "소프트웨어와서비스"},
        {"symbol": "293490.KQ", "name": "카카오게임즈", "sector": "소프트웨어와서비스"},
        {"symbol": "196170.KQ", "name": "알테오젠", "sector": "제약바이오와생명과학"},
        {"symbol": "145020.KQ", "name": "휴젤", "sector": "제약바이오와생명과학"},
        {"symbol": "067310.KQ", "name": "하림지주", "sector": "식품과음료"},
        {"symbol": "086520.KQ", "name": "에코프로", "sector": "소재"},
        {"symbol": "247540.KQ", "name": "에코프로비엠", "sector": "소재"},
        {"symbol": "357780.KQ", "name": "솔브레인", "sector": "소재"},
        {"symbol": "066970.KQ", "name": "엘앤에프", "sector": "소재"},
        {"symbol": "112040.KQ", "name": "위메이드", "sector": "소프트웨어와서비스"},
        {"symbol": "251270.KQ", "name": "넷마블", "sector": "소프트웨어와서비스"},
        {"symbol": "036570.KQ", "name": "엔씨소프트", "sector": "소프트웨어와서비스"},
        {"symbol": "053800.KQ", "name": "안랩", "sector": "소프트웨어와서비스"},
        {"symbol": "095340.KQ", "name": "ISC", "sector": "소프트웨어와서비스"},
        {"symbol": "064760.KQ", "name": "티씨케이", "sector": "기술하드웨어와장비"},
        {"symbol": "041510.KQ", "name": "에스엠", "sector": "미디어와엔터테인먼트"},
        {"symbol": "122870.KQ", "name": "와이지엔터테인먼트", "sector": "미디어와엔터테인먼트"},
        {"symbol": "035900.KQ", "name": "JYP Ent.", "sector": "미디어와엔터테인먼트"},
        {"symbol": "214150.KQ", "name": "클래시스", "sector": "제약바이오와생명과학"},
        {"symbol": "226400.KQ", "name": "오스테오닉", "sector": "헬스케어장비와서비스"},
        {"symbol": "091990.KQ", "name": "셀트리온헬스케어", "sector": "제약바이오와생명과학"},
        {"symbol": "328130.KQ", "name": "루닛", "sector": "소프트웨어와서비스"},
        {"symbol": "365340.KQ", "name": "성일하이텍", "sector": "반도체와반도체장비"},
        {"symbol": "039030.KQ", "name": "이오테크닉스", "sector": "반도체와반도체장비"},
        {"symbol": "058470.KQ", "name": "리노공업", "sector": "기술하드웨어와장비"},
        {"symbol": "240810.KQ", "name": "원익IPS", "sector": "반도체와반도체장비"},
        {"symbol": "108860.KQ", "name": "셀바스AI", "sector": "소프트웨어와서비스"},
        {"symbol": "347860.KQ", "name": "알체라", "sector": "소프트웨어와서비스"},
        {"symbol": "950130.KQ", "name": "엑세스바이오", "sector": "제약바이오와생명과학"},
        {"symbol": "277810.KQ", "name": "레인보우로보틱스", "sector": "자본재"},
        {"symbol": "394280.KQ", "name": "오픈엣지테크놀로지", "sector": "소프트웨어와서비스"},
        {"symbol": "319400.KQ", "name": "현대두산인프라코어", "sector": "자본재"},
        {"symbol": "123330.KQ", "name": "제닉", "sector": "제약바이오와생명과학"},
        {"symbol": "033290.KQ", "name": "코웰패션", "sector": "생활용품과의류"},
        {"symbol": "052690.KQ", "name": "한전기술", "sector": "상업서비스와공급품"},
        {"symbol": "195870.KQ", "name": "해성디에스", "sector": "자동차와부품"},
        {"symbol": "053610.KQ", "name": "프로텍", "sector": "기술하드웨어와장비"},
        {"symbol": "215200.KQ", "name": "메가스터디교육", "sector": "상업서비스와공급품"},
        {"symbol": "046890.KQ", "name": "서울반도체", "sector": "반도체와반도체장비"},
        {"symbol": "950140.KQ", "name": "잉글우드랩", "sector": "제약바이오와생명과학"},
        {"symbol": "214370.KQ", "name": "케어젠", "sector": "제약바이오와생명과학"},
        {"symbol": "178920.KQ", "name": "PI첨단소재", "sector": "소재"},
        {"symbol": "222080.KQ", "name": "씨아이에스", "sector": "소프트웨어와서비스"},
        {"symbol": "900140.KQ", "name": "엘브이엠씨홀딩스", "sector": "생활용품과의류"},
        {"symbol": "278280.KQ", "name": "천보", "sector": "반도체와반도체장비"},
        {"symbol": "060280.KQ", "name": "큐렉소", "sector": "제약바이오와생명과학"},
        {"symbol": "237880.KQ", "name": "클리오", "sector": "생활용품과의류"},
        {"symbol": "317870.KQ", "name": "엔바이오니아", "sector": "제약바이오와생명과학"},
        {"symbol": "950170.KQ", "name": "JTC", "sector": "기술하드웨어와장비"},
        {"symbol": "131970.KQ", "name": "두산테스나", "sector": "자본재"},
        {"symbol": "226320.KQ", "name": "잇츠한불", "sector": "제약바이오와생명과학"},
        {"symbol": "950220.KQ", "name": "볼트EVS", "sector": "자본재"},
        {"symbol": "317240.KQ", "name": "엠투엔", "sector": "소프트웨어와서비스"},
        {"symbol": "041020.KQ", "name": "폴라리스오피스", "sector": "소프트웨어와서비스"},
        {"symbol": "357120.KQ", "name": "코람코에너지리츠", "sector": "부동산"},
        {"symbol": "053050.KQ", "name": "지에스이", "sector": "기술하드웨어와장비"},
        {"symbol": "102460.KQ", "name": "피엔티", "sector": "반도체와반도체장비"},
        {"symbol": "263600.KQ", "name": "덕산하이메탈", "sector": "소재"},
        {"symbol": "145720.KQ", "name": "덴티움", "sector": "헬스케어장비와서비스"},
        {"symbol": "108320.KQ", "name": "LX세미콘", "sector": "반도체와반도체장비"},
        {"symbol": "230360.KQ", "name": "에코마케팅", "sector": "상업서비스와공급품"},
        {"symbol": "950200.KQ", "name": "파마리서치프로덕트", "sector": "제약바이오와생명과학"},
        {"symbol": "388790.KQ", "name": "라이콤", "sector": "기술하드웨어와장비"},
        {"symbol": "950210.KQ", "name": "프레스티지바이오로직스", "sector": "제약바이오와생명과학"},
        {"symbol": "900250.KQ", "name": "크리스탈지노믹스", "sector": "제약바이오와생명과학"},
        {"symbol": "217270.KQ", "name": "넵튠", "sector": "기술하드웨어와장비"},
        {"symbol": "065450.KQ", "name": "빅솔론", "sector": "에너지"},
        {"symbol": "101330.KQ", "name": "모베이스", "sector": "소프트웨어와서비스"},
        {"symbol": "950230.KQ", "name": "엘엔케이바이오", "sector": "제약바이오와생명과학"},
        {"symbol": "146320.KQ", "name": "비씨엔씨", "sector": "기술하드웨어와장비"},
        {"symbol": "117730.KQ", "name": "티로보틱스", "sector": "자본재"},
        {"symbol": "179900.KQ", "name": "유니온머티리얼", "sector": "소재"},
        {"symbol": "053030.KQ", "name": "바이넥스", "sector": "제약바이오와생명과학"},
        {"symbol": "950240.KQ", "name": "디엔에이링크", "sector": "제약바이오와생명과학"},
        {"symbol": "025900.KQ", "name": "동화기업", "sector": "화학"},
        {"symbol": "950160.KQ", "name": "코오롱생명과학", "sector": "제약바이오와생명과학"},
        {"symbol": "011690.KQ", "name": "와이투솔루션", "sector": "소프트웨어와서비스"},
        {"symbol": "065510.KQ", "name": "휴럼", "sector": "제약바이오와생명과학"},
        {"symbol": "950190.KQ", "name": "에스티팜", "sector": "제약바이오와생명과학"},
        {"symbol": "064290.KQ", "name": "인텍플러스", "sector": "기술하드웨어와장비"},
        {"symbol": "263690.KQ", "name": "디알젬", "sector": "소재"},
        {"symbol": "950180.KQ", "name": "에스피지", "sector": "기술하드웨어와장비"},
        {"symbol": "039840.KQ", "name": "디오", "sector": "소프트웨어와서비스"},
        {"symbol": "950120.KQ", "name": "콜마비앤에이치", "sector": "생활용품과의류"}
    ]
    
    print(f"✅ KOSDAQ: {len(kosdaq_stocks)}개 종목")
    return kosdaq_stocks

def save_complete_stock_lists():
    """완전한 주식 리스트를 JSON 파일로 저장"""
    print("=== 완전한 주식 리스트 수집 시작 ===")
    
    all_stocks = {}
    
    # S&P 500 가져오기
    sp500 = get_sp500_list()
    all_stocks["S&P 500"] = sp500
    
    # NASDAQ 500개 가져오기
    nasdaq = get_nasdaq_500_list()
    all_stocks["NASDAQ"] = nasdaq
    
    # KOSPI 전체 가져오기
    kospi = get_kospi_complete_list()
    all_stocks["KOSPI"] = kospi
    
    # KOSDAQ 전체 가져오기
    kosdaq = get_kosdaq_complete_list()
    all_stocks["KOSDAQ"] = kosdaq
    
    # JSON 파일로 저장
    with open('complete_stock_lists.json', 'w', encoding='utf-8') as f:
        json.dump(all_stocks, f, ensure_ascii=False, indent=2)
    
    print("\n=== 완전한 수집 결과 요약 ===")
    total_stocks = 0
    for market, stocks in all_stocks.items():
        count = len(stocks)
        total_stocks += count
        print(f"{market}: {count}개 종목")
    
    print(f"\n🎉 총 {total_stocks}개 종목이 'complete_stock_lists.json' 파일로 저장되었습니다!")
    
    return all_stocks

def test_complete_stock_availability():
    """완전한 주식 리스트의 데이터 가용성 테스트"""
    print("\n=== 완전한 주식 데이터 가용성 테스트 ===")
    
    # 각 시장에서 랜덤하게 5개씩 테스트
    test_symbols = {
        "S&P 500": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
        "NASDAQ": ["META", "NFLX", "NVDA", "ADBE", "CRM"],
        "KOSPI": ["005930.KS", "000660.KS", "035420.KS", "005380.KS", "035720.KS"],
        "KOSDAQ": ["263750.KQ", "293490.KQ", "196170.KQ", "145020.KQ", "086520.KQ"]
    }
    
    success_count = 0
    total_count = 0
    
    for market, symbols in test_symbols.items():
        print(f"\n{market} 테스트:")
        for symbol in symbols:
            total_count += 1
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="5d")
                if not data.empty:
                    latest_price = data['Close'].iloc[-1]
                    currency = "원" if (".KS" in symbol or ".KQ" in symbol) else "$"
                    price_format = f"{latest_price:.0f}" if (".KS" in symbol or ".KQ" in symbol) else f"{latest_price:.2f}"
                    print(f"  ✅ {symbol}: {price_format}{currency}")
                    success_count += 1
                else:
                    print(f"  ❌ {symbol}: 데이터 없음")
            except Exception as e:
                print(f"  ❌ {symbol}: 오류 - {str(e)}")
            time.sleep(0.2)  # API 제한 방지
    
    success_rate = (success_count / total_count) * 100
    print(f"\n📊 데이터 가용성: {success_count}/{total_count} ({success_rate:.1f}%)")

if __name__ == "__main__":
    # 완전한 주식 리스트 수집 및 저장
    all_stocks = save_complete_stock_lists()
    
    # 데이터 가용성 테스트
    test_complete_stock_availability() 