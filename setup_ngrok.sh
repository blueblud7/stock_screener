#!/bin/bash

# 📡 ngrok 터널링 설정 스크립트

echo "🌐 ngrok 터널링 설정..."
echo "================================"

# ngrok 설치 확인
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok이 설치되지 않았습니다!"
    echo ""
    echo "🔧 설치 방법:"
    echo "1. https://ngrok.com/download 접속"
    echo "2. 회원가입 후 다운로드"
    echo "3. 설치 완료 후 다시 실행"
    echo ""
    echo "💡 macOS 사용자:"
    echo "brew install ngrok/ngrok/ngrok"
    echo ""
    exit 1
fi

echo "✅ ngrok 발견"

# 포트 8504에서 실행 중인지 확인
if ! lsof -Pi :8504 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ 포트 8504에서 앱이 실행되지 않고 있습니다."
    echo "먼저 다른 터미널에서 다음 명령어로 앱을 실행하세요:"
    echo ""
    echo "  ./start.sh"
    echo "  또는"
    echo "  streamlit run complete_app.py --server.port 8504"
    echo ""
    read -p "앱이 실행되면 Enter를 눌러 계속하세요..."
fi

echo ""
echo "🚀 ngrok 터널 생성 중..."
echo "포트 8504를 외부에 노출합니다..."
echo ""
echo "⚠️  주의사항:"
echo "• 생성되는 URL은 일시적입니다 (8시간 후 만료)"
echo "• 무료 계정은 동시 터널 1개 제한"
echo "• 보안을 위해 필요 시에만 사용하세요"
echo ""

# ngrok 실행
ngrok http 8504 