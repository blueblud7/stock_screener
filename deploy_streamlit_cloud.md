# 🚀 Streamlit Cloud 배포 가이드

## 📋 준비사항
- GitHub 계정 (이미 완료 ✅)
- 저장소가 Public이어야 함

## 🔧 배포 단계

### 1. Streamlit Cloud 접속
1. [https://share.streamlit.io](https://share.streamlit.io) 접속
2. GitHub 계정으로 로그인

### 2. 새 앱 배포
1. "New app" 클릭
2. Repository: `blueblud7/stock_screener`
3. Branch: `master`
4. **Main file path: `complete_app.py`** ⭐ (완전한 851개 종목 버전)
5. App URL: 원하는 주소 설정 (예: `stock-screener-complete`)

### 3. 배포 완료
- 자동으로 패키지 설치 및 앱 실행
- 공개 URL 생성: `https://앱이름.streamlit.app`

## ⚠️ 주의사항

### 완전한 버전 사용
- **complete_app.py**: 851개 종목 지원 (S&P 500: 503개, NASDAQ: 154개, KOSPI: 110개, KOSDAQ: 84개)
- **cloud_app.py**: 테스트 버전 (각 시장별 15-20개 종목)

### 메모리 최적화
- 첫 실행 시 `complete_stock_lists.json` 자동 로딩
- 캐싱으로 메모리 사용량 최소화
- 배치 처리로 안정성 확보

## 🌐 배포 후 접속
- 전 세계 어디서나 접속 가능
- 브라우저만 있으면 OK
- 모바일에서도 접속 가능 