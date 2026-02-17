import os
import traceback

vectorstore = None
rag_chain = None
loaded_files = []
MAX_FILES = 10

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


# ---------------- LLM ----------------
llm = OllamaLLM(
    model="mistral",
    temperature=0.2
)

# ---------------- EMBEDDINGS ----------------
# small fast local embedding model (VERY IMPORTANT)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ---------------- PROMPT ----------------
prompt = PromptTemplate.from_template("""
You are a helpful AI assistant that answers questions ONLY from the provided PDF context.

If the answer is not in the context, say:
"I could not find that information in the uploaded documents."

Context:
{context}

Question:
{question}

Answer clearly and concisely:
""")


# ---------------- PDF LOADER ----------------
def load_pdf(pdf_path):
    global vectorstore, rag_chain, loaded_files

    try:
        if pdf_path in loaded_files:
            return "File already uploaded."

        if len(loaded_files) >= MAX_FILES:
            return "Maximum 10 PDFs reached."

        print("Loading:", pdf_path)

        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        # remove empty pages
        documents = [doc for doc in documents if doc.page_content.strip() != ""]

        if len(documents) == 0:
            return "PDF contains no readable text (likely scanned)."

        # ---- SPLITTING ----
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=120
        )
        docs = splitter.split_documents(documents)

        # safety: avoid memory explosion
        if len(docs) > 4000:
            return "PDF too large. Try a smaller document."

        # ---- VECTOR STORE ----
        if vectorstore is None:
            vectorstore = FAISS.from_documents(docs, embeddings)
        else:
            vectorstore.add_documents(docs)

        loaded_files.append(pdf_path)

        # ---- RETRIEVER ----
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        return f"Loaded successfully ({len(loaded_files)}/{MAX_FILES})"

    except Exception as e:
        traceback.print_exc()
        return f"Failed to load: {str(e)}"


# ---------------- ASK ----------------
def ask_pdf(question: str):
    global rag_chain

    if rag_chain is None:
        return "Upload a PDF first."

    try:
        return rag_chain.invoke(question)
    except Exception as e:
        traceback.print_exc()
        return "Error while generating answer."