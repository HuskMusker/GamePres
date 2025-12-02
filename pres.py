import streamlit as st
import re
import random

# ==========================
# НАСТРОЙКА СТРАНИЦЫ
# ==========================
st.set_page_config(
    page_title="Цифровой квест: стань цифровым куратором!",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================
# ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ
# ==========================
DEFAULT_STATE = {
    "total_score": 0,
    "mission1_score": 0,
    "mission2_score": 0,
    "mission3_score": 0,
    "mission4_score": 0,
    "final_test_score": 0,
    "badges": [],
    "current_page": "start",
    # флаги проверки миссий
    "mission1_checked": False,
    "mission2_checked": False,
    "mission3_checked": False,
    "mission4_checked": False,
    "final_test_checked": False,
    # для мини-игры с паролем
    "password_game_input": "",
    "password_game_score": 0,
    "password_game_feedback": "",
    "password_game_attempts": 0,
    "missions_unlocked": 1,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


def recompute_total():
    st.session_state.total_score = (
            st.session_state.mission1_score
            + st.session_state.mission2_score
            + st.session_state.mission3_score
            + st.session_state.mission4_score
            + st.session_state.final_test_score
    )


def go_to_page(page: str):
    st.session_state.current_page = page


# ==========================
# CSS В СТИЛЕ ПРЕЗЕНТАЦИИ + стили для игры
# ==========================
st.markdown(
    """
<style>
:root {
    --bg: #110B2F;
    --card1: #2F2D4D;
    --card2: #3B175E;
    --accent-green: #00FF00;
    --accent-cyan: #47CAFF;
    --text-main: #FFFFFF;
    --text-muted: #C2C2D9;
    --danger: #FF4B4B;
    --warning: #FFA500;
}

/* Анимации для значек */
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7); }
    70% { box-shadow: 0 0 0 15px rgba(0, 255, 0, 0); }
    100% { box-shadow: 0 0 0 0 rgba(0, 255, 0, 0); }
}

.pulse-badge {
    animation: pulse 2s infinite;
}

/* Анимация появления */
.fade-in {
    animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Стили для заблокированных элементов */
.locked {
    opacity: 0.5;
    filter: grayscale(70%);
    cursor: not-allowed;
}

/* Фон всего приложения */
.stApp {
    background: radial-gradient(circle at top left, #3B175E 0, #110B2F 40%, #050314 100%);
    color: var(--text-main);
    font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Центровка стандартных элементов */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Заголовки */
.main-header {
    font-size: 2.6rem;
    font-weight: 800;
    color: var(--accent-green);
    text-align: center;
    text-shadow: 0 0 18px rgba(0, 255, 0, 0.6);
    margin-bottom: 0.3em;
    letter-spacing: 0.03em;
}

.sub-header {
    font-size: 1.2rem;
    font-weight: 500;
    color: var(--accent-cyan);
    text-align: center;
    margin-bottom: 1.2em;
}

/* Карточки теории и миссий */
.mission-card, .theory-card {
    border-radius: 22px;
    padding: 1.6em 1.8em;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 10px 30px rgba(0,0,0,0.45);
    backdrop-filter: blur(10px);
}

.mission-card {
    background: linear-gradient(135deg, rgba(47,45,77,0.95), rgba(59,23,94,0.95));
}

.theory-card {
    background: linear-gradient(135deg, rgba(17,11,47,0.95), rgba(47,45,77,0.95));
    border-left: 4px solid var(--accent-cyan);
}

.theory-card h3, .theory-card h4 {
    margin-top: 0;
}

/* Кнопки */
.cyber-button {
    background: linear-gradient(90deg, var(--accent-green), var(--accent-cyan));
    color: #000;
    border: none;
    padding: 0.9em 1.8em;
    border-radius: 999px;
    font-weight: 700;
    cursor: pointer;
    margin: 0.5em;
    transition: all 0.25s ease;
    letter-spacing: 0.03em;
}
.cyber-button:hover {
    transform: translateY(-1px) scale(1.02);
    box-shadow: 0 0 20px rgba(0, 255, 160, 0.7);
}

/* Кнопки для игры с паролем */
.password-btn {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 10px;
    padding: 0.8em;
    margin: 0.2em;
    font-family: "Courier New", monospace;
    font-size: 1.2rem;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.2s ease;
    flex: 1;
    min-width: 50px;
    text-align: center;
}
.password-btn:hover {
    background: rgba(71, 202, 255, 0.2);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

.password-btn-weak {
    background: rgba(255, 75, 75, 0.2);
    border: 1px solid rgba(255, 75, 75, 0.5);
}
.password-btn-weak:hover {
    background: rgba(255, 75, 75, 0.3);
}

/* Поле пароля */
.password-display {
    background: rgba(0,0,0,0.3);
    border: 2px solid var(--accent-cyan);
    border-radius: 12px;
    padding: 1em;
    font-family: "Courier New", monospace;
    font-size: 1.5rem;
    letter-spacing: 2px;
    text-align: center;
    margin: 1em 0;
    min-height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    word-break: break-all;
}

/* Дорожная карта */
.roadmap-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 2.5em 0 1.5em 0;
}
.roadmap-line {
    width: min(900px, 100%);
    height: 6px;
    background: linear-gradient(90deg, var(--accent-green), var(--accent-cyan), var(--accent-green));
    border-radius: 999px;
    position: relative;
    margin-top: 1.8em;
}
.roadmap-point {
    position: absolute;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 20%, #FFFFFF 0, #3B175E 40%, #110B2F 100%);
    border: 2px solid var(--accent-green);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.6rem;
    transform: translate(-50%, -50%);
    transition: all 0.25s ease;
}
.roadmap-point:hover {
    transform: translate(-50%, -55%) scale(1.05);
    box-shadow: 0 0 18px rgba(0, 255, 0, 0.7);
}
.roadmap-label {
    position: absolute;
    top: 72px;
    transform: translateX(-50%);
    white-space: nowrap;
    color: var(--text-muted);
    font-size: 0.8rem;
    text-align: center;
}

/* Значки */
.badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: radial-gradient(circle at top left, #FFD700, #C68C00);
    color: #000;
    padding: 0.4em 0.9em;
    border-radius: 999px;
    margin: 0.25em;
    font-weight: 700;
    font-size: 0.9rem;
}

/* Счёт */
.score-display {
    font-size: 1.3rem;
    color: var(--accent-green);
    text-align: center;
    margin: 0.7em 0 1.5em 0;
}

/* Таблица профиля/устройства */
.fake-profile, .device-scan {
    background: rgba(15, 10, 40, 0.9);
    border-radius: 18px;
    padding: 1.4em 1.6em;
    border: 1px solid rgba(255,255,255,0.08);
}

/* Индикаторы правил */
.rule-indicator {
    display: flex;
    align-items: center;
    margin: 0.5em 0;
    padding: 0.5em;
    border-radius: 8px;
    background: rgba(255,255,255,0.05);
}
.rule-indicator.passed {
    background: rgba(0, 255, 0, 0.1);
    border-left: 4px solid var(--accent-green);
}
.rule-indicator.failed {
    background: rgba(255, 75, 75, 0.1);
    border-left: 4px solid var(--danger);
}

/* Боковая панель */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1B1638, #0A071A);
    border-right: 1px solid rgba(255,255,255,0.12);
}
</style>
""",
    unsafe_allow_html=True,
)


# ==========================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ИГРЫ С ПАРОЛЕМ
# ==========================

def check_password_game_rules(password: str):
    """Проверяет пароль по всем правилам и возвращает детальный отчет"""
    rules = {
        "length_12": {
            "passed": len(password) >= 12,
            "message": "Длина ≥ 12 символов",
            "hint": f"Сейчас: {len(password)} символов" if len(password) < 12 else "✓"
        },
        "upper_lower": {
            "passed": bool(re.search(r'[A-ZА-Я]', password)) and bool(re.search(r'[a-zа-я]', password)),
            "message": "Заглавные и строчные буквы",
            "hint": "Нужны буквы обоих регистров"
        },
        "digits": {
            "passed": bool(re.search(r'\d', password)),
            "message": "Хотя бы одна цифра",
            "hint": "Добавьте цифры (0-9)"
        },
        "special_chars": {
            "passed": bool(re.search(r'[!@#$%^&*()\-_=+\[\]{}|;:,.<>?/`~]', password)),
            "message": "Специальные символы",
            "hint": "Добавьте ! @ # $ % и др."
        },
        "no_personal_info": {
            "passed": not any(word in password.lower() for word in [
                "alexey", "алексей", "2008", "2009", "москва", "moscow",
                "школа", "school", "паспорт", "passport", "логин", "login"
            ]),
            "message": "Без личных данных",
            "hint": "Не используйте имена, даты, города"
        },
        "no_weak_sequences": {
            "passed": not any(seq in password.lower() for seq in [
                "123456", "qwerty", "password", "12345", "12345678",
                "123123", "111111", "1234", "000000", "654321"
            ]),
            "message": "Без простых последовательностей",
            "hint": "Избегайте qwerty, 123456 и т.д."
        }
    }

    # Подсчет очков
    score = sum(1 for rule in rules.values() if rule["passed"])

    return rules, score


def add_to_password(char: str):
    """Добавляет символ к паролю в игре"""
    st.session_state.password_game_input += char


def clear_password():
    """Очищает пароль в игре"""
    st.session_state.password_game_input = ""
    st.session_state.password_game_feedback = ""


def check_password_game():
    """Проверяет пароль в игре и показывает результат"""
    password = st.session_state.password_game_input
    if not password:
        st.session_state.password_game_feedback = " Пароль пустой! Добавьте символы."
        return

    rules, score = check_password_game_rules(password)

    # Сохраняем результат
    st.session_state.password_game_score = score
    st.session_state.password_game_attempts += 1

    # Формируем фидбэк
    if score == 6:
        feedback = " Отличный пароль! Все правила соблюдены!"
        st.session_state.password_game_feedback = feedback
    else:
        feedback_parts = [f"Ваш пароль: `{password}`"]
        feedback_parts.append(f"Оценка: {score}/6 баллов")
        feedback_parts.append("\n**Что нужно улучшить:**")

        for rule_name, rule in rules.items():
            if not rule["passed"]:
                feedback_parts.append(f" {rule['message']} — {rule['hint']}")

        feedback_parts.append("\n**Что сделано правильно:**")
        correct_rules = [rule for rule in rules.values() if rule["passed"]]
        if correct_rules:
            for rule in correct_rules:
                feedback_parts.append(f"{rule['message']}")
        else:
            feedback_parts.append("Пока ничего... Попробуйте добавить элементы!")

        st.session_state.password_game_feedback = "\n".join(feedback_parts)


# ==========================
# СЮЖЕТ И ПРОГРЕССИЯ
# ==========================

def update_progress():
    """Обновляет прогресс прохождения и открывает новые миссии"""
    completed_missions = sum([
        st.session_state.mission1_checked,
        st.session_state.mission2_checked,
        st.session_state.mission3_checked,
        st.session_state.mission4_checked,
    ])

    # Открываем миссии постепенно
    st.session_state.missions_unlocked = min(4, completed_missions + 1)

    # Сюжетные сообщения при переходе
    story_messages = {
        1: " *Миссия активирована!* Виртуальный мир атакуют хакеры-тени. "
           "Твоя первая задача — создать неприступный пароль.",
        2: " *Новая угроза обнаружена!* В соцсетях появились фейковые профили. "
           "Проверь настройки приватности.",
        3: " *Тревога!* Распространяются фейковые новости. "
           "Научись отличать правду от вымысла.",
        4: " *Критическая уязвимость!* Обнаружены бреши в защите устройств. "
           "Проведи экстренное сканирование.",
        5: " *Финальная битва!* Пройди итоговый тест и стань Цифровым Куратором."
    }

    if completed_missions + 1 in story_messages:
        st.session_state.story_message = story_messages[completed_missions + 1]


def evaluate_password_strength(pwd: str) -> int:
    """Оцениваем пароль по 0–3"""
    if not pwd:
        return 0
    score = 0
    if len(pwd) >= 12:
        score += 1
    if re.search(r"[a-z]", pwd) and re.search(r"[A-Z]", pwd):
        score += 1
    if re.search(r"\d", pwd) and re.search(r"[^A-Za-z0-9]", pwd):
        score += 1
    return score


def award_badge(badge_name, description):
    """Награждает значком с анимацией"""
    if badge_name not in st.session_state.badges:
        st.session_state.badges.append(badge_name)
        st.session_state.new_badge = (badge_name, description)
        return True
    return False


def show_badge_animation():
    """Показывает анимацию получения значка"""
    if hasattr(st.session_state, 'new_badge'):
        badge_name, description = st.session_state.new_badge

        st.markdown(f"""
        <div style="
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: radial-gradient(circle at center, rgba(59,23,94,0.95), rgba(17,11,47,0.98));
            border: 3px solid #FFD700;
            border-radius: 24px;
            padding: 2em;
            z-index: 1000;
            box-shadow: 0 0 40px rgba(255, 215, 0, 0.6);
            animation: badgePop 0.8s ease-out;
            text-align: center;
            min-width: 300px;
        ">
            <div style="font-size: 4em; margin-bottom: 0.2em;"></div>
            <h3 style="color: #FFD700; margin-bottom: 0.5em;">НОВЫЙ ЗНАЧОК!</h3>
            <div class="badge" style="font-size: 1.2em; margin: 0.5em auto;">{badge_name}</div>
            <p style="color: #C2C2D9; margin-top: 1em;">{description}</p>
        </div>
        <style>
        @keyframes badgePop {{
            0% {{ transform: translate(-50%, -50%) scale(0.1); opacity: 0; }}
            70% {{ transform: translate(-50%, -50%) scale(1.1); opacity: 1; }}
            100% {{ transform: translate(-50%, -50%) scale(1); opacity: 1; }}
        }}
        </style>
        """, unsafe_allow_html=True)

        # Удаляем после показа
        del st.session_state.new_badge


# ==========================
# СТРАНИЦЫ
# ==========================

# СЛАЙД 1 — ЗАСТАВКА
if st.session_state.current_page == "start":
    st.markdown(
        '<div class="main-header"> Цифровой квест: стань цифровым куратором!</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-header">Интерактивный урок по информационной безопасности и цифровой гигиене</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="text-align:center;color:#C2C2D9;margin-bottom:2em;">Возраст: 14–16 лет</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(" Начать квест", use_container_width=True, type="primary"):
            go_to_page("roadmap")

# ДОРОЖНАЯ КАРТА
elif st.session_state.current_page == "roadmap":
    update_progress()

    st.markdown('<div class="main-header"> Дорожная карта миссий</div>', unsafe_allow_html=True)

    # Сюжетное сообщение
    if hasattr(st.session_state, 'story_message'):
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(59,23,94,0.9), rgba(17,11,47,0.9));
            border: 2px solid #00FF00;
            border-radius: 16px;
            padding: 1.2em;
            margin-bottom: 1.5em;
            text-align: center;
        ">
            <span style="color:#47CAFF; font-size:1.1em;">{st.session_state.story_message}</span>
        </div>
        """, unsafe_allow_html=True)

    # Отображаем дорожную карту с миссиями
    c1, c2, c3, c4, c5 = st.columns(5)

    missions = [
        (1, "🔐 Миссия 1\nПароли", "mission1_theory"),
        (2, "👤 Миссия 2\nСоцсети", "mission2_theory"),
        (3, "📰 Миссия 3\nФейки", "mission3_theory"),
        (4, "⚙️ Миссия 4\nУстройства", "mission4_theory"),
        (5, "🎓 Финальный тест", "final_test")
    ]

    for i, (mission_num, label, page) in enumerate(missions):
        col = [c1, c2, c3, c4, c5][i]
        with col:
            unlocked = mission_num <= st.session_state.get('missions_unlocked', 1)

            if unlocked:
                if st.button(label, use_container_width=True, key=f"roadmap_btn_{mission_num}"):
                    go_to_page(page)
            else:
                st.button(
                    f"🔒 {label.split()[0]}\n(скрыто)",
                    use_container_width=True,
                    disabled=True,
                    help="Пройдите предыдущие миссии для разблокировки"
                )

            # Показываем счёт только для пройденных
            if mission_num == 1:
                score = st.session_state.mission1_score
                color = "#00FF00" if score >= 6 else "#FF4B4B"
            elif mission_num == 2:
                score = st.session_state.mission2_score
                color = "#00FF00" if score >= 8 else "#FF4B4B"
            elif mission_num == 3:
                score = st.session_state.mission3_score
                color = "#00FF00" if score >= 8 else "#FF4B4B"
            elif mission_num == 4:
                score = st.session_state.mission4_score
                color = "#00FF00" if score >= 7 else "#FF4B4B"
            else:
                score = st.session_state.final_test_score
                color = "#00FF00" if score >= 6 else "#FF4B4B"

            if unlocked:
                st.markdown(
                    f"<div style='text-align:center;color:{color};font-size:0.9rem;'>Счёт: {score}/{[6, 8, 8, 7, 8][mission_num - 1]}</div>",
                    unsafe_allow_html=True,
                )

# ==========================
# МИССИЯ 1 — ПАРОЛИ (ТЕОРИЯ)
# ==========================
elif st.session_state.current_page == "mission1_theory":
    st.markdown('<div class="main-header"> Теория: надёжные пароли</div>', unsafe_allow_html=True)

    st.markdown(
        """
    <div class="theory-card">
      <h3 style="color:#47CAFF;">Почему пароли так важны?</h3>
      <p>Пароль — это первая линия защиты вашего цифрового пространства. Как ключ от дома, 
      он должен быть уникальным и сложным для подбора.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Чего НЕ делать")
        st.markdown(
            """
        <div class="theory-card">
        • Использовать личные данные (имя, дату рождения)<br>
        • Применять простые последовательности (123456, qwerty)<br>
        • Использовать один пароль везде<br>
        • Хранить пароли в незащищённых местах<br>
        • Делиться паролями с другими
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown("### Что делать")
        st.markdown(
            """
        <div class="theory-card">
        • Минимум 12 символов<br>
        • Буквы верхнего и нижнего регистра<br>
        • Цифры и специальные символы<br>
        • Отдельный пароль для каждого сервиса<br>
        • Менеджер паролей<br>
        • Двухфакторная аутентификация (2FA)
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("### Технические факты")
    st.markdown(
        """
    <div class="theory-card">
      • Пароль из 8 символов (только буквы) можно взломать за часы<br>
      • Пароль из 12+ символов (буквы+цифры+символы) — уже сотни лет перебора<br>
      • 2FA снижает риск взлома почти на 99%<br>
      • Большинство взломов происходит из-за слабых или повторяющихся паролей
    </div>
    """,
        unsafe_allow_html=True,
    )

    _, c2, _ = st.columns([1, 2, 1])
    with c2:
        if st.button(" Перейти к сборке пароля", use_container_width=True, type="primary"):
            go_to_page("mission1_practice")

# ==========================
# МИССИЯ 1 — ПРАКТИКА (МИНИ-ИГРА С ПАРОЛЕМ)
# ==========================
elif st.session_state.current_page == "mission1_practice":
    st.markdown('<div class="main-header"> Миссия 1: собери безопасный пароль</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Собери пароль из предложенных элементов, соблюдая все правила</div>',
                unsafe_allow_html=True)

    # Отображаем текущий пароль
    st.markdown(f'<div class="password-display">{st.session_state.password_game_input or "..."}</div>',
                unsafe_allow_html=True)

    # Кнопки для управления паролем
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(" Очистить пароль", use_container_width=True, on_click=clear_password):
            pass
    with col2:
        if st.button(" Проверить пароль", use_container_width=True, type="primary", on_click=check_password_game):
            pass
    with col3:
        if st.button(" Завершить миссию", use_container_width=True):
            # Сохраняем результаты
            st.session_state.mission1_score = st.session_state.password_game_score
            st.session_state.mission1_checked = True
            recompute_total()

            if st.session_state.password_game_score >= 5:
                if " Мастер паролей" not in st.session_state.badges:
                    st.session_state.badges.append(" Мастер паролей")

            go_to_page("roadmap")

    # Панель с символами для сборки пароля
    st.markdown("### Выберите символы для пароля:")

    # Заглавные буквы
    st.markdown("#### Заглавные буквы:")
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    upper_letters = ["A", "B", "C", "D", "E", "F", "G"]
    for i, letter in enumerate(upper_letters):
        with [col1, col2, col3, col4, col5, col6, col7][i]:
            if st.button(letter, key=f"upper_{letter}", use_container_width=True):
                add_to_password(letter)

    # Строчные буквы
    st.markdown("#### Строчные буквы:")
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    lower_letters = ["a", "b", "c", "d", "e", "f", "g"]
    for i, letter in enumerate(lower_letters):
        with [col1, col2, col3, col4, col5, col6, col7][i]:
            if st.button(letter, key=f"lower_{letter}", use_container_width=True):
                add_to_password(letter)

    # Цифры
    st.markdown("#### Цифры:")
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    digits = ["0", "1", "2", "3", "4", "5", "6"]
    for i, digit in enumerate(digits):
        with [col1, col2, col3, col4, col5, col6, col7][i]:
            if st.button(digit, key=f"digit_{digit}", use_container_width=True):
                add_to_password(digit)

    # Специальные символы
    st.markdown("#### Специальные символы:")
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    specials = ["!", "@", "#", "$", "%", "^", "&"]
    for i, spec in enumerate(specials):
        with [col1, col2, col3, col4, col5, col6, col7][i]:
            if st.button(spec, key=f"spec_{spec}", use_container_width=True):
                add_to_password(spec)

    # Слабые элементы (для обучения)
    st.markdown("#### Слабые элементы (не использовать!):")
    col1, col2, col3 = st.columns(3)
    weak_elements = ["123456", "qwerty", "password"]
    weak_hints = ["Простая последовательность", "Расположение клавиш", "Словарное слово"]

    for i, (weak, hint) in enumerate(zip(weak_elements, weak_hints)):
        with [col1, col2, col3][i]:
            if st.button(f"{weak}\n({hint})", key=f"weak_{weak}",
                         use_container_width=True,
                         help="Этот элемент сделает пароль слабым!"):
                add_to_password(weak)

    # Отображение обратной связи и проверки правил
    if st.session_state.password_game_feedback:
        st.markdown("### Результат проверки:")
        st.markdown(f"""
        <div class="mission-card">
        {st.session_state.password_game_feedback.replace(' ', '<br>')}
        </div>
        """, unsafe_allow_html=True)

    # Если пароль есть, показываем правила
    if st.session_state.password_game_input:
        password = st.session_state.password_game_input
        rules, score = check_password_game_rules(password)

        st.markdown("### Проверка правил:")
        for rule_name, rule in rules.items():
            status = "passed" if rule["passed"] else "failed"
            icon = "✅" if rule["passed"] else "❌"
            st.markdown(f"""
            <div class="rule-indicator {status}">
                <span style="font-size: 1.2em; margin-right: 10px;">{icon}</span>
                <div>
                    <strong>{rule['message']}</strong><br>
                    <small>{rule['hint']}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Прогресс-бар
        st.markdown(f"**Прогресс: {score}/6 правил**")
        st.progress(score / 6)

    # Информация о миссии
    st.markdown("---")
    st.markdown("### Задание:")
    st.markdown("""
    <div class="theory-card">
    1. Собери пароль из предложенных символов<br>
    2. Пароль должен соответствовать ВСЕМ правилам:<br>
       &nbsp;&nbsp;• Длина не менее 12 символов<br>
       &nbsp;&nbsp;• Заглавные и строчные буквы<br>
       &nbsp;&nbsp;• Цифры и специальные символы<br>
       &nbsp;&nbsp;• Без личных данных (имя, дата рождения)<br>
       &nbsp;&nbsp;• Без простых последовательностей (123456, qwerty)<br>
    3. Нажмите "Проверить пароль" для оценки<br>
    4. Наберите минимум 5 баллов для успешного прохождения<br>
    5. Нажмите "Завершить миссию" для сохранения результата
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    _, c2, _ = st.columns([1, 2, 1])
    with c2:
        if st.button(" Назад к дорожной карте", use_container_width=True):
            go_to_page("roadmap")

# ==========================
# МИССИЯ 2 — СОЦСЕТИ (остаётся без изменений)
# ==========================
elif st.session_state.current_page == "mission2_theory":
    st.markdown('<div class="main-header"> Теория: безопасность в соцсетях</div>', unsafe_allow_html=True)

    st.markdown(
        """
    <div class="theory-card">
      <h3 style="color:#47CAFF;">Цифровой след — это надолго</h3>
      <p>Каждое действие в социальных сетях оставляет след: лайки, комментарии, фото, истории. 
      Эту информацию могут использовать мошенники, работодатели и учебные заведения.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("### Опасности открытого профиля")
    st.markdown(
        """
    <div class="theory-card">
      <h4> Доксинг</h4>
      <p>Сбор и публикация личной информации без согласия: ФИО, адрес, телефон, место учёбы.</p>

      <h4>Социальная инженерия</h4>
      <p>Мошенники используют ваши данные, чтобы выманить ещё больше информации или деньги.</p>

      <h4> Геолокация</h4>
      <p>Постоянная геолокация позволяет понять, где вы живёте, учитесь и когда вас нет дома.</p>

      <h4> Фишинг через «знакомых»</h4>
      <p>Фейковые аккаунты друзей, которые просят «срочно скинуть код из СМС».</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("### Базовые настройки безопасности")
    st.markdown(
        """
    <div class="theory-card">
      • Закрытый профиль / доступ только друзьям<br>
      • Ограничение видимости даты рождения и школы<br>
      • Контроль отметок и тегов на фото<br>
      • Регулярная «чистка» списка друзей<br>
      • Осторожность с личной информацией в постах
    </div>
    """,
        unsafe_allow_html=True,
    )

    _, c2, _ = st.columns([1, 2, 1])
    with c2:
        if st.button(" Перейти к проверке профиля", use_container_width=True, type="primary"):
            go_to_page("mission2_practice")

elif st.session_state.current_page == "mission2_practice":
    st.markdown('<div class="main-header"> Миссия 2: проверь профиль</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Теперь не просто найти опасности, а настроить профиль правильно</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div class="fake-profile">
      <h3 style="color:#00FF00;margin-bottom:0.4em;">Профиль: Алексей_2008</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:1em;margin-top:0.6em;">
        <div>
          <h4>Информация</h4>
          <ul>
            <li> Геолокация: <strong>всегда включена, видна всем</strong></li>
            <li>Дата рождения: <strong>15.03.2008, видна всем</strong></li>
            <li>Город: <strong>Москва</strong> (открыто)</li>
            <li> Школа: <strong>фото школы с адресом</strong></li>
          </ul>
        </div>
        <div>
          <h4>Активность</h4>
          <ul>
            <li>Сторис: <strong>фото паспорта</strong></li>
            <li> Профиль: <strong>полностью открытый</strong></li>
            <li>Друзья: <strong>список открыт всем</strong></li>
            <li> Переписка: <strong>регулярно общается с незнакомцами</strong></li>
          </ul>
        </div>
      </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("### Задание: выбери, что сделать с каждой настройкой")

    options = ["Оставить как есть", "Ограничить доступ", "Удалить / выключить"]

    profile_questions = {
        "Геолокация всегда включена и видна всем": "Удалить / выключить",
        "Дата рождения полностью открыта": "Ограничить доступ",
        "Фото школы с адресом": "Удалить / выключить",
        "Фото паспорта в сторис": "Удалить / выключить",
        "Профиль полностью открытый": "Ограничить доступ",
        "Список друзей открыт всем": "Ограничить доступ",
        "Переписка с незнакомцами": "Удалить / выключить",
        "Принимает все заявки в друзья": "Ограничить доступ",
    }

    user_choices = {}
    for q in profile_questions:
        col_l, col_r = st.columns([2, 1])
        with col_l:
            st.write(f"• {q}")
        with col_r:
            user_choices[q] = st.selectbox(
                "Действие:",
                options,
                key=f"m2_{q}",
            )

    if st.button(" Проверить миссию 2"):
        score = 0
        for q, correct in profile_questions.items():
            if user_choices.get(q) == correct:
                score += 1

        st.session_state.mission2_score = min(score, 8)
        st.session_state.mission2_checked = True
        recompute_total()

        if score == 8:
            st.success(" Ты идеально настроил профиль! +8 баллов")
            st.balloons()
        else:
            st.info(f"Ты набрал {score}/8. Попробуй посмотреть, где ещё можно усилить приватность.")

        if " Чистый профиль" not in st.session_state.badges and st.session_state.mission2_score >= 7:
            st.session_state.badges.append(" Чистый профиль")

    st.markdown("---")
    _, c2, _ = st.columns([1, 2, 1])
    with c2:
        if st.button(" Назад к дорожной карте", use_container_width=True):
            go_to_page("roadmap")

# ==========================
# МИССИЯ 3 — ФЕЙКИ (остаётся без изменений)
# ==========================
elif st.session_state.current_page == "mission3_theory":
    st.markdown('<div class="main-header"> Теория: как отличить фейк от правды</div>', unsafe_allow_html=True)

    st.markdown(
        """
    <div class="theory-card">
      <h3 style="color:#47CAFF;">Информационная война — реальность</h3>
      <p>Фейковые новости распространяются быстрее правдивых. Их цель — манипулировать эмоциями, 
      создавать панику и управлять мнением людей.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("###  Признаки фейковой новости")
    st.markdown(
        """
    <div class="theory-card">
      1. Кликбейтный, эмоциональный заголовок<br>
      2. Нет автора или он неясен<br>
      3. Нет даты или она сильно устарела<br>
      4. Сомнительный, неизвестный источник<br>
      5. Ошибки в тексте, странная логика<br>
      6. Давление на эмоции: страх, гнев, шок<br>
      7. Нет ссылок на исследования и документы<br>
      8. Картинки «из другого места»<br>
      9. Категоричные фразы: «все учёные доказали», «100% правда»<br>
      10. Легко проверяется и противоречит известным фактам
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("###  Алгоритм проверки")
    st.markdown(
        """
    <div class="theory-card">
      <strong>1. Источник:</strong> кто автор, что за сайт, есть ли контакты?<br><br>
      <strong>2. Факты:</strong> есть ли подтверждение в других надёжных источникаи?<br><br>
      <strong>3. Контекст:</strong> когда написано, как оформлено, не вырвано ли из контекста?<br><br>
      <strong>4. Критическое мышление:</strong> кому выгодна эта информация, какие эмоции она вызывает?
    </div>
    """,
        unsafe_allow_html=True,
    )

    _, c2, _ = st.columns([1, 2, 1])
    with c2:
        if st.button(" Перейти к расследованию новости", use_container_width=True, type="primary"):
            go_to_page("mission3_practice")

elif st.session_state.current_page == "mission3_practice":
    st.markdown('<div class="main-header">📰 Миссия 3: расследуй новость</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Выяви признаки фейка и оцени источники</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div class="mission-card">
      <h2 style="color:#FF4B4B;text-align:center;margin-bottom:0.2em;">СЕНСАЦИЯ!</h2>
      <h3 style="text-align:center;">Учёные доказали, что зарядка телефона ночью вызывает потерю памяти!</h3>
      <p style="text-align:center;font-style:italic;">Источник: SuperNews.ru</p>
      <p style="text-align:center;color:#C2C2D9;">Опубликовано: «недавно»</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("### 1. Какие элементы заставляют сомневаться в новости?")
    fake_signs_options = {
        "Крикливый кликбейтный заголовок": True,
        "Точный источник с ссылкой на научную статью": False,
        "Неясная формулировка «опубликовано недавно»": True,
        "Сайт SuperNews.ru неизвестен и сомнителен": True,
        "Подробное описание исследования: методика, выборка": False,
        "Нет конкретных ссылок на учёных и институт": True,
    }

    selected_signs = st.multiselect(
        "Отметь элементы, которые выглядят подозрительно:",
        list(fake_signs_options.keys()),
        key="m3_signs",
    )

    st.markdown("### 2. Оцени источники: «скорее надёжный» или «скорее сомнительный»")
    sources = {
        "Официальный сайт крупного университета": True,
        "Анонимный канал в мессенджере": False,
        "Личный блог без ссылок на источники": False,
        "Государственный портал с открытой статистикой": True,
        "Накрученный новостной сайт с кучей рекламы": False,
        "Крупное международное агентство новостей": True,
    }

    user_source_eval = {}
    for s in sources:
        col_l, col_r = st.columns([2, 1])
        with col_l:
            st.write(f"• {s}")
        with col_r:
            user_source_eval[s] = st.radio(
                "Оценка:",
                ["Скорее надёжный", "Скорее сомнительный"],
                key=f"m3_src_{s}",
                horizontal=False,
            )

    if st.button("Проверить миссию 3"):
        score = 0

        # 1) признаки фейка — 0–2 балла
        correct_signs = {k for k, v in fake_signs_options.items() if v}
        selected = set(selected_signs)
        right = len(selected & correct_signs)
        wrong = len(selected - correct_signs)

        if right >= 3 and wrong == 0:
            score += 2
        elif right >= 2 and wrong <= 1:
            score += 1

        # 2) источники — 0–6 баллов
        for s, reliable in sources.items():
            user_rel = user_source_eval.get(s) == "Скорее надёжный"
            if user_rel == reliable:
                score += 1

        st.session_state.mission3_score = min(score, 8)
        st.session_state.mission3_checked = True
        recompute_total()

        if score == 8:
            st.success(" Ты блестяще разобрался с фейками и источниками! +8 баллов")
            st.balloons()
        else:
            st.info(f"Ты набрал {score}/8. Обрати внимание, какие источники и признаки были неточными.")

        if " Антифейкер" not in st.session_state.badges and st.session_state.mission3_score >= 7:
            st.session_state.badges.append(" Антифейкер")

    st.markdown("---")
    _, c2, _ = st.columns([1, 2, 1])
    with c2:
        if st.button(" Назад к дорожной карте", use_container_width=True):
            go_to_page("roadmap")

# ==========================
# МИССИЯ 4 — УСТРОЙСТВА (остаётся без изменений)
# ==========================
elif st.session_state.current_page == "mission4_theory":
    st.markdown('<div class="main-header"> Теория: защита устройств</div>', unsafe_allow_html=True)

    st.markdown(
        """
    <div class="theory-card">
      <h3 style="color:#47CAFF;">Устройство — ваш цифровой двойник</h3>
      <p>Смартфон или компьютер хранят переписки, фото, доступ к банковским счетам, 
      историю поиска, геолокацию и контакты. Потеря или взлом устройства — это не только «сломанный телефон», 
      но и утечка огромного объёма личной информации.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("###  Основные угрозы")
    st.markdown(
        """
    <div class="theory-card">
      <h4> Мобильные угрозы</h4>
      • Вредоносные приложения<br>
      • СМС-фишинг<br>
      • Небезопасные открытые Wi-Fi сети<br>
      • Уязвимости операционной системы<br><br>
      <h4> Компьютерные угрозы</h4>
      • Вирусы и трояны<br>
      • Фишинговые сайты<br>
      • Рекламное и шпионское ПО<br>
      • Кейлоггеры (запись нажатий клавиш)
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("###Защита устройства")
    st.markdown(
        """
    <div class="theory-card">
      • Обновления системы и приложений<br>
      • Надёжная блокировка экрана (пароль, биометрия)<br>
      • Установка приложений только из официальных магазинов<br>
      • Проверка разрешений приложений<br>
      • Функция «Найти устройство» и резервные копии
    </div>
    """,
        unsafe_allow_html=True,
    )

    _, c2, _ = st.columns([1, 2, 1])
    with c2:
        if st.button("🚀 Перейти к сканированию устройства", use_container_width=True, type="primary"):
            go_to_page("mission4_practice")

elif st.session_state.current_page == "mission4_practice":
    st.markdown('<div class="main-header"> Миссия 4: сканирование устройства</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Определи, как правильно устранить проблемы</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div class="device-scan">
      <h4> Обнаружены проблемы:</h4>
      <p>Представь, что ты открываешь «Сканер безопасности» на смартфоне.  
      Он нашёл несколько уязвимостей, для каждой нужно выбрать корректное действие.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    actions = ["Оставить как есть", "Отключить / удалить", "Включить защиту / настроить"]

    device_issues = {
        "Обновления системы отключены": "Включить защиту / настроить",
        "GPS всегда включён": "Отключить / удалить",
        "Bluetooth постоянно активен": "Отключить / удалить",
        "Установлен сторонний APK из неизвестного источника": "Отключить / удалить",
        "Подозрительное приложение с лишними разрешениями": "Отключить / удалить",
        "Пароль разблокировки: 0000": "Включить защиту / настроить",
        "На устройстве нет блокировки экрана": "Включить защиту / настроить",
    }

    user_actions = {}
    for issue in device_issues:
        col_l, col_r = st.columns([2, 1])
        with col_l:
            st.write(f"• {issue}")
        with col_r:
            user_actions[issue] = st.selectbox(
                "Действие:",
                actions,
                key=f"m4_{issue}",
            )

    if st.button(" Проверить миссию 4"):
        score = 0
        for issue, correct in device_issues.items():
            if user_actions.get(issue) == correct:
                score += 1

        st.session_state.mission4_score = min(score, 7)
        st.session_state.mission4_checked = True
        recompute_total()

        if score == 7:
            st.success(" Отлично! Ты грамотно защитил устройство. +7 баллов")
            st.balloons()
        else:
            st.info(f"Ты набрал {score}/7. Подумай, какие настройки ещё можно усилить.")

        if " Хозяин устройства" not in st.session_state.badges and st.session_state.mission4_score >= 6:
            st.session_state.badges.append("️ Хозяин устройства")

    st.markdown("---")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button(" Перейти к финальному тесту", use_container_width=True):
            go_to_page("final_test")
        if st.button(" Назад к дорожной карте", use_container_width=True):
            go_to_page("roadmap")

# ==========================
# ФИНАЛЬНЫЙ ТЕСТ (остаётся без изменений)
# ==========================
elif st.session_state.current_page == "final_test":
    st.markdown('<div class="main-header"> Финальный тест</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Проверь, готов ли ты к званию цифрового куратора</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### 1. Пароли")
    q1 = st.radio(
        "Какое утверждение о паролях наиболее верное?",
        [
            "Главное — запомнить пароль, остальное неважно",
            "Можно использовать один длинный пароль для всех сервисов",
            "Лучше использовать разные сложные пароли и менеджер паролей",
        ],
        key="ft_q1",
    )

    st.markdown("#### 2. Соцсети")
    q2 = st.multiselect(
        "Какие из действий безопасны?",
        [
            "Публиковать фото паспорта в сторис, но только на 24 часа",
            "Ограничить видимость даты рождения только для друзей",
            "Принимать в друзья только тех, кого знаешь лично",
            "Всегда указывать школу и класс в описании профиля",
        ],
        key="ft_q2",
    )

    st.markdown("#### 3. Подозрительное сообщение")
    q3 = st.radio(
        "Тебе пишет «админ школы» и просит прислать код из СМС для участия в конкурсе. Что ты сделаешь?",
        [
            "Отправлю код, если страница выглядит настоящей",
            "Спрошу у друзей и всё равно отправлю, если все так делают",
            "Не отправлю код, проверю информацию через официальные каналы",
        ],
        key="ft_q3",
    )

    st.markdown("#### 4. Фейковые новости")
    q4 = st.radio(
        "Что из этого — хороший первый шаг при проверке новости?",
        [
            "Сразу переслать новость друзьям — пусть тоже знают",
            "Проверить источник и поискать подтверждение в других СМИ",
            "Сразу написать гневный комментарий автору новости",
        ],
        key="ft_q4",
    )

    st.markdown("#### 5. Источники")
    q5 = st.radio(
        "Где с большей вероятностью окажется проверенная информация?",
        [
            "Анонимный Telegram-канал без описания",
            "Официальный сайт госоргана или крупного университета",
            "Мем-страница с шутками и картинками",
        ],
        key="ft_q5",
    )

    st.markdown("#### 6. Термин")
    q6 = st.text_input(
        "Как называется механизм, когда при входе помимо пароля нужно ввести код из СМС или приложение-генератор?",
        key="ft_q6",
    )

    st.markdown("#### 7. Устройства")
    q7 = st.radio(
        "Что из перечисленного самое разумное в открытой Wi-Fi сети в кафе?",
        [
            "Войти в интернет-банк и перевести деньги",
            "Зайти в соцсети и поменять все пароли",
            "Избегать ввода паролей и по возможности использовать VPN",
        ],
        key="ft_q7",
    )

    st.markdown("#### 8. Бонус")
    q8 = st.multiselect(
        "Что помогает уменьшить последствия взлома устройства?",
        [
            "Регулярные резервные копии данных",
            "Использование одного пароля везде",
            "Шифрование устройства",
            "Хранение паролей на стикере, приклеенном к монитору",
        ],
        key="ft_q8",
    )

    if st.button(" Проверить финальный тест"):
        score = 0

        if q1 == "Лучше использовать разные сложные пароли и менеджер паролей":
            score += 1

        if set(q2) == {
            "Ограничить видимость даты рождения только для друзей",
            "Принимать в друзья только тех, кого знаешь лично",
        }:
            score += 1

        if q3 == "Не отправлю код, проверю информацию через официальные каналы":
            score += 1

        if q4 == "Проверить источник и поискать подтверждение в других СМИ":
            score += 1

        if q5 == "Официальный сайт госоргана или крупного университета":
            score += 1

        ans6 = q6.strip().lower()
        if any(
                key in ans6
                for key in ["2fa", "двухфактор", "двух фактор", "двухэтап", "двух этап"]
        ):
            score += 1

        if q7 == "Избегать ввода паролей и по возможности использовать VPN":
            score += 1

        if set(q8) == {"Регулярные резервные копии данных", "Шифрование устройства"}:
            score += 1

        st.session_state.final_test_score = score
        st.session_state.final_test_checked = True
        recompute_total()

        if score == 8:
            st.success(" Идеально! Ты набрал максимум за финальный тест.")
            st.balloons()
        else:
            st.info(f"Ты набрал {score}/8 за финальный тест.")

        if " Выпускник квеста" not in st.session_state.badges and score >= 6:
            st.session_state.badges.append(" Выпускник квеста")

    st.markdown("---")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🏁 Посмотреть своё звание", use_container_width=True):
            go_to_page("final")
        if st.button("🗺️ Назад к дорожной карте", use_container_width=True):
            go_to_page("roadmap")

# ==========================
# ФИНАЛЬНЫЙ ЭКРАН (остаётся без изменений)
# ==========================
elif st.session_state.current_page == "final":
    recompute_total()
    total = st.session_state.total_score

    st.markdown('<div class="main-header"> Твоё звание</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="score-display"> Итоговый счёт: {total} баллов</div>',
        unsafe_allow_html=True,
    )

    if total <= 15:
        st.error(
            """
        ## 🟡 Новичок  
        Ты сделал первые шаги в цифровой безопасности.  
        Попробуй ещё раз пройти миссии и тест — каждая попытка делает тебя сильнее.
        """
        )
    elif total <= 25:
        st.warning(
            """
        ## 🟠 Продвинутый пользователь  
        Ты уже неплохо разбираешься в рисках и умеешь защищать себя.  
        Но до уровня наставника другим ещё чуть-чуть не хватает.
        """
        )
    elif total <= 33:
        st.info(
            """
        ## 🔵 Защитник данных  
        Отличный результат! Ты уверенно чувствуешь себя в цифровой среде и можешь помогать друзьям.  
        Ещё немного практики — и ты станешь настоящим цифровым куратором.
        """
        )
    else:
        st.success(
            """
        ## 🟢 Цифровой куратор  
        Поздравляем! Ты прошёл все миссии и финальный тест на высоком уровне.  
        Ты — человек, который не только сам в безопасности, но и может обучать других.
        """
        )
        st.balloons()

    if st.session_state.badges:
        st.markdown("###  Твои значки:")
        for badge in st.session_state.badges:
            st.markdown(f'<span class="badge">{badge}</span>', unsafe_allow_html=True)

    st.markdown("---")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("Открыть дорожную карту", use_container_width=True):
            go_to_page("roadmap")
        if st.button("Начать всё сначала", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            for key, value in DEFAULT_STATE.items():
                st.session_state[key] = value
            go_to_page("start")
            st.experimental_rerun()

# ==========================
# БОКОВАЯ ПАНЕЛЬ — ПРОГРЕСС
# ==========================
with st.sidebar:
    st.markdown("### Прогресс")
    recompute_total()
    st.markdown(f"**Общий счёт:** {st.session_state.total_score} баллов")
    st.markdown(f"**Миссия 1 (пароли):** {st.session_state.mission1_score}/6")
    st.markdown(f"**Миссия 2 (соцсети):** {st.session_state.mission2_score}/8")
    st.markdown(f"**Миссия 3 (фейки):** {st.session_state.mission3_score}/8")
    st.markdown(f"**Миссия 4 (устройства):** {st.session_state.mission4_score}/7")
    st.markdown(f"**Финальный тест:** {st.session_state.final_test_score}/8")
    st.markdown("---")
    if st.button("На главную"):
        go_to_page("start")
    if st.button(" Дорожная карта"):
        go_to_page("roadmap")

    if st.session_state.badges:
        st.markdown("###  Значки")
        for badge in st.session_state.badges:
            st.markdown(
                f'<div class="badge" style="margin:0.15em 0;font-size:0.8rem;">{badge}</div>',
                unsafe_allow_html=True,
            )