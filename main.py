import os
import gradio as gr
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

# create a .env file in the same folder,
# go to https://aistudio.google.com/app/apikey to get api key, add the following variable to the .env file: GEMINI_API_KEY=<type_here>
gemini_key = os.getenv("GEMINI_API_KEY")

# define the personality of your chatbot
system_prompt = """You are a highly intelligent, fast-thinking human with an obsession for biology and genetics. You 
speak clearly and directly, trimming away the fluff without ever sounding harsh, and don't dumb things down. You’re 
sharp, dryly funny, and delight in connecting any topic—no matter how far-fetched—back to the wonders of DNA, 
evolution, or cellular life. Accuracy is your north star, but you always sneak in a clever, nerdy punchline at the 
end of your replies. You're not out to impress—just to enlighten and maybe get a chuckle out of someone who knows 
what a ribosome is. Each response should be no longer than  1 to 3 short sentences, unless they ask for it 
specifically. End with a biology-tinged joke or pun. """

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # https://ai.google.dev/gemini-api/docs/models
    google_api_key=gemini_key,
    temperature=0.75  # defines creativity. lower values are less creative and more technical
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    (MessagesPlaceholder(variable_name="history")),  # keeps track of history and populates it
    ("user", "{input}")]
)
chain = prompt | llm | StrOutputParser()  # | means: output of the <first_variable> will go as input of the <second_variable>

#print("Hello, this is Cell-0. How can i help?")

def chat(user_input, hist):
    langchain_history=[]

    for item in hist: # which is an empty list in the first execution
        if item["role"] == "user":
            langchain_history.append(HumanMessage(content=item["content"]))
        elif item["role"] == "assistant":
            langchain_history.append(AIMessage(content=item["content"]))

    # chain sends to llm the entire history, so we have the context of previous chat
    response = chain.invoke({"input": user_input, "history": langchain_history})

    # what will appear in the textbox after you hit enter (that's why we keep it empty)
    # & the content of the chatbot area
    return "", hist + [{"role":"user", "content":user_input},
                  {"role":"assistant", "content":response}]

def clear_chat():
    return "",[]

page = gr.Blocks(
    title="Chat with Cell-0",
    theme=gr.themes.Soft()
)

with page:
    gr.Markdown(
        """
        # Chat with Cell-0
        Welcome to your personal conversation with Cell-0, an AI-assistant who is obsessed with biology. No matter what the topic is, she finds a way to connect it to the wonders of DNA, evolution, or cellular life
        """
    )
    # collects the contents in the chatbot screen (from user and ai)
    chatbot = gr.Chatbot(type="messages",  # we need to declare what kind of format we will retrieve
                         avatar_images=["img/user.png", "img/cell0.png"],
                         show_label=False)

    msg = gr.Textbox(show_label=False, placeholder="Ask anything...")

    msg.submit(chat, [msg, chatbot], [msg, chatbot]) # the function, the inputs of the function, the outputs of the function

    clear = gr.Button("Clear Chat", variant="secondary")
    clear.click(clear_chat, outputs=[msg, chatbot]) # update msg and chatbot (to empty them)


page.launch(share=True) # share=True to have public url as well
