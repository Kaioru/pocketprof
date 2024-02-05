import os
import dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAI
from openai import OpenAI as OpenAIClient
from pydub import AudioSegment
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredPowerPointLoader
from langchain_community.document_loaders import PlaywrightURLLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_core.runnables import RunnablePassthrough
from langchain import hub
import telebot

dotenv.load_dotenv()

persist_directory = './chroma_store'
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

if not os.path.isdir(persist_directory):
    print("Generating indexes..")
    docs = []
    for file in os.listdir('./datasets'):
        path = os.path.join('./datasets', file)
        loaders = {
            '.pdf': PyPDFLoader,
            '.pptx': UnstructuredPowerPointLoader,
        }
        file_name, file_extension = os.path.splitext(path)

        loader = loaders.get(file_extension)

        if loader is not None:
            print(file_name)
            docs.extend(loader(path).load())

    sources_file = open('./datasets/sources/html.txt', 'r')
    sources = sources_file.readlines()
    loader = PlaywrightURLLoader(urls=sources)
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
You are an professor for question-answering tasks. Use the following pieces of retrieved context to answer the question, do not mention anything about contexts. If you don't know the answer, just say that you don't know, do not mention about contexts. Use three sentences maximum and keep the answer concise. Do not sound overly scientific, assume the role as a professor named Pocket Professor.

Context: {context}

Question: {question}
""",
    input_variables=["context", "question"]
)

llm = OpenAI()

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

openAIClient = OpenAIClient()
bot = telebot.TeleBot(os.environ["TELEGRAM_BOT_TOKEN"], parse_mode=None)

@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.reply_to(message, """
Hey, I'm Pocket Prof.! How can I help you?
              
You can ask me various questions regarding NTU, SCSE, and it's modules.
Here are some examples of things you can ask me:
    * Ask me about CE2005 labs
    * Ask me about the AU requirements for CS
    * Ask me about what you'll learn in CS
""")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    response = chain.invoke(message.text)
    bot.reply_to(message, response)

@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    file_info = bot.get_file(message.voice.file_id)
    file_path = f'./voices/{message.voice.file_id}.ogg'
    file_path_mp3 = f'./voices/{message.voice.file_id}.mp3'
    downloaded_file = bot.download_file(file_info.file_path)
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    AudioSegment.from_file(file_path).export(file_path_mp3, format="mp3")

    with open(file_path_mp3, 'rb') as mp3_file:
        transcript = openAIClient.audio.transcriptions.create(
            model="whisper-1", 
            file=mp3_file,
            response_format="text",
            language="en"
        )
        print(transcript)
        response = chain.invoke(transcript)
        bot.reply_to(message, response)

        tts_path = f'./voices/{message.voice.file_id}-response.mp3'
        tts = openAIClient.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=response,
        )
        tts.stream_to_file(tts_path)

        with open(tts_path, 'rb') as audio:
            bot.send_voice(message.chat.id, audio)
    
bot.infinity_polling()