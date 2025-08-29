"""LangGraph single-node graph template.
Returns a predefined response. Replace logic and configuration as needed.
"""
import json
from dataclasses import dataclass
from typing import Any, Dict, TypedDict ,Annotated ,List

from langgraph.graph import StateGraph ,add_messages ,END , MessagesState
# from langgraph.runtime import Runtime

from langchain_core.messages import AIMessage, BaseMessage ,ToolMessage ,HumanMessage

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode,tools_condition

from langgraph.config import get_stream_writer

llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash',api_key="AIzaSyDK1CNcAhSrM4qy3UVIXLu7J7Qk2U51Rug")



from typing import Literal
# reactjs useStream sdk  recognine  only certain message type for  example ai,tool,human,system
# class WeatherMessage(BaseMessage):
#     type: Literal["weather"] = "weather"
#     city: str
#     temperature: float
#     condition: str
#     content:str

    # @property
    # def content(self) -> str:
    #     return f"Weather in {self.city}: {self.temperature}°C, {self.condition}"


from langchain_core.tools import tool


@tool
def weather_tool(city:str):
    """find the weather of given city"""

    weather={'city':f'{city}','temperature':25.4,'condition':'foggy'}
    return weather





from typing import Dict, Any

from langchain_core.messages import ToolMessage ,SystemMessage



tools=[weather_tool]
tool_map = {'weather_tool':weather_tool}

# tool_node = ToolNode(tools=tools)


def call_model(state:MessagesState ):
    print('call_agent')
    print("\n\n\n\n\n",state['messages'][-1],"\n\n\n\n\n")


    response = llm.bind_tools(tools=tools).invoke(state['messages'])

    return {'messages':[response]}







def tool_node(state:MessagesState):
    """custom toolnode handle tool calls from llm generated tool_call request"""
    tool_messages =[]

    for tool_call in state['messages'][-1].tool_calls:
            tool_name=tool_call['name']
            tool_args=tool_call['args']
            tool_id=tool_call['id']
            
            #execute tool
            tool = tool_map[tool_name]
            result = tool.invoke(tool_args)
            
            data = result
            content = f"weather in {data['city']} is {data['condition']}, and temperature is {data['temperature']}"

            print('content' , content)
            print('result' , result)
            #ToolMessage list
            tool_message = ToolMessage(content=content,tool_call_id=tool_id,name=tool_name,additional_kwargs=result)
            tool_messages.append(tool_message)
        
    return {'messages':tool_messages}


def tools_route(state: MessagesState) -> Literal['tools', END]:
    last_ai_message = state['messages'][-1]
    if hasattr(last_ai_message, "tool_calls") and last_ai_message.tool_calls:
        return "tools"
    return END





def weather_builder():

    graph_b=StateGraph(MessagesState)
    graph_b.add_node('call_model',call_model)
    graph_b.add_node('tools',tool_node)
    graph_b.add_edge("__start__", "call_model")
    graph_b.add_conditional_edges('call_model',tools_route)
    graph_b.add_edge('tools','call_model')

    return graph_b.compile()

