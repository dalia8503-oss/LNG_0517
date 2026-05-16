import subprocess, sys

def _install(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

for _pip, _mod in [("streamlit","streamlit"),("Pillow","PIL"),("requests","requests")]:
    try: __import__(_mod)
    except ImportError:
        print(f"{_pip} 설치 중..."); _install(_pip)

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import requests
from io import BytesIO
import json
import os
import time
import base64
import random

_MUSIC_URL = (
    "https://raw.githubusercontent.com/dalia8503-oss/lng_0517/main/"
    "%EC%9A%B0%EB%A6%AC%EB%8A%94%20%EB%AA%A8%EB%91%90%20%EC%B9%9C%EA%B5%AC.mp3"
)
_MUSIC_HTML = f"""
    <style>
      body {{ margin:0; padding:4px; background:transparent; }}
      #btn {{
        display:none; padding:7px 16px; background:#2563eb; color:#fff;
        border:none; border-radius:20px; cursor:pointer; font-size:13px;
        box-shadow:0 2px 8px rgba(0,0,0,0.2);
      }}
    </style>
    <audio id="bgm" loop>
      <source src="{_MUSIC_URL}" type="audio/mp3">
    </audio>
    <button id="btn" onclick="document.getElementById('bgm').play();this.style.display='none';">
      🎵 음악 켜기
    </button>
    <script>
      document.getElementById('bgm').play().catch(function() {{
        document.getElementById('btn').style.display = 'inline-block';
      }});
    </script>
"""

def play_background_music(_=None):
    components.html(_MUSIC_HTML, height=50)

# --- 1. 공용 데이터 저장소 (JSON) 관리 ---
# 모든 참가자와 진행자가 진행 상황(현재 문제 번호 등)을 공유하기 위한 파일입니다.
DATA_FILE = "live_game_state.json"

def init_game_state(total=50):
    if not os.path.exists(DATA_FILE):
        default_state = {
            "current_q": 0,
            "zoom_level": 1,
            "submissions": {},
            "hall_of_fame": [],
            "quiz_order": random.sample(range(total), total)
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(default_state, f, ensure_ascii=False)

def load_state():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        if "quiz_order" not in state:
            state["quiz_order"] = random.sample(range(50), 50)
            save_state(state)
        return state
    except:
        init_game_state()
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

def save_state(state):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=4)

init_game_state() # 시작 시 파일 초기화 확인

# --- 2. 기본 설정 및 포켓몬 데이터 ---
st.set_page_config(page_title="가족 초청 포켓몬 퀴즈!", page_icon="⚡", layout="wide")

pokemon_db = [
    {"name": "피카츄",    "id": 25,  "hint": "전기를 찌릿찌릿! 지우의 영원한 단짝이야."},
    {"name": "리자몽",    "id": 6,   "hint": "불꽃을 뿜는 거대한 드래곤처럼 생겼어."},
    {"name": "이브이",    "id": 133, "hint": "여러 가지 모습으로 진화할 수 있는 귀여운 여우 포켓몬!"},
    {"name": "팬텀",      "id": 94,  "hint": "장난을 좋아하는 보라색 유령 포켓몬이야."},
    {"name": "루카리오",  "id": 448, "hint": "파동을 사용하는 멋진 격투 포켓몬!"},
    {"name": "개굴닌자",  "id": 658, "hint": "물수리검을 던지는 닌자 개구리야."},
    {"name": "블래키",    "id": 197, "hint": "달빛을 받으면 몸의 무늬가 빛나는 이브이의 진화형이야."},
    {"name": "님피아",    "id": 700, "hint": "리본 같은 촉각을 가진 예쁜 페어리 포켓몬이야."},
    {"name": "이상해씨",  "id": 1,   "hint": "등에 커다란 씨앗을 짊어지고 있어."},
    {"name": "꼬부기",    "id": 7,   "hint": "단단한 등딱지를 가진 귀여운 거북이 포켓몬."},
    {"name": "파이리",    "id": 4,   "hint": "꼬리에 불꽃이 타오르고 있어!"},
    {"name": "잠만보",    "id": 143, "hint": "먹고 자는 것을 제일 좋아하는 뚱뚱한 포켓몬이야."},
    {"name": "뮤츠",      "id": 150, "hint": "사람들이 만들어낸 아주 강력한 전설의 포켓몬!"},
    {"name": "뮤",        "id": 151, "hint": "모든 포켓몬의 유전자를 가졌다고 전해지는 환상의 포켓몬이야."},
    {"name": "레쿠쟈",    "id": 384, "hint": "오존층을 날아다니는 초록색의 거대한 전설의 드래곤!"},
    {"name": "한카리아스","id": 445, "hint": "마하의 속도로 날아다니는 상어처럼 생긴 드래곤 포켓몬이야."},
    {"name": "가디안",    "id": 282, "hint": "트레이너를 지키기 위해 모든 힘을 다하는 우아한 포켓몬."},
    {"name": "따라큐",    "id": 778, "hint": "피카츄랑 비슷하게 생겼지만 사실은 천을 덮어쓴 유령이야."},
    {"name": "망나뇽",    "id": 149, "hint": "바다에서 사람을 구해주는 착한 드래곤 포켓몬."},
    {"name": "루기아",    "id": 249, "hint": "바다의 신이라고 불리는 전설의 포켓몬!"},
    {"name": "팽도리",    "id": 393, "hint": "자존심이 강한 귀여운 펭귄 포켓몬이야."},
    {"name": "나몰빼미",  "id": 722, "hint": "동그란 모양을 한 올빼미 포켓몬."},
    {"name": "염버니",    "id": 813, "hint": "발차기를 잘하는 불꽃 타입 토끼야."},
    {"name": "흥나숭",    "id": 810, "hint": "막대기로 장단을 맞추는 걸 좋아하는 원숭이 포켓몬."},
    {"name": "울머기",    "id": 816, "hint": "겁이 많아서 항상 눈물을 흘리는 물 포켓몬이야."},
    {"name": "나오하",    "id": 906, "hint": "풀 타입의 고양이 포켓몬! 달콤한 냄새가 나."},
    {"name": "뜨아거",    "id": 909, "hint": "사과처럼 생긴 불꽃 타입 악어 포켓몬이야."},
    {"name": "꾸왁스",    "id": 912, "hint": "머리 스타일을 항상 깔끔하게 유지하는 오리 포켓몬."},
    {"name": "샤미드",    "id": 134, "hint": "물에 녹아들 수 있는 이브이의 진화형."},
    {"name": "쥬피썬더",  "id": 135, "hint": "번개처럼 빠른 이브이의 진화형!"},
    {"name": "부스터",    "id": 136, "hint": "아주 뜨거운 불꽃을 뿜는 이브이의 진화형이야."},
    {"name": "에브이",    "id": 196, "hint": "태양의 힘을 받는 이브이의 진화형."},
    {"name": "리피아",    "id": 470, "hint": "광합성을 하는 식물 같은 이브이의 진화형."},
    {"name": "글레이시아", "id": 471, "hint": "주변의 공기를 얼려버리는 이브이의 얼음 진화형."},
    {"name": "마기라스",  "id": 248, "hint": "산을 무너뜨릴 만큼 강한 바위, 악 타입 포켓몬."},
    {"name": "보만다",    "id": 373, "hint": "하늘을 날고 싶다는 소원이 이루어져 날개가 생긴 드래곤."},
    {"name": "메타그로스", "id": 376, "hint": "4개의 뇌를 가져서 슈퍼컴퓨터보다 똑똑한 강철 포켓몬!"},
    {"name": "가이오가",  "id": 382, "hint": "바다를 넓혔다고 전해지는 전설의 포켓몬이야."},
    {"name": "그란돈",    "id": 383, "hint": "땅을 넓혔다고 전해지는 거대한 전설의 포켓몬."},
    {"name": "디아루가",  "id": 483, "hint": "시간을 조종할 수 있는 전설의 포켓몬!"},
    {"name": "펄기아",    "id": 484, "hint": "공간을 일그러뜨릴 수 있는 전설의 포켓몬!"},
    {"name": "기라티나",  "id": 487, "hint": "깨어진 세계에 살고 있는 신비한 전설의 포켓몬."},
    {"name": "아르세우스", "id": 493, "hint": "포켓몬 세계를 창조했다고 전해지는 신 같은 포켓몬이야."},
    {"name": "조로아크",  "id": 571, "hint": "다른 사람이나 포켓몬의 모습으로 둔갑할 수 있어."},
    {"name": "푸린",      "id": 39,  "hint": "동그랗고 귀여워. 노래를 부르면 모두 잠들어버려!"},
    {"name": "고라파덕",  "id": 54,  "hint": "항상 머리를 감싸 쥐고 있는 오리 포켓몬."},
    {"name": "야돈",      "id": 79,  "hint": "항상 멍~하니 꼬리를 물에 담그고 있어."},
    {"name": "잉어킹",    "id": 129, "hint": "파닥파닥 뛰기만 하지만 진화하면 아주 무서워져."},
    {"name": "갸라도스",  "id": 130, "hint": "잉어킹이 진화한 아주 사납고 거대한 물의 드래곤!"},
    {"name": "토게피",    "id": 175, "hint": "알껍데기를 입고 있는 작고 귀여운 포켓몬이야."},
]

# --- 3. 세션 상태 관리 (개별 접속자용) ---
if 'role' not in st.session_state:
    st.session_state.role = None # 'admin' 또는 'player'
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# --- 4. 이미지 캐싱 로직 ---
@st.cache_data
def get_pokemon_image(pokemon_id, zoom_level):
    url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pokemon_id}.png"
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        background = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(background, img).convert("RGB")
        width, height = img.size
        
        if zoom_level == 1:
            return img.crop((width * 0.425, height * 0.425, width * 0.575, height * 0.575))
        elif zoom_level == 2:
            return img.crop((width * 0.3, height * 0.3, width * 0.7, height * 0.7))
        else:
            return img
    except Exception:
        return None

# ==========================================
# 화면 로직: 1. 로그인 화면
# ==========================================
MUSIC_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "우리는 모두 친구.mp3")
play_background_music(MUSIC_FILE)

if st.session_state.role is None:
    st.markdown("""
        <style>
        h1 { font-size: 1.75rem !important; }
        p, div, label, .stMarkdown { font-size: 0.98rem !important; }
        </style>
        <h1 style="text-align:center;">나는 누구일까요~?</h1>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align:center; position:relative; width:180px; height:180px; margin:0 auto 10px auto;">
            <img id="pika-front"
                 src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png"
                 style="width:180px; position:absolute; top:0; left:0;
                        animation: showFront 2s step-end infinite;" />
            <img id="pika-back"
                 src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/25.png"
                 style="width:180px; position:absolute; top:0; left:0;
                        animation: showBack 2s step-end infinite;" />
        </div>
        <style>
        @keyframes showFront { 0%,49%{opacity:1} 50%,100%{opacity:0} }
        @keyframes showBack  { 0%,49%{opacity:0} 50%,100%{opacity:1} }
        </style>
    """, unsafe_allow_html=True)

    pokemon_img = os.path.join(os.path.dirname(os.path.abspath(__file__)), "포켓몬스터.jpg")
    if os.path.exists(pokemon_img):
        st.image(pokemon_img, use_column_width=True)
    st.markdown("<p style='text-align:center;'>스크린의 문제를 보고 가장 먼저 정답을 맞혀보세요!</p>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        name_input = st.text_input("참가자 이름 (또는 닉네임)", placeholder="예: 홍길동")
        phone_input = st.text_input("휴대폰 번호 뒷자리 (4자리)", placeholder="예: 1234", max_chars=4)
        
        submit_btn = st.form_submit_button("입장하기 🚀")
        
        if submit_btn:
            # 관리자(진행자) 비밀 로그인 로직
            if name_input == "admin" and phone_input == "1234":
                st.session_state.role = "admin"
                st.rerun()
            elif name_input and len(phone_input) == 4:
                st.session_state.role = "player"
                st.session_state.user_name = name_input
                st.session_state.user_id = f"{name_input}_{phone_input}"
                st.rerun()
            else:
                st.error("이름과 휴대폰 번호 뒷자리 4자리를 정확히 입력해주세요!")

# ==========================================
# 화면 로직: 2. 진행자 (Host) 화면 - 프로젝터용
# ==========================================
elif st.session_state.role == "admin":
    # 실시간 상태 불러오기
    state = load_state()
    current_q_idx = state["current_q"]
    
    # 퀴즈 종료 여부 확인
    if current_q_idx >= len(pokemon_db):
        st.title("🎉 모든 퀴즈가 종료되었습니다! 🎉")
        if st.button("행사 초기화 (모든 기록 삭제)"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.session_state.role = None
            st.rerun()
        st.stop()

    current_pokemon = pokemon_db[state["quiz_order"][current_q_idx]]
    q_key = str(current_q_idx)
    submissions = state["submissions"].get(q_key, [])
    hall_of_fame = state["hall_of_fame"]

    # ── 2컬럼: 왼쪽(퀴즈) / 오른쪽(랭킹+명예의 전당) ──
    left, right = st.columns([3, 2])

    with left:
        col_title, col_reset = st.columns([4, 1])
        with col_title:
            st.title(f"🔍 [문제 {current_q_idx + 1}] 이게 누구게?")
        with col_reset:
            st.write("")
            if st.button("🔄 전체 초기화", type="secondary"):
                if os.path.exists(DATA_FILE):
                    os.remove(DATA_FILE)
                init_game_state(len(pokemon_db))
                st.rerun()

        display_img = get_pokemon_image(current_pokemon["id"], state["zoom_level"])
        if display_img:
            img_col, _ = st.columns([4, 1])
            with img_col:
                st.image(display_img, use_column_width=True)
        if state["zoom_level"] == 3:
            st.success(f"정답은 '{current_pokemon['name']}' 였습니다! 🎉")

        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔍 조금만 더 보여줄까요~?"):
                if state["zoom_level"] < 3:
                    state["zoom_level"] += 1
                    save_state(state)
                    st.rerun()
        with col2:
            if st.button("💡 힌트 좀 드릴까요~?!"):
                st.info(f"힌트: {current_pokemon['hint']}")
        with col3:
            if st.button("▶️ 다음은 누구일까요?!"):
                q_key_now = str(current_q_idx)
                for sub in state["submissions"].get(q_key_now, []):
                    if sub['id'] not in state["hall_of_fame"]:
                        state["hall_of_fame"].append(sub['id'])
                        break
                state["current_q"] += 1
                state["zoom_level"] = 1
                save_state(state)
                st.rerun()

    with right:
        st.subheader(f"🏆 {current_q_idx + 1}번 문제 정답자 랭킹")
        if st.button("🔄 누가 제일 빨랐을까요~?"):
            st.rerun()

        if not submissions:
            st.write("아직 정답자가 없습니다...")
        else:
            rank = 1
            for sub in submissions:
                user_info = f"{sub['name']} ({sub['id'].split('_')[1]})"
                if sub['id'] in hall_of_fame:
                    st.markdown(f"🌟 **[명예의 전당]** {user_info}")
                else:
                    if rank == 1:
                        st.success(f"🥇 1등: {user_info} 🎁")
                    elif rank == 2:
                        st.warning(f"🥈 2등: {user_info}")
                    else:
                        st.write(f"🔹 {rank}등: {user_info}")
                    rank += 1

        st.markdown("---")
        st.subheader("🌟 명예의 전당 (시상 대상자)")
        if not hall_of_fame:
            st.write("아직 없습니다.")
        else:
            id_to_name = {}
            for q_subs in state["submissions"].values():
                for sub in q_subs:
                    id_to_name[sub['id']] = sub['name']
            for i, uid in enumerate(hall_of_fame, 1):
                name = id_to_name.get(uid, uid)
                phone = uid.split('_')[1] if '_' in uid else ''
                st.write(f"🏅 {i}. {name} ({phone})")

# ==========================================
# 화면 로직: 3. 참가자 (Player) 화면 - 스마트폰용
# ==========================================
elif st.session_state.role == "player":
    # 최신 상태를 불러와서 현재 문제 번호 확인
    state = load_state()
    current_q_idx = state["current_q"]
    
    # 참가자 UI 헤더
    st.title("모바일 답안 입력기 📱")
    st.write(f"안녕하세요, **{st.session_state.user_name}**님!")
    
    if current_q_idx >= len(pokemon_db):
        st.info("모든 퀴즈가 종료되었습니다. 감사합니다!")
        st.stop()
        
    current_pokemon = pokemon_db[state["quiz_order"][current_q_idx]]
    q_key = str(current_q_idx)
    
    st.markdown("---")
    st.subheader(f"현재 📌 **{current_q_idx + 1}번 문제** 진행 중!")
    st.write("프로젝터 화면을 보고 정답을 입력하세요.")
    
    # 이미 정답을 맞춘 경우
    user_already_solved = False
    if q_key in state["submissions"]:
        for sub in state["submissions"][q_key]:
            if sub["id"] == st.session_state.user_id:
                user_already_solved = True
                break
                
    if user_already_solved:
        st.success("✅ 정답을 제출하셨습니다! 프로젝터 화면의 결과를 확인해주세요.")
        if st.button("현재 문제 진행상황 새로고침 🔄"):
            st.rerun()
    else:
        # 답안 입력 폼
        with st.form(key=f"answer_form_{current_q_idx}"):
            user_answer = st.text_input("정답 입력 후 엔터(Enter)를 치세요!").strip()
            submit_btn = st.form_submit_button("정답 제출 ⚡")
            
            if submit_btn:
                # 정답 확인
                if user_answer.replace(" ", "") == current_pokemon["name"]:
                    # 상태를 다시 한 번 불러와서 동시성 이슈 방지
                    latest_state = load_state()
                    if q_key not in latest_state["submissions"]:
                        latest_state["submissions"][q_key] = []
                        
                    # 중복 제출 방지 체크
                    already_in = any(s["id"] == st.session_state.user_id for s in latest_state["submissions"][q_key])
                    if not already_in:
                        # 정답자 리스트에 추가 (시간순으로 자동 기록됨)
                        latest_state["submissions"][q_key].append({
                            "id": st.session_state.user_id,
                            "name": st.session_state.user_name,
                            "timestamp": time.time()
                        })
                        save_state(latest_state)
                        st.success("정답입니다! 🎉")
                        st.rerun()
                elif user_answer:
                    st.warning("앗, 오답입니다! 화면을 다시 잘 보고 입력해주세요. 🤔")

    st.markdown("---")
    st.caption("진행자가 다음 문제로 넘어가면 아래 버튼을 누르세요.")
    if st.button("다음 문제로 업데이트 🔄"):
        st.rerun()