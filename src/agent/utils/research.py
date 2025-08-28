from typing import TypedDict, Annotated, Optional ,Literal ,List
from langgraph.graph import add_messages, StateGraph, END ,MessagesState
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_core.messages import HumanMessage, AIMessageChunk, ToolMessage ,BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_tavily import TavilySearch
import os
os.environ['GOOGLE_API_KEY'] = "AIzaSyDK1CNcAhSrM4qy3UVIXLu7J7Qk2U51Rug"
os.environ['TAVILY_API_KEY']= "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"




class State(TypedDict):
    workspace:Annotated[list[BaseMessage], add_messages]
    final:BaseMessage



# search_tool = TavilySearchResults(
#     max_results=4,
# )

search_tool = TavilySearch(
    max_results=5,
    topic="general",
    # include_answer=False,
    # include_raw_content=False,
    include_images=True,
    # include_image_descriptions=False,
    # search_depth="basic",
    # time_range="day",
    # include_domains=None,
    # exclude_domains=None
)

# print(search_tool.invoke('pm modi last visit').keys())    #tavilySearch output dict 
# output is  dict_keys(['query', 'follow_up_questions', 'answer', 'images', 'results', 'response_time', 'request_id'])


# print(search_tool.invoke('pm modi last visit'))

# print(search_tool.invoke('pm modi last visit')['images'])
# print(search_tool.invoke('pm modi last visit')['results'][0].keys())
# output is dict_keys(['url', 'title', 'content', 'score', 'raw_content'])


# print(search_tool.invoke('pm modi last visit')['results'][0]['title'])
# print(search_tool.invoke('pm modi last visit')['results'])
# print(search_tool.invoke('pm modi last visit')['results'][0]['url'])

tools = [search_tool]
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash')
llm_with_tools = llm.bind_tools(tools=tools)

def entry(state:MessagesState)->State:
    return {'workspace':state.get('messages',[]),"final":""}

def final(state:State)->MessagesState:
    return {'messages':[state.get('final',"")]}


def model(state:State)->State:
    
    result = llm_with_tools.invoke(state["workspace"])
    return {
        "workspace": [result], "final":result
    }

def tools_router(state: State)->Literal['tool_node',"final"]:
    last_message = state["workspace"][-1]
    #checking tool_calls 
    if(hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0):
        return "tool_node"
    else: 
        return "final"

def tool_node(state)->Literal['model']:
    """Custom tool node that handles tool calls from the LLM."""
    # Get the tool calls from the last message
    tool_calls = state["workspace"][-1].tool_calls
    
    # Initialize list to store tool messages for return , so graph state update
    tool_messages = []
    
    # Process each tool call
    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        print(tool_name)
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]
        
        # Handle the search tool
        if tool_name == "tavily_search":
            # Execute the search tool with the provided arguments
            search_results = search_tool.invoke(tool_args)['results']
            images = search_tool.invoke(tool_args)['images'] #link of images
            print(len(search_results))
            # Create a ToolMessage for this result
            tool_message = ToolMessage(
                content=str(search_results),
                tool_call_id=tool_id,
                name=tool_name,
                additional_kwargs={'search_related_images':images} # use for display image 
            )
            
            tool_messages.append(tool_message)
    # print(tool_messages)
    # Add the tool messages to the state
    return {"workspace": tool_messages}



def research_build():
    graph_builder = StateGraph(State,input_schema=MessagesState,output_schema=MessagesState)

    graph_builder.add_node("entry", entry)
    graph_builder.add_node("final", final)
    graph_builder.add_node("model", model)
    graph_builder.add_edge("entry", "model")
    graph_builder.add_node("tool_node", tool_node)
    graph_builder.set_entry_point("entry")

    graph_builder.add_conditional_edges("model", tools_router)
    graph_builder.add_edge("tool_node", "model")
    graph_builder.add_edge("model","final")

    
    return graph_builder.compile()


# res  = graph.invoke({'messages':[HumanMessage(content='pm modi last visit')]})
# print(res['messages'])