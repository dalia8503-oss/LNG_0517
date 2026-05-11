import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import json
import os
import time
import base64

def play_background_music(file_path):
    if not os.path.exists(file_path):
        return
    with open(file_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <audio autoplay loop style="display:none">
            <source src="data:audio/mp3;base64,{data}" type="audio/mp3">
        </audio>
    """, unsafe_allow_html=True)

# --- 1. 공용 데이터 저장소 (JSON) 관리 ---
# 모든 참가자와 진행자가 진행 상황(현재 문제 번호 등)을 공유하기 위한 파일입니다.
DATA_FILE = "live_game_state.json"

def init_game_state():
    if not os.path.exists(DATA_FILE):
        default_state = {
            "current_q": 0,       # 현재 진행 중인 문제 인덱스
            "zoom_level": 1,      # 현재 줌 단계 (1:초근접, 2:중간, 3:전체)
            "submissions": {},    # 문제별 제출 기록 {"0": [], "1": []}
            "hall_of_fame": []    # 명예의 전당 (선물 수령자)
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(default_state, f, ensure_ascii=False)

def load_state():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        init_game_state()
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

def save_state(state):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=4)

init_game_state() # 시작 시 파일 초기화 확인

# --- 2. 기본 설정 및 포켓몬 데이터 ---
st.set_page_config(page_title="가족 초청 포켓몬 퀴즈!", page_icon="⚡", layout="centered")

pokemon_db = [
    {"name": "피카츄", "id": 25, "hint": "전기를 찌릿찌릿! 지우의 영원한 단짝이야."},
    {"name": "리자몽", "id": 6, "hint": "불꽃을 뿜는 거대한 드래곤처럼 생겼어."},
    {"name": "이브이", "id": 133, "hint": "여러 가지 모습으로 진화할 수 있는 귀여운 여우 포켓몬!"},
    {"name": "팬텀", "id": 94, "hint": "장난을 좋아하는 보라색 유령 포켓몬이야."},
    {"name": "루카리오", "id": 448, "hint": "파동을 사용하는 멋진 격투 포켓몬!"},
    {"name": "꼬부기", "id": 7, "hint": "단단한 등딱지를 가진 귀여운 거북이 포켓몬."},
    {"name": "파이리", "id": 4, "hint": "꼬리에 불꽃이 타오르고 있어!"},
    {"name": "이상해씨", "id": 1, "hint": "등에 커다란 씨앗을 짊어지고 있어."},
    {"name": "잠만보", "id": 143, "hint": "먹고 자는 것을 제일 좋아하는 뚱뚱한 포켓몬이야."},
    {"name": "뮤", "id": 151, "hint": "모든 포켓몬의 유전자를 가졌다고 전해지는 환상의 포켓몬이야."}
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
    st.title("⚡ 가족 초청 퀴즈 대회 ⚡")
    pokemon_img = os.path.join(os.path.dirname(os.path.abspath(__file__)), "포켓몬스터.jpg")
    if os.path.exists(pokemon_img):
        st.image(pokemon_img, use_column_width=True)
    st.markdown("스크린의 문제를 보고 가장 먼저 정답을 맞혀보세요!")
    
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

    current_pokemon = pokemon_db[current_q_idx]
    
    st.title(f"🔍 [문제 {current_q_idx + 1}] 이게 누구게?")
    
    # 1. 메인 이미지 표시 구역
    with st.container():
        display_img = get_pokemon_image(current_pokemon["id"], state["zoom_level"])
        if display_img:
            st.image(display_img, use_column_width=True)
            
        if state["zoom_level"] == 3:
            st.success(f"정답은 '{current_pokemon['name']}' 였습니다! 🎉")

    st.markdown("---")
    
    # 2. 진행자 컨트롤 패널
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
            state["current_q"] += 1
            state["zoom_level"] = 1 # 다음 문제는 다시 초근접으로
            save_state(state)
            st.rerun()

    st.markdown("---")
    
    # 3. 실시간 순위판 (현재 문제 정답자)
    st.subheader(f"🏆 {current_q_idx + 1}번 문제 정답자 랭킹")
    if st.button("🔄 누가 제일 빨랐을까요~?"):
        st.rerun()
        
    q_key = str(current_q_idx)
    submissions = state["submissions"].get(q_key, [])
    hall_of_fame = state["hall_of_fame"]
    
    if not submissions:
        st.write("아직 정답자가 없습니다...")
    else:
        # 이미 제출된 기록을 화면에 순서대로 표시
        rank = 1
        for sub in submissions:
            user_info = f"{sub['name']} ({sub['id'].split('_')[1]})"
            
            # 이미 1등을 해서 명예의 전당에 있는 사람은 회색 처리
            if sub['id'] in hall_of_fame:
                st.markdown(f"🌟 [명예의 전당] {user_info} - 정답 제출!")
            else:
                if rank == 1:
                    st.success(f"🥇 1등: {user_info} 🎁 (현재 1등!)")
                    # 1등에게 선물 주고 명예의 전당으로 보내는 버튼
                    if st.button(f"'{sub['name']}'님 명예의 전당 등록 및 1등 제외", key=f"hof_{sub['id']}"):
                        state["hall_of_fame"].append(sub['id'])
                        save_state(state)
                        st.rerun()
                elif rank == 2:
                    st.warning(f"🥈 2등: {user_info}")
                else:
                    st.write(f"🔹 {rank}등: {user_info}")
                rank += 1

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
        
    current_pokemon = pokemon_db[current_q_idx]
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