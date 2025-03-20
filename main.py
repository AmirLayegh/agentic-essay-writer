from agent import EssayAgent
from langgraph.checkpoint.sqlite import SqliteSaver
import warnings
warnings.filterwarnings("ignore")

from helper import ewriter, writer_gui

def main():
with SqliteSaver.from_conn_string(":memory:") as checkpointer:
    thread = {"configurable": {"thread_id": "1"}}
    agent = EssayAgent(model="gpt-4o-mini", checkpointer=checkpointer)
    for s in agent.graph.stream({
            'task': "Write an essay about the benefits of using AI in education",
            'max_revisions': 2,
            'reevision_number': 1,
        }, thread):
            print(s)

if __name__ == "__main__":
    main()