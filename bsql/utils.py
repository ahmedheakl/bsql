import yaml


def load_config():
    """Load configuration file for the project."""
    with open("./config/config.yml", "r", encoding="utf8") as ymlfile:
        cfg = yaml.safe_load(ymlfile)
        return cfg


def get_variable_name(var):
    for name, value in globals().items():
        if value is var:
            return name
    return None


# def set_custom_prompt():
#     """
#     Prompt template for QA retrieval for each vectorstore
#     """
#     prompt = PromptTemplate(
#         template=qa_template1, input_variables=["context", "question"]
#     )
#     return prompt
