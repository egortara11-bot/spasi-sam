import streamlit as st
import streamlit.components.v1 as components
from gigachat import GigaChat

st.set_page_config(page_title="Спаси-сам", page_icon="logo.png", layout="wide")

situations = [
    {
        "icon": "🥴",
        "title": "Обморок",
        "pose": "legs_up",
        "steps": [
            "Проверьте реакцию: аккуратно потрясите за плечи и громко спросите: «Что случилось?»",
            "Если без сознания — запрокиньте голову назад и посчитайте дыхание до 10 секунд.",
            "Срочно звоните в скорую: 103 или 112.",
            "Если дышит — уложите на спину и приподнимите ноги выше уровня сердца (или поверните на бок).",
            "Расстегните воротник и пуговицы, откройте форточку или окно.",
            "Не оставляйте человека одного до приезда врачей.",
        ],
        "dont": ["Не давайте нюхать нашатырный спирт и не бейте по щекам!"],
        "source": "Памятка МЧС России",
    },
    {
        "icon": "🫀",
        "title": "Сердечный приступ",
        "pose": "half_sitting",
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
        "pose": "legs_up",
        "steps": [
            "Сразу вызовите скорую: 103 или 112.",
            "Уложите пострадавшего и приподнимите раненую конечность выше уровня сердца.",
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
        "pose": "sitting",
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
        "pose": "half_sitting",
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

def detect_pose_from_text(text):
    t = text.lower()
    if "открытый перелом" in t or "видно кость" in t:
        return "flat_back"
    if "[поза: ноги_вверх]" in t or "выше сердца" in t or "выше уровня сердца" in t or "приподнимите ног" in t or "поднять ног" in t or "сломал ногу" in t:
        return "legs_up"
    if "[поза: полусидя]" in t or "полусидя" in t or "полулежа" in t:
        return "half_sitting"
    if "[поза: на_боку]" in t or "на бок" in t or "боковое положение" in t:
        return "recovery_side"
    if "[поза: на_спине]" in t or "реанимац" in t or "непрямой массаж" in t or "неподвижн" in t or "на спину" in t:
        return "flat_back"
    if "[поза: сидя]" in t or "наклоните голову вперед" in t or "усадите" in t:
        return "sitting"
    return "standing"

def render_3d_mannequin(pose):
    html_code = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{ margin: 0; overflow: hidden; background: #0f172a; font-family: sans-serif; color: white; border-radius: 12px; }}
#label {{ position: absolute; top: 10px; left: 10px; right: 10px; background: rgba(30, 41, 59, 0.9); padding: 8px 12px; border-radius: 8px; font-size: 13px; font-weight: bold; border-left: 4px solid #38bdf8; pointer-events: none; }}
#btns {{ position: absolute; bottom: 30px; left: 8px; right: 8px; display: flex; flex-wrap: wrap; gap: 4px; justify-content: center; }}
.pbtn {{ background: #1e293b; color: #e2e8f0; border: 1px solid #475569; border-radius: 6px; padding: 4px 8px; font-size: 11px; cursor: pointer; }}
.pbtn:hover {{ background: #38bdf8; color: #0f172a; font-weight: bold; }}
#hint {{ position: absolute; bottom: 8px; width: 100%; text-align: center; font-size: 11px; color: #94a3b8; pointer-events: none; }}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
<div id="label">Положение 3D-модели:<br><span id="pose-title" style="color:#38bdf8">Загрузка...</span></div>
<div id="btns">
    <button class="pbtn" onclick="applyPose('standing')">🧍 Стоя</button>
    <button class="pbtn" onclick="applyPose('legs_up')">🦵 Ноги выше сердца</button>
    <button class="pbtn" onclick="applyPose('half_sitting')">🛋️ Полусидя</button>
    <button class="pbtn" onclick="applyPose('recovery_side')">🛌 На боку</button>
    <button class="pbtn" onclick="applyPose('flat_back')">🚑 На спине</button>
    <button class="pbtn" onclick="applyPose('sitting')">🪑 Сидя</button>
</div>
<div id="hint">🔄 Зажмите мышку (или палец), чтобы крутить 3D-модель</div>
<script>
const titles = {{
    "standing": "🧍 Ожидание (базовая стойка)",
    "legs_up": "🦵 На спине, ноги выше уровня сердца",
    "half_sitting": "🛋️ Полусидя с согнутыми коленями",
    "recovery_side": "🛌 Устойчивое боковое положение",
    "flat_back": "🚑 Ровно на спине (покой / СЛР)",
    "sitting": "🪑 Сидя (покой и осмотр)"
}};

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(2.4, 1.8, 2.5);

const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

scene.add(new THREE.AmbientLight(0xffffff, 0.7));
const dirLight = new THREE.DirectionalLight(0xffffff, 0.9);
dirLight.position.set(4, 8, 5);
scene.add(dirLight);
scene.add(new THREE.GridHelper(6, 12, 0x334155, 0x1e293b));

const matBody = new THREE.MeshStandardMaterial({{ color: 0x38bdf8, roughness: 0.35 }});
const matJoint = new THREE.MeshStandardMaterial({{ color: 0xf8fafc, roughness: 0.2 }});
const matHeart = new THREE.MeshStandardMaterial({{ color: 0xef4444, emissive: 0x7f1d1d }});
const matProp = new THREE.MeshStandardMaterial({{ color: 0x475569, roughness: 0.7 }});

const human = new THREE.Group();
scene.add(human);

const pelvis = new THREE.Group();
human.add(pelvis);
pelvis.add(new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.16, 0.22), matBody));

const spine = new THREE.Group();
spine.position.set(0, 0.08, 0);
pelvis.add(spine);

const torsoMesh = new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.52, 0.22), matBody);
torsoMesh.position.set(0, 0.26, 0);
spine.add(torsoMesh);

const heartMesh = new THREE.Mesh(new THREE.SphereGeometry(0.06, 16, 16), matHeart);
heartMesh.position.set(0.05, 0.35, 0.12);
spine.add(heartMesh);

const head = new THREE.Group();
head.position.set(0, 0.56, 0);
spine.add(head);
const headMesh = new THREE.Mesh(new THREE.SphereGeometry(0.15, 24, 24), matJoint);
headMesh.position.set(0, 0.14, 0);
head.add(headMesh);

function makeLimb(w, len, mat) {{
    const g = new THREE.Group();
    g.add(new THREE.Mesh(new THREE.SphereGeometry(w * 0.65, 12, 12), matJoint));
    const m = new THREE.Mesh(new THREE.CylinderGeometry(w * 0.5, w * 0.45, len, 12), mat);
    m.position.y = -len / 2;
    g.add(m);
    const end = new THREE.Group();
    end.position.y = -len;
    g.add(end);
    return {{ root: g, end: end }};
}}

const lUpperArm = makeLimb(0.09, 0.32, matBody);
lUpperArm.root.position.set(0.25, 0.48, 0);
spine.add(lUpperArm.root);
const lLowerArm = makeLimb(0.08, 0.30, matBody);
lUpperArm.end.add(lLowerArm.root);

const rUpperArm = makeLimb(0.09, 0.32, matBody);
rUpperArm.root.position.set(-0.25, 0.48, 0);
spine.add(rUpperArm.root);
const rLowerArm = makeLimb(0.08, 0.30, matBody);
rUpperArm.end.add(rLowerArm.root);

const lThigh = makeLimb(0.12, 0.44, matBody);
lThigh.root.position.set(0.12, -0.05, 0);
pelvis.add(lThigh.root);
const lCalf = makeLimb(0.10, 0.44, matBody);
lThigh.end.add(lCalf.root);

const rThigh = makeLimb(0.12, 0.44, matBody);
rThigh.root.position.set(-0.12, -0.05, 0);
pelvis.add(rThigh.root);
const rCalf = makeLimb(0.10, 0.44, matBody);
rThigh.end.add(rCalf.root);

const pillow = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.28, 0.42), matProp);
scene.add(pillow);

function resetAll() {{
    pelvis.position.set(0, 0.95, 0);
    pelvis.rotation.set(0, 0, 0);
    spine.rotation.set(0, 0, 0);
    head.rotation.set(0, 0, 0);
    lUpperArm.root.rotation.set(0, 0, 0);
    lLowerArm.root.rotation.set(0, 0, 0);
    rUpperArm.root.rotation.set(0, 0, 0);
    rLowerArm.root.rotation.set(0, 0, 0);
    lThigh.root.rotation.set(0, 0, 0);
    lCalf.root.rotation.set(0, 0, 0);
    rThigh.root.rotation.set(0, 0, 0);
    rCalf.root.rotation.set(0, 0, 0);
    pillow.visible = false;
    pillow.rotation.set(0, 0, 0);
    controls.target.set(0, 0.65, 0);
}}

function applyPose(p) {{
    resetAll();
    document.getElementById("pose-title").innerText = titles[p] || titles["standing"];

    if (p === "legs_up") {{
        pelvis.position.set(0, 0.14, 0);
        pelvis.rotation.x = -Math.PI / 2;
        lThigh.root.rotation.x = -0.65;
        lCalf.root.rotation.x = 0.65;
        rThigh.root.rotation.x = -0.65;
        rCalf.root.rotation.x = 0.65;
        lUpperArm.root.rotation.z = 0.2;
        rUpperArm.root.rotation.z = -0.2;
        pillow.visible = true;
        pillow.position.set(0, 0.14, 0.62);
        controls.target.set(0, 0.25, 0);
    }} else if (p === "half_sitting") {{
        pelvis.position.set(0, 0.14, 0);
        pelvis.rotation.x = -Math.PI / 2;
        spine.rotation.x = 0.8;
        head.rotation.x = 0.15;
        lThigh.root.rotation.x = -0.45;
        lCalf.root.rotation.x = 0.9;
        rThigh.root.rotation.x = -0.45;
        rCalf.root.rotation.x = 0.9;
        lUpperArm.root.rotation.x = -0.5;
        rUpperArm.root.rotation.x = -0.5;
        pillow.visible = true;
        pillow.position.set(0, 0.20, -0.32);
        pillow.rotation.x = 0.5;
        controls.target.set(0, 0.35, 0);
    }} else if (p === "recovery_side") {{
        pelvis.position.set(0, 0.16, 0);
        pelvis.rotation.x = -Math.PI / 2;
        pelvis.rotation.y = 1.35;
        lThigh.root.rotation.x = -0.7;
        lCalf.root.rotation.x = 1.0;
        lUpperArm.root.rotation.x = -0.7;
        lLowerArm.root.rotation.x = -0.8;
        controls.target.set(0, 0.2, 0);
    }} else if (p === "flat_back") {{
        pelvis.position.set(0, 0.14, 0);
        pelvis.rotation.x = -Math.PI / 2;
        lUpperArm.root.rotation.z = 0.2;
        rUpperArm.root.rotation.z = -0.2;
        controls.target.set(0, 0.2, 0);
    }} else if (p === "sitting") {{
        pelvis.position.set(0, 0.48, 0);
        lThigh.root.rotation.x = -Math.PI / 2;
        lCalf.root.rotation.x = Math.PI / 2;
        rThigh.root.rotation.x = -Math.PI / 2;
        rCalf.root.rotation.x = Math.PI / 2;
        spine.rotation.x = 0.1;
        lUpperArm.root.rotation.x = -0.4;
        lLowerArm.root.rotation.x = -0.6;
        rUpperArm.root.rotation.x = -0.4;
        rLowerArm.root.rotation.x = -0.6;
        pillow.visible = true;
        pillow.position.set(0, 0.20, 0);
        controls.target.set(0, 0.5, 0);
    }}
}}

applyPose("{pose}");

let t = 0;
function animate() {{
    requestAnimationFrame(animate);
    t += 0.05;
    const s = 1 + Math.sin(t * 2) * 0.12;
    heartMesh.scale.set(s, s, s);
    controls.update();
    renderer.render(scene, camera);
}}
animate();
</script>
</body>
</html>"""
    components.html(html_code, height=480)

def ask_ai(chat_history):
    api_key = st.secrets.get("GIGACHAT_CREDENTIALS", "")
    if api_key == "":
        return "Ошибка: не найден ключ GIGACHAT_CREDENTIALS в настройках секретов!"

    prompt = (
        "Ты умный помощник по первой медицинской помощи. Отвечай строго по правилам МЧС и Минздрава. "
        "Пиши понятно и коротко: список действий, в какое положение уложить пострадавшего, напоминание вызвать 112 или 103 и список того, что делать нельзя. "
        "В самом конце ответа обязательно добавь с новой строки одну метку позы для 3D-манекена строго из списка: "
        "[ПОЗА: НОГИ_ВВЕРХ], [ПОЗА: ПОЛУСИДЯ], [ПОЗА: НА_БОКУ], [ПОЗА: НА_СПИНЕ] или [ПОЗА: СИДЯ]."
    )
    all_messages = [{"role": "system", "content": prompt}] + chat_history

    try:
        bot = GigaChat(credentials=api_key, scope="GIGACHAT_API_PERS", verify_ssl_certs=False)
        models_info = bot.get_models()
        for m in models_info.data:
            try:
                model_name = m.id_
                chat_bot = GigaChat(credentials=api_key, model=model_name, scope="GIGACHAT_API_PERS", verify_ssl_certs=False)
                response = chat_bot.chat({"model": model_name, "messages": all_messages})
                return response.choices[0].message.content
            except Exception:
                continue
        return "Не удалось получить ответ от доступных моделей."
    except Exception as err:
        return "Не удалось связаться с нейросетью: " + str(err)

st.title("🚑 Спаси-сам: Помощник по первой помощи")
st.write("Школьный проект: электронная памятка при неотложных состояниях с 3D-ассистентом.")
st.error("⚠️ Внимание! Первым делом всегда звоните спасателям: 112 или 103!")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_pose" not in st.session_state:
    st.session_state.current_pose = "standing"

with st.sidebar:
    try:
        st.image("logo.png", width=130)
    except Exception:
        pass

    st.header("Настройки")
    if st.button("Очистить переписку"):
        st.session_state.messages = []
        st.session_state.current_pose = "standing"
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

user_query = st.chat_input("Напишите, что случилось (например: сломал ногу или упал в обморок)...")

if user_query:
    if "selected_preset" in st.session_state:
        del st.session_state["selected_preset"]
    st.session_state.messages.append({"role": "user", "content": user_query})
    answer = ask_ai(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.current_pose = detect_pose_from_text(user_query + " " + answer)
    st.rerun()

left_col, right_col = st.columns([3, 2])

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
            clean_text = msg["content"]
            for tag in ["[ПОЗА: НОГИ_ВВЕРХ]", "[ПОЗА: ПОЛУСИДЯ]", "[ПОЗА: НА_БОКУ]", "[ПОЗА: НА_СПИНЕ]", "[ПОЗА: СИДЯ]"]:
                clean_text = clean_text.replace(tag, "")
            st.write(clean_text.strip())

with right_col:
    st.subheader("🧍 3D-помощник положения тела")
    render_3d_mannequin(st.session_state.current_pose)

st.divider()
st.caption("Проект по информатике ученика 9 класса. Не является медицинской консультацией.")
