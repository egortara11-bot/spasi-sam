import streamlit as st
from gigachat import GigaChat

situations = [
    {
        "icon": "🥴",
        "title": "Обморок",
        "keys": ["обморок", "сознан", "потерял", "отключил", "слабост"],
        "steps": [
            "Проверьте реакцию: аккуратно потрясите за плечи и громко спросите: «Что случилось?»",
            "Если без сознания — запрокиньте голову назад и посчитайте дыхание до 10 секунд.",
            "Срочно звоните в скорую: 103 или 112.",
            "Если дышит — переверните на бок. Если не дышит — начинайте сердечно-легочную реанимацию.",
            "Расстегните воротник и пуговицы, откройте форточку или окно.",
            "Не оставляйте человека одного до приезда врачей.",
        ],
        "dont": ["Не давайте нюхать нашатырный спирт и не бейте по щекам!"],
        "source": "Памятка МЧС России",
    },
    {
        "icon": "🫀",
        "title": "Сердечный приступ",
        "keys": ["сердц", "инфаркт", "груд", "давит"],
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
        "keys": ["кров", "порез", "рана"],
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
        "keys": ["ожог", "обжег", "кипят", "пламя"],
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
        "keys": ["мороз", "холод", "замерз", "обморож"],
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

def ask_ai(chat_history):
    api_key = st.secrets.get("GIGACHAT_CREDENTIALS", "")
    if api_key == "":
        return "Ошибка: не найден ключ GIGACHAT_CREDENTIALS в настройках секретов!"

    prompt = (
        "Ты умный помощник по первой медицинской помощи. Отвечай строго по правилам МЧС и Минздрава. "
        "Пиши понятно и коротко: список действий, напоминание вызвать 112 или 103 и список того, что делать нельзя."
    )

    all_messages = [{"role": "system", "content": prompt}] + chat_history

    try:
        init_bot = GigaChat(
            credentials=api_key,
            scope="GIGACHAT_API_PERS",
            verify_ssl_certs=False
        )
        try:
            models_list = init_bot.get_models()
            model_name = models_list.data[0].id
        except Exception:
            model_name = "GigaChat"

        chat_bot = GigaChat(
            credentials=api_key,
            model=model_name,
            scope="GIGACHAT_API_PERS",
            verify_ssl_certs=False
        )

        response = chat_bot.chat({"messages": all_messages})
        return response.choices[0].message.content
    except Exception as err:
        return "Не удалось связаться с нейросетью: " + str(err)

def check_situation(user_text):
    clean_text = user_text.lower().replace("ё", "е")
    words = clean_text.split()
    
    for item in situations:
        if item["title"].lower() in clean_text:
            return item
        for k in item["keys"]:
            for w in words:
                if k in w:
                    return item
    return None

st.set_page_config(page_title="Первая помощь", page_icon="🚑")

st.title("🚑 Помощник по первой помощи")
st.write("Школьный проект: электронная памятка при неотложных состояниях.")
st.error("⚠️ Внимание! Первым делом всегда звоните спасателям: 112 или 103!")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Настройки")
    if st.button("Очистить переписку"):
        st.session_state.messages = []
        if "selected_preset" in st.session_state:
            del st.session_state["selected_preset"]
        st.rerun()

st.write("Быстрый выбор ситуации:")

button_cols = st.columns(len(situations))
for idx in range(len(situations)):
    sit = situations[idx]
    if button_cols[idx].button(sit["icon"] + " " + sit["title"]):
        st.session_state.selected_preset = sit

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

    found_item = None
    if len(st.session_state.messages) == 0:
        found_item = check_situation(user_query)

    if found_item:
        with st.chat_message("user"):
            st.write(user_query)
        with st.chat_message("assistant"):
            st.subheader(found_item["icon"] + " " + found_item["title"])
            st.write("**План действий:**")
            for action in found_item["steps"]:
                st.checkbox(action, key="query_" + action)
            if len(found_item["dont"]) > 0:
                warnings = ""
                for d in found_item["dont"]:
                    warnings += "- " + d + "\n"
                st.warning("**Чего делать нельзя:**\n" + warnings)
            st.caption("Источник информации: " + found_item["source"])
    else:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.write(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Спрашиваю у нейросети..."):
                answer = ask_ai(st.session_state.messages)
                st.write(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

st.divider()
st.caption("Проект по информатике ученика средней школы. Не является медицинской консультацией.")

