"""
Execution of the {{ cookiecutter.ml_tool_name }}
"""
from {{ cookiecutter.project_name_in_src }}.{{ cookiecutter.ml_tool_name }} import {{ cookiecutter.ml_class_name }}

# Usage of Heuristic class
if __name__ == "__main__":
    with {{ cookiecutter.ml_class_name }}() as {{ cookiecutter.ml_class_name| lower }}:
        {{cookiecutter.ml_class_name | lower}}.logger.info("Starting the ml tool {{ cookiecutter.ml_tool_name }}")
