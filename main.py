from src.config.common_imports import *

def main():
    def_df = load_definitions(DEF_PATH)
    df_raw = load_raw_and_rename(RAW_PATH, def_df)
    convert_dtypes(df_raw, def_df)
    df_processed = preprocess_enumerated(df_raw, def_df)
    
    # 중간 저장
    output_path = Path(PROCESSED).parent / 'preprocessed_survey.xlsx'
    df_processed.to_excel(output_path, index=False)

    ### 통계
    # 객관식 문항
    objective = summarize_objective(df_processed, def_df)
    objective.to_excel(Path(PROCESSED).parent / 'objective_summary.xlsx', index=False)

    # 주관식 / 기타 문항
    open_ended = summarize_open_ended(df_processed, def_df)
    print(f"잡음 응답수 : {open_ended['is_noise'].sum()}")

    open_ended.to_excel(Path(PROCESSED).parent / 'open_ended_summary.xlsx', index=False)

    print("----------- 분석 완료")
    print("- 객관식:", objective.shape)
    print("- 주관식/기타:", open_ended.shape)

if __name__ == '__main__':
    main()
