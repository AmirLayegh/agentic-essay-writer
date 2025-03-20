import streamlit as st
from agent import EssayAgent
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import os
import json
import time
import warnings
warnings.filterwarnings("ignore")

# Set up page configuration
st.set_page_config(
    page_title="Agentic Essay Writer",
    page_icon="✍️",
    layout="wide"
)

st.title("✍️ Agentic Essay Writer")
st.markdown("""
This application helps you write well-researched essays using AI. Simply enter your essay topic,
and the AI will help you plan, research, and write your essay with multiple revisions.
""")

# Create a debug section at the top (for troubleshooting)
debug_expander = st.expander("Debug Information")
with debug_expander:
    debug_area = st.empty()

# Define the database path
db_path = 'checkpoints.db'

# Initialize session state
if 'agent_initialized' not in st.session_state:
    # Create a SQLite connection
    conn = sqlite3.connect(db_path, check_same_thread=False)
    # Initialize the SqliteSaver with the direct connection
    memory = SqliteSaver(conn)
    # Create the agent
    st.session_state.agent = EssayAgent(model="gpt-4o-mini", checkpointer=memory)
    # Initialize the thread
    st.session_state.thread = {"configurable": {"thread_id": "essay_thread_1"}}
    # Mark as initialized
    st.session_state.agent_initialized = True
    # Initialize collected states
    st.session_state.collected_states = []
    
# Create the input form
with st.form("essay_form"):
    essay_topic = st.text_area(
        "Enter your essay topic:",
        placeholder="Example: Write an essay about the benefits of using AI in education",
        height=100
    )
    submitted = st.form_submit_button("Generate Essay")

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Planning", "Research", "Writing", "Revisions", "Raw Data"])

# Extract state data from nested structure
def extract_state_data(states):
    # Initialize combined state with default values
    combined_state = {
        'plan': None,
        'content': [],
        'draft': None,
        'critique': None,
        'revision_number': 0
    }
    
    # Process each state update from all nodes
    for state in states:
        # Extract data from the 'planner' node
        if 'planner' in state and 'plan' in state['planner']:
            combined_state['plan'] = state['planner']['plan']
        
        # Extract data from the 'research_plan' or 'research_critique' nodes
        if 'research_plan' in state and 'content' in state['research_plan']:
            combined_state['content'] = state['research_plan']['content']
        elif 'research_critique' in state and 'content' in state['research_critique']:
            combined_state['content'] = state['research_critique']['content']
        
        # Extract data from the 'generate' node
        if 'generate' in state:
            if 'draft' in state['generate']:
                combined_state['draft'] = state['generate']['draft']
            if 'revision_number' in state['generate']:
                combined_state['revision_number'] = state['generate']['revision_number']
        
        # Extract data from the 'reflect' node
        if 'reflect' in state and 'critique' in state['reflect']:
            combined_state['critique'] = state['reflect']['critique']
    
    return combined_state

# Function to display content in tabs
def update_tabs(combined_state):
    # Update Plan tab
    with tab1:
        tab1.empty()
        if combined_state.get('plan'):
            tab1.subheader("Essay Plan")
            tab1.write(combined_state['plan'])
        else:
            tab1.info("Waiting for planning stage...")
    
    # Update Research tab
    with tab2:
        tab2.empty()
        if combined_state.get('content'):
            tab2.subheader("Research Results")
            for idx, content in enumerate(combined_state.get('content', []), 1):
                with tab2.expander(f"Research Source {idx}"):
                    st.write(content)
        else:
            tab2.info("Waiting for research stage...")
    
    # Update Writing tab
    with tab3:
        tab3.empty()
        if combined_state.get('draft'):
            tab3.subheader("Current Draft")
            tab3.write(combined_state['draft'])
        else:
            tab3.info("Waiting for writing stage...")
    
    # Update Revisions tab
    with tab4:
        tab4.empty()
        if combined_state.get('critique'):
            tab4.subheader(f"Revision {combined_state.get('revision_number', 0)}")
            tab4.write("**Critique:**")
            tab4.write(combined_state['critique'])
            if combined_state.get('draft'):
                tab4.write("**Updated Draft:**")
                tab4.write(combined_state['draft'])
        else:
            tab4.info("Waiting for revision stage...")
    
    # Update Raw Data tab
    with tab5:
        tab5.subheader("Current State")
        tab5.json(combined_state)
        
        tab5.subheader("All Raw State Updates")
        for i, state in enumerate(st.session_state.collected_states):
            with tab5.expander(f"State Update {i+1}"):
                tab5.json(state)

# If an essay is being generated, collect and process agent outputs
if submitted and essay_topic:
    # Clear any previously collected states
    st.session_state.collected_states = []
    
    # Run agent
    with st.spinner("Generating your essay..."):
        try:
            # Debug info
            debug_area.write("Starting agent...")
            
            # Process each state update from the agent
            for state in st.session_state.agent.graph.stream({
                'task': essay_topic,
                'max_revisions': 2,
                'revision_number': 1,
            }, st.session_state.thread):
                # Add to collected states
                st.session_state.collected_states.append(state)
                
                # Update debug info
                debug_area.write(f"Received state update:\n{json.dumps(state, indent=2)}")
                
                # Extract and display state data
                combined_state = extract_state_data(st.session_state.collected_states)
                update_tabs(combined_state)
                
                # Short sleep to let UI update
                time.sleep(0.5)
            
            # Final state update
            combined_state = extract_state_data(st.session_state.collected_states)
            update_tabs(combined_state)
            
            # Debug completion
            debug_area.write("Agent completed successfully!")
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            debug_area.write(f"Exception details: {str(e)}")
            import traceback
            debug_area.write(traceback.format_exc())
    
    # Add a download button for the final essay
    combined_state = extract_state_data(st.session_state.collected_states)
    if combined_state.get('draft'):
        st.download_button(
            label="Download Essay",
            data=combined_state['draft'],
            file_name="essay.txt",
            mime="text/plain"
        )
else:
    # Initialize tabs with waiting messages
    update_tabs({})

# Add some helpful information in the sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    This AI Essay Writer uses advanced language models to help you:
    
    1. Plan your essay structure
    2. Research relevant information
    3. Generate well-written content
    4. Revise and improve the essay
    
    The process is iterative and will make multiple revisions to ensure quality.
    """)
    
    st.header("Tips")
    st.markdown("""
    - Be specific in your essay topic
    - The AI will research and incorporate relevant information
    - Multiple revisions help improve the quality
    - You can download the final essay as a text file
    """)