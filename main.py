import asyncio
from constants import TABLE_INDEX_DIR, TABLEINFO_DIR, DATA_DIR, DB_PATH
from models import TableInfo
from prompts import (
    TABLE_SUMMARY_PROMPT,
    TEXT_TO_SQL_PROMPT,
    RESPONSE_SYNTHESIS_PROMPT,
)
from utils.data_utils import (
    check_and_create_folders,
    load_csv_files,
    get_tableinfo_with_index,
    save_table_info,
)
from utils.db_utils import create_database_if_not_exists
from utils.index_utils import index_all_tables
from workflows.text_to_sql import TextToSQLWorkflow
from llama_index.llms.openai import OpenAI
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
)
from llama_index.core import (
    SQLDatabase,
    VectorStoreIndex,
)
from llama_index.core.retrievers import SQLRetriever


async def main():
    # Step 1: Check and create necessary folders
    check_and_create_folders([TABLE_INDEX_DIR, TABLEINFO_DIR])

    # Step 2: Load CSV files
    dfs = load_csv_files(DATA_DIR)

    # Step 3: Load or create table information
    llm = OpenAI(model="gpt-4o-mini")
    table_names = set()
    table_infos = []

    for idx, df in enumerate(dfs):
        table_info = get_tableinfo_with_index(idx, TABLEINFO_DIR)
        if table_info:
            table_infos.append(table_info)
            table_names.add(table_info.table_name)
        else:
            attempt = 0
            max_attempts = 3  # Limit the number of attempts
            while attempt < max_attempts:
                df_str = df.head(10).to_csv()
                table_info = llm.structured_predict(
                    TableInfo,
                    TABLE_SUMMARY_PROMPT,
                    table_str=df_str,
                    exclude_table_name_list=str(list(table_names)),
                )
                table_name = table_info.table_name
                print(f"Processed table: {table_name}")
                if table_name not in table_names:
                    table_names.add(table_name)
                    break
                else:
                    print(
                        f"Table name '{table_name}' already exists. Attempting to generate a unique name."
                    )
                attempt += 1
            else:
                # If unable to get a unique name, append the index to ensure uniqueness
                table_info.table_name = f"{table_name}_{idx}"
                table_names.add(table_info.table_name)
                print(f"Assigned unique table name: {table_info.table_name}")
            save_table_info(idx, table_info, TABLEINFO_DIR)
            table_infos.append(table_info)

    # Step 4: Create database and tables if not exist
    engine, metadata_obj = create_database_if_not_exists(DB_PATH, dfs, table_infos)
    sql_database = SQLDatabase(engine)

    # Step 5: Create object index for table schemas
    table_node_mapping = SQLTableNodeMapping(sql_database)
    table_schema_objs = [
        SQLTableSchema(table_name=info.table_name, context_str=info.table_summary)
        for info in table_infos
    ]
    obj_index = ObjectIndex.from_objects(
        table_schema_objs, table_node_mapping, VectorStoreIndex
    )
    obj_retriever = obj_index.as_retriever(similarity_top_k=3)

    # Step 6: Create SQL retriever
    sql_retriever = SQLRetriever(sql_database)

    # Step 7: Index all tables
    vector_index_dict = index_all_tables(sql_database, TABLE_INDEX_DIR)

    # Step 8: Initialize the workflow
    llm = OpenAI(model="gpt-4o-mini")
    workflow = TextToSQLWorkflow(
        obj_retriever,
        TEXT_TO_SQL_PROMPT,
        sql_retriever,
        RESPONSE_SYNTHESIS_PROMPT,
        llm,
        vector_index_dict,
        sql_database,
        verbose=True,
    )

    # Step 9: Run the workflow
    query = "What was the year that The Notorious B.I.G was signed to Bad Boy?"
    response = await workflow.run(query=query)
    print(str(response))


if __name__ == "__main__":
    asyncio.run(main())