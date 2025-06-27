from src.config.common_imports import *

def main():
    def_df = load_definitions(DEF_PATH) # 정의서 로드
    df     = load_raw_and_rename(RAW_PATH, def_df) # 정의서 기반으로 컬럼id 매핑

    convert_dtypes(df, def_df) # 컬럼 데이터 타입 지정
    preprocess_enumerated(df, def_df) # 전처리
    ### 중간저장 : 전처리 결과 확인
    df.to_excel(Path(PROCESSED).parent / 'preprocessed_survey.xlsx', index=False)

    ### 통계
    # 객관식 문항
    objective = summarize_objective(df, def_df)
    objective.to_excel(Path(PROCESSED).parent / 'objective_summary.xlsx', index=False)

    # 주관식 / 기타 문항
    open_ended = summarize_open_ended(df, def_df)
    open_ended.to_excel(Path(PROCESSED).parent / 'open_ended_summary.xlsx', index=False)

    print("----------- 분석 완료")
    print("- 객관식:", objective.shape)
    print("- 주관식/기타:", open_ended.shape)

if __name__ == '__main__':
    main()
