'''열거형 문항 처리'''

from src.config.common_imports import *

def preprocess_enumerated(df: pd.DataFrame, def_df: pd.DataFrame) -> None:
    for _, r in def_df.iterrows():
        col, raw_list = r['column_id'], r['값 목록'] or ''
        if col not in df.columns:
            continue

        opts   = next(csv.reader([raw_list], delimiter=',', quotechar='"'))
        strict = str(r['enumerated_strict']).upper() == 'TRUE'
        sep    = r.get('복수선택 구분자', '|') or '|'
        is_multi = '복수선택' in r['응답유형']

        # 공란, NaN 일 경우 : 빈 리스트 반환
        def safe_split(v):
            if pd.isna(v) or str(v).strip()=='':
                return []
            return [x.strip() for x in str(v).split(sep) if x.strip()]

        if is_multi: # 객관식(복수선택)
            ser = df[col].astype(object).apply(safe_split)
            def classify(lst):
                allow = [x for x in lst if x in opts]
                extra = [x for x in lst if x not in opts]
                if extra and not strict:
                    raise ValueError(f"{col} – 허용값 외: {extra}")
                return allow + (['기타'] if extra else []), extra

            result = ser.apply(classify)
            df[col] = result.map(lambda x: x[0])
            if strict and result.map(lambda x: bool(x[1])).any():
                etc = f"{col}_etc"
                df.insert(df.columns.get_loc(col)+1, etc,
                          result.map(lambda x: x[1][0] if x[1] else None))
        else: # 객관식(단일선택)
            ser = df[col].astype(str).replace({'nan':np.nan,'None':np.nan,'':np.nan})
            if strict:
                valid = [o for o in opts if o!='기타']
                mask = ser.notna() & ~ser.isin(valid)
                if mask.any():
                    etc = f"{col}_etc"
                    df.insert(df.columns.get_loc(col)+1, etc, None)
                    df.loc[mask, etc] = ser[mask].astype(str)
                    ser.loc[mask] = '기타'
                df[col] = pd.Categorical(ser, categories=opts)
            else:
                df[col] = ser
                
    return df