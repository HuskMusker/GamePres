import streamlit as st
import re
import json
import time
import pandas as pd
import streamlit.components.v1 as components
import base64
from pathlib import Path

# ------------------------------
# Функция для получения base64 изображения
# ------------------------------
@st.cache_data
def get_base64_image(image_path):
    """Читает локальный файл и возвращает base64-строку для data URI."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

# ------------------------------
# Настройка страницы
# ------------------------------
st.set_page_config(
    page_title="Цифровой куратор",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Вставка фонового изображения через base64
base64_img = get_base64_image("bg.png")  # файл bg.png должен быть в папке с приложением
if base64_img:
    bg_image_tag = f'<img class="bg-image" src="data:image/png;base64,{base64_img}" alt="background">'
else:
    # Если файл не найден – пустой тег (можно заменить на прозрачный пиксель)
    bg_image_tag = '<img class="bg-image" src="" alt="background">'

st.markdown(
    f"""
    <style>
    /* Фоновое изображение */
    .bg-image {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        opacity: 1;               /* изображение полностью видимо */
        z-index: -2;               /* позади оверлея и контента */
        object-fit: cover;
        pointer-events: none;
    }}
    /* Монохромный полупрозрачный слой ПЕРЕД фоновым изображением */
    .bg-overlay {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(17, 14, 31, 0.7);  /* монохромный (тёмно-фиолетовый) полупрозрачный фон */
        z-index: -1;               /* выше картинки, но ниже контента */
        pointer-events: none;
    }}
    </style>
    {bg_image_tag}
    <div class="bg-overlay"></div>
    """,
    unsafe_allow_html=True
)

# Якорь и скрипт для гарантированной прокрутки вверх при каждом rerun
st.markdown('<div id="top"></div>', unsafe_allow_html=True)
components.html("""
<script>
var el = document.getElementById('top');
if (el) el.scrollIntoView({behavior: 'instant'});
</script>
""", height=0)



# ------------------------------
# CSS (лёгкие подчёркнутые поля, улучшенная типографика)
# ------------------------------
st.markdown(
    """
<style>
:root {
    --bg-primary: #110E1F;
    --bg-card: rgba(255, 255, 255, 0.05);
    --bg-card-hover: rgba(255, 255, 255, 0.08);
    --border-card: rgba(255, 255, 255, 0.06);
    --text-primary: #FFFFFF;
    --text-secondary: #F0F0F8;
    --text-muted: #8A8AA8;
    --accent-green: #00BD63;
    --accent-cyan: #40C4FF;
    --shadow-card: 0 8px 30px rgba(0, 0, 0, 0.5);
    --shadow-card-hover: 0 12px 40px rgba(0, 0, 0, 0.7);
    --radius-card: 20px;
    --radius-button: 100px;
    --transition-speed: 0.25s;
    --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    /* Добавляем переменную для фона полей ввода */
    --input-bg: rgba(21, 28, 49, 1);
}

.stApp {
    background: var(--bg-primary);
    color: var(--text-primary);
    font-family: var(--font-family);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(24px); }
    to { opacity: 1; transform: translateY(0); }
}

.block-container {
    padding: 2.5rem 2rem;
    animation: fadeInUp 0.5s cubic-bezier(0.2, 0.9, 0.3, 1) forwards;
}

.main-header {
    font-size: 2.4rem;
    font-weight: 600;
    color: var(--accent-green);
    letter-spacing: -0.03em;
    margin-bottom: 0.5em;
    border-left: 5px solid var(--accent-cyan);
    padding-left: 1.2rem;
    line-height: 1.2;
}
h2, h3, h4 {
    font-weight: 500;
    letter-spacing: -0.01em;
}
.sub-header {
    font-size: 1.2rem;
    font-weight: 400;
    color: var(--text-secondary);
    margin-bottom: 1.5em;
}

/* Обёртка для центрирования всего ряда */
.sort-row-wrapper {
    display: flex;
    justify-content: center;      /* горизонтальное центрирование */
    margin: 0.5rem 0;            /* небольшой вертикальный отступ */
}
/* Отключаем растягивание st.columns на всю ширину */
.sort-row-wrapper .stHorizontalBlock {
    width: auto !important;
    flex: 0 0 auto !important;
}

.mission-card, .theory-card {
    background: var(--bg-card);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--border-card);
    border-radius: var(--radius-card);
    padding: 1.8rem 2rem;
    margin-bottom: 1.8rem;
    box-shadow: var(--shadow-card);
    transition: all var(--transition-speed) cubic-bezier(0.2, 0.9, 0.3, 1);
}
.mission-card:hover, .theory-card:hover {
    background: var(--bg-card-hover);
    box-shadow: var(--shadow-card-hover);
    transform: translateY(-3px);
}
.theory-card {
    border-left: 5px solid var(--accent-cyan);
}
.mission-card h3, .theory-card h3 {
    color: var(--accent-cyan);
    font-weight: 500;
    margin-top: 0;
    font-size: 1.3rem;
}

.stButton button {
    background: var(--accent-green);
    color: #000;
    border: none;
    padding: 0.7rem 2rem;
    border-radius: var(--radius-button);
    font-weight: 600;
    font-size: 0.95rem;
    cursor: pointer;
    transition: all var(--transition-speed) cubic-bezier(0.2, 0.9, 0.3, 1);
    box-shadow: 0 2px 12px rgba(0, 230, 118, 0.25);
    letter-spacing: 0.02em;
    line-height: 1.4;
}
.stButton button:hover:not(:disabled) {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 6px 24px rgba(0, 230, 118, 0.35);
    background: #00C853;
}
.stButton button:active:not(:disabled) {
    transform: scale(0.97);
}
.stButton button:disabled {
    opacity: 0.4;
    cursor: not-allowed;
    box-shadow: none;
}

/* Кнопка "Назад" в nav-container */
.nav-container > div:first-child .stButton button {
    background: rgba(255, 255, 255, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.5);
    color: #FFFFFF;
    box-shadow: none;
}
.nav-container > div:first-child .stButton button:hover {
    background: rgba(255, 255, 255, 0.25);
    border-color: #FFFFFF;
    color: #FFFFFF;
}

section[data-testid="stSidebar"] {
    background: rgba(11, 10, 22, 0.92);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-right: 1px solid var(--border-card);
    padding: 1.5rem 0.5rem;
}
.sidebar-header {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--accent-green);
    margin-bottom: 0.75rem;
    padding-left: 0.5rem;
}
.stProgress > div > div {
    background: linear-gradient(90deg, var(--accent-cyan), var(--accent-green)) !important;
    border-radius: 100px;
    height: 6px !important;
}
section[data-testid="stSidebar"] .stButton button {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    text-align: left;
    padding: 0.5rem 0.8rem;
    border-radius: 12px;
    font-weight: 400;
    transition: all var(--transition-speed) cubic-bezier(0.2, 0.9, 0.3, 1);
    width: 100%;
    justify-content: flex-start;
    font-size: 0.95rem;
}
section[data-testid="stSidebar"] .stButton button:hover:not(:disabled) {
    background: var(--bg-card-hover);
    color: var(--text-primary);
    transform: translateX(4px);
}
section[data-testid="stSidebar"] .stButton button:disabled {
    opacity: 0.35;
    cursor: not-allowed;
    transform: none;
}

.nav-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 2.5rem;
    padding-top: 1.25rem;
    border-top: 1px solid var(--border-card);
}

p, li, .stMarkdown {
    color: var(--text-secondary);
    line-height: 1.7;
}
strong, b {
    color: var(--text-primary);
    font-weight: 600;
}
a {
    color: var(--accent-cyan);
    text-decoration: none;
    transition: color var(--transition-speed);
}
a:hover {
    color: var(--accent-green);
    text-decoration: underline;
}

.score-display {
    font-size: 1.6rem;
    font-weight: 600;
    color: var(--accent-green);
    margin: 0.7em 0 1em;
    letter-spacing: -0.01em;
}
.badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 215, 0, 0.12);
    color: #FFD54F;
    padding: 0.2rem 0.8rem;
    border-radius: 100px;
    font-weight: 600;
    font-size: 0.8rem;
    border: 1px solid rgba(255, 215, 0, 0.15);
}

.stRadio > div, .stCheckbox > div {
    margin-bottom: 0.6rem;
}
.stRadio label, .stCheckbox label {
    color: #FFFFFF !important;
    font-weight: 400;
}
.stSelectbox, .stTextArea, .stSlider {
    background: var(--bg-card);
    border-radius: 12px;
    padding: 0.2rem 0.4rem;
}
.streamlit-expanderHeader {
    color: var(--text-primary) !important;
    background: var(--bg-card) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border-card) !important;
    transition: all var(--transition-speed) cubic-bezier(0.2, 0.9, 0.3, 1);
}
.streamlit-expanderHeader:hover {
    background: var(--bg-card-hover) !important;
}
.streamlit-expanderContent {
    background: transparent !important;
    border: none !important;
    padding-top: 0.8rem !important;
}

/* 🔽 ИЗМЕНЁННЫЙ БЛОК: добавлен фон для полей ввода */
textarea, input[type="text"], input[type="password"], input[type="email"] {
    max-width: 100% !important;
    width: 100% !important;
    padding: 8px 0 !important;
    font-size: 0.95rem !important;
    line-height: 1.4 !important;
    background: var(--input-bg) !important;   /* <-- теперь фон не прозрачный */
    border: none !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.4) !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
    transition: all var(--transition-speed);
}
textarea:focus, input:focus {
    border-bottom-color: var(--accent-cyan) !important;
    outline: none !important;
    box-shadow: 0 1px 0 0 var(--accent-cyan) !important;
}
.stTextArea label, .stTextInput label {
    color: var(--text-secondary) !important;
    font-weight: 500;
    margin-bottom: 0.2rem;
}
.stTextArea textarea {
    min-height: 60px;
}
input::placeholder, textarea::placeholder {
    color: rgba(255, 255, 255, 0.5) !important;
}

::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: var(--bg-primary);
}
::-webkit-scrollbar-thumb {
    background: var(--text-muted);
    border-radius: 100px;
}
::-webkit-scrollbar-thumb:hover {
    background: var(--text-secondary);
}

div[data-testid="stAlert"] {
    border-left-width: 4px !important;
    border-left-style: solid !important;
    border-radius: 12px !important;
    border: none !important;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    background: var(--bg-card) !important;
}
div[data-testid="stAlert"][data-kind="success"] {
    border-left-color: var(--accent-green) !important;
}
div[data-testid="stAlert"][data-kind="error"] {
    border-left-color: #FF5252 !important;
}
div[data-testid="stAlert"][data-kind="warning"] {
    border-left-color: #FFC107 !important;
}
div[data-testid="stAlert"][data-kind="info"] {
    border-left-color: var(--accent-cyan) !important;
}

.bridge-block {
    background: rgba(64, 196, 255, 0.08);
    border-left: 4px solid var(--accent-cyan);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    margin: 1.5rem 0 1rem 0;
    color: #E0E0E0;
    backdrop-filter: blur(4px);
}
.bridge-block strong {
    color: var(--accent-cyan);
}

.step-indicator {
    font-size: 0.9rem;
    color: var(--text-muted);
    margin-bottom: 0.8rem;
}
.step-indicator .progress-bar-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
}
.step-indicator .progress-bar {
    height: 4px;
    background: rgba(255,255,255,0.1);
    border-radius: 2px;
    flex: 1;
    margin-left: 10px;
}
.step-indicator .progress-fill {
    height: 100%;
    background: var(--accent-cyan);
    border-radius: 2px;
    transition: width 0.3s ease;
}

@media (max-width: 992px) {
    section[data-testid="stSidebar"] .stButton button {
        font-size: 0.85rem;
        padding: 0.4rem 0.6rem;
    }
    .main-header {
        font-size: 1.8rem;
        padding-left: 0.8rem;
    }
    .mission-card, .theory-card {
        padding: 1.2rem 1.4rem;
        border-radius: 16px;
    }
    .block-container {
        padding: 1.5rem 1rem;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------------
# Инициализация состояния
# ------------------------------
INIT_STATE = {
    "page": "intro",
    "step_12": 0,
    "max_reached_step_12": 0,
    "completed_steps_12": [False]*5,
    "intro_q1": None,
    "match_Владелец информации": None,
    "match_Обладатель информации": None,
    "match_Провайдер": None,
    "match_Владелец сайта": None,
    "match_Пользователь": None,
    "step1_checked": False,
    "step1_score": 0,
    "step2_q1": None,
    "step2_q2": None,
    "step2_q3": None,
    "step2_q4": None,
    "step2_reflection": "",
    "step2_self_score": 0,
    "step3_q1": None,
    "step3_q2": None,
    **{f"checklist_{i}": False for i in range(1, 11)},
    "step4_checked": False,
    "final_score_slider": 5,
    "final_text": "",
    "step_13": 0,
    "max_reached_step_13": 0,
    "completed_steps_13": [False]*7,
    **{f"m13_sort_idx_{i}": 0 for i in range(1, 9)},
    "m13_sort_checked": False,
    "m13_sort_score": 0,
    "m13_password": "",
    "m13_password_checks": [False]*7,
    "m13_password_checked": False,
    "m13_memo": {},
    "m13_memo_sent": False,
    "m13_memo_checklist": [False]*5,
    "m13_case_choice": None,
    "m13_case_justification": "",
    "m13_case_sent": False,
    "m13_case_checklist": [False]*4,
    "m13_project": "",
    "m13_project_sent": False,
    "m13_project_checklist": [False]*5,
    "m13_diagnostic": {},
    "m13_diagnostic_checks": [False]*7,
    "m13_diagnostic_checked": False,
    "m13_diag_score": 0,
    "module12_finished": False,
    "timer_active": False,
    "timer_duration": 900,
    "timer_start": 0.0,
}

for key, value in INIT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ------------------------------
# Вспомогательные функции
# ------------------------------
def go_to_page(page):
    st.session_state.page = page
    st.rerun()

def go_to_step_12(idx):
    if idx <= st.session_state.max_reached_step_12:
        st.session_state.step_12 = idx
        st.rerun()

def go_to_step_13(idx):
    if idx <= st.session_state.max_reached_step_13:
        st.session_state.step_13 = idx
        st.rerun()

def advance_step_12():
    cur = st.session_state.step_12
    if cur < 4:
        st.session_state.completed_steps_12[cur] = True
        st.session_state.step_12 = cur + 1
        st.session_state.max_reached_step_12 = max(st.session_state.max_reached_step_12, cur + 1)
    elif cur == 4:
        st.session_state.completed_steps_12[cur] = True
        st.session_state.step_12 = 5
        st.session_state.max_reached_step_12 = 5
        st.session_state.module12_finished = True
    st.rerun()

def advance_step_13():
    cur = st.session_state.step_13
    if cur < 6:
        st.session_state.completed_steps_13[cur] = True
        st.session_state.step_13 = cur + 1
        st.session_state.max_reached_step_13 = max(st.session_state.max_reached_step_13, cur + 1)
    elif cur == 6:
        st.session_state.completed_steps_13[cur] = True
        st.session_state.step_13 = 7
        st.session_state.max_reached_step_13 = 7
    st.rerun()

def render_step_indicator(module_name, current, total):
    pct = (current + 1) / total
    st.markdown(
        f'''
        <div class="step-indicator">
            <div class="progress-bar-container">
                <span>Шаг {current+1} из {total} — {module_name}</span>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {pct*100}%;"></div>
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

def render_nav_buttons(back_step, next_step, next_disabled, back_label="⬅️ Назад", next_label="Далее ➡️"):
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([8, 2])
    with col1:
        if back_step is not None:
            if st.button(back_label, key=f"back_{back_step}"):
                if st.session_state.page == "module12":
                    st.session_state.step_12 = back_step
                elif st.session_state.page == "module13":
                    st.session_state.step_13 = back_step
                st.rerun()
    with col2:
        if st.button(next_label, disabled=next_disabled, key=f"next_{next_step}"):
            if st.session_state.page == "module12":
                advance_step_12()
            elif st.session_state.page == "module13":
                advance_step_13()
    st.markdown('</div>', unsafe_allow_html=True)

def calculate_auto_score():
    score_12 = 0
    if st.session_state.intro_q1 == "B":
        score_12 += 1
    correct_map_12 = {
        "Владелец информации": "Человек или организация, создавшая информацию",
        "Обладатель информации": "Тот, кто владеет информацией на законных основаниях",
        "Провайдер": "Компания, предоставляющая доступ в интернет",
        "Владелец сайта": "Тот, кто управляет сайтом",
        "Пользователь": "Любой человек, пользующийся интернетом"
    }
    for term, correct_def in correct_map_12.items():
        user_ans = st.session_state.get(f"match_{term}", None)
        if user_ans == correct_def:
            score_12 += 1
    if st.session_state.step2_q1 == "A": score_12 += 1
    if st.session_state.step2_q2 == "A": score_12 += 1
    if st.session_state.step2_q3 == "D": score_12 += 1
    if st.session_state.step2_q4 == "B": score_12 += 1
    score_12 += st.session_state.step2_self_score
    if st.session_state.step3_q1 == "B": score_12 += 1
    if st.session_state.step3_q2 == "D": score_12 += 1
    checklist_count = sum([st.session_state.get(f"checklist_{i}", False) for i in range(1, 11)])
    score_12 += checklist_count
    final_psw = st.session_state.final_score_slider
    if final_psw >= 7:
        score_12 += 2
    elif final_psw >= 4:
        score_12 += 1
    if len(st.session_state.final_text.strip()) > 0:
        score_12 += 1
    max_12 = 30

    sort_score = st.session_state.get("m13_sort_score", 0)
    pw_score = sum(st.session_state.m13_password_checks)
    diag_score = st.session_state.get("m13_diag_score", 0)
    total_13_auto = sort_score + pw_score + diag_score
    max_13_auto = 8 + 7 + 12

    total = score_12 + total_13_auto
    max_total = max_12 + max_13_auto
    return total, max_total

def generate_csv_data():
    data = {"Вопрос": [], "Ответ": []}
    data["Вопрос"].append("1.2 Вступление (ответственность за данные)")
    data["Ответ"].append(st.session_state.intro_q1)
    for term in ["Владелец информации", "Обладатель информации", "Провайдер", "Владелец сайта", "Пользователь"]:
        data["Вопрос"].append(f"1.2 Соотнесение: {term}")
        data["Ответ"].append(st.session_state.get(f"match_{term}", ""))
    for q in ["step2_q1", "step2_q2", "step2_q3", "step2_q4"]:
        data["Вопрос"].append(f"1.2 Вопрос {q}")
        data["Ответ"].append(st.session_state.get(q, ""))
    data["Вопрос"].append("1.2 Самооценка безопасности пароля")
    data["Ответ"].append(st.session_state.final_score_slider)
    data["Вопрос"].append("1.2 Обоснование")
    data["Ответ"].append(st.session_state.final_text)
    data["Вопрос"].append("1.3 Памятка (отправлена)")
    data["Ответ"].append("Да" if st.session_state.m13_memo_sent else "Нет")
    data["Вопрос"].append("1.3 Кейс (выбор)")
    data["Ответ"].append(st.session_state.m13_case_choice)
    data["Вопрос"].append("1.3 Кейс (обоснование)")
    data["Ответ"].append(st.session_state.m13_case_justification)
    data["Вопрос"].append("1.3 Проект (отправлен)")
    data["Ответ"].append("Да" if st.session_state.m13_project_sent else "Нет")
    data["Вопрос"].append("1.3 Диагностика (балл)")
    data["Ответ"].append(st.session_state.m13_diag_score)
    return pd.DataFrame(data)

def generate_mailto_body():
    auto_score, max_auto = calculate_auto_score()
    lines = [
        f"Результаты диагностики курса 'Цифровой куратор'",
        f"Автоматический балл: {auto_score} из {max_auto}",
        f"Процент выполнения: {int(auto_score/max_auto*100)}%",
        "",
        "Открытые задания:",
    ]
    open_tasks = {
        "Памятка по приватности": st.session_state.m13_memo_sent,
        "Кейс (обоснование)": st.session_state.m13_case_sent,
        "Итоговый проект": st.session_state.m13_project_sent,
        "Диагностика (открытые вопросы)": st.session_state.m13_diagnostic_checked
    }
    for task, completed in open_tasks.items():
        status = "Выполнено" if completed else "Не отправлено"
        lines.append(f"- {task}: {status}")
    lines.append("")
    lines.append("Данные экспортированы из приложения 'Цифровой наставник'.")
    return "%0D%0A".join(lines)

# ------------------------------
# Боковая панель
# ------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-header">⚖️ Цифровой куратор</div>', unsafe_allow_html=True)
    if st.sidebar.button("🏠 Главная", key="nav_home"):
        go_to_page("intro")

    st.markdown("---")
    st.markdown("#### Модуль 1.2")
    steps_12 = ["Вступление", "Кто есть кто", "Личные данные", "Этика", "Заключение"]
    for i, name in enumerate(steps_12):
        if i <= st.session_state.max_reached_step_12:
            btn_label = f"{'✅' if st.session_state.completed_steps_12[i] else '📌'} {name}"
            if st.sidebar.button(btn_label, key=f"nav12_{i}", disabled=(i > st.session_state.max_reached_step_12)):
                st.session_state.page = "module12"
                go_to_step_12(i)
        else:
            st.sidebar.button(f"⏳ {name}", disabled=True, key=f"nav12_disabled_{i}")
    comp12 = sum(st.session_state.completed_steps_12)
    st.caption(f"Прогресс: {comp12}/5")

    st.markdown("---")
    st.markdown("#### Модуль 1.3")
    steps_13 = ["Старт", "Анализ угроз", "Создание пароля", "Памятка", "Кейс", "Проект", "Диагностика"]
    for i, name in enumerate(steps_13):
        if i <= st.session_state.max_reached_step_13:
            btn_label = f"{'✅' if st.session_state.completed_steps_13[i] else '📌'} {name}"
            if st.sidebar.button(btn_label, key=f"nav13_{i}", disabled=(i > st.session_state.max_reached_step_13)):
                st.session_state.page = "module13"
                go_to_step_13(i)
        else:
            st.sidebar.button(f"⏳ {name}", disabled=True, key=f"nav13_disabled_{i}")
    comp13 = sum(st.session_state.completed_steps_13)
    st.caption(f"Прогресс: {comp13}/7")

    st.markdown("---")
    total_completed = comp12 + comp13
    total_steps = 5 + 7
    st.progress(total_completed / total_steps)
    st.caption(f"Всего пройдено: {total_completed}/{total_steps}")

    if st.session_state.module12_finished and comp13 == 7:
        if st.sidebar.button("📊 Итоговая диагностика", key="nav_diag"):
            go_to_page("diagnostics")

# ------------------------------
# Основной контент
# ------------------------------
if st.session_state.page == "intro":
    st.markdown('<div class="main-header">Добро пожаловать на курс «Цифровой куратор»!</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="theory-card">
      <p>Этот курс поможет тебе освоить навыки цифрового куратора – специалиста, который помогает людям безопасно пользоваться интернетом и защищать свои данные.</p>
      <p>Курс состоит из двух модулей:</p>
      <ul>
        <li><strong>1.2 Нормативно-правовая база и этика</strong> – ты узнаешь о законах, регулирующих защиту данных, правах клиентов и этических принципах работы.</li>
        <li><strong>1.3 Информационная безопасность и защита персональных данных</strong> – ты научишься распознавать угрозы, создавать надёжные пароли, настраивать приватность и составлять рекомендации для клиентов.</li>
      </ul>
      <p>В конце курса тебя ждёт диагностика, которая проверит знания из обоих модулей и определит твой уровень.</p>
      <p><strong>Готов начать?</strong></p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Начать обучение", use_container_width=True):
            st.session_state.page = "module12"
            st.session_state.step_12 = 0
            st.rerun()

# ---------- МОДУЛЬ 1.2 ----------
elif st.session_state.page == "module12":
    step = st.session_state.step_12
    total_steps_12 = 6

    if step == 0:
        render_step_indicator("Модуль 1.2", step, total_steps_12)
        st.markdown('<div class="main-header">Зачем будущему куратору знать законы?</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="theory-card">
          <p><strong>Представь:</strong> ты помогаешь пожилому человеку зарегистрироваться на портале Госуслуг.
          Ты просишь его продиктовать паспортные данные, СНИЛС, номер телефона.
          Ты уверен, что делаешь доброе дело. Но знаешь ли ты, что несёшь юридическую ответственность за сохранность этих данных?</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("### 🎥 Видео")
        col1, col2, col3 = st.columns([0.3, 2, 0.3])
        with col2:
            st.video("VidPlaceHold.mp4")
        st.markdown("---")
        st.markdown("### ❓ Вопрос")
        options = {
            "A": "Сам пенсионер, так как он добровольно передал данные",
            "B": "Цифровой куратор, так как он работает с данными клиента",
            "C": "Оператор сайта Госуслуг, так как он обрабатывает данные"
        }
        choice = st.radio(
            "Как ты думаешь, кто несёт ответственность за сохранность данных пенсионера?",
            options.keys(),
            format_func=lambda x: f"{x}: {options[x]}",
            key="intro_q1"
        )
        if st.session_state.intro_q1 is not None:
            ans = st.session_state.intro_q1
            if ans == "B":
                st.success("✅ Совершенно верно! Цифровой куратор несёт ответственность за сохранность данных клиента с момента их получения. Это закреплено в законе № 152-ФЗ «О персональных данных».")
            elif ans == "A":
                st.error("❌ Неверно. Пенсионер передал данные добровольно, но это не снимает ответственности с того, кто эти данные принимает и обрабатывает.")
            else:
                st.error("❌ Неверно. Оператор сайта отвечает за обработку данных на своей платформе, ноты как цифровой куратор также несёшь ответственность за данные, которые получаешь при работе с клиентом.")
        st.markdown("""
        <div class="bridge-block">
          <strong>💡 Совет от помощника:</strong> запомни этот момент — он пригодится в практическом блоке 1.3, когда ты будешь учиться защищать данные на деле.
        </div>
        """, unsafe_allow_html=True)
        render_nav_buttons(None, 1, st.session_state.intro_q1 is None)

    elif step == 1:
        render_step_indicator("Модуль 1.2", step, total_steps_12)
        st.markdown('<div class="main-header">Кто есть кто в цифровом мире?</div>', unsafe_allow_html=True)
        st.markdown("### 📊 Инфографика")
        terms_info = [
            ("👤 Владелец информации", "Человек или организация, которая создала информацию или имеет законное право ей распоряжаться.", "Ты написал пост в соцсети — ты владелец этой информации."),
            ("📂 Обладатель информации", "Тот, кто владеет информацией на законных основаниях (может не быть её создателем).", "Школа хранит личные дела учеников — она обладатель этих данных."),
            ("🌐 Провайдер", "Компания, которая предоставляет доступ в интернет.", "Ростелеком, МТС, Билайн — провайдеры."),
            ("🖥️ Владелец сайта", "Тот, кто управляет сайтом и определяет его содержание.", "Администратор портала Госуслуг — владелец сайта."),
            ("🙋 Пользователь", "Любой человек, который пользуется интернетом.", "Ты и твои будущие клиенты — пользователи.")
        ]
        for term, definition, example in terms_info:
            with st.expander(term):
                st.markdown(f"**Определение:** {definition}")
                st.markdown(f"**Пример:** {example}")
        st.markdown("""
        <div class="theory-card">
          <strong>Важно запомнить:</strong> Федеральный закон № 149-ФЗ «Об информации, информационных технологиях и о защите информации» вводит принцип: «Информация является свободной, но её распространение может быть ограничено». Свобода информации не означает вседозволенности.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("### 🧩 Задание: соотнеси термин и определение")
        definitions_pool = [
            "Человек или организация, создавшая информацию",
            "Тот, кто владеет информацией на законных основаниях",
            "Компания, предоставляющая доступ в интернет",
            "Тот, кто управляет сайтом",
            "Любой человек, пользующийся интернетом"
        ]
        correct_map = {
            "Владелец информации": "Человек или организация, создавшая информацию",
            "Обладатель информации": "Тот, кто владеет информацией на законных основаниях",
            "Провайдер": "Компания, предоставляющая доступ в интернет",
            "Владелец сайта": "Тот, кто управляет сайтом",
            "Пользователь": "Любой человек, пользующийся интернетом"
        }
        terms = list(correct_map.keys())
        user_matches = {}
        for term in terms:
            user_matches[term] = st.selectbox(
                term,
                ["Выбери определение..."] + definitions_pool,
                key=f"match_{term}"
            )
        if st.button("✅ Проверить", key="check_step1"):
            st.session_state.step1_checked = True
            score = 0
            for term in terms:
                if user_matches[term] == correct_map[term]:
                    score += 1
                    st.success(f"{term}: ✅ Верно!")
                else:
                    st.error(f"{term}: ❌ Неверно. Правильно: {correct_map[term]}")
            st.session_state.step1_score = score
            if score == 5:
                st.success("🎉 Отлично! Ты верно определил всех участников цифрового пространства.")
            elif 3 <= score <= 4:
                st.info(f"👍 Ты верно определил большинство терминов ({score} из 5). Обрати внимание на пары, отмеченные красным.")
            else:
                st.warning(f"📚 Вам стоит повторить материал. Ты правильно определили только {score} из 5.")
        st.markdown("""
        <div class="bridge-block">
          <strong>💡 Совет от помощника:</strong> зафиксируй в памяти, кто такой пользователь — это твои будущие клиенты, чьи данные ты будешь защищать в блоке 1.3.
        </div>
        """, unsafe_allow_html=True)
        render_nav_buttons(0, 2, not st.session_state.step1_checked)

    elif step == 2:
        render_step_indicator("Модуль 1.2", step, total_steps_12)
        st.markdown('<div class="main-header">Личные данные: что это и почему их нужно защищать?</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="theory-card">
          <h3>Что такое персональные данные?</h3>
          <p>Персональные данные (ПД) — это любая информация, которая прямо или косвенно относится к определённому или определяемому человеку (субъекту персональных данных).</p>
          <p><strong>Примеры:</strong> имя, дата рождения, адрес, телефон, email, паспортные данные, СНИЛС, фотографии, геолокация.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("### ❓ Вопрос 1")
        q1 = st.radio(
            "Что из перечисленного НЕ является персональными данными?",
            {
                "A: Анонимный никнейм в игре": "Анонимный никнейм в игре",
                "B: Номер телефона": "Номер телефона",
                "C: Адрес электронной почты": "Адрес электронной почты",
                "D: Серия и номер паспорта": "Серия и номер паспорта"
            },
            key="step2_q1"
        )
        if st.session_state.step2_q1 is not None:
            if st.session_state.step2_q1 == "A":
                st.success("✅ Верно! Анонимный никнейм сам по себе не является ПД, так как по нему нельзя идентифицировать человека.")
            else:
                st.error("❌ Неверно. Номер телефона, email и паспортные данные — это персональные данные.")
        st.markdown("---")
        st.markdown("""
        <div class="theory-card">
          <h3>Главный закон: № 152-ФЗ «О персональных данных»</h3>
          <p>Семь ключевых принципов обработки ПД:</p>
          <ol>
            <li>Законность и справедливость</li>
            <li>Ограничение конкретными целями</li>
            <li>Минимизация (собирай только нужное)</li>
            <li>Достоверность и актуальность</li>
            <li>Ограничение срока хранения</li>
            <li>Безопасность</li>
            <li>Ответственность</li>
          </ol>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("### ❓ Вопрос 2")
        q2 = st.radio(
            "Какие данные ты имеешь право собирать у клиента по закону № 152-ФЗ?",
            {
                "A: Только те, которые необходимы для достижения конкретной цели": "Только те, которые необходимы для достижения конкретной цели",
                "B: Любые данные, которые клиент согласился предоставить": "Любые данные, которые клиент согласился предоставить",
                "C: Все данные, которые могут пригодиться в будущем": "Все данные, которые могут пригодиться в будущем",
                "D: Только данные, запрошенные оператором сайта": "Только данные, запрошенные оператором сайта"
            },
            key="step2_q2"
        )
        if st.session_state.step2_q2 is not None:
            if st.session_state.step2_q2 == "A":
                st.success("✅ Верно! Принцип минимизации: только те данные, которые действительно нужны для цели.")
            else:
                st.error("❌ Неверно. Закон ограничивает сбор данных принципом минимизации и целевого использования.")
        st.markdown("---")
        st.markdown("""
        <div class="theory-card">
          <h3>Права субъекта персональных данных</h3>
          <ul>
            <li><strong>Право на информацию:</strong> ты должен сообщить человеку, какие данные собираешь и зачем.</li>
            <li><strong>Право на доступ:</strong> человек может запросить все свои данные.</li>
            <li><strong>Право на уточнение:</strong> можно требовать исправить неверные данные.</li>
            <li><strong>Право на блокирование и удаление:</strong> можно потребовать удалить данные.</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("### ❓ Вопрос 3")
        q3 = st.radio(
            "Клиент просит удалить все его данные из вашей базы. Что ты обязан сделать по закону?",
            {
                "A: Отказать, так как данные уже обработаны": "Отказать, так как данные уже обработаны",
                "B: Удалить данные в течение 30 дней": "Удалить данные в течение 30 дней",
                "C: Объяснить, что удаление невозможно, и предложить альтернативу": "Объяснить, что удаление невозможно, и предложить альтернативу",
                "D: Удалить данные в срок, установленный законом": "Удалить данные в срок, установленный законом"
            },
            key="step2_q3"
        )
        if st.session_state.step2_q3 is not None:
            if st.session_state.step2_q3 == "D":
                st.success("✅ Верно! Закон № 152-ФЗ даёт субъекту право на удаление данных. Срок обычно 30 дней.")
            else:
                st.error("❌ Неверно. Правильный ответ: удалить данные в установленный законом срок (обычно 30 дней).")
        st.markdown("---")
        st.markdown("""
        <div class="theory-card">
          <h3>Ответственность за утечку</h3>
          <p>За утечку персональных данных предусмотрена административная (существенный штраф до 100 000 руб.) и гражданско-правовая (компенсация ущерба) ответственность. В тяжёлых случаях — уголовная.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("### ❓ Вопрос 4")
        q4 = st.radio(
            "Какая ответственность грозит за утечку персональных данных клиентов, если она произошла по твоей вине?",
            {
                "A: Только дисциплинарная (выговор)": "Только дисциплинарная (выговор)",
                "B: Административная (штраф) и возможная гражданско-правовая": "Административная (штраф) и возможная гражданско-правовая",
                "C: Только уголовная": "Только уголовная",
                "D: Никакой, если утечка произошла случайно": "Никакой, если утечка произошла случайно"
            },
            key="step2_q4"
        )
        if st.session_state.step2_q4 is not None:
            if st.session_state.step2_q4 == "B":
                st.success("✅ Верно! Основная ответственность — административная и гражданско-правовая.")
            else:
                st.error("❌ Неверно. Правильный ответ: административная и гражданско-правовая ответственность.")
        st.markdown("---")
        st.slider("Оцени свой ответ (0–5 баллов)", 0, 5, key="step2_self_score")
        st.markdown("### ✍️ Рефлексивное задание")
        st.write("Представь, что к тебе пришёл клиент и просит удалить его данные. Какие права у него есть? Напиши краткий ответ (3–5 предложений).")
        reflection = st.text_area("Твой ответ:", key="step2_reflection", height=80)
        st.markdown("""
        <div class="bridge-block">
          <strong>💡 Совет от помощника:</strong> уже сейчас подумай, как технически можно обеспечить удаление данных — этот навык ты прокачаешь в разделе 1.3.
        </div>
        """, unsafe_allow_html=True)
        all_answered = all([
            st.session_state.step2_q1,
            st.session_state.step2_q2,
            st.session_state.step2_q3,
            st.session_state.step2_q4,
            len(st.session_state.step2_reflection.strip()) > 0
        ])
        render_nav_buttons(1, 3, not all_answered)

    elif step == 3:
        render_step_indicator("Модуль 1.2", step, total_steps_12)
        st.markdown('<div class="main-header">Этика цифрового куратора: как принимать правильные решения?</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="theory-card">
          <h3>Что такое этика?</h3>
          <p>Этика — это не закон, а свод моральных правил, которые ты сам решаешь соблюдать. Закон говорит «нельзя делать плохо», а этика говорит «поступай хорошо».</p>
          <p><strong>Главные принципы:</strong> уважение прав, не причинение вреда, честность, конфиденциальность, информированное согласие.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("### 🧑‍💼 Кейс")
        st.markdown("""
        <div class="mission-card">
          <p>Ты работаешь цифровым куратором. К тебе пришла пожилая женщина для регистрации на Госуслугах. Она использует очень простой пароль «123456» и говорит, что это единственный пароль, который она запоминает. Ты знаешь, что это небезопасно.</p>
          <p><strong>Как ты поступишь?</strong></p>
        </div>
        """, unsafe_allow_html=True)
        case_options = {
            "A": "Промолчать, чтобы не смущать женщину, и продолжить регистрацию с её паролем",
            "B": "Объяснить риски и предложить помощь в создании надёжного пароля",
            "C": "Придумать пароль самостоятельно и записать его на бумажку"
        }
        case_choice = st.radio("Выбери вариант:", case_options.keys(), format_func=lambda x: f"{x}: {case_options[x]}", key="step3_q1")
        if st.session_state.step3_q1 is not None:
            if st.session_state.step3_q1 == "B":
                st.success("✅ Это и этичное, и профессиональное решение. Ты заботишься о безопасности клиента, но не навязываешь своё мнение.")
            elif st.session_state.step3_q1 == "A":
                st.error("❌ Это неэтичное решение. Ты знаешь о риске, но не предупреждаешь клиента, нарушая принцип «не навреди».")
            else:
                st.error("❌ Это неэтичное и потенциально незаконное решение. Ты не получил информированного согласия клиента на изменение пароля.")
        st.markdown("### ❓ Какие законы и этические принципы ты учитывал?")
        principle_choice = st.radio(
            "Выбери наиболее полный ответ:",
            {
                "A: Принцип конфиденциальности и право на частную жизнь": "Принцип конфиденциальности и право на частную жизнь",
                "B: Принцип «не навреди» и обязанность обеспечивать безопасность данных": "Принцип «не навреди» и обязанность обеспечивать безопасность данных",
                "C: Принцип информированного согласия": "Принцип информированного согласия",
                "D: Все перечисленные выше": "Все перечисленные выше"
            },
            key="step3_q2"
        )
        if st.session_state.step3_q2 is not None:
            if st.session_state.step3_q2 == "D":
                st.success("✅ Верно! Ты учёл все ключевые аспекты профессиональной этики.")
            else:
                st.warning("⚠️ Ты прав частично, но в этой ситуации важно учитывать все принципы одновременно.")
        st.markdown("""
        <div class="bridge-block">
          <strong>💡 Совет от помощника:</strong> держи этот кейс в уме — совсем скоро в разделе 1.3 ты разберёшь его на практике и составишь план действий для клиента.
        </div>
        """, unsafe_allow_html=True)
        both_answered = (st.session_state.step3_q1 is not None) and (st.session_state.step3_q2 is not None)
        render_nav_buttons(2, 4, not both_answered)

    elif step == 4:
        render_step_indicator("Модуль 1.2", step, total_steps_12)
        st.markdown('<div class="main-header">Что мы узнали о законах и этике?</div>', unsafe_allow_html=True)
        st.markdown("### 📌 Резюме")
        st.markdown("""
        <div class="theory-card">
          <ul>
            <li><strong>📜 Закон № 149-ФЗ</strong> — регулирует цифровую среду, определяет субъектов.</li>
            <li><strong>🛡️ Закон № 152-ФЗ</strong> — защищает персональные данные.</li>
            <li><strong>⚖️ Этика</strong> — свод правил: информированное согласие, конфиденциальность, "не навреди".</li>
            <li><strong>🔒 Твоя ответственность</strong> — ты отвечаешь за сохранность данных клиентов.</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("### ✅ Чек-лист самопроверки")
        with st.expander("📋 Этот чек-лист поможет вам оценить свои знания. Он не обязателен, но рекомендуем его заполнить."):
            checklist_items = [
                "Я знаю, что такое информация по закону № 149-ФЗ",
                "Я могу назвать 5 субъектов цифрового пространства",
                "Я знаю, что такое персональные данные и приведу 5 примеров",
                "Я знаю 7 принципов обработки ПД из закона № 152-ФЗ",
                "Я знаю 4 права субъекта персональных данных",
                "Я понимаю, что я несу ответственность за сохранность данных клиента",
                "Я знаю, какая ответственность грозит за утечку данных",
                "Я понимаю, что этика — это не закон, но важный ориентир",
                "Я могу отличить этичную просьбу от нарушения",
                "Я знаю, что запрещено делать в интернете"
            ]
            checked = []
            for i, item in enumerate(checklist_items, 1):
                chk = st.checkbox(item, key=f"checklist_{i}")
                checked.append(chk)
            if st.button("📋 Подвести итог", key="check_checklist"):
                st.session_state.step4_checked = True
                count = sum(checked)
                missing = [checklist_items[i-1] for i, c in enumerate(checked, 1) if not c]
                if count == 10:
                    st.success("🎉 Отлично! Ты готов переходить к практическому разделу 1.3.")
                elif count >= 8:
                    st.info(f"👍 Очень хорошо! Рекомендуем повторить темы: {', '.join(missing)}.")
                else:
                    st.warning(f"📚 Рекомендуем вернуться к материалам, особенно к: {', '.join(missing)}.")
        st.markdown("---")
        st.markdown("### 🔢 Финальное задание: мост к практике")
        st.write("Оцени безопасность твоего текущего пароля (от личного аккаунта) по шкале от 1 до 10 и обоснуй оценку в 2–3 предложениях.")
        col1, col2 = st.columns([1, 3])
        with col1:
            score = st.slider("Оценка (1–10)", 1, 10, key="final_score_slider")
        with col2:
            justification = st.text_area("Обоснование:", key="final_text", height=80)
        st.markdown("""
        <div class="bridge-block" style="border-left-color: var(--accent-green);">
          <strong>💡 Совет от помощника: готовься к практике!</strong>
          <p>Теперь ты знаешь правовые основы и этические принципы. В следующем разделе <strong>«Информационная безопасность»</strong> ты научишься:</p>
          <ul>
            <li>Распознавать киберугрозы (фишинг, вирусы, утечки)</li>
            <li>Создавать надёжные пароли и настраивать двухфакторную аутентификацию</li>
            <li>Защищать данные на компьютере и в интернете</li>
            <li>Разрабатывать чек-лист безопасности для клиентов</li>
          </ul>
          <p><em>Подготовься к практической работе: тебе понадобятся компьютер, браузер и доступ в интернет.</em></p>
          <p><strong>Помните:</strong> знания правил без практики бесполезны; умение защищать данные идёт рука об руку с пониманием этики.</p>
        </div>
        """, unsafe_allow_html=True)
        render_nav_buttons(3, 5, len(st.session_state.final_text.strip()) == 0)

    elif step == 5:
        render_step_indicator("Модуль 1.2", step, total_steps_12)
        st.markdown('<div class="main-header">🎉 Модуль 1.2 завершён!</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="theory-card">
          <p>Ты успешно освоил нормативно-правовую базу и этические принципы работы цифрового куратора.</p>
          <p>Теперь ты готов перейти к практическому модулю <strong>«Информационная безопасность и защита персональных данных»</strong>.</p>
          <p>В этом модуле ты научишься:</p>
          <ul>
            <li>Распознавать киберугрозы и мошеннические схемы</li>
            <li>Создавать надёжные пароли и настраивать двухфакторную аутентификацию</li>
            <li>Настраивать приватность в соцсетях и мессенджерах</li>
            <li>Составлять рекомендации для клиентов и действовать в случае утечки данных</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="nav-container">', unsafe_allow_html=True)
        col1, col2 = st.columns([8, 2])
        with col2:
            if st.button("➡️ Перейти к модулю 1.3"):
                st.session_state.page = "module13"
                st.session_state.step_13 = 0
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ---------- МОДУЛЬ 1.3 ----------
elif st.session_state.page == "module13":
    step = st.session_state.step_13
    total_steps_13 = 8

    if step == 0:
        render_step_indicator("Модуль 1.3", step, total_steps_13)
        st.markdown('<div class="main-header">Вспомним законы: твоя правовая основа</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="theory-card">
          <p>В разделе 1.2 ты узнал, что цифровой куратор — это не просто помощник по компьютеру, а профессионал, который работает с личной информацией людей и несёт за это ответственность.</p>
          <p>Ты уже знаешь:</p>
          <ul>
            <li>какие законы защищают персональные данные (№ 149-ФЗ, № 152-ФЗ);</li>
            <li>какие права есть у клиента (на информацию, доступ, уточнение, удаление);</li>
            <li>какие обязанности и ответственность лежат на тебе как на операторе данных;</li>
            <li>основные этические принципы: информированное согласие, конфиденциальность, «не навреди».</li>
          </ul>
          <p><strong>Теперь мы переходим к практике.</strong> В этом модуле ты будешь не просто читать, а <strong>действовать как настоящий цифровой куратор-наставник</strong>. Твоя задача — подготовить пакет рекомендаций для клиента, который хочет защитить свои данные.</p>
          <p><em>Важно: в каждом задании тебе нужно будет не просто выполнить действие, но и <strong>объяснить, почему это важно</strong>, ссылаясь на законы и этические принципы из раздела 1.2.</em></p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("### 🎥 Видео-воспоминание")
        col1, col2, col3 = st.columns([0.3, 2, 0.3])
        with col2:
            st.video("VidPlaceHold.mp4")
        render_nav_buttons(None, 1, False, back_label=None, next_label="Начать проект ➡️")

    elif step == 1:
        render_step_indicator("Модуль 1.3", step, total_steps_13)
        st.markdown('<div class="main-header">Блок 1. Анализ угроз: что может угрожать клиенту?</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="theory-card">
          <p>Прежде чем помогать клиенту, нужно понять, от чего его защищать. Вспомни основные виды угроз:</p>
          <ul>
            <li>фишинг (мошеннические письма и сайты);</li>
            <li>социальная инженерия (манипуляция через эмоции);</li>
            <li>слабые пароли и их повторное использование;</li>
            <li>кража данных через утечки и взломы;</li>
            <li>неправильные настройки приватности.</li>
          </ul>
          <p><strong>Задание:</strong> для каждой ситуации выбери подходящую категорию, используя кнопки <strong>◀</strong> и <strong>▶</strong> для перебора.</p>
        </div>
        """, unsafe_allow_html=True)

        situations = {
            "1": "Вы получили письмо от «банка» с просьбой перейти по ссылке и подтвердить данные карты",
            "2": "Ваш друг просит скинуть пароль от почты, потому что «срочно нужно подтвердить аккаунт»",
            "3": "Вы используете один и тот же пароль для Госуслуг, электронной почты и соцсетей",
            "4": "Ваш аккаунт взломали, и данные клиентов оказались в открытом доступе",
            "5": "Вы выложили фотографию паспорта в открытом Instagram-аккаунте",
            "6": "Звонит «сотрудник полиции» и просит продиктовать код из SMS для проверки",
            "7": "Ваш пароль состоит из даты рождения и имени кота",
            "8": "Вы не знаете, какие настройки приватности включены в вашем Telegram"
        }
        categories = [
            "Фишинг и мошенничество",
            "Социальная инженерия",
            "Слабые пароли и идентификация",
            "Неправильная приватность",
            "Утечка и взлом"
        ]
        correct_map = {
            "1": "Фишинг и мошенничество",
            "2": "Социальная инженерия",
            "3": "Слабые пароли и идентификация",
            "4": "Утечка и взлом",
            "5": "Неправильная приватность",
            "6": "Социальная инженерия",
            "7": "Слабые пароли и идентификация",
            "8": "Неправильная приватность"
        }

        cats_list = ["Не выбрана"] + categories
        for sid in range(1, 9):
            idx = st.session_state[f"m13_sort_idx_{sid}"]
            st.write(f"**Ситуация {sid}:** {situations[str(sid)]}")
        
            # Открываем центрирующий контейнер
            st.markdown('<div class="sort-row-wrapper">', unsafe_allow_html=True)
        
            col_empty_left, col1, col2, col3, col_empty_right = st.columns([3, 0.5, 1.5, 0.5, 3])
            
            with col1:
                if st.button("◀", key=f"left_{sid}"):
                    new_idx = (idx - 1) % len(cats_list)
                    st.session_state[f"m13_sort_idx_{sid}"] = new_idx
                    st.rerun()
            
            with col2:
                st.markdown(
                    f"<div style='text-align:center; font-weight:bold; padding: 0.5rem 0;'>{cats_list[idx]}</div>",
                    unsafe_allow_html=True
                )
            
            with col3:
                if st.button("▶", key=f"right_{sid}"):
                    new_idx = (idx + 1) % len(cats_list)
                    st.session_state[f"m13_sort_idx_{sid}"] = new_idx
                    st.rerun()
        
            # Закрываем центрирующий контейнер
            st.markdown('</div>', unsafe_allow_html=True)
        
            st.markdown("---")

        if st.button("✅ Проверить сортировку", key="check_sort"):
            st.session_state.m13_sort_checked = True
            score = 0
            for sid in range(1, 9):
                idx = st.session_state[f"m13_sort_idx_{sid}"]
                if idx > 0 and cats_list[idx] == correct_map[str(sid)]:
                    score += 1
                    st.success(f"Ситуация {sid}: ✅ Верно")
                else:
                    st.error(f"Ситуация {sid}: ❌ Неверно. Правильно: {correct_map[str(sid)]}")
            st.session_state.m13_sort_score = score
            if score == 8:
                st.success("🎉 Отлично! Ты правильно определил все виды угроз.")
            elif score >= 6:
                st.info(f"👍 Хорошо, ты справился с большинством ситуаций ({score} из 8).")
            else:
                st.warning(f"📚 Стоит повторить материал. Правильно определено только {score} из 8.")
            st.markdown("""
            <div class="bridge-block">
              <strong>📌 Связь с теорией 1.2:</strong> Запомни: если ты как куратор не распознаешь угрозу, ты не сможешь защитить клиента. Это нарушает принцип "не навреди" и обязанность по обеспечению безопасности данных (№ 152-ФЗ).
            </div>
            """, unsafe_allow_html=True)

        render_nav_buttons(0, 2, not st.session_state.m13_sort_checked)

    elif step == 2:
        render_step_indicator("Модуль 1.3", step, total_steps_13)
        st.markdown('<div class="main-header">Блок 2. Создаём надёжный пароль</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="theory-card">
          <p>Теперь твоя задача — помочь клиенту создать надёжный пароль. Вспомни требования:</p>
          <ul>
            <li>длина: минимум 12 символов;</li>
            <li>сложность: заглавные и строчные буквы, цифры, спецсимволы;</li>
            <li>уникальность: для каждого сервиса свой пароль.</li>
          </ul>
          <p><strong>Задание:</strong> придумай пароль, который соответствует всем трём требованиям. Запиши его в поле ниже. Затем проверь свой пароль по чек-листу.</p>
        </div>
        """, unsafe_allow_html=True)
        password = st.text_input("Введите пароль:", type="password", key="m13_password_input", placeholder="Придумайте надёжный пароль")
        if password:
            st.session_state.m13_password = password
        st.markdown("#### Проверь свой пароль по чек-листу:")
        checks = [
            "Длина >= 12 символов",
            "Есть заглавные буквы (A–Z)",
            "Есть строчные буквы (a–z)",
            "Есть цифры (0–9)",
            "Есть спецсимволы (! @ # $ % ^ & * и т.п.)",
            "Не содержит личную информацию (дата рождения, имя, номер телефона)",
            "Я запомню этот пароль (или сохраню в менеджере паролей)"
        ]
        check_values = []
        for i, text in enumerate(checks):
            val = st.checkbox(text, key=f"m13_pw_check_{i}")
            check_values.append(val)
            st.session_state.m13_password_checks[i] = val
        if st.button("Проверить пароль", key="check_password"):
            score = sum(check_values)
            st.session_state.m13_password_checked = True
            if score == 7:
                st.success("🎉 Отлично! Твой пароль соответствует всем требованиям безопасности.")
            elif score >= 5:
                st.info(f"👍 Хороший пароль, но есть что улучшить ({score} из 7).")
            else:
                st.warning(f"⚠️ Пароль слишком слабый ({score} из 7). Усили его, чтобы защитить данные клиента.")
            st.markdown("""
            <div class="bridge-block">
              <strong>📌 Связь с теорией 1.2:</strong> По закону № 152-ФЗ ты обязан обеспечивать безопасность персональных данных. Слабый пароль — это нарушение.
            </div>
            """, unsafe_allow_html=True)
        render_nav_buttons(1, 3, not st.session_state.m13_password_checked)

    elif step == 3:
        render_step_indicator("Модуль 1.3", step, total_steps_13)
        st.markdown('<div class="main-header">Блок 3. Как настроить приватность в соцсетях</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="theory-card">
          <p>Теперь ты — куратор. Твоя задача — помочь клиенту понять, как настроить приватность в его соцсетях и мессенджерах.</p>
          <p>Вспомни из раздела 1.3:</p>
          <ul>
            <li>что нужно скрыть: номер телефона, дату рождения, геолокацию, список друзей, нежелательные фото;</li>
            <li>почему это важно: чтобы защитить данные от мошенников и злоумышленников.</li>
          </ul>
          <p><strong>Задание:</strong> заполни памятку для клиента. Используй шаблон ниже. Объясни клиенту, <em>почему</em> каждый шаг важен, ссылаясь на закон или этический принцип из раздела 1.2.</p>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.m13_memo_sent:
            with st.expander("✅ Чек-лист самопроверки (поможет подготовить качественную памятку)"):
                memo_checklist_items = [
                    "Указан тип клиента",
                    "Перечислены соцсети/мессенджеры",
                    "Все 5 шагов заполнены",
                    "Для каждого шага есть обоснование (ссылка на закон/этику)",
                    "Есть дополнительные рекомендации"
                ]
                memo_checks = []
                for i, item in enumerate(memo_checklist_items):
                    val = st.checkbox(item, key=f"m13_memo_check_{i}")
                    memo_checks.append(val)
                    st.session_state.m13_memo_checklist[i] = val

            st.markdown("#### 📝 Шаблон памятки (компактный дизайн)")
            with st.form("memo_form"):
                for_whom = st.text_input("Для кого (тип клиента):", key="m13_memo_for_whom", placeholder="например, пожилой человек, подросток")
                social = st.text_input("Соцсети/мессенджеры клиента:", key="m13_memo_social", placeholder="например, ВКонтакте, Telegram")
                st.markdown("**Шаг 1. Скрыть номер телефона**")
                step1_what = st.text_input("Что нужно сделать:", key="m13_memo_step1_what", placeholder="Опишите действие")
                step1_why = st.text_input("Почему это важно (ссылка на закон/этику):", key="m13_memo_step1_why", placeholder="Обоснование")
                st.markdown("**Шаг 2. Скрыть дату рождения**")
                step2_what = st.text_input("Что нужно сделать:", key="m13_memo_step2_what", placeholder="Опишите действие")
                step2_why = st.text_input("Почему это важно (ссылка на закон/этику):", key="m13_memo_step2_why", placeholder="Обоснование")
                st.markdown("**Шаг 3. Скрыть геолокацию**")
                step3_what = st.text_input("Что нужно сделать:", key="m13_memo_step3_what", placeholder="Опишите действие")
                step3_why = st.text_input("Почему это важно (ссылка на закон/этику):", key="m13_memo_step3_why", placeholder="Обоснование")
                st.markdown("**Шаг 4. Скрыть список друзей**")
                step4_what = st.text_input("Что нужно сделать:", key="m13_memo_step4_what", placeholder="Опишите действие")
                step4_why = st.text_input("Почему это важно (ссылка на закон/этику):", key="m13_memo_step4_why", placeholder="Обоснование")
                st.markdown("**Шаг 5. Проверить, какие фото видны другим**")
                step5_what = st.text_input("Что нужно сделать:", key="m13_memo_step5_what", placeholder="Опишите действие")
                step5_why = st.text_input("Почему это важно (ссылка на закон/этику):", key="m13_memo_step5_why", placeholder="Обоснование")
                additional = st.text_area("Дополнительные рекомендации:", key="m13_memo_additional", height=80, placeholder="Любые другие советы")
                submitted = st.form_submit_button("📤 Отправить на проверку наставнику")
                if submitted:
                    st.session_state.m13_memo = {
                        "for_whom": for_whom,
                        "social_networks": social,
                        "step1_what": step1_what, "step1_why": step1_why,
                        "step2_what": step2_what, "step2_why": step2_why,
                        "step3_what": step3_what, "step3_why": step3_why,
                        "step4_what": step4_what, "step4_why": step4_why,
                        "step5_what": step5_what, "step5_why": step5_why,
                        "additional": additional
                    }
                    st.session_state.m13_memo_sent = True
                    st.success("✅ Памятка отправлена на проверку наставнику. Ты можешь перейти к следующему блоку.")
                    st.rerun()
        else:
            st.success("✅ Памятка отправлена на проверку наставнику.")
            with st.expander("💡 Пример хорошей памятки (для самопроверки)"):
                st.markdown("""
                **Для кого:** пожилой человек  
                **Соцсети:** ВКонтакте, Одноклассники  
                **Шаг 1. Скрыть номер телефона**  
                *Что сделать:* зайти в настройки → приватность → кто видит номер телефона → «Только я»  
                *Почему важно:* Ст. 7 152-ФЗ – конфиденциальность ПД. Номер телефона может использоваться для мошенничества.  
                **Шаг 2–5** (аналогично с краткими инструкциями и ссылками на закон).  
                """)
        render_nav_buttons(2, 4, not st.session_state.m13_memo_sent)

    elif step == 4:
        render_step_indicator("Модуль 1.3", step, total_steps_13)
        st.markdown('<div class="main-header">Блок 4. Разбор кейса: как помочь клиенту в реальной ситуации?</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="theory-card">
          <p><strong>Кейс:</strong> Ты работаешь цифровым куратором. К тебе пришла женщина 60 лет. Она рассказывает:</p>
          <blockquote>
            "Мне позвонили из банка и сказали, что с моей карты пытаются списать 50 000 рублей. Чтобы отменить операцию, мне нужно продиктовать код из SMS. Я уже начала диктовать, но потом вспомнила, что вы говорили про мошенников. Я положила трубку и пришла к вам. Я очень боюсь, что мои данные уже украли."
          </blockquote>
          <p><strong>Твоя задача — помочь клиенту.</strong> Что ты скажешь и сделаешь?</p>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.m13_case_sent:
            with st.expander("✅ Чек-лист самопроверки (поможет подготовить ответ)"):
                case_checklist_items = [
                    "Выбран вариант действий",
                    "Обоснование содержит ссылку на закон № 152-ФЗ",
                    "Обоснование содержит ссылку на этический принцип",
                    "Ответ написан понятным языком"
                ]
                for i, item in enumerate(case_checklist_items):
                    st.session_state.m13_case_checklist[i] = st.checkbox(item, key=f"m13_case_check_{i}")

            st.markdown("#### Выбери вариант действий:")
            case_options = {
                "A": "Сказать клиенту: «Всё в порядке, ничего страшного не случилось. Не переживайте».",
                "B": "Объяснить, что это был фишинг, и предложить пошаговый план действий: проверить карту, сменить пароли, включить двухфакторную аутентификацию.",
                "C": "Сказать клиенту: «Вы правильно сделали, что положили трубку. Теперь вам нужно срочно заблокировать карту и сменить все пароли. Я помогу вам это сделать и объясню, как защитить себя в будущем».",
                "D": "Игнорировать ситуацию и переключиться на другой вопрос клиента."
            }
            choice = st.radio(
                "Твой выбор:",
                case_options.keys(),
                format_func=lambda x: f"{x}: {case_options[x]}",
                key="m13_case_choice"
            )
            if st.session_state.m13_case_choice:
                if choice == "C":
                    st.success("✅ Отлично! Ты правильно оценил ситуацию, дал чёткий план и проявил эмпатию.")
                elif choice == "B":
                    st.info("ℹ️ Ты правильно определил угрозу, но не хватает немедленных шагов (блокировка карты).")
                elif choice == "A":
                    st.error("❌ Недостаточно! Ты успокаиваешь, но не даёшь действий. Это нарушает принцип «не навреди».")
                else:
                    st.error("❌ Недопустимо! Игнорирование ситуации — нарушение профессиональной обязанности.")
            st.markdown("#### Объясни, почему ты выбрал именно этот вариант.")
            st.markdown("*Ссылайся на конкретные законы или этические принципы из раздела 1.2.*")
            justification = st.text_area("Твое обоснование (3–5 предложений):", key="m13_case_justification", height=100, placeholder="Введи обоснование...")
            if st.button("📤 Отправить на проверку наставнику", key="send_case"):
                st.session_state.m13_case_sent = True
                st.success("✅ Твой ответ отправлен на проверку. Ты можешь перейти к следующему блоку.")
                st.rerun()
        else:
            st.success("✅ Кейс отправлен на проверку.")
            with st.expander("💡 Пример хорошего ответа"):
                st.markdown("""
                **Выбран вариант C.**  
                *Обоснование:* Согласно ст. 7 152-ФЗ я обязан обеспечить конфиденциальность данных. Немедленная блокировка карты минимизирует ущерб, смена паролей предотвратит дальнейший доступ. Я действую согласно принципу «не навреди» и предоставляю клиенту информированное согласие на все шаги.
                """)
        st.markdown("""
        <div class="bridge-block">
          <strong>📌 Подсказка:</strong> Вспомни: твоя обязанность — не только технически помочь, но и юридически защитить клиента.
        </div>
        """, unsafe_allow_html=True)
        render_nav_buttons(3, 5, not st.session_state.m13_case_sent)

    elif step == 5:
        render_step_indicator("Модуль 1.3", step, total_steps_13)
        st.markdown('<div class="main-header">Итоговый проект: пакет рекомендаций для клиента</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="theory-card">
          <p>Ты прошёл все блоки практических заданий. Теперь твоя задача — создать единый пакет рекомендаций для клиента.</p>
          <p><strong>Ситуация:</strong> К тебе приходит клиент — пожилая женщина, которая только начала пользоваться интернетом. Она хочет защитить свои данные, но не знает, с чего начать. Она использует смартфон и ноутбук, у неё есть аккаунты в Госуслугах, ВКонтакте и Telegram.</p>
          <p><strong>Твоя задача:</strong> подготовить для неё документ (памятку/инструкцию/чек-лист) на 1–2 страницы, который включает:</p>
          <ol>
            <li>Рекомендации по паролям.</li>
            <li>Рекомендации по приватности.</li>
            <li>Алгоритм действий при подозрении на фишинг.</li>
            <li>Алгоритм действий при утечке данных.</li>
            <li>Ссылки на законы и этические принципы.</li>
          </ol>
          <p><strong>Важно:</strong> документ должен быть написан простым, понятным языком. Объём: не менее 10 пунктов/рекомендаций.</p>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.m13_project_sent:
            with st.expander("✅ Чек-лист самопроверки (поможет подготовить проект)"):
                project_checklist_items = [
                    "Есть все 5 разделов",
                    "Объём не менее 10 пунктов",
                    "Текст написан простым языком",
                    "Есть структура (заголовки, списки)",
                    "Приведены конкретные примеры"
                ]
                for i, item in enumerate(project_checklist_items):
                    st.session_state.m13_project_checklist[i] = st.checkbox(item, key=f"m13_proj_check_{i}")

            project_text = st.text_area("Введи текст твоего пакета рекомендаций:", height=400, key="m13_project_text", placeholder="Начни писать...")
            if project_text:
                st.session_state.m13_project = project_text
            if st.button("📤 Сохранить проект и отправить на проверку наставнику", key="send_project"):
                st.session_state.m13_project_sent = True
                st.success("✅ Твой проект сохранён и отправлен на проверку. Ты можешь перейти к диагностике.")
                st.rerun()
        else:
            st.success("✅ Проект отправлен на проверку.")
            with st.expander("💡 Пример структуры хорошего пакета"):
                st.markdown("""
                **Памятка по безопасности для бабушки Варвары**
                1. Пароли: используй фразу из 4 слов + цифры, например, «КотМурзик2023ЛюбитРыбу!»
                2. Приватность: в ВКонтакте закрой профиль от посторонних.
                ...
                5. При подозрительном звонке: положите трубку и перезвоните в банк по номеру с обратной стороны карты.
                """)
        render_nav_buttons(4, 6, not st.session_state.m13_project_sent)

    elif step == 6:
        render_step_indicator("Модуль 1.3", step, total_steps_13)
        st.markdown('<div class="main-header">Диагностика: проверь себя</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="theory-card">
          <p>Ты почти завершил модуль. Теперь проверь, как ты усвоил материал. В этом задании нужно применить все полученные знания: и правовые (раздел 1.2), и практические (раздел 1.3).</p>
          <p><strong>Ситуация:</strong> К тебе пришёл клиент — твой друг, который активно пользуется интернетом. Он говорит:</p>
          <blockquote>
            "Мне пришло письмо от Госуслуг, что мой аккаунт взломали. Я сменил пароль, но мне всё равно страшно. Я не знаю, что ещё сделать, чтобы защитить себя."
          </blockquote>
          <p><strong>Твоя задача:</strong> проанализировать ситуацию и предложить клиенту полный план защиты. Для этого:</p>
          <ol>
            <li>Определи, что уже нарушено или может быть нарушено (какие угрозы присутствуют?).</li>
            <li>Какие права есть у клиента по закону № 152-ФЗ (что он может потребовать, куда обратиться?).</li>
            <li>Составь пошаговый план действий (не менее 5 шагов).</li>
            <li>Напиши краткое сообщение клиенту, где объясняешь его права и дальнейшие шаги.</li>
            <li>Укажи, какие этические принципы ты соблюдаешь в этой ситуации.</li>
          </ol>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("⏱️ Таймер (для самоконтроля)"):
            timer_on = st.checkbox("Включить таймер", value=st.session_state.timer_active, key="timer_checkbox")
            if timer_on:
                if not st.session_state.timer_active or st.session_state.timer_start == 0:
                    st.session_state.timer_start = time.time()
                    st.session_state.timer_active = True
                elapsed = time.time() - st.session_state.timer_start
                remaining = max(0, st.session_state.timer_duration - elapsed)
                mins, secs = divmod(int(remaining), 60)
                st.write(f"Осталось: {mins:02d}:{secs:02d}")
                if remaining == 0:
                    st.warning("⏰ Время вышло! Рекомендуем завершить диагностику.")
                if st.button("Отключить таймер"):
                    st.session_state.timer_active = False
                    st.rerun()
            else:
                st.session_state.timer_active = False

        st.markdown("#### 1. Какие угрозы присутствуют?")
        threats = st.text_area("Твой ответ (3–5 предложений):", key="m13_diag_threats", height=100, placeholder="Опишите угрозы...")
        st.markdown("#### 2. Какие права есть у клиента по закону № 152-ФЗ?")
        rights = st.text_area("Твой ответ (3–5 предложений):", key="m13_diag_rights", height=100, placeholder="Права клиента...")
        st.markdown("#### 3. Пошаговый план действий (не менее 5 шагов)")
        plan = st.text_area("Твой план (маркированный список):", key="m13_diag_plan", height=120, placeholder="1. ...\n2. ...")
        st.markdown("#### 4. Сообщение клиенту (от имени куратора)")
        message = st.text_area("Твое сообщение (5–8 предложений):", key="m13_diag_message", height=120, placeholder="Здравствуйте! ...")
        st.markdown("#### 5. Какие этические принципы ты соблюдаешь?")
        ethics = st.text_area("Твой ответ (3–5 предложений):", key="m13_diag_ethics", height=100, placeholder="Конфиденциальность, ...")

        st.markdown("#### Чек-лист самопроверки (отметь перед отправкой)")
        diag_checks = [
            "Я определил все возможные угрозы",
            "Я сослался на конкретные статьи закона № 152-ФЗ",
            "Я составил чёткий пошаговый план (не менее 5 шагов)",
            "Моё сообщение написано простым, понятным языком",
            "Я указал, какие этические принципы соблюдаю",
            "Я проверил ответы на ошибки и неясности",
            "Я использовал материалы из раздела 1.2 и 1.3"
        ]
        diag_check_values = []
        for i, text in enumerate(diag_checks):
            val = st.checkbox(text, key=f"m13_diag_check_{i}")
            diag_check_values.append(val)

        if st.button("🔍 Проверить диагностику", key="check_diagnostic"):
            st.session_state.m13_diagnostic_checked = True
            st.session_state.m13_diagnostic = {
                "threats": threats,
                "rights": rights,
                "plan": plan,
                "message": message,
                "ethics": ethics
            }
            st.session_state.m13_diagnostic_checks = diag_check_values
            score = 0
            keywords = {
                "threats": ["фишинг", "взлом", "утечка", "мошенничество", "данные"],
                "rights": ["152-ФЗ", "доступ", "удаление", "уточнение", "информация"],
                "plan": ["пароль", "двухфакторная", "проверить", "сообщить", "заблокировать"],
                "message": ["защита", "данные", "безопасность", "помощь"],
                "ethics": ["конфиденциальность", "не навреди", "информированное согласие", "ответственность"]
            }
            for key, words in keywords.items():
                text = st.session_state.m13_diagnostic[key].lower()
                if any(word in text for word in words):
                    score += 1
            check_score = sum(diag_check_values)
            total_diag = score + check_score
            st.session_state.m13_diag_score = total_diag
            st.markdown(f"**Результат диагностики:** {total_diag} из 12 баллов")
            if total_diag >= 10:
                st.success("🎉 Отлично! Ты показал высокий уровень знаний и умений.")
            elif total_diag >= 7:
                st.info("👍 Хороший результат. Обрати внимание на пробелы в ответах.")
            else:
                st.warning("📚 Рекомендуем повторить материал разделов 1.2 и 1.3.")

        render_nav_buttons(5, 7, not st.session_state.m13_diagnostic_checked, next_label="🏁 Завершить модуль")

    elif step == 7:
        st.session_state.page = "diagnostics"
        st.rerun()

# ---------- ИТОГОВАЯ ДИАГНОСТИКА ----------
elif st.session_state.page == "diagnostics":
    st.markdown('<div class="main-header">📊 Итоговая диагностика курса</div>', unsafe_allow_html=True)

    auto_score, max_auto = calculate_auto_score()
    st.markdown(f'<div class="score-display">Автоматический балл: {auto_score} из {max_auto}</div>', unsafe_allow_html=True)
    st.progress(auto_score / max_auto)
    st.caption(f"Процент выполнения: {int(auto_score/max_auto*100)}%")

    st.markdown("### 📋 Ожидает оценки наставника")
    open_tasks = {
        "Памятка по приватности": st.session_state.m13_memo_sent,
        "Кейс (обоснование)": st.session_state.m13_case_sent,
        "Итоговый проект": st.session_state.m13_project_sent,
        "Диагностика (открытые вопросы)": st.session_state.m13_diagnostic_checked
    }
    for task, completed in open_tasks.items():
        status = "✅ Выполнено" if completed else "⏳ Не отправлено"
        st.write(f"- {task}: {status}")

    st.info("ℹ️ Баллы за открытые задания выставляются наставником после проверки. Они не включены в автоматический балл.")

    percent = auto_score / max_auto if max_auto > 0 else 0
    if percent >= 0.7:
        level = "🏆 Профессиональный куратор"
        advice = "Ты отлично владеешь правовыми и практическими аспектами цифровой безопасности."
    elif percent >= 0.4:
        level = "🎖️ Уверенный куратор"
        advice = "У тебя хорошие знания, но есть небольшие пробелы. Повтори темы, связанные с фишингом, социальной инженерией и настройками приватности."
    else:
        level = "🏅 Начинающий куратор"
        advice = "Тебе стоит вернуться к материалам обоих модулей и пройти курс заново для закрепления."

    st.markdown(f"**Твой уровень:** {level}")
    st.success(f"💡 {advice}")

    csv_df = generate_csv_data()
    csv_data = csv_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Скачать ответы (CSV)",
        data=csv_data,
        file_name='digital_mentor_answers.csv',
        mime='text/csv',
    )

    st.markdown("---")
    st.markdown("### 📧 Отправить результаты на почту")
    with st.form("email_form"):
        user_email = st.text_input("Введите ваш email:", placeholder="example@mail.com")
        submitted_email = st.form_submit_button("📤 Отправить результаты")
        if submitted_email:
            if user_email and re.match(r"[^@]+@[^@]+\.[^@]+", user_email):
                mailto_link = f"mailto:digitalmentor@example.com?subject=Результаты%20диагностики&body={generate_mailto_body()}"
                st.markdown(f'<a href="{mailto_link}" target="_blank">Нажмите здесь, чтобы открыть почтовый клиент и отправить результаты</a>', unsafe_allow_html=True)
                st.success(f"Письмо готово для отправки на {user_email} (через вашу почтовую программу).")
            else:
                st.error("Пожалуйста, введите корректный email.")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Пройти диагностику заново"):
            keys_to_reset = [key for key in st.session_state if key.startswith("m13_diag") or key.startswith("m13_diagnostic")]
            for key in keys_to_reset:
                if key in INIT_STATE:
                    st.session_state[key] = INIT_STATE[key]
                else:
                    st.session_state[key] = INIT_STATE.get(key, None)
            st.session_state.page = "module13"
            st.session_state.step_13 = 6
            st.rerun()
    with col2:
        if st.button("🏠 На главную"):
            st.session_state.page = "intro"
            st.rerun()
