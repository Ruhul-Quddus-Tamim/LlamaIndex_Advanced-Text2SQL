import os
import re
import pandas as pd
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    text,
    inspect,
)
from typing import List, Tuple
from models import TableInfo


def sanitize_column_name(col_name: str) -> str:
    return re.sub(r"\W+", "_", col_name)


def create_table_from_dataframe(
    df: pd.DataFrame, table_name: str, engine, metadata_obj
):
    sanitized_columns = {col: sanitize_column_name(col) for col in df.columns}
    df = df.rename(columns=sanitized_columns)

    columns = [
        Column(col, String) if dtype == "object" else Column(col, Integer)
        for col, dtype in zip(df.columns, df.dtypes)
    ]

    table = Table(table_name, metadata_obj, *columns)
    metadata_obj.create_all(engine)

    with engine.connect() as conn:
        for _, row in df.iterrows():
            insert_stmt = table.insert().values(**row.to_dict())
            conn.execute(insert_stmt)
        conn.commit()


def get_engine_and_metadata(db_path: str) -> Tuple[any, MetaData]:
    engine = create_engine(f"sqlite:///{db_path}")
    metadata_obj = MetaData()
    return engine, metadata_obj


def create_database_if_not_exists(
    db_path: str, dfs: List[pd.DataFrame], table_infos: List[TableInfo]
):
    engine, metadata_obj = get_engine_and_metadata(db_path)
    inspector = inspect(engine)  # Create an inspector instance

    for idx, df in enumerate(dfs):
        table_info = table_infos[idx]
        if not inspector.has_table(table_info.table_name):
            print(f"Creating table: {table_info.table_name}")
            create_table_from_dataframe(df, table_info.table_name, engine, metadata_obj)
        else:
            print(f"Table {table_info.table_name} already exists, skipping creation.")
    return engine, metadata_obj