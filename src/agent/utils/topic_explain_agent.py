
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, END,START ,MessagesState
from langchain_core.messages import SystemMessage, HumanMessage,AIMessage,ToolMessage

from langchain.prompts import ChatPromptTemplate

from typing import TypedDict, List,Annotated
from langchain_google_genai import ChatGoogleGenerativeAI

# model = ChatGoogleGenerativeAI(model='gemini-2.0-flash',api_key="AIzaSyDK1CNcAh***********k2U51Rug",disable_streaming=True)
stream_model = ChatGoogleGenerativeAI(model='gemini-1.5-flash',api_key="AIzaSyDK1CNcAhSrM4qy3UVIXLu7J7Qk2U51Rug")



from langgraph.config import get_stream_writer

import time

def topic_explain_node(state:MessagesState)->MessagesState:
    writer =get_stream_writer()
    message = state['messages'][-1].content
    writer('starting summarazing topic.......')
    # print(state['messages'][-1])
    # summary  = f"""this is  summamry on given by llm on  topic}"""
    context = state["messages"][-1].content
    # print(context)
    summary=''
    prompt = ChatPromptTemplate.from_messages([('system',"your are helpful assistant ,explain the topic  given  by  user , reposnse format is defination, and use-case  in bullet point , most important point "),("human","topic :{context}")]).format_messages(context=context)
    for chunk in stream_model.stream(prompt):
        summary+=chunk.content
        writer(summary)
    return {"messages": [AIMessage(content=summary)]}

# Setup the graph

def explain_build():

    builder = StateGraph(MessagesState)
    builder.add_node("topic_explain", topic_explain_node)

    builder.add_edge(START,"topic_explain")

    return builder.compile()
