import subprocess
import sys
import os
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

REQUIRED = [("qrcode[pil]", "qrcode"), ("Pillow", "PIL"),
            ("streamlit", "streamlit"), ("requests", "requests"), ("pyngrok", "pyngrok")]
for pip_name, import_name in REQUIRED:
    try:
        __import__(import_name)
    except ImportError:
        print(f"{pip_name} 설치 중...")
        install(pip_name)

import qrcode          # type: ignore
from pyngrok import ngrok  # type: ignore

PORT = 8501
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".ngrok_token")

# ngrok 인증 토큰 로드 (최초 1회만 입력)
if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, "r") as f:
        token = f.read().strip()
else:
    print("\n" + "=" * 52)
    print("  ngrok 인증 토큰이 필요합니다. (최초 1회만)")
    print("  1. https://ngrok.com 에서 무료 가입")
    print("  2. 로그인 후 Your Authtoken 복사")
    print("=" * 52)
    token = input("  토큰 붙여넣기 후 Enter: ").strip()
    with open(TOKEN_FILE, "w") as f:
        f.write(token)

ngrok.set_auth_token(token)

# Streamlit을 백그라운드로 실행
script_dir = os.path.dirname(os.path.abspath(__file__))
quiz_file = os.path.join(script_dir, "lng_quiz.py")

print("\nStreamlit 서버 시작 중...")
proc = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", quiz_file,
     "--server.address", "0.0.0.0",
     "--server.port", str(PORT),
     "--server.headless", "true",
     "--browser.gatherUsageStats", "false"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)

time.sleep(3)  # Streamlit이 뜰 때까지 대기

# ngrok 공개 터널 생성
print("공개 접속 주소 생성 중...")
tunnel = ngrok.connect(PORT, "http")
public_url = tunnel.public_url

print("\n" + "=" * 52)
print("  [포켓몬 퀴즈 대회] 서버 시작!")
print(f"  공개 접속 주소: {public_url}")
print("=" * 52)
print("  아래 QR코드를 스마트폰으로 스캔하세요!\n")

qr = qrcode.QRCode(border=1)
qr.add_data(public_url)
qr.make(fit=True)
qr.print_ascii(invert=True)

print(f"\n  인터넷이 연결된 모든 기기에서 접속 가능합니다!")
print("  종료하려면 Ctrl+C 를 누르세요.")
print("=" * 52 + "\n")

try:
    proc.wait()
except KeyboardInterrupt:
    print("\n서버를 종료합니다...")
    ngrok.kill()
    proc.terminate()