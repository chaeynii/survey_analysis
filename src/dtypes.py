from src.config.common_imports import *

def convert_dtypes(df: pd.DataFrame, def_df: pd.DataFrame) -> None:
    for _, r in def_df.iterrows():
        col, dtype = r['column_id'], r['데이터유형']
        if col not in df.columns or not dtype:
            continue
        if dtype == 'datetime':
            df[col] = pd.to_datetime(df[col], errors='coerce')
        elif dtype in ('int','integer'):
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
        elif dtype == 'categorical':
            df[col] = df[col].astype('category')
        elif dtype == 'text':
            df[col] = df[col].astype(str)