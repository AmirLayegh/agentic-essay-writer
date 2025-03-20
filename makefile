run-writer:
	uv run python -m main

run-streamlit:
	uv run streamlit run streamlit_app.py

run-sqlite:
	uv run python -m sqlite3 essay_writer.db

run-st-app:
	uv run streamlit run st_app.py