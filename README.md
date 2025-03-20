# ✍️ Agentic AI Essay Writer Powered by LangGraph and Streamlit

An intelligent AI-powered essay writing assistant that helps you plan, research, and write well-structured essays with multiple revisions.
<p align="center">
  <img src="/sources/gui.png" alt="Essay Writer Workflow GUI">
</p>


## 🌟 Features

- 🤖 AI-powered essay planning and writing
- 🔍 Automated research gathering using Tavily API
- 📝 Multi-stage essay generation process:
  - 📝 Planning and outlining
  - 🔍 Research and information gathering
  - ✍️ Essay writing
  - 🔄 Revision and improvement
- 📊 Interactive Streamlit interface
- 💾 State persistence using SQLite
- 🔄 Multiple revision cycles for quality improvement

## 🔑 Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- OpenAI API key
- Tavily API key

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/AmirLayegh/agentic-essay-writer.git
cd essay-writer
```

2. Use uv sync command to create and activate a virtual environment:
```bash
uv sync
```


3. Set up environment variables by placing your API keys in a `.env` file in the root of the repository:
``` bash
OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
TAVILY_API_KEY="YOR_TAVILY_API_KEY"
```

## 💻 Usage 

1. Start the Streamlit application:
```bash
make run-st-app
```

2. Open your web browser and navigate to the provided URL (typically http://localhost:8501)

3. Enter your essay topic in the text area and click "Generate Essay"

4. Monitor the progress through the different tabs:
   - 📝 Planning: View the essay outline
   - 🔍 Research: See gathered information
   - ✍️ Writing: Read the current draft
   - 🔄 Revisions: Track improvements
   - 📊 Raw Data: Access detailed state information

5. Download your final essay using the download button

## 🏗️ Project Structure

- `st_app.py`: Main Streamlit application interface
- `agent.py`: Core essay writing agent implementation
- `schemas.py`: Data models and type definitions
- `prompts.py`: AI model prompts
- `main.py`: Command-line interface

## 🚀 How It Works (Powered by LangGraph)

<p align="center">
  <img src="/sources/graph.png" alt="Essay Writer Workflow Graph">
</p>


The AI Essay Writer uses a sophisticated graph-based workflow:

1. **📝 Planning**: Creates a detailed essay outline
2. **🔍 Research**: Gathers relevant information using Tavily API
3. **✍️ Writing**: Generates the initial essay draft
4. **🔄 Revision**: Performs multiple iterations of improvement
5. **🔄 Finalization**: Produces a polished essay

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments 🙏

- Deeplearning.ai Course on AI agents in LangGraph(https://learn.deeplearning.ai/courses/ai-agents-in-langgraph)
- OpenAI for providing the language models
- Tavily for the research API
- Streamlit for the web interface framework
- LangGraph for the workflow management
