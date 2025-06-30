from src.config.common_imports import *

def get_open_ended_columns(def_df: pd.DataFrame, df: pd.DataFrame):
    # 주관식 컬럼
    text_cols = def_df.loc[
        def_df['응답유형'].str.contains('주관식', na=False),
        'column_id'
    ].tolist()
    text_cols = [c for c in text_cols if c in df.columns]

    # _etc 컬럼 (기타응답)
    valid_base = set(def_df['column_id'])
    etc_cols = [c for c in df.columns if c.endswith('_etc') and c[:-4] in valid_base]

    return text_cols, etc_cols

def summarize_open_ended(df: pd.DataFrame, def_df: pd.DataFrame) -> pd.DataFrame:

## 작성예정
    return df_text