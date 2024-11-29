import os
import pandas as pd
from pathlib import Path
from typing import List, Optional
import json
from models import TableInfo


def check_and_create_folders(folders: List[str]):
    for folder in folders:
        if not Path(folder).exists():
            os.makedirs(folder)


def load_csv_files(data_dir: str) -> List[pd.DataFrame]:
    data_path = Path(data_dir)
    csv_files = sorted(data_path.glob("*.csv"))
    dfs = []
    for csv_file in csv_files:
        print(f"Processing file: {csv_file}")
        try:
            df = pd.read_csv(csv_file, on_bad_lines="skip")  # Skip bad lines
            dfs.append(df)
        except Exception as e:
            print(f"Error parsing {csv_file}: {str(e)}")
    return dfs


def get_tableinfo_with_index(idx: int, tableinfo_dir: str) -> Optional[TableInfo]:
    results_gen = Path(tableinfo_dir).glob(f"{idx}_*.json")
    results_list = list(results_gen)
    if len(results_list) == 0:
        return None
    elif len(results_list) == 1:
        path = results_list[0]
        return TableInfo.parse_file(path)
    else:
        raise ValueError(f"More than one file matching index: {list(results_gen)}")


def save_table_info(idx: int, table_info: TableInfo, tableinfo_dir: str):
    out_file = f"{tableinfo_dir}/{idx}_{table_info.table_name}.json"
    with open(out_file, "w") as f:
        json.dump(table_info.dict(), f)