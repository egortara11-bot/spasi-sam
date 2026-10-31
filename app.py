import streamlit as st
from gigachat import GigaChat

SITUATIONS = [
    {
        "icon": "🥴",
        "title": "Обморок",
        "keys": ["обморок", "сознан", "потерял", "отключил", "слабост"],
        "steps": [
            "Проверьте, реагирует ли человек: аккуратно потрясите за плечи и громко спросите: «Что с вами?»",
            "Если без сознания, запрокиньте ему голову и проверьте дыхание до 10 секунд.",
            "Срочно вызовите скорую: 103 или 112.",
            "Если дышит, поверните его на бок. Если не дышит — нужно делать реанимацию.",
            "Расстегните воротник, откройте окно для свежего воздуха.",
            "Ждите скорую помощь рядом с человеком.",
        ],
        "dont": ["Не давайте нюхать нашатырный спирт и не бейте по щекам."],
        "source": "Памятка МЧС России / Минздрав",
    },
    {
        "icon": "🫀",
        "title": "Сердечный приступ",
        "keys": ["сердц", "инфаркт", "груд", "давит"],
        "steps": [
            "Сразу звоните в скорую: 103 или 112!",
            "Помогите человеку сесть полусидя, согнув колени.",
            "Расстегните одежду, откройте окно.",
            "Если у него есть свои таблетки от врача, помогите достать.",
            "Следите за дыханием до приезда врачей.",
        ],
        "dont": ["Не разрешайте человеку ходить или вставать."],
        "source": "Рекомендации Минздрава РФ",
    },
    {
        "icon": "🩹",
        "title": "Сильное кровотечение",
        "keys": ["кров", "порез", "рана"],
        "steps": [
            "Вызовите скорую: 103 или 112.",
            "Сильно прижмите рану чистой салфеткой или рукой через ткань.",
            "Наложите тугую давящую повязку бинтом.",
            "Если кровь бьет струей из руки или ноги и повязка не спасает — наложите жгут выше раны.",
            "Обязательно запишите точное время наложения жгута!",
        ],
        "dont": ["Не трогайте открытую рану грязными руками."],
        "source": "Инструкция Минздрава по первой помощи",
    },
    {
        "icon": "🌡️",
        "title": "Ожог",
        "keys": ["ожог", "обжег", "кипят", "пламя"],
        "steps": [
            "Уберите причину ожога (выключите плиту, потушите ткань).",
            "Охлаждайте место ожога холодной проточной водой 15-20 минут.",
            "Накройте чистой салфеткой или бинтом без нажима.",
            "Если ожог сильный — звоните 103 или 112.",
        ],
        "dont": ["Не мажьте ожог маслом, кремом или спиртом!", "Не вскрывайте волдыри."],
        "source": "Памятка МЧС России",
    },
    {
        "icon": "🥶",
        "title": "Обморожение",
        "keys": ["мороз", "холод", "замерз", "обморож"],
        "steps": [
            "Заведите человека в теплое помещение.",
            "Снимите мокрую и холодную одежду.",
            "Укутайте замерзшие руки или ноги теплым пледом или одеялом.",
            "Дайте теплое сладкое питье (чай, компот).",
            "Вызовите скорую 103 или 112.",
        ],
        "dont": ["Не растирайте снегом!", "Не опускайте сразу в горячую воду."],
        "source": "Памятка МЧС России",
    },
]

def ask_ai(history):
    key = st.secrets.get("GIGACHAT_CREDENTIALS", "")
    if key == "":
        return "В настройках не указан ключ API."
    
    system_instruction = (
        "Ты помощник по первой помощи. Отвечай строго по правилам МЧС России и Минздрава. "
        "Пиши кратко и по делу: шаги действий, напоминание про 112/103 и запрещенные действия."
    )
    
    full_messages = [{"role": "system", "content": system_instruction}] + history
    
    try:
        giga = GigaChat(credentials=key, verify_ssl_certs=False)
        answer = giga.chat({"messages": full_messages})
        return answer.choices[0].message.content
    except Exception as e:
        return "Ошибка связи с сервисом: " + str(e)

def find_situation(text):
    text = text.lower().replace("ё", "е")
    words = text.split()
    for situation in SITUATIONS:
        if situation["title"].lower() in text:
            return situation
        for key in situation["keys"]:
            for word in words:
                if key in word:
                    return situation
    return None

st.set_page_config(page_title="Первая помощь", page_icon="🚑")

st.title("🚑 Первая помощь")
st.write("Справочник первой помощи при неотложных ситуациях.")
st.error("❗ **Первым делом всегда звоните в скорую помощь: 103 или 112!**")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Управление")
    if st.button("🔄 Очистить чат"):
        st.session_state.messages = []
        if "current_preset" in st.session_state:
            del st.session_state["current_preset"]
        st.rerun()

st.write("Частые случаи:")
cols = st.columns(len(SITUATIONS))
for i in range(len(SITUATIONS)):
    item = SITUATIONS[i]
    if cols[i].button(item["icon"] + " " + item["title"]):
        st.session_state.current_preset = item

if "current_preset" in st.session_state:
    res = st.session_state.current_preset
    st.success("Инструкция из базы:")
    st.subheader(res["icon"] + " " + res["title"])
    st.write("**Порядок действий:**")
    for step in res["steps"]:
        st.checkbox(step, key="btn_" + step)
    if len(res["dont"]) > 0:
        st.warning("**Чего делать нельзя:**\n" + "\n".join(["- " + d for d in res["dont"]]))
    st.caption("Источник: " + res["source"])

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Опишите ситуацию или задайте вопрос...")

if user_input:
    if "current_preset" in st.session_state:
        del st.session_state["current_preset"]
        
    match = None
    if len(st.session_state.messages) == 0:
        match = find_situation(user_input)
    
    if match:
        with st.chat_message("user"):
            st.write(user_input)
        with st.chat_message("assistant"):
            st.subheader(match["icon"] + " " + match["title"])
            st.write("**Порядок действий:**")
            for step in match["steps"]:
                st.checkbox(step, key="chat_" + step)
            if len(match["dont"]) > 0:
                st.warning("**Чего делать нельзя:**\n" + "\n".join(["- " + d for d in match["dont"]]))
            st.caption("Источник: " + match["source"])
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
            
        with st.chat_message("assistant"):
            with st.spinner("Думаю..."):
                reply = ask_ai(st.session_state.messages)
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

st.divider()
st.caption("Проект по информатике. Сайт носит информационный характер и не заменяет вызов врача.")
