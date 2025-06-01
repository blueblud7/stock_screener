#!/bin/bash

# 📈 빠른 실행 스크립트
echo "🚀 주식 스크리너 시작..."

# 포트 8504가 사용중이면 종료
if lsof -Pi :8504 -sTCP:LISTEN -t >/dev/null ; then
    echo "기존 프로세스 종료 중..."
    lsof -ti:8504 | xargs kill -9
    sleep 2
fi

# Streamlit 앱 실행
streamlit run complete_app.py --server.port 8504 