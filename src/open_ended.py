from src.config.common_imports import *
from src.config.settings import EXCLUDE_COLUMNS, BASE_DIR
import yaml, re

# 패턴 리스트 (정규식) - config 파일 읽기
with open(BASE_DIR / 'src/config/noise_config.yaml', encoding="utf-8") as f:
    noise_config = yaml.safe_load(f)

# exact 응답 set
EXACT_NOISE_RESPONSES = set(noise_config.get('exact', []))

# 정규식 컴파일
COMMON_NOISE_PATTERNS = [re.compile(p) for p in noise_config.get('regex_common', [])]
INFO_ENTRY_NOISE_PATTERNS = [re.compile(p) for p in noise_config.get('regex_info_entry', [])]

# 특수문자나 숫자만, 한글 자모만
REGEX_PUNCT_OR_NUM = re.compile(r'^[\W\d_]+$')
REGEX_HANGUL_JAMO = re.compile(r'^[ㄱ-ㅎㅏ-ㅣ]+$')
MIN_LEN = 2

def is_noise_extended(s: str, is_free: bool = False) -> bool:
    s = str(s).strip()
    if not s or len(s) < 2:
        return True
    if s in EXACT_NOISE_RESPONSES:
        return True
    if REGEX_PUNCT_OR_NUM.match(s) or REGEX_HANGUL_JAMO.match(s):
        return True
    for pattern in COMMON_NOISE_PATTERNS:
        if pattern.match(s):
            return True
    if not is_free:
        for pattern in INFO_ENTRY_NOISE_PATTERNS:
            if pattern.match(s):
                return True
    return False

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
    _, etc_cols = get_open_ended_columns(def_df, df)
    for col in etc_cols:
        base_col = col.replace('_etc', '')
        q_txt = def_df.loc[def_df['column_id'] == base_col, '컬럼'].values[0]

        ser_full = df[col].dropna().astype(str)
        vc = ser_full.value_counts()

        total = len(ser_full)
        if total == 0:
            continue

        for resp, cnt in vc.items():
            results.append({
                'column_id': col,
                'question':   f"{q_txt} (기타)",
                'field':      'etc',
                'original_response': resp,
                'is_noise':    is_noise_extended(resp),
                'count':       cnt,
                'total':       total,
                'pct':         cnt / total * 100
            })

    return pd.DataFrame(results)

def summarize_text_simple(df: pd.DataFrame, def_df: pd.DataFrame) -> pd.DataFrame:
    """
    주관식 응답을 _etc처럼 단순 count & pct로 집계
    """
    results = []
    text_cols = def_df.loc[
        def_df['응답유형'].str.contains('주관식', na=False),
        'column_id'
    ].tolist()
    
    text_cols = [c for c in text_cols if c not in EXCLUDE_COLUMNS and c in df.columns]

    for col in text_cols:
        row = def_df.loc[def_df['column_id'] == col]
        question_text = row['컬럼'].iat[0]
        is_free_opinion = '자유롭게' in question_text and '의견' in question_text

        ser_full = df[col].dropna().astype(str)
        total_full = len(ser_full)

        # 개별 응답 잡음 여부 판단 → 결과 기록
        for resp, cnt in ser_full.value_counts().items():
            noisy = is_noise_extended(resp, is_free=is_free_opinion)
            results.append({
                'column_id': col,
                'question':   question_text,
                'field':      'text_simple',
                'original_response': resp,
                'is_noise':   noisy,
                'count':      int(cnt),
                'total':      total_full,
                'pct':        cnt / total_full * 100
            })
    return pd.DataFrame(results)


def summarize_open_ended(df: pd.DataFrame, def_df: pd.DataFrame) -> pd.DataFrame:
    df_etc  = summarize_etc(df, def_df)
    df_text = summarize_text_simple(df, def_df)
    return pd.concat([df_etc, df_text], ignore_index=True)