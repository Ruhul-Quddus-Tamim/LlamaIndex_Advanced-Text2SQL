import os
from pathlib import Path
from typing import Dict, List
from llama_index.core import (
    SQLDatabase,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.schema import TextNode
from sqlalchemy import text
from llama_index.core.objects import SQLTableSchema


def index_all_tables(
    sql_database: SQLDatabase, table_index_dir: str = "table_index_dir"
) -> Dict[str, VectorStoreIndex]:
    """Index all tables."""
    if not Path(table_index_dir).exists():
        os.makedirs(table_index_dir)

    vector_index_dict = {}
    engine = sql_database.engine
    for table_name in sql_database.get_usable_table_names():
        table_index_path = f"{table_index_dir}/{table_name}"
        if not os.path.exists(table_index_path):
            print(f"Indexing rows in table: {table_name}")
            # get all rows from table
            with engine.connect() as conn:
                cursor = conn.execute(text(f'SELECT * FROM "{table_name}"'))
                result = cursor.fetchall()
                row_tups = [tuple(row) for row in result]

            # index each row, put into vector store index
            nodes = [TextNode(text=str(t)) for t in row_tups]

            # put into vector store index (use default embeddings)
            index = VectorStoreIndex(nodes)

            # save index
            index.set_index_id("vector_index")
            index.storage_context.persist(table_index_path)
        else:
            print(f"Index for table {table_name} already exists, skipping indexing.")
            # rebuild storage context
            storage_context = StorageContext.from_defaults(persist_dir=table_index_path)
            # load index
            index = load_index_from_storage(storage_context, index_id="vector_index")
        vector_index_dict[table_name] = index

    return vector_index_dict


def get_table_context_and_rows_str(
    query_str: str,
    table_schema_objs: List[SQLTableSchema],
    vector_index_dict: Dict[str, VectorStoreIndex],
    sql_database: SQLDatabase,
    verbose: bool = False,
):
    """Get table context string."""
    context_strs = []
    for table_schema_obj in table_schema_objs:
        # first append table info + additional context
        table_info = sql_database.get_single_table_info(table_schema_obj.table_name)
        if table_schema_obj.context_str:
            table_opt_context = " The table description is: "
            table_opt_context += table_schema_obj.context_str
            table_info += table_opt_context

        # also lookup vector index to return relevant table rows
        vector_retriever = vector_index_dict[table_schema_obj.table_name].as_retriever(
            similarity_top_k=2
        )
        relevant_nodes = vector_retriever.retrieve(query_str)
        if len(relevant_nodes) > 0:
            table_row_context = "\nHere are some relevant example rows (values in the same order as columns above):\n"
            for node in relevant_nodes:
                table_row_context += str(node.get_content()) + "\n"
            table_info += table_row_context

        if verbose:
            print(f"> Table Info: {table_info}")

        context_strs.append(table_info)
    return "\n\n".join(context_strs)