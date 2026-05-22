import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import streamlit.components.v1 as components

st.set_page_config(page_title="포켓몬 퀴즈 (발표용)", page_icon="⚡", layout="wide")

# ── 배경음악 ──
_MUSIC_URL = (
    "https://raw.githubusercontent.com/dalia8503-oss/lng_0517/main/"
    "%EC%9A%B0%EB%A6%AC%EB%8A%94%20%EB%AA%A8%EB%91%90%20%EC%B9%9C%EA%B5%AC.mp3"
)
components.html(f"""
    <style>body{{margin:0;padding:4px;background:transparent;}}
    #btn{{display:none;padding:7px 16px;background:#2563eb;color:#fff;
          border:none;border-radius:20px;cursor:pointer;font-size:13px;}}</style>
    <audio id="bgm" loop><source src="{_MUSIC_URL}" type="audio/mp3"></audio>
    <button id="btn" onclick="document.getElementById('bgm').play();this.style.display='none';">
      🎵 음악 켜기</button>
    <script>
      document.getElementById('bgm').play().catch(function(){{
        document.getElementById('btn').style.display='inline-block';
      }});
    </script>
""", height=50)

# ── 포켓몬 데이터 ──
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
    {"name": "글레이시아","id": 471, "hint": "주변의 공기를 얼려버리는 이브이의 얼음 진화형."},
    {"name": "마기라스",  "id": 248, "hint": "산을 무너뜨릴 만큼 강한 바위, 악 타입 포켓몬."},
    {"name": "보만다",    "id": 373, "hint": "하늘을 날고 싶다는 소원이 이루어져 날개가 생긴 드래곤."},
    {"name": "메타그로스","id": 376, "hint": "4개의 뇌를 가져서 슈퍼컴퓨터보다 똑똑한 강철 포켓몬!"},
    {"name": "가이오가",  "id": 382, "hint": "바다를 넓혔다고 전해지는 전설의 포켓몬이야."},
    {"name": "그란돈",    "id": 383, "hint": "땅을 넓혔다고 전해지는 거대한 전설의 포켓몬."},
    {"name": "디아루가",  "id": 483, "hint": "시간을 조종할 수 있는 전설의 포켓몬!"},
    {"name": "펄기아",    "id": 484, "hint": "공간을 일그러뜨릴 수 있는 전설의 포켓몬!"},
    {"name": "기라티나",  "id": 487, "hint": "깨어진 세계에 살고 있는 신비한 전설의 포켓몬."},
    {"name": "아르세우스","id": 493, "hint": "포켓몬 세계를 창조했다고 전해지는 신 같은 포켓몬이야."},
    {"name": "조로아크",  "id": 571, "hint": "다른 사람이나 포켓몬의 모습으로 둔갑할 수 있어."},
    {"name": "푸린",      "id": 39,  "hint": "동그랗고 귀여워. 노래를 부르면 모두 잠들어버려!"},
    {"name": "고라파덕",  "id": 54,  "hint": "항상 머리를 감싸 쥐고 있는 오리 포켓몬."},
    {"name": "야돈",      "id": 79,  "hint": "항상 멍~하니 꼬리를 물에 담그고 있어."},
    {"name": "잉어킹",    "id": 129, "hint": "파닥파닥 뛰기만 하지만 진화하면 아주 무서워져."},
    {"name": "갸라도스",  "id": 130, "hint": "잉어킹이 진화한 아주 사납고 거대한 물의 드래곤!"},
    {"name": "토게피",    "id": 175, "hint": "알껍데기를 입고 있는 작고 귀여운 포켓몬이야."},
]

# ── 세션 상태 초기화 ──
if "q_idx" not in st.session_state:
    st.session_state.q_idx = 0
if "zoom" not in st.session_state:
    st.session_state.zoom = 1
if "show_hint" not in st.session_state:
    st.session_state.show_hint = False

@st.cache_data
def get_pokemon_image(pokemon_id, zoom_level):
    url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pokemon_id}.png"
    try:
        response = requests.get(url, timeout=5)
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(bg, img).convert("RGB")
        w, h = img.size
        if zoom_level == 1:
            return img.crop((w * 0.425, h * 0.425, w * 0.575, h * 0.575))
        elif zoom_level == 2:
            return img.crop((w * 0.3, h * 0.3, w * 0.7, h * 0.7))
        return img
    except Exception:
        return None

# ── 퀴즈 종료 ──
if st.session_state.q_idx >= len(pokemon_db):
    st.title("🎉 모든 문제가 끝났습니다!")
    if st.button("처음부터 다시"):
        st.session_state.q_idx = 0
        st.session_state.zoom = 1
        st.session_state.show_hint = False
        st.rerun()
    st.stop()

pokemon = pokemon_db[st.session_state.q_idx]

# ── 레이아웃 ──
left, right = st.columns([3, 1])

with left:
    # 정답 공개 배너
    if st.session_state.zoom == 3:
        st.markdown(
            f"<div style='background:#166534;color:#bbf7d0;border-radius:10px;"
            f"padding:8px 16px;font-size:1.3rem;font-weight:700;margin-bottom:8px;'>"
            f"🎉 정답: {pokemon['name']}</div>",
            unsafe_allow_html=True
        )

    st.title(f"🔍 [문제 {st.session_state.q_idx + 1} / {len(pokemon_db)}] 이게 누구게?")

    img = get_pokemon_image(pokemon["id"], st.session_state.zoom)
    if img:
        img_col, _ = st.columns([3.2, 1.8])
        with img_col:
            st.image(img, use_column_width=True)

    if st.session_state.show_hint:
        st.info(f"💡 힌트: {pokemon['hint']}")

    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🔍 조금만 더 보여줄까요~?"):
            if st.session_state.zoom < 3:
                st.session_state.zoom += 1
                st.session_state.show_hint = False
                st.rerun()
    with col2:
        if st.button("💡 힌트 좀 드릴까요~?!"):
            st.session_state.show_hint = True
            st.rerun()
    with col3:
        if st.button("▶️ 다음은 누구일까요?!"):
            st.session_state.q_idx += 1
            st.session_state.zoom = 1
            st.session_state.show_hint = False
            st.rerun()
    with col4:
        if st.button("🔄 처음으로"):
            st.session_state.q_idx = 0
            st.session_state.zoom = 1
            st.session_state.show_hint = False
            st.rerun()

with right:
    st.markdown("### 진행 현황")
    st.metric("현재 문제", f"{st.session_state.q_idx + 1} / {len(pokemon_db)}")
    progress = st.session_state.q_idx / len(pokemon_db)
    st.progress(progress)
    st.markdown("---")
    st.markdown("**남은 문제**")
    remaining = len(pokemon_db) - st.session_state.q_idx - 1
    st.metric("", f"{remaining}문제")
