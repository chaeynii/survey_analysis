from src.config.common_imports import *
from src.config.settings import EXCLUDE_COLUMNS

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

def summarize_etc(df: pd.DataFrame, def_df: pd.DataFrame) -> pd.DataFrame:
    results = []
    text_cols, etc_cols = get_open_ended_columns(def_df, df)

    for col in etc_cols:
        q_txt = def_df.loc[def_df['column_id']==col.replace('_etc',''), '컬럼'].values[0] # 기존 질문 텍스트 : "컬럼"
        ser = df[col].dropna().astype(str)
        total = len(ser)
        if total==0:
            continue

        for resp, cnt in ser.value_counts().items():
            results.append({
                'column_id': col,
                'question':   f"{q_txt} (기타)",
                'field':      'etc',
                'response':   resp,
                'count':      cnt,
                'total':      total,
                'pct':        cnt/total*100
            })
    return pd.DataFrame(results)


# def summarize_text(df: pd.DataFrame, def_df: pd.DataFrame, top_n: int=10) -> pd.DataFrame:
#     results = []
#     text_cols, etc_cols = get_open_ended_columns(def_df, df)

#     for col in text_cols:
#         q_txt = def_df.loc[def_df['column_id']==col, '컬럼'].values[0]
#         ser   = df[col].dropna().astype(str)
#         total = len(ser)
#         if total==0:
#             continue

#         # 1) 원문 상위 top_n
#         for resp, cnt in ser.value_counts().head(top_n).items():
#             results.append({
#                 'column_id': col,
#                 'question':   q_txt,
#                 'field':      'text_top',
#                 'response':   resp,
#                 'count':      cnt,
#                 'total':      total,
#                 'pct':        cnt/total*100
#             })

#         # 2) 키워드 빈도 (CountVectorizer 예시)
#         #    한글 분석은 별도 형태소분석기 적용 필요합니다
#         vec = CountVectorizer(stop_words='english')
#         X   = vec.fit_transform(ser)
#         words = vec.get_feature_names_out()
#         freqs = X.toarray().sum(axis=0)
#         for word, cnt in sorted(zip(words, freqs), key=lambda x: -x[1])[:top_n]:
#             results.append({
#                 'column_id': col,
#                 'question':   q_txt,
#                 'field':      'keyword',
#                 'response':   word,
#                 'count':      int(cnt),
#                 'total':      total,
#                 'pct':        cnt/total*100
#             })

#     return pd.DataFrame(results)

def summarize_text_simple(df: pd.DataFrame, def_df: pd.DataFrame) -> pd.DataFrame:
    """
    주관식 응답을 _etc처럼 단순 count & pct로 집계
    """
    results = []
    text_cols = def_df.loc[
        def_df['응답유형'].str.contains('주관식', na=False),
        'column_id'
    ].tolist()
    
    text_cols = [c for c in text_cols if c not in EXCLUDE_COLUMNS]

    for col in text_cols:
        if col not in df.columns:
            continue

        # 2) 실제 응답(빈값/NaN 제외)
        ser   = df[col].dropna().astype(str)
        total = len(ser)
        if total == 0:
            continue

        # 3) value_counts() → count + pct
        for resp, cnt in ser.value_counts().items():
            results.append({
                'column_id': col,
                'question':   def_df.loc[def_df['column_id']==col, '컬럼'].iat[0],
                'field':      'text_simple',
                'response':   resp,
                'count':      int(cnt),
                'total':      total,
                'pct':        cnt/total*100
            })
    return pd.DataFrame(results)

def summarize_open_ended(df: pd.DataFrame, def_df: pd.DataFrame) -> pd.DataFrame:
    df_etc  = summarize_etc(df, def_df)
    df_text = summarize_text_simple(df, def_df)
    return pd.concat([df_etc, df_text], ignore_index=True)