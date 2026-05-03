import streamlit as st
from groq import Groq
from pypdf import PdfReader

# 1. Groq Bağlantısı (API Anahtarını Streamlit Secrets'tan alacağız)
# Yerel test için: client = Groq(api_key="SENİN_API_ANAHTARIN")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Lucid AI", page_icon="✨", layout="wide")

def text_to_speech(text):
    js_code = f"<script>var msg = new SpeechSynthesisUtterance('{text.replace("'", "")}'); msg.lang = 'tr-TR'; window.speechSynthesis.speak(msg);</script>"
    st.components.v1.html(js_code, height=0)

with st.sidebar:
    st.title("✨ Lucid Ayarlar")
    # Groq'un hızlı modelleri: llama3-8b-8192 veya llama3-70b-8192
    selected_model = st.selectbox("Zeka Modeli", ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"], index=0)
    
    uploaded_file = st.file_uploader("Lucid'e bir PDF okutun", type="pdf")
    pdf_text = ""
    if uploaded_file:
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            pdf_text += page.extract_text()
        st.success("Lucid dökümanı analiz etti!")

    speak_out = st.checkbox("Lucid cevapları sesli okusun", value=False)

    if st.button("Sohbeti Sıfırla"):
        st.session_state.messages = []
        st.rerun()

st.title("✨ Lucid: Kişisel Asistanınız")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Lucid'e bir şeyler sorun..."):
    final_prompt = prompt
    if pdf_text:
        final_prompt = f"Senin adın Lucid. Dökümana göre cevap ver: {pdf_text}\n\nSoru: {prompt}"
    else:
        final_prompt = f"Senin adın Lucid. Kullanıcı sorusu: {prompt}"

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Groq API Çağrısı
        completion = client.chat.completions.create(
            model=selected_model,
            messages=[{"role": "user", "content": final_prompt}],
        )
        msg = completion.choices[0].message.content
        st.markdown(msg)
        
        if speak_out:
            text_to_speech(msg)
    
    st.session_state.messages.append({"role": "assistant", "content": msg})
