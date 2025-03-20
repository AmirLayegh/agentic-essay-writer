from dotenv import load_dotenv
import os

def get_env_variable(variable_name):
    load_dotenv(override=True)
    return os.getenv(variable_name)

def load_env_variables():
    load_dotenv(override=True)
