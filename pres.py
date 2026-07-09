import streamlit as st
import random

# ------------------------------
# Настройка страницы
# ------------------------------
st.set_page_config(
    page_title="Правовой навигатор",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------
# CSS в стиле демо-приложения
# ------------------------------
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
}

.stApp {
    background: radial-gradient(circle at top left, #3B175E 0, #110B2F 40%, #050314 100%);
    color: var(--text-main);
    font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.main-header {
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--accent-green);
    text-shadow: 0 0 18px rgba(0, 255, 0, 0.6);
    margin-bottom: 0.3em;
    letter-spacing: 0.03em;
}

.sub-header {
    font-size: 1.2rem;
    font-weight: 500;
    color: var(--accent-cyan);
    margin-bottom: 1.2em;
}

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

.cyber-button {
    background: linear-gradient(90deg, var(--accent-green), var(--accent-cyan));
    color: #000;
    border: none;
    padding: 0.7em 1.5em;
    border-radius: 999px;
    font-weight: 700;
    cursor: pointer;
    margin: 0.5em 0.3em;
    transition: all 0.25s ease;
    letter-spacing: 0.03em;
}
.cyber-button:hover {
    transform: translateY(-1px) scale(1.02);
    box-shadow: 0 0 20px rgba(0, 255, 160, 0.7);
}

.score-display {
    font-size: 1.3rem;
    color: var(--accent-green);
    margin: 0.7em 0 1.5em 0;
}

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

/* Боковая панель */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1B1638, #0A071A);
    border-right: 1px solid rgba(255,255,255,0.12);
}

/* Навигационные кнопки */
.nav-container {
    display: flex;
    justify-content: space-between;
    margin-top: 2rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------------
# Инициализация состояния
# ------------------------------
INIT_STATE = {
    "step": 0,                      # текущий шаг (0-4, 5 - финал)
    "max_reached_step": 0,          # максимальный достигнутый шаг (для навигации)
    "completed_steps": [False]*5,   # завершённость каждого из 5 шагов
    # Ответы по шагам
    "intro_q1": None,               # шаг 0
    # шаг 1 (сопоставление)
    "match_Владелец информации": None,
    "match_Обладатель информации": None,
    "match_Провайдер": None,
    "match_Владелец сайта": None,
    "match_Пользователь": None,
    "step1_checked": False,         # нажата ли кнопка "Проверить" на шаге 1
    # шаг 2 (4 вопроса + рефлексия)
    "step2_q1": None,
    "step2_q2": None,
    "step2_q3": None,
    "step2_q4": None,
    "step2_reflection": "",
    "step2_self_score": 0,          # слайдер самооценки (0-5)
    # шаг 3 (кейс + принципы)
    "step3_q1": None,
    "step3_q2": None,
    # шаг 4 (чек-лист + финальное задание)
    **{f"checklist_{i}": False for i in range(1, 11)},
    "step4_checked": False,
    "final_score_slider": 5,        # оценка пароля (1-10)
    "final_text": "",
}

for key, value in INIT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ------------------------------
# Вспомогательные функции
# ------------------------------
def go_to_step(step_idx):
    """Переход на указанный шаг (если разрешён)."""
    if step_idx <= st.session_state.max_reached_step:
        st.session_state.step = step_idx
        st.rerun()

def advance_step():
    """Переход на следующий шаг после завершения текущего."""
    cur = st.session_state.step
    if cur < 4:
        st.session_state.completed_steps[cur] = True
        st.session_state.step = cur + 1
        st.session_state.max_reached_step = max(st.session_state.max_reached_step, cur + 1)
    elif cur == 4:
        # Завершение модуля: переход к финальному экрану
        st.session_state.completed_steps[cur] = True
        st.session_state.step = 5
        st.session_state.max_reached_step = 5
    st.rerun()

# ------------------------------
# Боковая панель (навигация и прогресс)
# ------------------------------
with st.sidebar:
    st.markdown("## ⚖️ Правовой навигатор")
    # Прогресс-бар
    completed_count = sum(st.session_state.completed_steps)
    total_steps = 5
    st.progress(completed_count / total_steps)
    st.caption(f"Пройдено {completed_count} из {total_steps} разделов")

    st.markdown("### 📚 Разделы")
    steps_info = [
        "🎬 Вступление",
        "👥 Кто есть кто",
        "🔒 Личные данные",
        "🤝 Этика куратора",
        "📋 Заключение"
    ]
    for i, name in enumerate(steps_info):
        # Определяем статус: done/current/future
        if i < st.session_state.max_reached_step or (i == st.session_state.max_reached_step and st.session_state.step == i):
            # разрешён переход
            btn_label = f"{'✅' if st.session_state.completed_steps[i] else '📌'} {name}"
            if st.sidebar.button(btn_label, key=f"nav_{i}", disabled=(i > st.session_state.max_reached_step)):
                go_to_step(i)
        else:
            st.sidebar.button(f"🔒 {name}", disabled=True, key=f"nav_disabled_{i}")

# ------------------------------
# Шаг 0: Вступление
# ------------------------------
if st.session_state.step == 0:
    st.markdown('<div class="main-header">Зачем будущему куратору знать законы?</div>', unsafe_allow_html=True)

    # Текст, предваряющий видео
    st.markdown("""
    <div class="theory-card">
      <p><strong>Представьте:</strong> вы помогаете пожилому человеку зарегистрироваться на портале Госуслуг.
      Вы просите его продиктовать паспортные данные, СНИЛС, номер телефона.
      Вы уверены, что делаете доброе дело. Но знаете ли вы, что несёте юридическую ответственность за сохранность этих данных?</p>
    </div>
    """, unsafe_allow_html=True)

    # Сценарий видео (текстовая имитация)
    st.markdown("### 🎥 Сценарий видео")
    st.markdown("""
    <div class="mission-card" style="font-size:0.95rem; line-height:1.6;">
      <p><strong>0:00–0:15</strong> — Пожилой человек и молодой помощник за компьютером. На экране — портал Госуслуг.<br>
      <em>«Представьте: вы помогаете пожилому человеку зарегистрироваться на портале Госуслуг».</em></p>
      <p><strong>0:15–0:30</strong> — Помощник записывает данные в блокнот. Рядом появляется значок «внимание».<br>
      <em>«Вы просите его продиктовать паспортные данные, СНИЛС, номер телефона. Вы уверены, что делаете доброе дело».</em></p>
      <p><strong>0:30–0:45</strong> — Значок «внимание» превращается в восклицательный знак. Вопросы: «Что, если телефон украдут?», «Что, если вы отправите данные не тому адресату?»<br>
      <em>«Но знаете ли вы, что несёте юридическую ответственность за сохранность этих данных?»</em></p>
      <p><strong>0:45–1:15</strong> — Надпись: «Цифровой куратор — это профессионал, который работает с личной информацией людей».<br>
      <em>«Цифровой куратор — это не просто "помощник по компьютеру". Это профессионал, который работает с личной информацией людей и несёт за это ответственность».</em></p>
      <p><strong>1:15–1:40</strong> — Иконки: закон, щит, книга.<br>
      <em>«В этом разделе мы разберём: что такое информация и как закон защищает её владельцев; какие у вас есть права и обязанности; что можно и чего нельзя делать в интернете».</em></p>
      <p><strong>1:40–2:00</strong> — Итоговая надпись: «Знание закона — это не бюрократическая преграда, а ваш профессиональный щит».</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    # Вопрос после видео
    st.markdown("### ❓ Вопрос")
    options = {
        "A": "Сам пенсионер, так как он добровольно передал данные",
        "B": "Цифровой куратор, так как он работает с данными клиента",
        "C": "Оператор сайта Госуслуг, так как он обрабатывает данные"
    }
    choice = st.radio(
        "Как вы думаете, кто несёт ответственность за сохранность данных пенсионера?",
        options.keys(),
        format_func=lambda x: f"{x}: {options[x]}",
        key="intro_q1"
    )

    # Обратная связь (появляется сразу после выбора)
    if st.session_state.intro_q1 is not None:
        ans = st.session_state.intro_q1
        if ans == "B":
            st.success("✅ Совершенно верно! Цифровой куратор несёт ответственность за сохранность данных клиента с момента их получения. Это закреплено в законе № 152-ФЗ «О персональных данных».")
        elif ans == "A":
            st.error("❌ Неверно. Пенсионер передал данные добровольно, но это не снимает ответственности с того, кто эти данные принимает и обрабатывает. Подробнее — в разделе о персональных данных.")
        else:
            st.error("❌ Неверно. Оператор сайта отвечает за обработку данных на своей платформе, но вы как цифровой куратор также несёте ответственность за данные, которые получаете при работе с клиентом.")

    # Кнопка "Далее" (активна после ответа)
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([8, 2])
    with col2:
        if st.button("Далее ➡️", disabled=(st.session_state.intro_q1 is None)):
            advance_step()
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------
# Шаг 1: Кто есть кто в цифровом мире
# ------------------------------
elif st.session_state.step == 1:
    st.markdown('<div class="main-header">Кто есть кто в цифровом мире?</div>', unsafe_allow_html=True)

    # Инфографика с кликабельными блоками (expander)
    st.markdown("### 📊 Инфографика")
    terms_info = [
        ("👤 Владелец информации", "Человек или организация, которая создала информацию или имеет законное право ей распоряжаться.", "Вы написали пост в соцсети — вы владелец этой информации."),
        ("📂 Обладатель информации", "Тот, кто владеет информацией на законных основаниях (может не быть её создателем).", "Школа хранит личные дела учеников — она обладатель этих данных."),
        ("🌐 Провайдер", "Компания, которая предоставляет доступ в интернет.", "Ростелеком, МТС, Билайн — провайдеры."),
        ("🖥️ Владелец сайта", "Тот, кто управляет сайтом и определяет его содержание.", "Администратор портала Госуслуг — владелец сайта."),
        ("🙋 Пользователь", "Любой человек, который пользуется интернетом.", "Вы и ваши будущие клиенты — пользователи.")
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

    st.markdown("### 🧩 Задание: соотнесите термин и определение")
    st.write("Выберите для каждого термина правильное определение из выпадающего списка.")

    # Перемешиваем определения для selectbox'ов
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

    # Выбор для каждого термина
    user_matches = {}
    for term in terms:
        user_matches[term] = st.selectbox(
            term,
            ["Выберите определение..."] + definitions_pool,
            key=f"match_{term}"
        )

    # Кнопка "Проверить"
    if st.button("✅ Проверить", key="check_step1"):
        st.session_state.step1_checked = True
        score = 0
        for term in terms:
            if user_matches[term] == correct_map[term]:
                score += 1
                st.success(f"{term}: ✅ Верно!")
            else:
                st.error(f"{term}: ❌ Неверно. Правильно: {correct_map[term]}")
        st.info(f"Вы набрали {score} из 5.")
        st.session_state.step1_score = score  # сохраним для итогового подсчёта (но не обязательно)

    # Кнопка "Далее" (активна после проверки)
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([8, 2])
    with col1:
        if st.button("⬅️ Назад"):
            st.session_state.step = 0
            st.rerun()
    with col2:
        if st.button("Далее ➡️", disabled=(not st.session_state.step1_checked)):
            advance_step()
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------
# Шаг 2: Личные данные
# ------------------------------
elif st.session_state.step == 2:
    st.markdown('<div class="main-header">Личные данные: что это и почему их нужно защищать?</div>', unsafe_allow_html=True)

    # Теоретический блок
    st.markdown("""
    <div class="theory-card">
      <h3 style="color:#47CAFF;">Что такое персональные данные?</h3>
      <p>Персональные данные (ПД) — это любая информация, которая прямо или косвенно относится к определённому или определяемому человеку (субъекту персональных данных).</p>
      <p><strong>Примеры:</strong> имя, дата рождения, адрес, телефон, email, паспортные данные, СНИЛС, фотографии, геолокация.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ❓ Вопрос 1")
    q1 = st.radio(
        "Что из перечисленного НЕ является персональными данными?",
        {
            "A": "Анонимный никнейм в игре",
            "B": "Номер телефона",
            "C": "Адрес электронной почты",
            "D": "Серия и номер паспорта"
        },
        key="step2_q1"
    )
    if st.session_state.step2_q1 is not None:
        if st.session_state.step2_q1 == "A":
            st.success("✅ Верно! Анонимный никнейм сам по себе не является ПД, так как по нему нельзя идентифицировать человека.")
        else:
            st.error("❌ Неверно. Номер телефона, email и паспортные данные — это персональные данные. Анонимный никнейм — нет, если он не связан с другой идентифицирующей информацией.")

    st.markdown("---")
    # Принципы обработки ПД
    st.markdown("""
    <div class="theory-card">
      <h3 style="color:#47CAFF;">Главный закон: № 152-ФЗ «О персональных данных»</h3>
      <p>Семь ключевых принципов обработки ПД:</p>
      <ol>
        <li>Законность и справедливость</li>
        <li>Ограничение конкретными целями</li>
        <li>Минимизация (собирайте только нужное)</li>
        <li>Достоверность и актуальность</li>
        <li>Ограничение срока хранения</li>
        <li>Безопасность</li>
        <li>Ответственность</li>
      </ol>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ❓ Вопрос 2")
    q2 = st.radio(
        "Какие данные вы имеете право собирать у клиента по закону № 152-ФЗ?",
        {
            "A": "Только те, которые необходимы для достижения конкретной цели",
            "B": "Любые данные, которые клиент согласился предоставить",
            "C": "Все данные, которые могут пригодиться в будущем",
            "D": "Только данные, запрошенные оператором сайта"
        },
        key="step2_q2"
    )
    if st.session_state.step2_q2 is not None:
        if st.session_state.step2_q2 == "A":
            st.success("✅ Верно! Принцип минимизации: только те данные, которые действительно нужны для цели.")
        else:
            st.error("❌ Неверно. Закон ограничивает сбор данных принципом минимизации и целевого использования.")

    st.markdown("---")
    # Права субъекта ПД
    st.markdown("""
    <div class="theory-card">
      <h3 style="color:#47CAFF;">Права субъекта персональных данных</h3>
      <ul>
        <li><strong>Право на информацию:</strong> вы должны сообщить человеку, какие данные собираете и зачем.</li>
        <li><strong>Право на доступ:</strong> человек может запросить все свои данные.</li>
        <li><strong>Право на уточнение:</strong> можно требовать исправить неверные данные.</li>
        <li><strong>Право на блокирование и удаление:</strong> можно потребовать удалить данные.</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ❓ Вопрос 3")
    q3 = st.radio(
        "Клиент просит удалить все его данные из вашей базы. Что вы обязаны сделать по закону?",
        {
            "A": "Отказать, так как данные уже обработаны",
            "B": "Удалить данные в течение 30 дней",
            "C": "Объяснить, что удаление невозможно, и предложить альтернативу",
            "D": "Удалить данные в срок, установленный законом"
        },
        key="step2_q3"
    )
    if st.session_state.step2_q3 is not None:
        if st.session_state.step2_q3 == "D":
            st.success("✅ Верно! Закон № 152-ФЗ даёт субъекту право на удаление данных. Срок обычно 30 дней.")
        else:
            st.error("❌ Неверно. Правильный ответ: удалить данные в установленный законом срок (обычно 30 дней).")

    st.markdown("---")
    # Ответственность
    st.markdown("""
    <div class="theory-card">
      <h3 style="color:#47CAFF;">Ответственность за утечку</h3>
      <p>За утечку персональных данных предусмотрена административная (штраф) и гражданско-правовая (компенсация ущерба) ответственность. В тяжёлых случаях — уголовная.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ❓ Вопрос 4")
    q4 = st.radio(
        "Какая ответственность грозит за утечку персональных данных клиентов, если она произошла по вашей вине?",
        {
            "A": "Только дисциплинарная (выговор)",
            "B": "Административная (штраф) и возможная гражданско-правовая",
            "C": "Только уголовная",
            "D": "Никакой, если утечка произошла случайно"
        },
        key="step2_q4"
    )
    if st.session_state.step2_q4 is not None:
        if st.session_state.step2_q4 == "B":
            st.success("✅ Верно! Основная ответственность — административная и гражданско-правовая.")
        else:
            st.error("❌ Неверно. Правильный ответ: административная и гражданско-правовая ответственность.")

    st.markdown("---")
    # Рефлексивное задание
    st.markdown("### ✍️ Рефлексивное задание")
    st.write("Представьте, что к вам пришёл клиент и просит удалить его данные из вашей базы. Какие права у него есть? Напишите краткий ответ (3–5 предложений).")
    reflection = st.text_area("Ваш ответ:", key="step2_reflection", height=120)

    # Самооценка
    st.slider("Оцените свой ответ (0–5 баллов)", 0, 5, key="step2_self_score")

    # Кнопки навигации
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([8, 2])
    with col1:
        if st.button("⬅️ Назад"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        # Проверяем, что все 4 вопроса отвечены и поле не пустое
        all_answered = all([
            st.session_state.step2_q1,
            st.session_state.step2_q2,
            st.session_state.step2_q3,
            st.session_state.step2_q4,
            len(st.session_state.step2_reflection.strip()) > 0
        ])
        if not all_answered:
            st.caption("⚠️ Ответьте на все вопросы и заполните поле выше.")
        if st.button("Далее ➡️", disabled=(not all_answered)):
            advance_step()
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------
# Шаг 3: Этика цифрового куратора
# ------------------------------
elif st.session_state.step == 3:
    st.markdown('<div class="main-header">Этика цифрового куратора: как принимать правильные решения?</div>', unsafe_allow_html=True)

    # Теоретический блок
    st.markdown("""
    <div class="theory-card">
      <h3 style="color:#47CAFF;">Что такое этика?</h3>
      <p>Этика — это не закон, а свод моральных правил, которые вы сами решаете соблюдать. Закон говорит «нельзя делать плохо», а этика говорит «поступай хорошо».</p>
      <p><strong>Главные принципы:</strong> уважение прав, не причинение вреда, честность, конфиденциальность, информированное согласие.</p>
    </div>
    """, unsafe_allow_html=True)

    # Кейс
    st.markdown("### 🧑‍💼 Кейс")
    st.markdown("""
    <div class="mission-card">
      <p>Вы работаете цифровым куратором. К вам пришла пожилая женщина для регистрации на Госуслугах. Она использует очень простой пароль «123456» и говорит, что это единственный пароль, который она запоминает. Вы знаете, что это небезопасно.</p>
      <p><strong>Как вы поступите?</strong></p>
    </div>
    """, unsafe_allow_html=True)

    case_options = {
        "A": "Промолчать, чтобы не смущать женщину, и продолжить регистрацию с её паролем",
        "B": "Объяснить риски и предложить помощь в создании надёжного пароля",
        "C": "Придумать пароль самостоятельно и записать его на бумажку"
    }
    case_choice = st.radio("Выберите вариант:", case_options.keys(), format_func=lambda x: f"{x}: {case_options[x]}", key="step3_q1")

    if st.session_state.step3_q1 is not None:
        if st.session_state.step3_q1 == "B":
            st.success("✅ Этичное и профессиональное решение. Вы заботитесь о безопасности клиента, но не навязываете своё мнение.")
        elif st.session_state.step3_q1 == "A":
            st.error("❌ Это неэтично. Вы знаете о риске, но не предупреждаете клиента, нарушая принцип «не навреди».")
        else:
            st.error("❌ Это неэтично и потенциально незаконно. Вы не получили информированного согласия и создали риск утечки данных.")

    # Рефлексивный вопрос
    st.markdown("### ❓ Какие законы и этические принципы вы учитывали?")
    principle_choice = st.radio(
        "Выберите наиболее полный ответ:",
        {
            "A": "Принцип конфиденциальности и право на частную жизнь",
            "B": "Принцип «не навреди» и обязанность обеспечивать безопасность данных",
            "C": "Принцип информированного согласия",
            "D": "Все перечисленные выше"
        },
        key="step3_q2"
    )
    if st.session_state.step3_q2 is not None:
        if st.session_state.step3_q2 == "D":
            st.success("✅ Верно! Вы учли все ключевые аспекты профессиональной этики.")
        else:
            st.warning("⚠️ Вы правы частично, но в этой ситуации важно учитывать все принципы одновременно.")

    # Навигация
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([8, 2])
    with col1:
        if st.button("⬅️ Назад"):
            st.session_state.step = 2
            st.rerun()
    with col2:
        both_answered = (st.session_state.step3_q1 is not None) and (st.session_state.step3_q2 is not None)
        if st.button("Далее ➡️", disabled=(not both_answered)):
            advance_step()
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------
# Шаг 4: Заключение
# ------------------------------
elif st.session_state.step == 4:
    st.markdown('<div class="main-header">Что мы узнали о законах и этике?</div>', unsafe_allow_html=True)

    # Резюмирующая инфографика
    st.markdown("### 📌 Резюме")
    st.markdown("""
    <div class="theory-card">
      <ul>
        <li><strong>📜 Закон № 149-ФЗ</strong> — регулирует цифровую среду, определяет субъектов.</li>
        <li><strong>🛡️ Закон № 152-ФЗ</strong> — защищает персональные данные.</li>
        <li><strong>⚖️ Этика</strong> — свод правил: информированное согласие, конфиденциальность, "не навреди".</li>
        <li><strong>🔒 Ваша ответственность</strong> — вы отвечаете за сохранность данных клиентов.</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

    # Чек-лист самопроверки
    st.markdown("### ✅ Чек-лист самопроверки")
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

    if st.button("📋 Проверить чек-лист", key="check_checklist"):
        st.session_state.step4_checked = True
        count = sum(checked)
        st.write(f"Вы отметили {count} из 10 пунктов.")
        if count == 10:
            st.success("🎉 Отлично! Вы готовы переходить к практическому разделу 1.3.")
        elif count >= 8:
            st.info("👍 Очень хорошо! Рекомендуем повторить темы, где вы не поставили галочку.")
        else:
            st.warning("📚 Рекомендуем вернуться к материалам, особенно к закону № 152-ФЗ.")

    # Финальное задание
    st.markdown("---")
    st.markdown("### 🔢 Финальное задание: мост к практике")
    st.write("Оцените безопасность вашего текущего пароля (от личного аккаунта) по шкале от 1 до 10 и обоснуйте оценку в 2–3 предложениях.")
    col1, col2 = st.columns([1, 3])
    with col1:
        score = st.slider("Оценка (1–10)", 1, 10, key="final_score_slider")
    with col2:
        justification = st.text_area("Обоснование:", key="final_text", height=80)

    # Навигация
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([8, 2])
    with col1:
        if st.button("⬅️ Назад"):
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("🏁 Завершить модуль"):
            # Сохраняем финальные ответы
            st.session_state.step4_checked = True
            advance_step()  # уйдет на step=5
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------
# Шаг 5: Итоговый экран (результаты)
# ------------------------------
elif st.session_state.step == 5:
    st.markdown('<div class="main-header">🏆 Результаты модуля</div>', unsafe_allow_html=True)

    # Подсчёт автоматических баллов
    auto_score = 0

    # Экран 0 (1 балл)
    if st.session_state.intro_q1 == "B":
        auto_score += 1

    # Экран 1 (сопоставление, до 5 баллов) – используем сохранённый step1_score, иначе пересчитываем
    correct_map = {
        "Владелец информации": "Человек или организация, создавшая информацию",
        "Обладатель информации": "Тот, кто владеет информацией на законных основаниях",
        "Провайдер": "Компания, предоставляющая доступ в интернет",
        "Владелец сайта": "Тот, кто управляет сайтом",
        "Пользователь": "Любой человек, пользующийся интернетом"
    }
    match_score = 0
    for term, correct_def in correct_map.items():
        user_ans = st.session_state.get(f"match_{term}", None)
        if user_ans == correct_def:
            match_score += 1
    auto_score += match_score

    # Экран 2 (4 вопроса по 1 баллу)
    if st.session_state.step2_q1 == "A": auto_score += 1
    if st.session_state.step2_q2 == "A": auto_score += 1
    if st.session_state.step2_q3 == "D": auto_score += 1
    if st.session_state.step2_q4 == "B": auto_score += 1

    # Экран 2 самооценка (0-5)
    self_ref_score = st.session_state.step2_self_score
    auto_score += self_ref_score

    # Экран 3 (2 вопроса)
    if st.session_state.step3_q1 == "B": auto_score += 1
    if st.session_state.step3_q2 == "D": auto_score += 1

    # Экран 4 чек-лист (количество отмеченных пунктов, максимум 10)
    checklist_count = sum([st.session_state.get(f"checklist_{i}", False) for i in range(1, 11)])
    auto_score += checklist_count

    # Финальное задание – самооценка пароля (слайдер от 1 до 10, но по ТЗ максимум 2 балла; преобразуем: оценка >=7 -> 2 балла, >=4 -> 1 балл, иначе 0)
    final_psw_score = st.session_state.final_score_slider
    if final_psw_score >= 7:
        final_bonus = 2
    elif final_psw_score >= 4:
        final_bonus = 1
    else:
        final_bonus = 0
    auto_score += final_bonus

    # Итого максимум 29
    max_possible = 29
    st.markdown(f'<div class="score-display">Вы набрали {auto_score} из {max_possible} баллов (автоматическая часть)</div>', unsafe_allow_html=True)

    # Интерпретация по шкале
    if auto_score >= 26:
        st.success("🎓 **Отлично!** Вы уверенно владеете правовыми основами и этикой цифрового куратора.")
    elif auto_score >= 20:
        st.info("👍 **Хорошо!** Есть небольшие пробелы, повторите соответствующие разделы.")
    elif auto_score >= 15:
        st.warning("📚 **Удовлетворительно.** Требуется повторить материал, особенно по персональным данным и этике.")
    else:
        st.error("🔄 **Требуется повторное изучение.** Вернитесь к модулю и уделите внимание ключевым темам.")

    st.markdown("---")
    st.markdown("### 🔗 Мост к разделу 1.3")
    st.markdown("""
    <div class="theory-card">
      <p>Теперь вы знаете правовые основы и этические принципы. В следующем разделе <strong>«Информационная безопасность»</strong> вы научитесь:</p>
      <ul>
        <li>Распознавать киберугрозы (фишинг, вирусы, утечки)</li>
        <li>Создавать надёжные пароли и настраивать двухфакторную аутентификацию</li>
        <li>Защищать данные на компьютере и в интернете</li>
        <li>Разрабатывать чек-лист безопасности для клиентов</li>
      </ul>
      <p><em>Подготовьтесь к практической работе: вам понадобятся компьютер, браузер и доступ в интернет.</em></p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Пройти модуль заново"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    with col2:
        st.write("✅ Модуль завершён. Успехов в разделе 1.3!")