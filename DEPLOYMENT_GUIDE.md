# 🌐 외부 접속 배포 가이드

현재 로컬에서만 접속 가능한 주식 스크리너를 외부에서도 접속할 수 있게 하는 방법들을 설명합니다.

## 🏆 추천 순서

1. **Streamlit Cloud** (무료, 영구적) 🥇
2. **ngrok** (무료, 임시적) 🥈  
3. **Heroku** (유료, 안정적) 🥉
4. **자체 서버** (고급 사용자) 🔧

---

## 1️⃣ Streamlit Cloud (가장 추천)

### ✅ 장점
- 완전 무료
- GitHub 연동으로 자동 배포
- 코드 변경 시 자동 업데이트
- 전 세계 어디서나 접속 가능
- HTTPS 지원

### ⚠️ 단점
- 메모리 제한 (1GB)
- CPU 제한
- 대용량 데이터 처리 제약

### 🚀 배포 방법

#### 1. Streamlit Cloud 가입
1. [https://share.streamlit.io](https://share.streamlit.io) 접속
2. GitHub 계정으로 로그인

#### 2. 앱 배포
1. "New app" 클릭
2. 설정값 입력:
   ```
   Repository: blueblud7/stock_screener
   Branch: master
   Main file path: cloud_app.py
   App URL: your-app-name
   ```
3. "Deploy!" 클릭

#### 3. 접속 주소
- `https://your-app-name.streamlit.app`

### 💡 최적화 팁
- 큰 JSON 파일 대신 코드에서 직접 종목 리스트 생성
- 캐싱(`@st.cache_data`) 적극 활용
- 메모리 사용량 최소화

---

## 2️⃣ ngrok (임시 접속)

### ✅ 장점
- 설정 간단
- 즉시 사용 가능
- 로컬 개발 환경 그대로 사용

### ⚠️ 단점
- 8시간 후 URL 만료 (무료 계정)
- 앱 종료 시 접속 불가
- 보안 위험

### 🚀 사용 방법

#### 1. ngrok 설치
```bash
# macOS
brew install ngrok/ngrok/ngrok

# 또는 https://ngrok.com/download 에서 다운로드
```

#### 2. 계정 설정 (무료)
1. [https://ngrok.com](https://ngrok.com) 가입
2. 인증 토큰 복사
3. `ngrok authtoken YOUR_TOKEN` 실행

#### 3. 앱 실행 및 터널 생성
```bash
# 터미널 1: 앱 실행
./start.sh

# 터미널 2: ngrok 터널
./setup_ngrok.sh
```

#### 4. 접속 주소 확인
- ngrok 실행 후 나타나는 URL 사용
- 예: `https://abcd1234.ngrok.io`

---

## 3️⃣ Heroku (유료 서비스)

### ✅ 장점
- 안정적인 서비스
- 24/7 운영 가능
- 확장성 좋음

### ⚠️ 단점
- 2022년부터 무료 플랜 폐지
- 월 $7+ 비용 발생
- 설정 복잡

### 🚀 배포 방법

#### 1. 필요 파일 생성
```bash
# Procfile
echo "web: streamlit run cloud_app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# runtime.txt (선택사항)
echo "python-3.9.18" > runtime.txt
```

#### 2. Heroku CLI 설치 및 배포
```bash
# Heroku CLI 설치
brew install heroku/brew/heroku

# 로그인
heroku login

# 앱 생성
heroku create your-app-name

# 배포
git push heroku master
```

---

## 4️⃣ 자체 서버 (VPS/AWS/GCP)

### ✅ 장점
- 완전한 제어권
- 무제한 리소스 (서버 스펙에 따라)
- 커스터마이징 자유

### ⚠️ 단점
- 서버 관리 필요
- 보안 설정 복잡
- 비용 발생

### 🚀 배포 예시 (Ubuntu)

```bash
# 1. 서버 접속 및 환경 설정
sudo apt update
sudo apt install python3 python3-pip nginx

# 2. 프로젝트 클론
git clone https://github.com/blueblud7/stock_screener.git
cd stock_screener

# 3. 패키지 설치
pip3 install -r requirements.txt

# 4. 앱 실행 (background)
nohup streamlit run cloud_app.py --server.port 8501 --server.address 0.0.0.0 &

# 5. Nginx 프록시 설정 (선택사항)
sudo nano /etc/nginx/sites-available/stockscreener
```

---

## 📊 비교표

| 방법 | 비용 | 난이도 | 안정성 | 속도 | 추천도 |
|------|------|--------|--------|------|--------|
| Streamlit Cloud | 무료 | ⭐ | ⭐⭐⭐ | ⭐⭐ | 🥇 |
| ngrok | 무료* | ⭐⭐ | ⭐ | ⭐⭐⭐ | 🥈 |
| Heroku | $7+/월 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 🥉 |
| 자체 서버 | $5+/월 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 🔧 |

*ngrok 무료 계정은 8시간 제한

---

## 🚀 즉시 시작하기

### 가장 빠른 방법 (ngrok)
```bash
# 1. 앱 실행 (터미널 1)
./start.sh

# 2. ngrok 설치 (macOS)
brew install ngrok/ngrok/ngrok

# 3. 터널 생성 (터미널 2)  
ngrok http 8504
```

### 가장 안정적인 방법 (Streamlit Cloud)
1. [https://share.streamlit.io](https://share.streamlit.io) 접속
2. GitHub 로그인
3. "New app" → Repository: `blueblud7/stock_screener` → Main file: `cloud_app.py`
4. 배포 완료!

---

## ⚠️ 보안 주의사항

1. **민감한 정보 제거**: API 키, 비밀번호 등은 환경변수 사용
2. **접속 제한**: 필요 시 IP 화이트리스트 설정
3. **HTTPS 사용**: 데이터 암호화를 위해 HTTPS 필수
4. **정기 업데이트**: 보안 패치 및 패키지 업데이트

---

## 📞 지원

문제 발생 시:
1. GitHub Issues: [blueblud7/stock_screener/issues](https://github.com/blueblud7/stock_screener/issues)
2. 로그 확인: `streamlit run cloud_app.py --logger.level=debug`
3. 브라우저 개발자 도구에서 에러 메시지 확인 