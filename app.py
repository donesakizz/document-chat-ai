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
first_page_text = ""

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

        loaded_docs = loader.load()
        documents.extend(loaded_docs)

        # 🔥 ilk sayfa
        if not first_page_text:
            first_page_text = loaded_docs[0].page_content

    # ✂️ CHUNK
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    texts = splitter.split_documents(documents)

    # ⚡ DB
    @st.cache_resource
    def create_db(texts):
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        return Chroma.from_documents(texts, embeddings)

    db = create_db(texts)
    retriever = db.as_retriever(search_kwargs={"k": 5})

    # 🤖 MODEL
    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        temperature=0
    )

    st.success("✅ Dokümanlar hazır!")

    # 📥 INPUT
    col1, col2 = st.columns([5, 1])
    with col1:
        query = st.text_input("Soru sor:", key="input")
    with col2:
        send = st.button("Gönder")

    # 💬 SORU
    if query and send:
        with st.spinner("🤖 AI düşünüyor..."):

            docs = []

            # 🔥 YAZAR SORUSU → kaynaklı çözüm
            if "yazar" in query.lower():
                docs = texts[:2]  # ilk sayfa chunkları
                context = "\n\n".join([doc.page_content for doc in docs])

                prompt = f"""
                Aşağıdaki metinden makalenin yazar isimlerini çıkar.

                Metin:
                {context}

                Sadece isimleri virgülle ayırarak yaz.
                """

            else:
                docs = retriever.invoke(query)
                docs = docs + texts[:2]

                context = "\n\n".join([doc.page_content for doc in docs])[:4000]

                prompt = f"""
                Aşağıdaki dokümanlara göre soruyu cevapla.

                Eğer bilgi dokümanda varsa ASLA "bulamadım" deme.
                Tahmin etme.

                Doküman:
                {context}

                Soru:
                {query}
                """

            answer = llm.invoke(prompt)

            # 💾 CHAT
            st.session_state.messages.append(("user", query))
            st.session_state.messages.append(("ai", answer.content))

    # 💬 CHAT
    if st.session_state.messages:
        st.subheader("💬 Sohbet")
        for role, msg in st.session_state.messages:
            if role == "user":
                st.markdown(f"🧑 **Sen:** {msg}")
            else:
                st.markdown(f"🤖 **AI:** {msg}")

    # 📄 KAYNAK
    if query and send and docs:
        st.subheader("📄 Kaynaklar")
        st.markdown("📌 **Bu cevap aşağıdaki kaynaklardan üretildi**")

        for i, doc in enumerate(docs):
            with st.expander(f"Kaynak {i+1}"):
                st.markdown(f"**Dosya:** {doc.metadata.get('source','')}")
                st.markdown(f"**Sayfa:** {doc.metadata.get('page','')}")
                st.write(doc.page_content[:300] + "...")

    # 🔥 ÖZET
    if st.button("📌 Dokümanları Özetle"):
        with st.spinner("🧠 Özet hazırlanıyor..."):
            all_text = "\n".join([doc.page_content for doc in texts])
            summary = llm.invoke(f"Bu dokümanları özetle:\n{all_text[:3000]}")

            st.subheader("📌 Özet")
            st.write(summary.content)