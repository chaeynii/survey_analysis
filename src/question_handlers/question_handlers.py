from config.common_imports import *
from config.settings import BASE_DIR, ORG_NAME, BASE_DATE
from utils.file_utils import load_yaml
from config.logging_config import setup_logging

logger = setup_logging("logs.log")

def load_flexible_keyword_map(path: Path) -> dict:
    raw = load_yaml(path)
    keyword_map = []
    for target, rules in raw.items():
        if rules is None:
            continue
        for rule in rules:
            if isinstance(rule, dict):
                keyword = rule['keyword']
                match_type = rule.get('match', 'contains')
            else:
                keyword = rule
                match_type = 'contains'
            keyword_map.append((keyword, match_type, target))
    return keyword_map

def flexible_match(text: str, keyword_map: list) -> str:
    for keyword, match_type, target in keyword_map:
        if match_type == 'contains' and keyword in text:
            return target
        if match_type == 'exact' and keyword == text.strip():
            return target
    return ''

def load_regex_map(path: Path) -> dict:
    raw = load_yaml(path)
    compiled_map = {}
    for category, patterns in raw.items():
        if not patterns: continue
        compiled_map[category] = [re.compile(p) for p in patterns]
    return compiled_map

def regex_match(text: str, regex_map: dict) -> str:
    for category, patterns in regex_map.items():
        for pattern in patterns:
            if pattern.search(text):
                return category
    return ''

def summarize_q05_used_titles(df):
    path = BASE_DIR / f"data/raw/{ORG_NAME}_공공데이터포털_크롤링_{BASE_DATE}.xlsx"
    official_titles = pd.read_excel(path)["데이터명"].dropna().astype(str).tolist()
    # 기관명_데이터명 → (full, short) 튜플 리스트
    title_pairs = [(t, t.split("_", 1)[-1]) if "_" in t else (t, t) for t in official_titles]

    map_path = BASE_DIR / 'correction_maps/q05_used_titles.yaml'
    keyword_map = load_flexible_keyword_map(map_path)
    
    def normalize_text(text: str) -> str:
        return re.sub(r'[\s_]+', '', str(text))

    def match(text):
        # 1. flexible 사전 기반 매핑
        result = flexible_match(text, keyword_map)
        if result:
            return result

        # 2. 공식 목록 기반 포함/역포함 매칭
        norm_text = normalize_text(text)
        for full, short in title_pairs:
            if normalize_text(full) in norm_text or normalize_text(short) in norm_text \
            or norm_text in normalize_text(full) or norm_text in normalize_text(short):
                return full

        return ''

    df['mapped'] = df['original_response'].astype(str).map(match)

    matched_count = (df['mapped'] != '').sum()
    logger.info(f"[Q07] 매핑된 응답 수: {matched_count} / 전체 응답 수: {len(df)}")

    return df

def summarize_q13_desired_new_data(df):
    map_path = BASE_DIR / 'correction_maps/q13_desired_new.yaml'
    keyword_map = load_regex_map(map_path)

    def match(text):
        result = regex_match(text, keyword_map)
        if result:
            return result
        return ''

    df['mapped'] = df['original_response'].astype(str).map(match)

    matched_count = (df['mapped'] != '').sum()
    logger.info(f"[Q15] 매핑된 응답 수: {matched_count} / 전체 응답 수: {len(df)}")

    return df

def summarize_q14_ai_suitable_data(df: pd.DataFrame) -> pd.DataFrame:
    # 1) 맵 로딩
    domain_map = load_regex_map(BASE_DIR / 'correction_maps/q13_desired_new.yaml')
    ai_map     = load_regex_map(BASE_DIR / 'correction_maps/q14_ai_suitable.yaml')

    # 2) 각 매핑 함수
    def match_domain(text: str) -> str:
        return regex_match(text, domain_map) or ''
    def match_ai(text: str) -> str:
        return regex_match(text, ai_map) or ''

    # 3) 매핑 실행
    df['mapped_domain'] = df['original_response'].astype(str).map(match_domain)
    df['mapped_ai']     = df['original_response'].astype(str).map(match_ai)

    # 4) 매핑 현황 출력
    total = len(df)
    d_count = (df['mapped_domain'] != '').sum()
    a_count = (df['mapped_ai']     != '').sum()
    logger.info(f"[Q16] 도메인 매핑: {d_count}/{total} ({d_count/total:.1%})")
    logger.info(f"[Q16] AI 속성 매핑: {a_count}/{total} ({a_count/total:.1%})")

    return df

def summarize_q15_local_issue_data(df):
    map_path = BASE_DIR / 'correction_maps/q15_local_issue.yaml'
    keyword_map = load_regex_map(map_path)

    def match(text):
        result = regex_match(text, keyword_map)
        if result:
            return result
        return ''

    df['mapped'] = df['original_response'].astype(str).map(match)

    matched_count = (df['mapped'] != '').sum()
    logger.info(f"[Q17] 매핑된 응답 수: {matched_count} / 전체 응답 수: {len(df)}")

    return df

def summarize_q16_open_comment(df):
    map_path = BASE_DIR / 'correction_maps/q16_comment.yaml'
    keyword_map = load_regex_map(map_path)

    def match(text):
        result = regex_match(text, keyword_map)
        if result:
            return result
        return ''

    df['mapped'] = df['original_response'].astype(str).map(match)

    matched_count = (df['mapped'] != '').sum()
    logger.info(f"[Q18] 매핑된 응답 수: {matched_count} / 전체 응답 수: {len(df)}")

    return df