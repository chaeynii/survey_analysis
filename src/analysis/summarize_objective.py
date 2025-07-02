from config.common_imports import *

def _get_opts(raw_list: str):
    return next(csv.reader([raw_list], delimiter=',', quotechar='"', skipinitialspace=True))

def summarize_single(df: pd.DataFrame, def_df: pd.DataFrame) -> pd.DataFrame:
    results = []
    for _, r in def_df.iterrows():
        col, q_text, resp_type = r['column_id'], r['컬럼'], r['응답유형']
        if '단일' not in resp_type:
            continue
        
        opts = _get_opts(r['값 목록'] or '')
        ser   = df[col].dropna().astype(str) # 실제 응답 시리즈
        total = len(ser)
        cnts = ser.value_counts().to_dict()
        
        for opt in opts:
            cnt = cnts.get(opt, 0)
            pct = (cnt / total * 100) if total > 0 else 0.0
            results.append({
                'column_id': col,
                'question':   q_text,
                'resp_type':  resp_type,
                'option':     opt,
                'count':      int(cnt),
                'total':      total,
                'pct':        pct
            })
    return pd.DataFrame(results)

def summarize_multi(df: pd.DataFrame, def_df: pd.DataFrame) -> pd.DataFrame:
    results = []
    for _, r in def_df.iterrows():
        col, q_text, resp_type = r['column_id'], r['컬럼'], r['응답유형']
        if '복수' not in resp_type:
            continue

        opts = _get_opts(r['값 목록'] or '')
        ser = df[col].apply(lambda x: x if isinstance(x, list) else [])
        total = int(ser.map(bool).sum()) # 1개 이상 선택한 응답자 수
        exploded = ser.explode().dropna().astype(str) # 옵션별 count
        cnts     = exploded.value_counts().to_dict()

        for opt in opts:
            cnt = cnts.get(opt, 0)
            pct = (cnt / total * 100) if total > 0 else 0.0
            results.append({
                'column_id': col,
                'question':   q_text,
                'resp_type':  resp_type,
                'option':     opt,
                'count':      int(cnt),
                'total':      total,
                'pct':        pct
            })
    return pd.DataFrame(results)

def summarize_objective(df: pd.DataFrame, def_df: pd.DataFrame) -> pd.DataFrame:
    single = summarize_single(df, def_df)
    multi  = summarize_multi(df, def_df)
    return pd.concat([single, multi], ignore_index=True)