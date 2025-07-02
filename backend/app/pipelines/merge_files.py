import pandas as pd
from typing import List
import os

def merge_excel_files(file_paths: List[str], output_path: str) -> str:
    """
    Merge multiple Excel files into one CSV and save to output_path.
    """
    try:
        dataframes = [pd.read_excel(path) for path in file_paths]
        merged_df = pd.concat(dataframes, ignore_index=True)
        merged_df.to_csv(output_path, index=False)
        return output_path
    except Exception as e:
        raise RuntimeError(f"Error merging files: {str(e)}")
