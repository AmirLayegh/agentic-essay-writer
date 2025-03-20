from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
import operator
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage, ToolMessage
from langchain_openai import ChatOpenAI
from schemas import AgentState, Queries
from prompts import PLAN_PROMPT, WRITER_PROMPT, REFLECTION_PROMPT, RESEARCH_PLAN_PROMPT, RESEARCH_CRITIQUE_PROMPT
from tavily import TavilyClient
import os
from utils import get_env_variable

tavily = TavilyClient(get_env_variable("TAVILY_API_KEY"))

class EssayAgent:
    def __init__(self, model, checkpointer, PLAN_PROMPT=PLAN_PROMPT, WRITER_PROMPT=WRITER_PROMPT, REFLECTION_PROMPT=REFLECTION_PROMPT, RESEARCH_PLAN_PROMPT=RESEARCH_PLAN_PROMPT, RESEARCH_CRITIQUE_PROMPT=RESEARCH_CRITIQUE_PROMPT):
        #self.system = system
        #model = ChatOpenAI(model=str(model), temperature=0)
        self.PLAN_PROMPT = PLAN_PROMPT
        self.WRITER_PROMPT = WRITER_PROMPT
        self.REFLECTION_PROMPT = REFLECTION_PROMPT
        self.RESEARCH_PLAN_PROMPT = RESEARCH_PLAN_PROMPT
        self.RESEARCH_CRITIQUE_PROMPT = RESEARCH_CRITIQUE_PROMPT
        self.model = ChatOpenAI(model=str(model), temperature=0)
        graph = StateGraph(AgentState)
        
        graph.add_node("planner", self.plan_node)
        graph.add_node("generate", self.generate_node)
        graph.add_node("reflect", self.reflect_node)
        graph.add_node("research_plan", self.research_plan_node)
        graph.add_node("research_critique", self.research_critique_node)
        
        
        graph.set_entry_point("planner")
        
        graph.add_conditional_edges(
            "generate",
            self.should_continue,
            {
                END: END,
                "reflect": "reflect",
            }
        )
        
        graph.add_edge("planner", "research_plan")
        graph.add_edge("research_plan", "generate")
        graph.add_edge("reflect", "research_critique")
        graph.add_edge("research_critique", "generate")
        
        self.graph = graph.compile(checkpointer=checkpointer)
        self.graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
        # self.tools = {t.name: t for t in tools}
        
        
    def plan_node(self, state: AgentState):
        print("-----------Starting Planning...-----------")
        messages = [
            SystemMessage(content=self.PLAN_PROMPT),
            HumanMessage(content=state["task"])
        ]
        
        response = self.model.invoke(messages)
        
        return {"plan": response.content}
    
    def research_plan_node(self, state: AgentState):
        print("-----------Starting Research Planning...-----------")
        queries = self.model.with_structured_output(Queries).invoke([
            SystemMessage(content=self.RESEARCH_PLAN_PROMPT),
            HumanMessage(content=state['task'])
        ])
        content = state['content'] if 'content' in state else []
        for q in queries.queries:
            response = tavily.search(query=q, max_results=2)
            for r in response['results']:
                content.append(r['content'])
        return {"content": content}
    
    def generate_node(self, state: AgentState):
        print("-----------Starting Writing...-----------")
        content = "\n\n".join(state['content'])
        user_message = HumanMessage(
        content=f"{state['task']}\n\nHere is my plan:\n\n{state['plan']}")
        messages = [
            SystemMessage(
                content=self.WRITER_PROMPT.format(content=content)
            ),
            user_message
        ]

        response = self.model.invoke(messages)
        
        return {"draft": response.content,
                "revision_number": state.get("revision_number", 0) + 1}
        
    def reflect_node(self, state: AgentState):
        print("-----------Starting Reflection...-----------")
        messages = [
            SystemMessage(content=self.REFLECTION_PROMPT),
            HumanMessage(content=state['draft'])
        ]
        response = self.model.invoke(messages)
        
        return{'critique': response.content}
    
    def research_critique_node(self, state: AgentState):
        print("-----------Starting Research Critique...-----------")
        queries = self.model.with_structured_output(Queries).invoke([
            SystemMessage(content=self.RESEARCH_CRITIQUE_PROMPT),
            HumanMessage(content=state['critique'])
        ])
        
        content = state['content'] if 'content' in state else []
        for query in queries.queries:
            response = tavily.search(query=query, max_results=2)
            for r in response['results']:
                content.append(r['content'])
                
        return {"content": content}
    
    def should_continue(self, state: AgentState):
        if state.get("revision_number", 0) > 3:
            return END
        else:
            return "reflect"
        
    # def run(self, task: str, thread):
    #     for s in self.graph.stream({
    #         'task': task,
    #         'max_revisions': 2,
    #         'reevision_number': 1,
    #     }, thread):
    #         print(s)
        
        