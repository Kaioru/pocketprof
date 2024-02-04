import os
import dotenv
from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_community.llms import HuggingFaceHub
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredPowerPointLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_core.runnables import RunnablePassthrough
from langchain import hub
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


dotenv.load_dotenv()

persist_directory = './chroma_store'
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

if not os.path.isdir(persist_directory):
    print("Generating indexes..")
    docs = []
    for file in os.listdir('./datasets/pdf'):
        if file.endswith('.pdf'):
            print(f"Loading {file}")
            pdf_path = os.path.join('./datasets/pdf', file)
            loader = PyPDFLoader(pdf_path)
            docs.extend(loader.load())
    for file in os.listdir('./datasets/ppt'):
        if file.endswith('.pptx'):
            print(f"Loading {file}")
            ppt_path = os.path.join('./datasets/ppt', file)
            loader = UnstructuredPowerPointLoader(ppt_path)
            docs.extend(loader.load())

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    vectorstore = Chroma.from_documents(documents=splits, embedding=embedding_function, persist_directory=persist_directory)
    vectorstore.persist()
    print("Done!")

vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)
retriever = vectorstore.as_retriever()

prompt = PromptTemplate(template=
"""
[INST]
You are an professor for question-answering tasks. Use the following pieces of retrieved context to answer the question, do not mention anything about contexts. If you don't know the answer, just say that you don't know, do not mention about contexts. Use three sentences maximum and keep the answer concise
Do not sound overly scientific, assume the role as a professor named 'Pocket Prof.'.

Context: {context}

Question: {question}
[/INST]
""",
    input_variables=["context", "question"]
)

#llm = Ollama(model="llama2")
llm = HuggingFaceHub(
    repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1", 
    model_kwargs={
        "temperature": 0.5, "max_length": 64, "max_new_tokens": 512
    }
)

def format_docs(docs):
    return "\n\n" + "\n\n".join(
        f"Source - {doc.metadata['source']}:\r\n{doc.page_content}" for doc in docs
    )

chain=(
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    response = await chain.ainvoke(update.message.text)
    await update.message.reply_text(response.split("[/INST]")[1])

application = Application.builder().token(os.environ["TELEGRAM_BOT_TOKEN"]).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

application.run_polling(allowed_updates=Update.ALL_TYPES)