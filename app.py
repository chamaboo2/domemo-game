import random
from collections import Counter
from math import comb

import streamlit as st
from streamlit_mic_recorder import speech_to_text

st.set_page_config(
    page_title="DOMEMO Battle",
    page_icon="🎲",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# Constants
# -----------------------------
TILE_COUNTS = {n: n for n in range(1, 8)}
TOTAL_TILES = sum(TILE_COUNTS.values())
HAND_SIZE = 7
FACE_UP_SIZE = 7
HIDDEN_SIZE = 7

# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f7f3ea 0%, #eee7d8 100%);
    }
    .block-container {
        max-width: 760px;
        padding-top: 0.7rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3, p, div, button {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .game-title {
        text-align: center;
        font-size: clamp(2.2rem, 8vw, 3.4rem);
        font-weight: 900;
        letter-spacing: 0.03em;
        margin-bottom: 0.15rem;
        color: #2b2925;
    }
    .sub-title {
        text-align: center;
        font-size: clamp(1.05rem, 4.3vw, 1.35rem);
        font-weight: 700;
        color: #655f57;
        margin-bottom: 0.9rem;
    }
    .panel {
        background: rgba(255,255,255,0.86);
        border: 2px solid rgba(87,77,62,0.14);
        border-radius: 22px;
        padding: 16px 12px;
        margin: 10px 0;
        box-shadow: 0 7px 20px rgba(72,62,48,0.06);
    }
    .panel-label {
        font-size: clamp(1.05rem, 4vw, 1.3rem);
        color: #5d574f;
        font-weight: 900;
        margin-bottom: 10px;
        text-align: center;
    }
    .tiles {
        display: flex;
        flex-wrap: wrap;
        gap: 9px;
        justify-content: center;
        align-items: center;
        min-height: 70px;
    }
    .tile {
        width: clamp(50px, 14vw, 62px);
        height: clamp(66px, 18vw, 82px);
        border-radius: 12px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: clamp(1.8rem, 8vw, 2.5rem);
        font-weight: 900;
        border: 3px solid #4c463d;
        background: #fffdf8;
        color: #2b2925;
        box-shadow: 0 5px 0 #c9c0b1;
        margin: 2px;
    }
    .tile.unknown {
        background: #4d4b47;
        color: #f7f3ea;
        border-color: #383632;
        box-shadow: 0 5px 0 #252421;
    }
    .tile.faceup {
        background: #f2e3bd;
        border-color: #8c7145;
        box-shadow: 0 5px 0 #c5aa77;
    }
    .tile.hidden {
        background: repeating-linear-gradient(45deg,#6d655c,#6d655c 6px,#5e574f 6px,#5e574f 12px);
        color: white;
        border-color: #49433d;
        box-shadow: 0 5px 0 #302c28;
    }
    .status {
        text-align: center;
        border-radius: 18px;
        padding: 16px 12px;
        font-size: clamp(1.2rem, 5vw, 1.65rem);
        line-height: 1.45;
        font-weight: 900;
        margin: 12px 0;
        background: #fff7de;
        border: 2px solid #e6d29e;
        color: #40371f;
    }
    .score-row {
        display: flex;
        justify-content: center;
        gap: 24px;
        margin: 10px 0 12px;
        font-size: clamp(1.05rem, 4.5vw, 1.35rem);
        font-weight: 900;
        color: #4f4942;
    }
    .voice-title {
        text-align: center;
        font-size: clamp(1.25rem, 5vw, 1.6rem);
        font-weight: 900;
        margin: 12px 0 6px;
        color: #2b2925;
    }
    .voice-result {
        text-align: center;
        font-size: clamp(1.2rem, 5vw, 1.55rem);
        font-weight: 900;
        padding: 10px;
        margin: 8px 0;
        border-radius: 14px;
        background: #eef7e9;
        color: #294622;
    }
    .voice-error {
        text-align: center;
        font-size: clamp(1rem, 4.3vw, 1.25rem);
        font-weight: 800;
        padding: 10px;
        margin: 8px 0;
        border-radius: 14px;
        background: #fff0ec;
        color: #71382d;
    }
    .choose-title {
        text-align: center;
        font-size: clamp(1.2rem, 5vw, 1.55rem);
        font-weight: 900;
        margin: 14px 0 8px;
    }
    .log-item {
        padding: 10px 11px;
        margin: 6px 0;
        background: #f8f5ef;
        border-radius: 10px;
        font-size: 1rem;
        color: #514c45;
    }
    .winner {
        text-align: center;
        font-size: clamp(1.8rem, 8vw, 2.7rem);
        font-weight: 900;
        padding: 22px 14px;
        border-radius: 20px;
        background: #fff2be;
        border: 2px solid #e0bd55;
        color: #4a3c12;
        margin: 12px 0;
    }
    div[data-testid="stButton"] button {
        border-radius: 16px;
        min-height: 64px;
        font-size: clamp(1.25rem, 5vw, 1.7rem);
        font-weight: 900;
    }
    div[data-testid="stButton"] button[kind="primary"] {
        background: #292724;
        border-color: #292724;
    }
    /* streamlit-mic-recorder のボタンを子ども向けに大きくする */
    iframe[title="streamlit_mic_recorder.streamlit_mic_recorder"] {
        min-height: 76px !important;
    }
    .small-note {
        color: #6e675f;
        font-size: 0.95rem;
        text-align: center;
        margin-top: 10px;
        font-weight: 700;
    }
    @media (max-width: 520px) {
        .block-container { padding-left: 0.65rem; padding-right: 0.65rem; }
        .panel { padding-left: 8px; padding-right: 8px; }
        .tiles { gap: 6px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def tile_html(value, style="normal"):
    label = "?" if value is None else str(value)
    css = "tile"
    if style == "unknown":
        css += " unknown"
    elif style == "faceup":
        css += " faceup"
    elif style == "hidden":
        css += " hidden"
    return f'<span class="{css}">{label}</span>'


def tiles_html(values, style="normal"):
    return '<div class="tiles">' + "".join(tile_html(v, style) for v in values) + "</div>"


def parse_spoken_number(text):
    """日本語の音声認識結果から1〜7を取り出す。"""
    if not text:
        return None

    normalized = str(text).strip().lower()
    normalized = normalized.translate(str.maketrans("１２３４５６７", "1234567"))

    # 数字が直接含まれている場合を最優先する。
    for n in range(1, 8):
        if str(n) in normalized:
            return n

    # 子どもが「ごです」「ななばん」のように言っても拾えるよう、
    # よく付く語尾だけを除いてから完全一致で判定する。
    cleaned = normalized.replace(" ", "").replace("　", "")
    for suffix in ("です", "だよ", "かな", "ばん", "番", "を", "。", "、", "！", "!"):
        cleaned = cleaned.replace(suffix, "")

    variants = {
        1: ("一", "いち", "イチ"),
        2: ("二", "に", "ニ"),
        3: ("三", "さん", "サン"),
        4: ("四", "よん", "ヨン", "し", "シ"),
        5: ("五", "ご", "ゴ"),
        6: ("六", "ろく", "ロク"),
        7: ("七", "なな", "ナナ", "しち", "シチ"),
    }
    for n, words in variants.items():
        if cleaned in words:
            return n
    return None


def new_game():
    bag = []
    for number, count in TILE_COUNTS.items():
        bag.extend([number] * count)
    random.shuffle(bag)

    st.session_state.user_hand = sorted(bag[:HAND_SIZE])
    st.session_state.cpu_hand = sorted(bag[HAND_SIZE : HAND_SIZE * 2])
    st.session_state.face_up = sorted(
        bag[HAND_SIZE * 2 : HAND_SIZE * 2 + FACE_UP_SIZE]
    )
    st.session_state.hidden = sorted(bag[-HIDDEN_SIZE:])
    st.session_state.turn = "user"
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.log = ["ゲーム開始。あなたの番です。"]
    st.session_state.cpu_failed_numbers = set()
    st.session_state.user_failed_numbers = set()
    st.session_state.turn_no = 1
    st.session_state.voice_feedback = None


def add_log(message):
    st.session_state.log.insert(0, message)
    st.session_state.log = st.session_state.log[:12]


def remove_one(hand, number):
    if number in hand:
        hand.remove(number)
        return True
    return False


def check_winner():
    if len(st.session_state.user_hand) == 0:
        st.session_state.game_over = True
        st.session_state.winner = "user"
        add_log("あなたの手札が0枚になりました。あなたの勝ちです。")
        return True
    if len(st.session_state.cpu_hand) == 0:
        st.session_state.game_over = True
        st.session_state.winner = "cpu"
        add_log("CPUの手札が0枚になりました。CPUの勝ちです。")
        return True
    return False


def user_guess(number):
    if st.session_state.game_over or st.session_state.turn != "user":
        return

    if remove_one(st.session_state.user_hand, number):
        st.session_state.face_up.append(number)
        st.session_state.face_up.sort()
        add_log(f"あなた：『{number}』 → 正解。続けてあなたの番です。")
        st.session_state.user_failed_numbers.discard(number)
        check_winner()
        return

    add_log(f"あなた：『{number}』 → ありません。CPUの番です。")
    st.session_state.user_failed_numbers.add(number)
    st.session_state.turn = "cpu"
    st.session_state.turn_no += 1


def cpu_weights():
    """CPU自身が各数字を1枚以上持つ確率を計算する。"""
    visible = Counter(st.session_state.user_hand + st.session_state.face_up)
    weights = {}
    hand_size = len(st.session_state.cpu_hand)
    hidden_size = len(st.session_state.hidden)
    unknown_pool_size = hand_size + hidden_size

    for n in range(1, 8):
        remaining_unknown = max(0, TILE_COUNTS[n] - visible[n])
        if n in st.session_state.cpu_failed_numbers:
            weights[n] = 0.0
            continue
        if hand_size <= 0 or remaining_unknown <= 0 or unknown_pool_size <= 0:
            weights[n] = 0.0
            continue

        # CPUから見た未知領域は「CPU自身の手札 + 伏せ札」。
        # その中からhand_size枚が自分の手札なので、
        # 1枚以上その数字を持つ確率を超幾何分布で求める。
        not_this_number = unknown_pool_size - remaining_unknown
        if not_this_number < hand_size:
            probability = 1.0
        else:
            probability = 1.0 - (
                comb(not_this_number, hand_size) / comb(unknown_pool_size, hand_size)
            )
        weights[n] = probability

    return weights

def choose_cpu_guess():
    weights = cpu_weights()
    best = max(weights.values()) if weights else 0
    candidates = [n for n, w in weights.items() if w == best and w > 0]

    if not candidates:
        # Defensive fallback; normally unreachable before the game ends.
        candidates = list(range(1, 8))

    # Random tie-break prevents identical play every game while preserving
    # the same inference quality.
    return random.choice(candidates)


def cpu_play_until_miss():
    """2人戦ルール：CPUは正解中は続行し、不正解で手番を渡す。"""
    safety = 0
    while (
        not st.session_state.game_over
        and st.session_state.turn == "cpu"
        and safety < 20
    ):
        safety += 1
        guess = choose_cpu_guess()
        if remove_one(st.session_state.cpu_hand, guess):
            st.session_state.face_up.append(guess)
            st.session_state.face_up.sort()
            add_log(f"CPU：『{guess}』 → 正解。CPUは続けて推理します。")
            st.session_state.cpu_failed_numbers.discard(guess)
            if check_winner():
                return
            continue

        add_log(f"CPU：『{guess}』 → ありません。あなたの番です。")
        st.session_state.cpu_failed_numbers.add(guess)
        st.session_state.turn = "user"
        st.session_state.turn_no += 1
        return


# -----------------------------
# Session initialization
# -----------------------------
if "user_hand" not in st.session_state:
    new_game()

# CPUの手番は画面操作を追加せず自動処理する。
if st.session_state.turn == "cpu" and not st.session_state.game_over:
    cpu_play_until_miss()

# -----------------------------
# Header
# -----------------------------
st.markdown('<div class="game-title">DOMEMO BATTLE</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">みえている すうじから、じぶんの すうじを あてよう</div>',
    unsafe_allow_html=True,
)

# CPU area
st.markdown('<div class="panel">', unsafe_allow_html=True)
st.markdown(
    f'<div class="panel-label">CPUの手札　残り {len(st.session_state.cpu_hand)} 枚</div>',
    unsafe_allow_html=True,
)
st.markdown(tiles_html(st.session_state.cpu_hand), unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Center board
st.markdown('<div class="panel">', unsafe_allow_html=True)
st.markdown(
    f'<div class="panel-label">場に見えているタイル　{len(st.session_state.face_up)} 枚</div>',
    unsafe_allow_html=True,
)
st.markdown(tiles_html(st.session_state.face_up, "faceup"), unsafe_allow_html=True)
st.markdown(
    f'<div class="panel-label" style="margin-top:14px;">伏せ札　{len(st.session_state.hidden)} 枚</div>',
    unsafe_allow_html=True,
)
st.markdown(
    tiles_html([None] * len(st.session_state.hidden), "hidden"),
    unsafe_allow_html=True,
)
st.markdown('</div>', unsafe_allow_html=True)

# Player area
st.markdown('<div class="panel">', unsafe_allow_html=True)
st.markdown(
    f'<div class="panel-label">あなたの手札　残り {len(st.session_state.user_hand)} 枚</div>',
    unsafe_allow_html=True,
)
st.markdown(
    tiles_html([None] * len(st.session_state.user_hand), "unknown"),
    unsafe_allow_html=True,
)
st.markdown('</div>', unsafe_allow_html=True)

# Status
if st.session_state.game_over:
    result = "あなたの勝ち" if st.session_state.winner == "user" else "CPUの勝ち"
    st.markdown(f'<div class="winner">{result}</div>', unsafe_allow_html=True)
else:
    status = "あなたのばん！ 1〜7から えらんでね" if st.session_state.turn == "user" else "CPUが かんがえています"
    st.markdown(f'<div class="status">{status}</div>', unsafe_allow_html=True)

st.markdown(
    f'<div class="score-row"><span>あなた {len(st.session_state.user_hand)}枚</span><span>CPU {len(st.session_state.cpu_hand)}枚</span></div>',
    unsafe_allow_html=True,
)

# User controls
if not st.session_state.game_over and st.session_state.turn == "user":
    st.markdown('<div class="voice-title">🎤 こえで こたえる</div>', unsafe_allow_html=True)
    spoken_text = speech_to_text(
        language="ja-JP",
        start_prompt="🎤 おして はなす",
        stop_prompt="⏹️ おわり",
        just_once=True,
        use_container_width=True,
        key="domemo_voice",
    )

    if spoken_text:
        spoken_number = parse_spoken_number(spoken_text)
        if spoken_number is not None:
            st.session_state.voice_feedback = f"『{spoken_number}』と きこえたよ"
            user_guess(spoken_number)
            st.rerun()
        else:
            st.session_state.voice_feedback = "1から7の すうじを いってね"

    if st.session_state.voice_feedback:
        css_class = "voice-result" if "きこえた" in st.session_state.voice_feedback else "voice-error"
        st.markdown(
            f'<div class="{css_class}">{st.session_state.voice_feedback}</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="choose-title">👇 または すうじを おす</div>', unsafe_allow_html=True)

    # スマホでも押しやすいように4個 + 3個の2段にする。
    top_cols = st.columns(4)
    for idx, number in enumerate(range(1, 5)):
        with top_cols[idx]:
            if st.button(str(number), key=f"guess_{number}", use_container_width=True, type="primary"):
                st.session_state.voice_feedback = None
                user_guess(number)
                st.rerun()

    bottom_cols = st.columns(3)
    for idx, number in enumerate(range(5, 8)):
        with bottom_cols[idx]:
            if st.button(str(number), key=f"guess_{number}", use_container_width=True, type="primary"):
                st.session_state.voice_feedback = None
                user_guess(number)
                st.rerun()

# History
with st.expander("対戦履歴を見る", expanded=False):
    for item in st.session_state.log:
        st.markdown(f'<div class="log-item">{item}</div>', unsafe_allow_html=True)

# Rule / reset controls
col_a, col_b = st.columns(2)
with col_a:
    if st.button("新しいゲーム", use_container_width=True):
        new_game()
        st.rerun()
with col_b:
    with st.popover("遊び方"):
        st.markdown(
            """
            **目的**  
            自分には見えない手札の数字を当て、先に手札を0枚にします。

            **このMVPの2人用セット**  
            - 1は1枚、2は2枚、…7は7枚、合計28枚
            - あなた：7枚
            - CPU：7枚
            - 表向きの場札：7枚
            - 伏せ札：7枚

            **手番**  
            1〜7から、自分の手札にあると思う数字を1つ選びます。  
            当たればその数字を1枚公開して手札から減らし、続けて宣言できます。  
            外れたときに手番がCPUへ移ります。
            """
        )

st.markdown(
    '<div class="small-note">MVP：ユーザー1人 vs CPU1人。CPUは見えているタイル数から推理します。</div>',
    unsafe_allow_html=True,
)
