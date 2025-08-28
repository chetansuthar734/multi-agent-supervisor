"""LangGraph single-node graph template.
Returns a predefined response. Replace logic and configuration as needed.
"""
import json
from dataclasses import dataclass
from typing import Any, Dict, TypedDict ,Annotated ,List

from langgraph.graph import StateGraph ,add_messages ,END
# from langgraph.runtime import Runtime

from langchain_core.messages import AIMessage, BaseMessage ,ToolMessage ,HumanMessage

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode,tools_condition
from langgraph.types import StreamWriter
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



class State(TypedDict):
   messages:Annotated[List[BaseMessage],add_messages]



from typing import Dict, Any

from langchain_core.messages import ToolMessage ,SystemMessage

#def tool_node(state: State):
#     return {
#         "messages": [
#             ToolMessage(
#                 content="Weather update",
#                 tool_call_id="weather_tool",
#                 additional_kwargs={
#                     "city": "raniwara",
#                     "temperature": 43.4,
#                     "condition": "foggy",
#                 }
#             ),

#             ToolMessage(
#                 content="Code snippet",
                # tool_call_id="code_tool",
                # name="code_tool",
#                 additional_kwargs={
#                     "code": "console.log('hello world');",
#                     "language": "javascript",
#                 }
#             )
#         ]
#     }


#def greet_node(state:State):
    # print(state['messages'])
    # return {'messages':[SystemMessage(content='your are helpful assistant with capability web search ,weather forecast')]}

# note : if you add themself AIMessage to  last of State then llm.invoke([Humanmessage(),AIMessage()]) ,llm think answer is generated so it not generate anything





tools=[weather_tool]
tool_map = {'weather_tool':weather_tool}





# tool_node = ToolNode(tools=tools)


def call_model(state: State ):
    print('call_agent')
    # print(state['messages'])
    response = llm.bind_tools(tools=tools).invoke(state['messages'])

    writer = get_stream_writer()  
    writer({"type": "progress","content": "Fetching weather..."})
    # writer({"type": "progress", "step": 2, "status": "Parsing results"})


    return {'messages':response}







def tool_node(state):
    """custom toolnode handle tool calls from llm generated tool_call request"""
    tool_messages =[]

    for tool_call in state['messages'][-1].tool_calls:
            tool_name=tool_call['name']
            tool_args=tool_call['args']
            tool_id=tool_call['id']
            
            #execute tool
            tool = tool_map[tool_name]
            result = tool.invoke(tool_args)
            data = json.dumps(result)

            #ToolMessage list
            tool_message = ToolMessage(content=data,tool_call_id=tool_id,name=tool_name,additional_kwargs=result)
            tool_messages.append(tool_message)
        
    return {'messages':tool_messages}


def tools_route(state: State) -> Literal['tools', END]:
    last_ai_message = state['messages'][-1]
    if hasattr(last_ai_message, "tool_calls") and last_ai_message.tool_calls:
        return "tools"
    return END





def weather_build():
    return (
        StateGraph(State)
        .add_node('call_model',call_model)
        .add_node('tools',tool_node)
        .add_edge("__start__", "call_model")
        .add_conditional_edges('call_model',tools_route)
        .add_edge('tools','call_model')
        ).compile(name="New Graph")

