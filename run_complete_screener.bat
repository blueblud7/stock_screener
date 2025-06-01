@echo off
chcp 65001 > nul
echo 🚀 완전한 주식 스크리너 대시보드 시작중...
echo =================================================

REM Python 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았습니다!
    pause
    exit /b 1
)
echo ✅ Python 발견

REM 패키지 설치
if exist requirements.txt (
    echo 📦 패키지 설치 중...
    pip install -r requirements.txt
)

REM 종목 리스트 확인
if not exist complete_stock_lists.json (
    echo ⚠️ 종목 리스트 파일이 없습니다. 생성 중...
    python complete_stock_lists.py
)

REM 포트 확인 (Windows에서는 netstat 사용)
netstat -an | find "8504" | find "LISTENING" >nul
if %errorlevel% equ 0 (
    echo ⚠️ 포트 8504가 이미 사용 중입니다.
    echo 기존 프로세스를 종료하고 계속합니다...
    for /f "tokens=5" %%a in ('netstat -aon ^| find "8504" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1
    timeout /t 2 >nul
)

echo.
echo =================================================
echo 🎉 모든 준비가 완료되었습니다!
echo.
echo 📊 완전한 주식 스크리너 대시보드 정보:
echo   • 지원 시장: S&P 500, NASDAQ, KOSPI, KOSDAQ
echo   • 총 종목 수: 851개
echo   • 기술적 지표: BB(20,2), RSI, MACD, 이동평균
echo   • 포트: 8504
echo.
echo 🌐 접속 주소: http://localhost:8504
echo.
echo ⚠️ 주의사항:
echo   • 첫 실행 시 종목 데이터 로딩에 시간이 걸릴 수 있습니다
echo   • 스크리닝 실행 시 851개 종목 분석에 약 5-10분 소요됩니다
echo   • 인터넷 연결이 필요합니다
echo.
echo 🚀 Streamlit 앱을 시작합니다...
echo =================================================

REM Streamlit 앱 실행
streamlit run complete_app.py --server.port 8504

echo.
echo 앱이 종료되었습니다.
pause 