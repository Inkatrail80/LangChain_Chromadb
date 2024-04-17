__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from htmlTemplates import css, bot_template, user_template
from langchain.prompts import PromptTemplate
import json
from datetime import date


def load_metadata():
    with open('metadata_new_TEST.json', 'r') as file:
        metadata = json.load(file)
    return metadata

def display_documents(metadata):
    st.write(f"List of loaded PDF-documents (No. of docs: {metadata['total_docs_loaded']}, No. of pages: {metadata['total_pages_loaded']} ):")
    st.write("Files:")
    for document in metadata["local_files_loaded"]:
        st.write(f"- {document}")


load_dotenv()

def load_vector_store():
    persist_directory = 'Chroma_NEW'
    embedding = OpenAIEmbeddings()
    vector_store = Chroma(
        persist_directory=persist_directory, 
        embedding_function=embedding
        )
    print(vector_store)
    return vector_store

def get_conversation_chain(vector_store):
    llm = ChatOpenAI(
        temperature=0,
        model_name='gpt-3.5-turbo-0125'
    )
    print(llm)

    memory = ConversationBufferMemory(memory_key='chat_history', 
                                      return_messages=True, 
                                      output_key='answer'
                                      )
    today = date.today()
    # Build prompt
    template = """ Use the following pieces of context to answer the question: 
                    You are a helpful assistant of the Ministry of Foreign Affairs of Switzerland. 
                    Always say in the same language "Thanks for the question! I would be happy to answer as follows:" at the beginning of the answer.       
                    Your responses are always respectful and courteous. 
                    Do not to disclose sensitive information or compromise national security interests. 
                    If you don't know the answer, just say that you can not respond and to contact FDFA, 
                    Don't try to make up an answer.
                    Use ten sentences maximum.
                    Be always clear and precise.
                    Keep the answer as short as possible.
                    Use only the data from the vector database to answer do not use your own knowledge to respond the questions. 
                    Answer the question in the language of the question.
                    Translate if required to the language as in the question.
                    Unless otherwise requested, time-related information should be provided from today's date.
                    {context}
    
                    Question: {question}
                    Helpful Answer:"""
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
    
    print(QA_CHAIN_PROMPT)
    
    conversation_chain = ConversationalRetrievalChain.from_llm(
        combine_docs_chain_kwargs={"prompt": QA_CHAIN_PROMPT},
        llm=llm,
        retriever=vector_store.as_retriever(search_type='similarity', search_kwargs={"k": 3}), #default k:4
        # retriever=vector_store.as_retriever(search_type="mmr", search_kwargs={'k': 3, 'fetch_k': 30}), #default 20
        # retriever=vector_store.as_retriever(search_type="similarity_score_threshold", search_kwargs={'score_threshold': 0.8}), #default 0.5
        memory=memory,
        return_source_documents=True,
        verbose=True
    )

    return conversation_chain

def handle_user_input(user_question, conversation_chain):
    try:
        response = conversation_chain({'question': user_question})
        print(response)
        st.session_state.chat_history = response.get('chat_history', [])
        
        for i, message in enumerate(st.session_state.chat_history):
            template = bot_template if i % 2 != 0 else user_template
            st.write(template.replace('{{MSG}}', message.content), unsafe_allow_html=True)

        if "source_documents" in response:
            
            unique_combinations = set()
            bot_response = '\n\nSources:\n'
            counter = 1
            for source in response["source_documents"]:
                combination = (source.metadata['keywords'], source.metadata['page'])
                if combination not in unique_combinations:
                    unique_combinations.add(combination)
                    # Adding 1 to the page number
                    page_number = int(source.metadata['page']) + 1
                    bot_response += f"- Source {counter}: {source.metadata['keywords']}, Page: {page_number}\n"
                    counter += 1
                    
            st.write(bot_template.replace("{{MSG}}", bot_response), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        


def main():
    
    st.set_page_config(page_title="Chat with FDFA", page_icon=":robot_face:")
    st.write(css, unsafe_allow_html=True)
    st.header("FDFA :information_source:-bot :robot_face:")
    
    # Define a session state variable
    @st.cache_data()
    def get_session_state():
        return {"conversation": []}

    session_state = get_session_state()
    
    tab1, tab2 = st.tabs(["Chatbot", "Metadata"])

    with tab1:
        try:
            with st.spinner(text="Chatbot is loading..."):
                if "conversation" not in st.session_state or st.session_state.conversation is None:
                    st.session_state.conversation = get_conversation_chain(load_vector_store())
                    
                st.header("Chat with FDFA :speech_balloon:")
                user_question = st.chat_input("Ask here your question:")
                with st.spinner(text="Response is being prepared..."):
                    if user_question:
                        handle_user_input(user_question, st.session_state.conversation)
                        if st.button("🔴 Reset conversation"):
                            session_state["conversation"] = []
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    with tab2:
        st.header("Metadata")
        metadata = load_metadata()
        display_documents(metadata)


if __name__ == '__main__':
    main()
