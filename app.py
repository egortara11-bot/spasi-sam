import streamlit as st
from gigachat import GigaChat

st.set_page_config(page_title="Спаси-сам", page_icon="logo.png", layout="wide")

situations = [
    {
        "icon": "🥴",
        "title": "Обморок",
        "pose": "ноги_вверх",
        "steps": [
            "Проверьте реакцию: аккуратно потрясите за плечи и громко спросите: «Что случилось?»",
            "Если без сознания — запрокиньте голову назад и посчитайте дыхание до 10 секунд.",
            "Срочно звоните в скорую: 103 или 112.",
            "Если дышит — уложите на спину и приподнимите ноги выше уровня сердца.",
            "Расстегните воротник и пуговицы, откройте форточку или окно.",
            "Не оставляйте человека одного до приезда врачей.",
        ],
        "dont": ["Не давайте нюхать нашатырный спирт и не бейте по щекам!"],
        "source": "Памятка МЧС России",
    },
    {
        "icon": "🫀",
        "title": "Сердечный приступ",
        "pose": "полусидя",
        "steps": [
            "Срочно наберите 103 или 112!",
            "Усадите человека полусидя, согнув ноги в коленях.",
            "Ослабьте галстук, ремень и воротник, проветрите комнату.",
            "Если у него с собой есть лекарство от врача — помогите его достать.",
            "Будьте рядом и следите, дышит ли он.",
        ],
        "dont": ["Не разрешайте вставать или ходить!"],
        "source": "Рекомендации Минздрава РФ",
    },
    {
        "icon": "🩹",
        "title": "Сильное кровотечение",
        "pose": "ноги_вверх",
        "steps": [
            "Сразу вызовите скорую: 103 или 112.",
            "Зажмите рану чистой тряпкой или салфеткой как можно сильнее.",
            "Туго замотайте бинтом поверх раны.",
            "Если кровь хлещет фонтаном из руки/ноги — наложите жгут выше места ранения.",
            "Напишите на бумажке или ручкой на коже точное время наложения жгута!",
        ],
        "dont": ["Не лезьте в рану грязными пальцами!"],
        "source": "Памятка первой помощи",
    },
    {
        "icon": "🌡️",
        "title": "Ожог",
        "pose": "сидя",
        "steps": [
            "Уберите источник опасности (выключите конфорку, сбейте огонь).",
            "Подержите обожженное место под холодной водой из-под крана минут 15-20.",
            "Накройте чистым бинтом или салфеткой, не прижимая сильно.",
            "При сильном ожоге вызывайте 103 или 112.",
        ],
        "dont": ["Не мажьте маслом, жиром, зеленкой или спиртом!", "Ни в коем случае не лопайте пузыри!"],
        "source": "Памятка МЧС России",
    },
    {
        "icon": "🥶",
        "title": "Обморожение",
        "pose": "сидя",
        "steps": [
            "Заведите пострадавшего в теплое помещение.",
            "Снимите всю промокшую и холодную одежду.",
            "Укутайте замерзшие части тела теплым пледом.",
            "Напоите горячим сладким чаем.",
            "Вызовите скорую по номеру 103 или 112.",
        ],
        "dont": ["Не растирайте снегом!", "Не суйте руки/ноги сразу в горячую воду!"],
        "source": "Памятка МЧС России",
    },
]

def get_pose(text):
    t = text.lower()
    if "выше сердца" in t or "приподнимите ног" in t or "поднять ног" in t or "сломал ногу" in t or "обморок" in t:
        return "ноги_вверх"
    if "полусидя" in t or "полулежа" in t or "сердц" in t:
        return "полусидя"
    if "на бок" in t or "боковое" in t:
        return "на_боку"
    if "реанимац" in t or "на спину" in t or "не дышит" in t:
        return "на_спине"
    return "сидя"

def ask_ai(chat_history):
    api_key = st.secrets.get("GIGACHAT_CREDENTIALS", "")
    if api_key == "":
        return "Ошибка: не найден ключ GIGACHAT_CREDENTIALS в настройках секретов!"

    prompt = (
        "Ты умный помощник по первой медицинской помощи. Отвечай строго по правилам МЧС и Минздрава. "
        "Пиши понятно и коротко: список действий, в какое положение уложить человека, напоминание вызвать 112 или 103 и что делать нельзя."
    )
    all_messages = [{"role": "system", "content": prompt}] + chat_history

    try:
        bot = GigaChat(
            credentials=api_key,
            scope="GIGACHAT_API_PERS",
            verify_ssl_certs=False
        )
        models_info = bot.get_models()
        for m in models_info.data:
            try:
                model_name = m.id_
                chat_bot = GigaChat(
                    credentials=api_key,
                    model=model_name,
                    scope="GIGACHAT_API_PERS",
                    verify_ssl_certs=False
                )
                response = chat_bot.chat({"model": model_name, "messages": all_messages})
                return response.choices[0].message.content
            except Exception:
                continue
        return "Не удалось получить ответ от доступных моделей."
    except Exception as err:
        return "Не удалось связаться с нейросетью: " + str(err)

st.title("🚑 Спаси-сам: Помощник по первой помощи")
st.write("Школьный проект: электронная памятка при неотложных состояниях.")
st.error("⚠️ Внимание! Первым делом всегда звоните спасателям: 112 или 103!")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_pose" not in st.session_state:
    st.session_state.current_pose = "ожидание"

with st.sidebar:
    try:
        st.image("logo.png", width=130)
    except Exception:
        pass

    st.header("Настройки")
    if st.button("Очистить переписку"):
        st.session_state.messages = []
        st.session_state.current_pose = "ожидание"
        if "selected_preset" in st.session_state:
            del st.session_state["selected_preset"]
        st.rerun()

    st.divider()
    st.subheader("Быстрый доступ")

    try:
        with open("spasi-sam.apk", "rb") as apk_file:
            st.download_button(
                label="📲 Скачать приложение (APK)",
                data=apk_file,
                file_name="Спаси-сам.apk",
                mime="application/vnd.android.package-archive"
            )
    except Exception:
        st.caption("Файл приложения spasi-sam.apk скоро появится.")

    with st.expander("💻 Установить приложение на ПК"):
        st.write(
            "1. Нажмите на **три полоски** в правом верхнем углу браузера.\n"
            "2. Выберите **«Дополнительно»** -> **«Добавить страницу на рабочий стол»**."
        )

    with st.expander("📱 Ярлык на телефон"):
        st.write(
            "**На Android:** меню браузера -> «Добавить на главный экран».\n\n"
            "**На iPhone:** кнопка «Поделиться» -> «На экран Домой»."
        )

left_col, right_col = st.columns([2, 1])

with left_col:
    st.write("Быстрый выбор ситуации:")
    button_cols = st.columns(len(situations))
    for idx in range(len(situations)):
        sit = situations[idx]
        if button_cols[idx].button(sit["icon"] + " " + sit["title"]):
            st.session_state.selected_preset = sit
            st.session_state.current_pose = sit["pose"]

    if "selected_preset" in st.session_state:
        card = st.session_state.selected_preset
        st.success("Найдена инструкция в базе:")
        st.subheader(card["icon"] + " " + card["title"])
        st.write("**Что нужно делать:**")
        for action in card["steps"]:
            st.checkbox(action, key="preset_" + action)
        if len(card["dont"]) > 0:
            bad_things = ""
            for d in card["dont"]:
                bad_things += "- " + d + "\n"
            st.warning("**Что делать категорически нельзя:**\n" + bad_things)
        st.caption("Источник информации: " + card["source"])

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

user_query = st.chat_input("Напишите, что случилось...")

if user_query:
    if "selected_preset" in st.session_state:
        del st.session_state["selected_preset"]

    st.session_state.messages.append({"role": "user", "content": user_query})
    answer = ask_ai(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.current_pose = get_pose(user_query + " " + answer)
    st.rerun()

with right_col:
    st.subheader("🧍 Положение пострадавшего")
    pose = st.session_state.current_pose

    if pose == "ожидание":
        st.info("Выберите ситуацию слева или напишите вопрос в чат — здесь появится схема, как правильно уложить человека.")
    elif pose == "ноги_вверх":
        st.success("**Поза: На спине, ноги выше уровня сердца**")
        st.code(
            "             ___ \n"
            "  _O________/   \\\n"
            " /        [Валик]\\\n"
            "===================",
            language="text"
        )
        st.write("🔹 Уложите человека на спину на ровную поверхность.")
        st.write("🔹 Подложите под ноги сумку, свернутую куртку или подушку (выше уровня сердца).")
        st.write("🔹 Это обеспечит приток крови к мозгу и уменьшит отек при травме.")
    elif pose == "полусидя":
        st.success("**Поза: Полусидя с упором спины**")
        st.code(
            "   O  \n"
            "  /|\\____/\\ \n"
            " /[Подушка]\\\n"
            "=============",
            language="text"
        )
        st.write("🔹 Усадите человека, подложив под спину и голову подушку или одежду.")
        st.write("🔹 Ноги слегка согните в коленях.")
        st.write("🔹 В такой позе сердцу и легким гораздо легче работать.")
    elif pose == "на_боку":
        st.success("**Поза: Устойчивое боковое положение**")
        st.code(
            "   _O_ \n"
            "  /   \\___/\\ \n"
            " =============",
            language="text"
        )
        st.write("🔹 Аккуратно поверните человека на бок.")
        st.write("🔹 Верхнюю ногу согните в колене для устойчивости, руку положите под щеку.")
        st.write("🔹 Защищает дыхательные пути, если человек без сознания.")
    elif pose == "на_спине":
        st.error("**Поза: Ровно на твердой поверхности**")
        st.code(
            "  _O___________ \n"
            " ================",
            language="text"
        )
        st.write("🔹 Уложите человека строго на спину на твердый пол.")
        st.write("🔹 Запрокиньте голову для проверки дыхания и подготовки к СЛР.")
    elif pose == "сидя":
        st.info("**Поза: Сидя в покое**")
        st.write("🔹 Усадите пострадавшего на стул или пол, обеспечьте полный покой.")
        st.write("🔹 Не позволяйте резко вставать.")

st.divider()
st.caption("Проект по информатике ученика 9 класса. Не является медицинской консультацией.")
