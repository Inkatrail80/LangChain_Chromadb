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

load_dotenv()

def load_metadata(metadata_file):
    with open(metadata_file, 'r') as file:
        metadata = json.load(file)
    return metadata

def display_documents(metadata):
    st.write(f"List of loaded PDF-documents (No. of docs: {metadata['total_docs_loaded']}, No. of pages: {metadata['total_pages_loaded']} ):")
    st.write("Files:")
    for document in metadata["local_files_loaded"]:
        st.write(f"- {document}")

def load_vector_store(persist_directory):
    embedding = OpenAIEmbeddings()
    vector_store = Chroma(
        persist_directory=persist_directory, 
        embedding_function=embedding
        )
    return vector_store

def get_conversation_chain(vector_store):
    llm = ChatOpenAI(
        temperature=0.01,
        model_name='gpt-3.5-turbo-0125'
    )
    memory = ConversationBufferMemory(memory_key='chat_history', 
                                      return_messages=True, 
                                      output_key='answer'
                                      )
    # Build prompt
    template = f""" Use the following pieces of context to answer the question: 
                    You are a helpful assistant of the Ministry of Foreign Affairs of Switzerland. 
                    Always say in the same language "Thanks for the question! I would be happy to answer as follows:" at the beginning of the answer.       
                    Your responses are always respectful and courteous. 
                    Do not to disclose sensitive information or compromise national security interests. 
                    If you don't know the answer, just say that you can not respond and to contact Federal Departement of Foreign Affairs FDFA.
                    Be always clear and precise. Keep the answer as short as possible.                    
                    Use only the data from the vector database to answer and do not use your own knowledge to respond the questions. 
                    If necessary, translate the information into the language as in the question.
                    Unless otherwise requested, time-related questions relate to the current time period.
                    {{context}}
    
                    Question: {{question}}
                    Helpful Answer:"""
                    
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
    
    conversation_chain = ConversationalRetrievalChain.from_llm(
        combine_docs_chain_kwargs={"prompt": QA_CHAIN_PROMPT},
        llm=llm,
        retriever=vector_store.as_retriever(search_type='similarity', search_kwargs={"k": 5}),
        memory=memory,
        return_source_documents=True,
        verbose=True
    )

    return conversation_chain

def handle_user_input(user_question, conversation_chain):
    try:
        response = conversation_chain({'question': user_question})
        
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
                    page_number = int(source.metadata['page']) + 1
                    bot_response += f"- Source {counter}: {source.metadata['keywords']}, Page: {page_number}\n"
                    counter += 1
                    
            st.write(bot_template.replace("{{MSG}}", bot_response), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        

def main():
    st.set_page_config(page_title="Chat with FDFA", page_icon=":robot_face:")
    # Hide Menu
    st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        button[kind="header"] {visibility:hidden;}
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)
    #End hide menu
    
    
    st.write(css, unsafe_allow_html=True)
    st.header("FDFA :information_source:-bot :robot_face:")
    
    @st.cache_data()
    def get_session_state():
        return {"conversation": []}

    session_state = get_session_state()
    
    persist_directories = {
        "Chroma_SOR": "metadata_SOR.json",
        # Add more directories as needed
    }
    database_options = persist_directories.keys()
    selected_directory = st.sidebar.selectbox("Select topic", database_options ,placeholder="Choose an option")
    theme_selected_directory = selected_directory.split('_')[1]
    st.subheader(f"Ask your questions about the topic: {theme_selected_directory}")
    st.text(f"Related documents (open data) can be found in the metadata description")
    metadata_file = persist_directories[selected_directory]
    
    tab1, tab2 = st.tabs(["Chatbot", "Metadata"])

    with tab1:
        try:
            with st.spinner(text="Chatbot is loading..."):
                # if "conversation" not in session_state or session_state["conversation"] is None:
                #     session_state["conversation"] = get_conversation_chain(load_vector_store(selected_directory))
                if "conversation" not in session_state or session_state["conversation"] is None or \
                    session_state.get("selected_database") != selected_directory:  # Check if database changed
                    session_state["conversation"] = get_conversation_chain(load_vector_store(selected_directory))
                    session_state["selected_database"] = selected_directory  # Store the selected database
                user_question = st.chat_input("Ask here your question:")
                with st.spinner(text="Response is being prepared..."):
                    if user_question:
                        handle_user_input(user_question, session_state["conversation"])
                        if st.button("🔴 Reset conversation"):
                            session_state["conversation"] = None
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")


    with tab2:
        try:
            
            with st.spinner(text="Metadata is loading..."):
                    metadata = load_metadata(metadata_file)
                    display_documents(metadata)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")


if __name__ == '__main__':
    main()
