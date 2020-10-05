"""
Execution of the {{ cookiecutter.ml_tool_name }}
"""
from src.{{ cookiecutter.ml_tool_name }} import {{ cookiecutter.ml_class_name }}

# Usage of Heuristic class
if __name__ == "__main__":
    analysis_tool = {{ cookiecutter.ml_class_name }}()  # instantiate
    analysis_tool.logger.info("Starting the ml tool {{ cookiecutter.ml_tool_name }}")
    analysis_tool.start()  # start infinite loop to listen to MQTT messages
