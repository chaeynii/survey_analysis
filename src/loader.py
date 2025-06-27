from src.config.common_imports import *

def load_definitions(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name='Sheet1', dtype=str).fillna('')
    return df.rename(columns={
        'enumerated_strict(TRUE인 경우, 값 목록 외의 값은 모두 "기타"로 분류함)':
            'enumerated_strict'
    })

def load_raw_and_rename(raw_path: str, def_df: pd.DataFrame) -> pd.DataFrame:
    raw = pd.read_excel(raw_path, dtype=str)
    rename_map = dict(zip(def_df['컬럼'], def_df['column_id']))
    return raw.rename(columns=rename_map)