# %% [markdown]
# code agent with human in loop

# %%
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from typing_extensions import Literal ,Annotated ,List ,TypedDict
from langgraph.graph import StateGraph,END,START,add_messages ,MessagesState
from langchain_core.messages import SystemMessage, HumanMessage,ToolMessage,BaseMessage ,AIMessage,AnyMessage
from langchain_core.tools import Tool
from langchain_experimental.utilities import PythonREPL
from uuid import uuid4

max_iters=2

@tool
def python_repl(code: str) -> str:
    """
    Use this function to execute Python code and get the results.
    """
    repl = PythonREPL()
    try:
        print("Running the Python REPL tool")
        print(code)
        result = repl.run(code)
        print("result")
        print(result)
    except BaseException as e:
        return f"Failed to execute. Error: {e!r}"
    
    return result


# %%
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash',api_key="AIzaSyDK1CNcAhSrM4qy3UVIXLu7J7Qk2U51Rug")
tools = [python_repl]
tools_by_name = {tool.name: tool for tool in tools}

llm_with_tools = llm.bind_tools(tools)



# %%
class State(TypedDict):
    """
    Represents the state of the Graph.
    """

    user_input: BaseMessage  # User’s task request
    workspace: List[BaseMessage]   # Chat history (questions, responses, tool outputs)
    new_input: str   # Flag to check for new user input
    code: List        # Stores the generated Python code
    iterations: int  # Tracks the number of execution attempts
    final_response: List # Stores the final response after execution

# code and new_input use for human in loop input  and code store





# %%

def tool_node(state: State):
    """Performs the tool call"""
    result = []
    workspace = state["workspace"]
    code =[]

    for tool_call in workspace[-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])

        code.append(ToolMessage(name = 'code',content=tool_call['args']['code'],additional_kwargs={'output':observation},tool_call_id=tool_call['id']))
        # print("code",tool_call['args']['code'])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))


    return {"workspace": workspace + result , "code":code}

# %%
def should_continue(state: State) -> Literal["tool_node", 'final']:
    """
    Decide if we should continue execution or stop.
    """
    workspace = state["workspace"]
    last_message = workspace[-1]
    iterations = state["iterations"]
    
    if iterations > max_iters:
        return "final"  # Stop execution if max iterations are reached
    # if last_message.tool_calls:
    #     return "tool_node"  # Continue execution if the LLM made a tool call
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tool_node"

    return "final"

# %%
def llm_call(state: State):
    """
    The LLM agent node. Generates code, calls tools, and analyzes results.
    """
    print("----- Calling LLM -----")
    workspace = state["workspace"]
    user_input = state["user_input"]
    iterations = state["iterations"]
    new_input = state["new_input"]

    if len(workspace) == 0:
        workspace += [
            SystemMessage(content="""You are a Python coding assistant with expertise in exploratory data analysis.
            Use the python_repl tool to execute the code. If an error occurs, resolve it and retry up to 3 times.
            Once execution succeeds, analyze the result and provide insights.
            Structure responses with a prefix, code block, result, and analysis."""
            )
        ]
    
    if new_input == "True": 
        workspace += [
            HumanMessage(content=f"The user wants to complete this task: {user_input}. Use the Python REPL tool to complete the task.")
        ]
        new_input = "False"
                
    code_solution = llm_with_tools.invoke(workspace)
    workspace += [(code_solution)]
    
    iterations += 1
    return {"workspace": workspace, "final_response": [code_solution], "iterations": iterations, "new_input": new_input}


def entry(state: MessagesState) -> State:
    messages = state["messages"]
    if not messages:
        raise ValueError("No input message provided.")

    return {
        'user_input': messages[-1],
        'workspace': [],
        'iterations': 0,
        'new_input': "True",
        'code': [],
        'final_response': []
    }


# def final(state:State)->MessagesState:
#     print(state)

#     return { 'messages':[* state['code'] ,*state['final_response']]} 

def final(state: State) -> MessagesState:
    return {
        'messages': state['code'] + state['final_response']
    }



# %%
def code_build():

    agent_builder = StateGraph(State,input_schema=MessagesState,output_schema=MessagesState)

# Add nodes
    agent_builder.add_node("entry", entry)
    agent_builder.add_node("llm_call", llm_call)
    agent_builder.add_node("tool_node", tool_node)
    agent_builder.add_node("final", final)

# Add edges
    agent_builder.add_edge(START, "entry")
    agent_builder.add_edge("entry", "llm_call")
    agent_builder.add_conditional_edges(
        "llm_call",
        should_continue,
        {
            "tool_node": "tool_node",
            "final": "final"
        }
    )
    agent_builder.add_edge("tool_node", "llm_call")
    return agent_builder.compile()

