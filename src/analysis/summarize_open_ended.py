from config.common_imports import *

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

def summarize_open_ended(
    df: pd.DataFrame,
    def_df: pd.DataFrame,
    mapped_col: str = 'mapped'
) -> pd.DataFrame:
    records = []

    # 1) 주관식 문항만 추출
    subj_defs = def_df[def_df['응답유형'].str.contains('주관식', na=False)]

    for _, row in subj_defs.iterrows():
        col_id    = row['column_id']
        question  = row['컬럼']
        resp_type = row['응답유형']

        # 2) df에서 해당 column_id만 필터
        df_q = df[df['column_id'] == col_id]
        if df_q.empty or mapped_col not in df_q.columns:
            continue

        # 3) mapped_col 값만 남기고 빈값 제거
        ser = df_q[mapped_col].fillna('').astype(str)
        ser = ser[ser != '']

        total = len(ser)
        if total == 0:
            continue

        # 4) 각 option(mappd_col)별 count 집계

        grp = (
            ser
            .value_counts(dropna=False)
            .rename_axis('option')        # 인덱스 이름을 option으로
            .reset_index(name='count')    # 인덱스 -> 컬럼
        )

        # 5) total, pct 계산
        grp['total'] = total
        grp['pct']   = grp['count'] / total * 100

        # 6) 메타 컬럼 추가
        grp.insert(0, 'column_id', col_id)
        grp.insert(1, 'question',   question)
        grp.insert(2, 'resp_type',  resp_type)

        # 7) 결과 리스트에 담기
        records.append(grp[['column_id','question','resp_type','option','count','total','pct']])

    # 8) 합쳐서 반환
    if not records:
        return pd.DataFrame(columns=['column_id','question','resp_type','option','count','total','pct'])
    return pd.concat(records, ignore_index=True)
