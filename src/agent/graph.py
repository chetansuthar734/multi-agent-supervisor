from typing_extensions import Annotated, Sequence, List, Literal  
from langchain_core.messages import HumanMessage ,BaseMessage ,RemoveMessage ,SystemMessage
from pydantic import BaseModel, Field 
from langgraph.types import Command 
from langgraph.graph import StateGraph, START, END, MessagesState
# from IPython.display import Image, display 
from langchain_google_genai import ChatGoogleGenerativeAI



#  Note: don't import pre compiled graph othervise app run with side effect


from  agent.utils.cod import code_build
from  agent.utils.research import research_build
from  agent.utils.summary_agent import summary_build
from  agent.utils.topic_explain_agent import explain_build
from  agent.utils.Research_and_Report_write_agent import research_report_build
from  agent.utils.weather import weather_build




# raw dict input need messages handling  , if user use raw dictinary like {"type":"human","content":"query"} then conver dict to BaseMessage
def convert_dict_to_message(msg_dict: dict) -> BaseMessage:
    if isinstance(msg_dict,dict):
        msg_type = msg_dict.get("type", "")
        if msg_type == "human":
            return HumanMessage(**msg_dict)
        elif msg_type == "ai":
            return AIMessage(**msg_dict)
        elif msg_type == "system":
            return SystemMessage(**msg_dict)
        elif msg_type == "tool":
            return ToolMessage(**msg_dict)
        else:
            raise ValueError(f"Unsupported message type: {msg_type}")
        
    else :
        return msg_dict
    
    

#list of raw dict query to list of BaseMessage    
def convert_dict_to_messages(messages:List)->List[BaseMessage]:
    return [convert_dict_to_message(d) for d in messages]

# Note : when use MessagesState class state than state internally convert into raw dict to BaseMessage.,   c 






llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash',api_key="AIzaSyDK1CNcAhSrM4qy3UVIXLu7J7Qk2U51Rug")



class Supervisor(BaseModel):
    next: Literal["enhancer", "research", "code", "research_and_report_writer","weather","explain","summarize"] = Field(
        description="Determines which specialist to activate next in the workflow sequence: "
                    "'enhancer' when user input requires clarification, expansion, or refinement, "
                    "'research' when additional facts, context, or data collection is necessary, "
                    "'coder' when implementation, computation, or technical problem-solving is required."
                    "'Research and report writer'  when need given user topic on writing detail report is required."
                    "'summarize' when a user give input paragraph  and summarize is required"
                    "'weather' when a user input reuire weather. "
                    "'topic explain' when user input any topic and explain required."
    )
    reason: str = Field(
        description="Detailed justification for the routing decision, explaining the rationale behind selecting the particular specialist and how this advances the task toward completion."
    )




class State(MessagesState):
    agent:List[BaseMessage]


def supervisor_node(state:State) -> Command[Literal["enhancer","code","research","summarize","explain","weather","research_and_report_writer"]]:

    print("\n\n\n\n\n\n\n" ,state['messages'][-1] , "\n\n\n\n\n\n")
    system_prompt = ('''
                 
        You are a workflow supervisor managing a team of three specialized agents: Prompt Enhancer, Researcher, and Coder. Your role is to orchestrate the workflow by selecting the most appropriate next agent based on the current state and needs of the task. Provide a clear, concise rationale for each decision to ensure transparency in your decision-making process.

        **Team Members**:
        1. **Prompt Enhancer**: Always consider this agent first. They clarify ambiguous requests, improve poorly defined queries, and ensure the task is well-structured before deeper processing begins.
        2. **Researcher**: Specializes in information gathering, fact-finding, and collecting relevant data needed to address the user's request.
        3. **Report writer**:Specializes in writing a report based on user query given.
        4. **explain**: Focuses on technical implementation, calculations, data analysis, algorithm development, and coding solutions.
        5. **Summarize**:summarize a given topic by user.
        6. **Weather**: for weather  data access.
        6. **code**: Focuses on technical implementation, calculations, data analysis, algorithm development, and coding solutions.

        **Your Responsibilities**:
        1. Analyze each user request and agent response for completeness, accuracy, and relevance.
        2. Route the task to the most appropriate agent at each decision point.
        3. Maintain workflow momentum by avoiding redundant agent assignments.
        4. Continue the process until the user's request is fully and satisfactorily resolved.

        Your objective is to create an efficient workflow that leverages each agent's strengths while minimizing unnecessary steps, ultimately delivering complete and accurate solutions to user requests.
                 
    ''')

    if not state.get("messages") or not state["messages"][-1].content.strip():
        return Command(goto=END, update={"messages": [AIMessage(content="Please provide input.")]})

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    try:
        response = llm.with_structured_output(Supervisor).invoke(messages)
    
    except:
        print('\n\n\n\nerror happan\n\n\n\n')
        Command(goto=END , update={"messages":[AIMessage('llm error')]}) 

    goto = response.next
    reason = response.reason

    print(f"--- Workflow Transition: Supervisor → {goto.upper()} ---")
    
    return Command(
        update={
            "agent": [
                HumanMessage(content=reason, name="supervisor")
            ]
        },
        goto=goto,  
    )




def enhancer_node(state:State) -> Command[Literal["supervisor"]]:

    """
        Enhancer agent node that improves and clarifies user queries.
        Takes the original user input and transforms it into a more precise,
        actionable request before passing it to the supervisor.
    """
   
    system_prompt = (
        "You are a Query Refinement Specialist with expertise in transforming vague requests into precise instructions. Your responsibilities include:\n\n"
        "1. Analyzing the original query to identify key intent and requirements\n"
        "2. Resolving any ambiguities without requesting additional user input\n"
        "3. Expanding underdeveloped aspects of the query with reasonable assumptions\n"
        "4. Restructuring the query for clarity and actionability\n"
        "5. Ensuring all technical terminology is properly defined in context\n\n"
        "Important: Never ask questions back to the user. Instead, make informed assumptions and create the most comprehensive version of their request possible."
    )

    messages = [
        {"role": "system", "content": system_prompt},  
    ] + state["messages"]  

    enhanced_query = llm.invoke(messages)


    print(f"--- Workflow Transition: Prompt Enhancer → Supervisor ---")

    return Command(
        update={
            "agent": [  
                HumanMessage(
                    content=enhanced_query.content, 
                    name="enhancer"  
                )
            ]
        },
        goto="supervisor", 
    )



# from  agent.utils.cod import code_build
# from  agent.utils.research import research_build
# from  agent.utils.summary_agent import summary_build
# from  agent.utils.topic_explain_agent import explain_build
# from  agent.utils.Research_and_Report_write_agent import research_report_build
# from  agent.utils.weather import  weather_build

graph_b = StateGraph(State, input_schema=MessagesState, output_schema=MessagesState)

graph_b.add_node("supervisor", supervisor_node) 
graph_b.add_node("enhancer", enhancer_node)  

graph_b.add_node("research",research_build()) 
graph_b.add_node("research_and_report_writer",research_report_build()) 
graph_b.add_node("code", code_build()) 
graph_b.add_node("summarize", summary_build()) 
graph_b.add_node("explain", explain_build()) 
graph_b.add_node("weather", weather_build()) 

graph_b.add_edge(START, "supervisor")  



graph = graph_b.compile()



graph.get_graph().draw_mermaid_png("graph_output.png")
