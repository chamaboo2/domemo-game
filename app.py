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
        padding-top: 0.25rem;
        padding-bottom: 1.1rem;
    }
    h1, h2, h3, p, div, button {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .game-title {
        text-align: center;
        font-size: clamp(2rem, 7vw, 2.7rem);
        font-weight: 900;
        letter-spacing: 0.05em;
        margin: 0 0 0.15rem;
        color: #2b2925;
        line-height: 1.05;
    }
    .status {
        text-align: center;
        border-radius: 14px;
        padding: 9px 8px;
        font-size: clamp(1.15rem, 4.8vw, 1.45rem);
        line-height: 1.25;
        font-weight: 900;
        margin: 5px 0 7px;
        background: #fff7de;
        border: 2px solid #e6d29e;
        color: #40371f;
    }
    .game-section {
        margin: 5px 0 7px;
        text-align: center;
    }
    .panel-label {
        font-size: clamp(1.05rem, 4.4vw, 1.3rem);
        color: #514b43;
        font-weight: 900;
        margin-bottom: 4px;
        text-align: center;
        line-height: 1.15;
    }
    .tiles {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        justify-content: center;
        align-items: center;
    }
    .tile {
        width: clamp(34px, 9.5vw, 44px);
        height: clamp(46px, 12vw, 56px);
        border-radius: 9px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: clamp(1.5rem, 6.3vw, 2rem);
        font-weight: 900;
        border: 2px solid #4c463d;
        background: #fffdf8;
        color: #2b2925;
        box-shadow: 0 3px 0 #c9c0b1;
        margin: 1px;
        box-sizing: border-box;
    }
    .tile.unknown {
        width: clamp(29px, 8vw, 37px);
        height: clamp(36px, 9.5vw, 44px);
        font-size: clamp(1.25rem, 5vw, 1.55rem);
        background: #4d4b47;
        color: #f7f3ea;
        border-color: #383632;
        box-shadow: 0 3px 0 #252421;
    }
    .tile.faceup {
        background: #f2e3bd;
        border-color: #8c7145;
        box-shadow: 0 3px 0 #c5aa77;
    }
    .hidden-info {
        text-align: center;
        margin-top: 3px;
        font-size: clamp(0.95rem, 3.8vw, 1.08rem);
        font-weight: 800;
        color: #6a635b;
    }
    .voice-title {
        text-align: center;
        font-size: clamp(1.08rem, 4.5vw, 1.3rem);
        font-weight: 900;
        margin: 7px 0 2px;
        color: #2b2925;
    }
    .voice-result {
        text-align: center;
        font-size: clamp(1.05rem, 4.4vw, 1.25rem);
        font-weight: 900;
        padding: 7px;
        margin: 5px 0;
        border-radius: 12px;
        background: #eef7e9;
        color: #294622;
    }
    .voice-error {
        text-align: center;
        font-size: clamp(1rem, 4.2vw, 1.18rem);
        font-weight: 800;
        padding: 7px;
        margin: 5px 0;
        border-radius: 12px;
        background: #fff0ec;
        color: #71382d;
    }
    .choose-title {
        text-align: center;
        font-size: clamp(1.15rem, 4.8vw, 1.4rem);
        font-weight: 900;
        margin: 7px 0 4px;
        color: #2b2925;
    }
    .log-item {
        padding: 9px 10px;
        margin: 5px 0;
        background: #f8f5ef;
        border-radius: 10px;
        font-size: 1rem;
        color: #514c45;
    }
    .winner {
        text-align: center;
        font-size: clamp(1.7rem, 7vw, 2.3rem);
        font-weight: 900;
        padding: 14px 10px;
        border-radius: 16px;
        background: #fff2be;
        border: 2px solid #e0bd55;
        color: #4a3c12;
        margin: 7px 0;
    }
    div[data-testid="stButton"] button {
        border-radius: 14px;
        min-height: 58px;
        font-size: clamp(1.55rem, 6vw, 2rem);
        font-weight: 900;
        padding-top: 0.25rem;
        padding-bottom: 0.25rem;
    }
    div[data-testid="stButton"] button[kind="primary"] {
        background: #292724;
        border-color: #292724;
    }
    iframe[title="streamlit_mic_recorder.streamlit_mic_recorder"] {
        min-height: 68px !important;
    }
    .small-note {
        color: #6e675f;
        font-size: 0.82rem;
        text-align: center;
        margin-top: 6px;
        font-weight: 700;
    }
    @media (max-width: 520px) {
        .block-container {
            padding-left: 0.45rem;
            padding-right: 0.45rem;
        }
        .tiles { gap: 3px; }
        div[data-testid="stVerticalBlock"] { gap: 0.25rem; }
        div[data-testid="stHorizontalBlock"] { gap: 0.35rem; }
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
        add_log("じぶんのカードが0まい。あなたのかちです。")
        return True
    if len(st.session_state.cpu_hand) == 0:
        st.session_state.game_over = True
        st.session_state.winner = "cpu"
        add_log("あいてのカードが0まい。あいてのかちです。")
        return True
    return False


def user_guess(number):
    if st.session_state.game_over or st.session_state.turn != "user":
        return

    if remove_one(st.session_state.user_hand, number):
        st.session_state.face_up.append(number)
        st.session_state.face_up.sort()
        add_log(f"あなた：『{number}』 → あたり。つづけてあなたのばんです。")
        st.session_state.user_failed_numbers.discard(number)
        check_winner()
        return

    add_log(f"あなた：『{number}』 → なし。あいてのばんです。")
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
            add_log(f"あいて：『{guess}』 → あたり。つづけます。")
            st.session_state.cpu_failed_numbers.discard(guess)
            if check_winner():
                return
            continue

        add_log(f"あいて：『{guess}』 → なし。あなたのばんです。")
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
# Header / board / controls
# -----------------------------
st.markdown('<div class="game-title">DOMEMO</div>', unsafe_allow_html=True)

# いちばん大事な「だれのばんか」を最上部に置く。
if st.session_state.game_over:
    result = "あなたの かち！" if st.session_state.winner == "user" else "あいての かち"
    st.markdown(f'<div class="winner">{result}</div>', unsafe_allow_html=True)
else:
    status = "あなたのばん！" if st.session_state.turn == "user" else "あいてが かんがえています"
    st.markdown(f'<div class="status">{status}</div>', unsafe_allow_html=True)

# 相手のカード。HTMLを1回で描画し、余分な白い帯を作らない。
st.markdown(
    '<div class="game-section">'
    f'<div class="panel-label">あいてのカード　あと {len(st.session_state.cpu_hand)}まい</div>'
    f'{tiles_html(st.session_state.cpu_hand)}'
    '</div>',
    unsafe_allow_html=True,
)

# 推理に必要な公開カードは数字を省略しない。カード自体だけコンパクトにする。
st.markdown(
    '<div class="game-section">'
    f'<div class="panel-label">みえているカード　{len(st.session_state.face_up)}まい</div>'
    f'{tiles_html(st.session_state.face_up, "faceup")}'
    f'<div class="hidden-info">みえないカード　{len(st.session_state.hidden)}まい</div>'
    '</div>',
    unsafe_allow_html=True,
)

# 自分の数字は見せず、残り枚数だけを小さな「？」で示す。
st.markdown(
    '<div class="game-section">'
    f'<div class="panel-label">じぶんのカード　あと {len(st.session_state.user_hand)}まい</div>'
    f'{tiles_html([None] * len(st.session_state.user_hand), "unknown")}'
    '</div>',
    unsafe_allow_html=True,
)

# User controls
if not st.session_state.game_over and st.session_state.turn == "user":
    st.markdown('<div class="choose-title">どの すうじ？</div>', unsafe_allow_html=True)

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

    st.markdown('<div class="voice-title">こえでも こたえられるよ</div>', unsafe_allow_html=True)
    spoken_text = speech_to_text(
        language="ja-JP",
        start_prompt="🎤 はなす",
        stop_prompt="■ おわり",
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
            **もくひょう**  
            じぶんには見えないカードの数字をあてて、先に0まいにします。

            **このMVPの2人用セット**  
            - 1は1枚、2は2枚、…7は7枚、合計28枚
            - あなた：7まい
            - あいて：7まい
            - みえているカード：7まい
            - みえないカード：7まい

            **じゅんばん**  
            1〜7から、じぶんのカードにあると思う数字を1つえらびます。  
            あたったら、その数字が1まいへって、つづけてこたえられます。  
            はずれたら、あいてのばんです。
            """
        )

st.markdown(
    '<div class="small-note">1人 vs あいて。あいても、みえている数字から考えます。</div>',
    unsafe_allow_html=True,
)
