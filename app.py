import streamlit as st
import os

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

from dotenv import load_dotenv
load_dotenv()

# 🔧 SAYFA AYARI
st.set_page_config(page_title="Doküman Chat", layout="wide")

# 🎨 SIDEBAR
with st.sidebar:
    st.title("⚙️ Ayarlar")
    st.write("Model: LLaMA 3")
    st.write("Chunk size: 1000")
    st.write("Chunk overlap: 200")

# 🧠 CHAT MEMORY
if "messages" not in st.session_state:
    st.session_state.messages = []

# 🏷️ BAŞLIK
st.markdown("## 📄 Dokümanların ile Sohbet Et")
st.caption("PDF, DOCX ve TXT dosyaları ile soru-cevap yapabilirsiniz")

uploaded_files = st.file_uploader("Dosya yükle", accept_multiple_files=True)

documents = []

# 📂 DOSYA YÜKLEME
if uploaded_files:
    for file in uploaded_files:
        file_path = f"temp_{file.name}"
        with open(file_path, "wb") as f:
            f.write(file.read())

        if file.name.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif file.name.endswith(".docx"):
            loader = Docx2txtLoader(file_path)
        else:
            loader = TextLoader(file_path)

        documents.extend(loader.load())

    # ✂️ CHUNKING
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = splitter.split_documents(documents)

    # ⚡ CACHE'LENMİŞ VECTOR DB
    @st.cache_resource
    def create_db(texts):
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        return Chroma.from_documents(texts, embeddings)

    db = create_db(texts)
    retriever = db.as_retriever()

    # 🤖 LLM
    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        temperature=0
    )

    st.success("✅ Dokümanlar hazır!")

    # 📥 INPUT + BUTTON
    col1, col2 = st.columns([5, 1])

    with col1:
        query = st.text_input("Soru sor:", key="input")

    with col2:
        send = st.button("Gönder")

    # 💬 SORU SORULDUĞUNDA
    if query and send:
        with st.spinner("🤖 AI düşünüyor..."):
            docs = retriever.invoke(query)

            context = "\n".join([doc.page_content for doc in docs])

            prompt = f"""
            Aşağıdaki dokümanlara göre soruyu cevapla:

            {context}

            Soru: {query}
            """

            answer = llm.invoke(prompt)

            # 💾 CHAT MEMORY
            st.session_state.messages.append(("user", query))
            st.session_state.messages.append(("ai", answer.content))

    # 💬 CHAT GÖRÜNÜMÜ
    if st.session_state.messages:
        st.subheader("💬 Sohbet")

        for role, msg in st.session_state.messages:
            if role == "user":
                st.markdown(f"🧑 **Sen:** {msg}")
            else:
                st.markdown(f"🤖 **AI:** {msg}")

    # 📄 KAYNAKLAR (GÜZEL GÖRÜNÜM)
    if query and send:
        st.subheader("📄 Kaynaklar")

        for i, doc in enumerate(docs):
            with st.expander(f"Kaynak {i+1}"):
                st.markdown(f"**Dosya:** {doc.metadata.get('source','')}")
                st.markdown(f"**Sayfa:** {doc.metadata.get('page','')}")
                st.write(doc.page_content[:300] + "...")

    # 🔥 ÖZETLEME
    if st.button("📌 Dokümanları Özetle"):
        with st.spinner("🧠 Özet hazırlanıyor..."):
            all_text = "\n".join([doc.page_content for doc in texts])

            summary_prompt = f"Bu dokümanları özetle:\n{all_text[:3000]}"
            summary = llm.invoke(summary_prompt)

            st.subheader("📌 Özet")
            st.write(summary.content)