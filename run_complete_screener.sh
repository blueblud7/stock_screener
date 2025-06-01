#!/bin/bash

# 📈 완전한 주식 스크리너 대시보드 실행 스크립트
# GitHub: https://github.com/blueblud7/stock_screener.git

echo "🚀 완전한 주식 스크리너 대시보드 시작중..."
echo "================================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수 정의
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Python 환경 확인
print_status "Python 환경 확인 중..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python 발견: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    print_success "Python 발견: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    print_error "Python이 설치되지 않았습니다!"
    exit 1
fi

# 2. 필요 패키지 설치 확인
print_status "필요 패키지 설치 확인 중..."
if [ -f "requirements.txt" ]; then
    print_status "requirements.txt 발견. 패키지 설치 중..."
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        print_success "패키지 설치 완료"
    else
        print_warning "일부 패키지 설치에 문제가 있을 수 있습니다"
    fi
else
    print_warning "requirements.txt 파일이 없습니다. 수동으로 패키지를 설치해주세요"
    print_status "필요 패키지: streamlit, yfinance, pandas, numpy, plotly, requests, beautifulsoup4"
fi

# 3. 종목 리스트 파일 확인
print_status "종목 리스트 파일 확인 중..."
if [ -f "complete_stock_lists.json" ]; then
    print_success "종목 리스트 파일 발견 (complete_stock_lists.json)"
else
    print_warning "종목 리스트 파일이 없습니다. 생성 중..."
    
    if [ -f "complete_stock_lists.py" ]; then
        print_status "종목 리스트 생성 중... (약 1-2분 소요)"
        $PYTHON_CMD complete_stock_lists.py
        
        if [ $? -eq 0 ] && [ -f "complete_stock_lists.json" ]; then
            print_success "종목 리스트 생성 완료!"
        else
            print_error "종목 리스트 생성 실패. 수동으로 실행해주세요: $PYTHON_CMD complete_stock_lists.py"
            exit 1
        fi
    else
        print_error "complete_stock_lists.py 파일이 없습니다!"
        exit 1
    fi
fi

# 4. 포트 중복 확인
PORT=8504
print_status "포트 $PORT 사용 가능 여부 확인 중..."

if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    print_warning "포트 $PORT이 이미 사용 중입니다."
    print_status "기존 프로세스를 종료하시겠습니까? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "포트 $PORT의 프로세스 종료 중..."
        lsof -ti:$PORT | xargs kill -9
        sleep 2
        print_success "프로세스 종료 완료"
    else
        PORT=8505
        print_status "대체 포트 $PORT 사용"
    fi
fi

# 5. Streamlit 설치 확인
print_status "Streamlit 설치 확인 중..."
if command -v streamlit &> /dev/null; then
    STREAMLIT_VERSION=$(streamlit version)
    print_success "Streamlit 발견"
else
    print_error "Streamlit이 설치되지 않았습니다!"
    print_status "설치 중: pip install streamlit"
    pip install streamlit
fi

# 6. 완전한 앱 파일 확인
if [ ! -f "complete_app.py" ]; then
    print_error "complete_app.py 파일이 없습니다!"
    print_status "다음 파일들이 필요합니다:"
    echo "  - complete_app.py (메인 앱)"
    echo "  - complete_stock_lists.py (종목 리스트 생성기)"
    echo "  - requirements.txt (패키지 목록)"
    exit 1
fi

# 7. 최종 시작 안내
echo ""
echo "================================================="
print_success "🎉 모든 준비가 완료되었습니다!"
echo ""
print_status "📊 완전한 주식 스크리너 대시보드 정보:"
echo "  • 지원 시장: S&P 500, NASDAQ, KOSPI, KOSDAQ"
echo "  • 총 종목 수: 851개"
echo "  • 기술적 지표: BB(20,2), RSI, MACD, 이동평균"
echo "  • 포트: $PORT"
echo ""
print_status "🌐 접속 주소: http://localhost:$PORT"
print_status "🌐 네트워크 접속: http://192.168.86.72:$PORT"
echo ""
print_warning "⚠️  주의사항:"
echo "  • 첫 실행 시 종목 데이터 로딩에 시간이 걸릴 수 있습니다"
echo "  • 스크리닝 실행 시 851개 종목 분석에 약 5-10분 소요됩니다"
echo "  • 인터넷 연결이 필요합니다 (실시간 주가 데이터)"
echo ""
print_status "🚀 Streamlit 앱을 시작합니다..."
echo "================================================="

# 8. Streamlit 앱 실행
sleep 2
streamlit run complete_app.py --server.port $PORT

# 9. 종료 처리
echo ""
print_status "앱이 종료되었습니다."
print_status "다시 실행하려면: ./run_complete_screener.sh" 