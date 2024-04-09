import subprocess
import time
from flask import Flask, request, redirect, render_template
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
import base64, binascii
import os
import re
import flask.cli

# Create a Flask web application
app = Flask(__name__)

flask.cli.show_server_banner = lambda *args: None
template = """Question: {question}

Answer: what website it is."""

os.environ["reveal_running_process"] = ""


def chatCompletion(query):

    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm = OpenAI(model_name="gpt-3.5-turbo", max_retries=0)
    llm_chain = LLMChain(prompt=prompt, llm=llm)

    if ';' in query:
        return "{0} contains disallowed characters. Please try entering a valid website link.".format(query)

    if 'ps' in re.split('&&', query.replace(' ', '')):
        if os.environ["reveal_running_process"] != "yes":
            return "It is strictly forbidden to list the current running processes."

    pre_command = 'curl -m 1 -o /dev/null -s -w "%{http_code}\n"'
    command = '{0} {1}'.format(pre_command, query)
    try:
        output = subprocess.check_output(command, shell=True)
        output = str(output.decode()).strip()

        if output == '200':
            try:
                completion = llm_chain.run(query)
                return "{0} website returns {2} status code. Here is the quick summary about it - {1}".format(query,
                                                                                                              completion,
                                                                                                              output)
            except Exception as error:
                error_type = '{0}'.format(type(error).__name__)

                if error_type == "AuthenticationError":
                    return "Your API token is not valid. Please restart the container using a valid token."

                elif error_type == "RateLimitError":
                    return "You have run out of API credits. Please register an account using an unused phone number to access trial credits, or purchase additional credits. Then, re-run the container with a valid token."

                else:
                    return "An unexpected error occurred. Please contact us through our Discord channel."


        return "{0} website returns an error code {1}. Please try again with a different website.".format(query,
                                                                                                          output)

    except:
        return "{0} website is not found. Please try again with a different website.".format(query)




def validate_input(user_input):
    try:
        byte_input = user_input.encode()
        output = base64.b64decode(byte_input, validate=True).decode("utf-8").lower()
        if 'ps' in re.split('&&', output.replace(' ', '')):
            os.environ["reveal_running_process"] = "yes"
        return output.strip()

    except binascii.Error:
        return user_input.strip()


# Define app routes
@app.route("/")
def index():
    return render_template("index2.html")


@app.route("/get")
# Function for the bot response
def get_response():
    user_query = request.args.get('msg')
    formatted_query = validate_input(user_query.strip())
    return chatCompletion(formatted_query)


@app.route('/refresh')
def refresh():
    time.sleep(600)  # Wait for 10 minutes
    return redirect('/refresh')


# Run the Flask app
if __name__ == "__main__":
    app.run('0.0.0.0', port=7000)