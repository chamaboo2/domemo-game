from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parent
p = ROOT / 'app.py'
s = p.read_text(encoding='utf-8')
ast.parse(s)

checks = [
    ('28 tile definition', 'TOTAL_TILES = sum(TILE_COUNTS.values())' in s and 'TILE_COUNTS = {n: n for n in range(1, 8)}' in s),
    ('7 tile hand', 'HAND_SIZE = 7' in s),
    ('7 face up', 'FACE_UP_SIZE = 7' in s),
    ('7 hidden', 'HIDDEN_SIZE = 7' in s),
    ('human hand concealed', 'tiles_html([None] * len(st.session_state.user_hand), "unknown")' in s),
    ('cpu hand visible', 'tiles_html(st.session_state.cpu_hand)' in s),
    ('correct human guess keeps turn', '続けてあなたの番です' in s),
    ('wrong human guess passes turn', 'st.session_state.turn = "cpu"' in s),
    ('cpu continues until miss', 'def cpu_play_until_miss()' in s and 'continue' in s),
    ('cpu probability uses hypergeometric', 'comb(not_this_number, hand_size)' in s),
    ('winner detection', 'len(st.session_state.user_hand) == 0' in s and 'len(st.session_state.cpu_hand) == 0' in s),
    ('speech input imported', 'from streamlit_mic_recorder import speech_to_text' in s),
    ('Japanese speech recognition', 'language="ja-JP"' in s),
    ('spoken number parser', 'def parse_spoken_number(text)' in s),
    ('voice fallback buttons retained', 'guess_1' not in s and 'key=f"guess_{number}"' in s),
    ('large child UI', 'min-height: 64px' in s and 'font-size: clamp(1.8rem, 8vw, 2.5rem)' in s),
    ('mobile two-row number buttons', 'top_cols = st.columns(4)' in s and 'bottom_cols = st.columns(3)' in s),
    ('history provided', '対戦履歴を見る' in s),
    ('new game provided', '新しいゲーム' in s),
    ('rules provided', '遊び方' in s),
]

# 音声変換ロジックだけをASTから取り出して単体テストする。
module = ast.parse(s)
func_node = next(n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == 'parse_spoken_number')
mini = ast.Module(body=[func_node], type_ignores=[])
ns = {}
exec(compile(mini, '<voice-parser>', 'exec'), ns)
parse = ns['parse_spoken_number']
voice_cases = {
    '1': 1, '５': 5, 'いち': 1, 'に': 2, 'さん': 3,
    'よん': 4, 'し': 4, 'ご': 5, 'ろく': 6,
    'なな': 7, 'しち': 7, 'ごです': 5, '七番': 7,
    'わからない': None,
}
voice_failed = [(text, expected, parse(text)) for text, expected in voice_cases.items() if parse(text) != expected]
if voice_failed:
    raise SystemExit(f'VOICE PARSER FAIL: {voice_failed}')

req = (ROOT / 'requirements.txt').read_text(encoding='utf-8')
if 'streamlit-mic-recorder==0.0.8' not in req:
    raise SystemExit('requirements missing streamlit-mic-recorder')

for i in range(1, 11):
    failed = [name for name, ok in checks if not ok]
    print(f'REVIEW {i}: ' + ('PASS' if not failed else 'FAIL: ' + ', '.join(failed)))
    if failed:
        raise SystemExit(1)
