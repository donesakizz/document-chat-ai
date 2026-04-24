📄 Document Chat AI

Bu proje, kullanıcıların yüklediği dokümanlar (PDF, DOCX, TXT) ile sohbet edebilmesini sağlayan bir yapay zeka uygulamasıdır.
Kullanıcılar dokümanlara soru sorabilir, özet çıkarabilir ve içerikten bilgi elde edebilir.

🚀 Özellikler
📂 PDF, DOCX ve TXT dosya yükleme
💬 Doküman üzerinden soru-cevap (RAG sistemi)
📌 Otomatik özetleme
📄 Kaynak (source) gösterme
👤 Yazar bilgisi çıkarımı
📚 Çoklu doküman desteği
🧠 Kullanılan Teknolojiler
Python
Streamlit
LangChain
ChromaDB (Vector Database)
HuggingFace Embeddings
Groq LLM (LLaMA 3)
⚙️ Kurulum
1. Repoyu klonla
git clone https://github.com/donesakizz/document-chat-ai.git
cd document-chat-ai
2. Gerekli paketleri yükle
pip install -r requirements.txt
3. API anahtarını ekle

Proje klasöründe .env dosyası oluştur ve içine yaz:

GROQ_API_KEY=your_api_key_here
4. Uygulamayı çalıştır
streamlit run app.py

🏗️ Nasıl Çalışır?
Kullanıcı doküman yükler
Doküman metne dönüştürülür
Metin küçük parçalara bölünür (chunking)
Bu parçalar embedding’e dönüştürülür
Embedding’ler vector database’e kaydedilir
Kullanıcı soru sorduğunda ilgili parçalar bulunur
LLM bu parçaları kullanarak cevap üretir
✨ Ekstra Özellikler
🔍 Cevaplara kaynak gösterme
🧠 Yazar bilgisi gibi özel veri çıkarımı
⚡ Hızlı ve kullanıcı dostu arayüz
🎯 Amaç

Bu projenin amacı, kullanıcıların kendi dokümanları üzerinde
hızlı, doğru ve kaynaklı bilgiye ulaşmasını sağlamaktır.
