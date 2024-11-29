import os

# Set environment variables
os.environ["OPENAI_API_KEY"] = (
    "YOU_OPENAI_API_KEY"
)

# Paths and directories
TABLE_INDEX_DIR = "table_index_dir"
TABLEINFO_DIR = "WikiTableQuestions_TableInfo"
DATA_DIR = "./WikiTableQuestions/csv/200-csv"
DB_PATH = "wiki_table_questions.db"