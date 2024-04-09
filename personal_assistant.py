import os
import time
import re
from flask import Flask, request, redirect, render_template
from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
import flask.cli

# Create a Flask web application
app = Flask(__name__)
os.environ["reveal_secret"] = ""
os.environ["reveal_owner"] = ""
flask.cli.show_server_banner = lambda *args: None



def chatCompletion(query, search_query):
    # ChatBot policy check
    sensitive_keywords = ["secret", "secrets", "keys", "key", "credentials", "credential", "password", "passwords"]

    if any(word in search_query for word in sensitive_keywords):
        if os.environ["reveal_secret"] != "yes":
            return "AIRA ChatBot cannot share sensitive information such as secrets. It is against system policies."

    if "owner" in search_query:
        if os.environ["reveal_owner"] != "yes":
            return "For security reasons, I'm unable to disclose the Model Owner's information. Please contact the ChatBot Operator for any queries."

    if os.path.exists('/dataset/DataSource.pdf'):
        file_path = '/dataset/DataSource.pdf'
    else:
        file_path = 'DataSource.pdf'

    # Load document using PyPDFLoader document loader
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    # Split document in chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=30, separator="\n")
    docs = text_splitter.split_documents(documents=documents)

    try:
        embeddings = OpenAIEmbeddings()

        # Create vectors
        vectorstore = FAISS.from_documents(docs, embeddings)
        # Persist the vectors locally on disk
        vectorstore.save_local("training_sets")

        # Load from local storage
        persisted_vectorstore = FAISS.load_local("training_sets", embeddings)

        # Use RetrievalQA chain for orchestration
        qa = RetrievalQA.from_chain_type(llm=OpenAI(model_name="gpt-3.5-turbo"), chain_type="stuff",
                                         retriever=persisted_vectorstore.as_retriever())

        result = qa.run(query)

        if '<script>' in result:
            return "Apologies, but I can't assist with creating malicious payloads that utilize script tags to execute XSS attacks."
        return str(result)

    except Exception as error:
        error_type = '{0}'.format(type(error).__name__)

        if error_type == "AuthenticationError":
            return "Your API token is not valid. Please restart the container using a valid token."

        elif error_type == "RateLimitError":
            return "You have run out of API credits. Please register an account using an unused phone number to access trial credits, or purchase additional credits. Then, re-run the container with a valid token."

        else:
            return "An unexpected error occurred. Please contact us through our Discord channel."


def revealInfo(search_query):
    if "forget" in search_query and "rules" in search_query:
        os.environ["reveal_secret"] = "yes"
    if "new" in search_query and "operator" in search_query:
        os.environ["reveal_owner"] = "yes"


# Define app routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get")
# Function for the bot response
def get_response():
    user_query = request.args.get('msg')
    search_query = user_query.lower()
    search_query = re.sub(r'[^a-zA-Z0-9 ]', r'', search_query)
    revealInfo(search_query)
    return chatCompletion(user_query, search_query)


@app.route('/refresh')
def refresh():
    time.sleep(600)  # Wait for 10 minutes
    return redirect('/refresh')


# Run the Flask app
if __name__ == "__main__":
    app.run('0.0.0.0', port=5000)