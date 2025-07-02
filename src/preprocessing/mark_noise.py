from config.common_imports import *
from config.settings import BASE_DIR, EXCLUDE_COLUMNS
from utils.file_utils import load_yaml
from analysis.summarize_open_ended import get_open_ended_columns

noise_config = load_yaml(BASE_DIR / 'src/config/noise_config.yaml')

EXACT_NOISE_RESPONSES = set(noise_config.get('exact', [])) # exact 응답 set
COMMON_NOISE_PATTERNS = [re.compile(p) for p in noise_config.get('regex_common', [])] # 정규식 컴파일
INFO_ENTRY_NOISE_PATTERNS = [re.compile(p) for p in noise_config.get('regex_info_entry', [])] # 정규식 컴파일

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

def mark_noise_in_etc(df: pd.DataFrame, def_df: pd.DataFrame) -> pd.DataFrame:
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

def mark_noise_in_text(df: pd.DataFrame, def_df: pd.DataFrame) -> pd.DataFrame:
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

def mark_noise(df: pd.DataFrame, def_df: pd.DataFrame) -> pd.DataFrame:
    df_etc  = mark_noise_in_etc(df, def_df)
    df_text = mark_noise_in_text(df, def_df)
    df_marked = pd.concat([df_etc, df_text], ignore_index=True)
    df_clean = df_marked[df_marked['is_noise'] == False].copy()
    
    return df_clean