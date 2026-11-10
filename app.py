import streamlit as st
from gigachat import GigaChat

st.set_page_config(page_title="Спаси-сам", page_icon="logo.png", layout="centered")

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    @media (prefers-color-scheme: dark) {
        .stApp {
            background: linear-gradient(135deg, #0f172a 1e-09%, #1e293b 100%);
        }
    }

    h1 {
        background: linear-gradient(45deg, #ff4b4b, #ff8f00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        animation: fadeInDown 0.8s ease-out;
    }

    div.stButton > button {
        border-radius: 14px;
        border: none;
        background: white;
        color: #1e293b;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    div.stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 25px rgba(255, 75, 75, 0.25);
        background: #ff4b4b;
        color: white;
    }

    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.3);
    }
</style>
""", unsafe_allow_html=True)

situations = [
    {
        "icon": "🥴",
        "title": "Обморок",
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

with st.sidebar:
    try:
        st.image("logo.png", width=130)
    except Exception:
        pass

    st.header("Настройки")
    if st.button("Очистить переписку"):
        st.session_state.messages = []
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
            "1. Нажмите на **три полоски** (или три точки) в правом верхнем углу браузера.\n"
            "2. Выберите **«Дополнительно»** $\\rightarrow$ **«Установить сайт как приложение»**.\n"
            "3. Подтвердите установку — на рабочем столе появится программа «Спаси-сам» с нашей иконкой!"
        )

    with st.expander("📱 Ярлык на телефон"):
        st.write(
            "**На Android (Chrome / Яндекс):**\n"
            "Нажмите на три точки в углу браузера и выберите «Добавить на главный экран».\n\n"
            "**На iPhone (Safari):**\n"
            "Нажмите кнопку «Поделиться» внизу экрана и выберите «На экран Домой»."
        )

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
    if len(card["dont"]) > 
