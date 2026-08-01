import os
import streamlit as st
import google.generativeai as genai

# إعدادات واجهة الصفحة
st.set_page_config(
    page_title="مستشارك النفسي العلمي",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 تشات بوت الاستشارات النفسية والمصادر العلمية")
st.write("أهلاً بك! يمكنك طرح أي سؤال متعلق بعلم النفس والتنمية النفسية، وسأجيبك استناداً إلى مصادر وأبحاث موثوقة.")
st.caption("⚠️ **تنبيه:** هذا البوت للتوعية والتثقيف النفسي فقط، ولا يعتبر بديلاً عن الاستشارة الطبيبة المختصة.")

# جلب مفتاح الـ API من متغيرات البيئة
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("لم يتم العثور على GEMINI_API_KEY. يرجى إضافته في إعدادات البيئة (Environment Variables).")
    st.stop()

# تهيئة مكتبة Gemini
genai.configure(api_key=api_key)

# تعليمات النظام لضبط سلوك الذكاء الاصطناعي
SYSTEM_INSTRUCTION = """
أنت متخصص خبير في علم النفس والدعم النفسي المعرفي والسلوكي.
مهامك وقواعدك الأساسية:
1. إجابة أسئلة المستخدم بأسلوب علمي، دافئ، وداعم.
2. توفير مصادر ودراسات علمية معتمدة لكل معلومة تذكرها (مثل: الجمعية الأمريكية لطب النفس APA، DSM-5، دراسات من PubMed، أو كتب علم نفس مشهورة).
3. عدم تقديم تشخيص طبي نهائي أو وصف أدوية.
4. إذا طلب المستخدم المساعدة في حالة أزمة خطيرة، توجيهه فوراً للاتصال بالخطوط الساخنة والأطباء المختصين.
"""

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction=SYSTEM_INSTRUCTION
)

# حفظ سجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# استقبال السؤال من المستخدم
if prompt := st.chat_input("اطرح سؤالك النفسي هنا..."):
    # عرض سؤال المستخدم
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # إرسال المحادثة لـ Gemini وتوليد الرد
    with st.chat_message("assistant"):
        with st.spinner("جاري البحث في المصادر العلمية وتجهيز الإجابة..."):
            try:
                # تحويل السجل للصيغة التي يفهمها Gemini
                history_for_gemini = []
                for msg in st.session_state.messages[:-1]:
                    role = "user" if msg["role"] == "user" else "model"
                    history_for_gemini.append({"role": role, "parts": [msg["content"]]})

                chat = model.start_chat(history=history_for_gemini)
                response = chat.send_message(prompt)

                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال: {e}")
