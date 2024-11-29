from llama_index.core.prompts import ChatPromptTemplate, PromptTemplate
from llama_index.core.llms import ChatMessage
from llama_index.core.prompts.default_prompts import DEFAULT_TEXT_TO_SQL_PROMPT

# Prompt for generating table summaries with emphasis on unique table names
TABLE_SUMMARY_PROMPT_STR = """\
Given the following table data, generate a JSON summary with the fields 'table_name' and 'table_summary'.

Requirements:
- The 'table_name' must be unique and descriptive, using underscores instead of spaces.
- Do NOT output a generic or previously used table name (e.g., 'table', 'my_table', or any from the list: {exclude_table_name_list}).
- Incorporate unique aspects of the table data into the 'table_name' to ensure uniqueness.
- The 'table_summary' should be a concise description of the table's content.

Table Data:
{table_str}

Summary:
"""

TABLE_SUMMARY_PROMPT = ChatPromptTemplate(
    message_templates=[ChatMessage.from_str(TABLE_SUMMARY_PROMPT_STR, role="user")]
)

# Text-to-SQL prompt
TEXT_TO_SQL_PROMPT = DEFAULT_TEXT_TO_SQL_PROMPT

# Response synthesis prompt
RESPONSE_SYNTHESIS_PROMPT_STR = (
    "Given an input question, synthesize a response from the query results.\n"
    "Query: {query_str}\n"
    "SQL: {sql_query}\n"
    "SQL Response: {context_str}\n"
    "Response:"
)

RESPONSE_SYNTHESIS_PROMPT = PromptTemplate(RESPONSE_SYNTHESIS_PROMPT_STR)