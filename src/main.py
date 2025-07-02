from config.common_imports import *

def main():
    df_raw, def_df = loader()
    df_processed = preprocess_enumerated(df_raw, def_df)
    
        # 중간 저장
    df_processed.to_excel(Path(PROCESSED).parent / 'preprocessed_survey.xlsx', index=False)

    # 통계
        # 객관식 문항
    objective = summarize_objective(df_processed, def_df)
    objective.to_excel(Path(PROCESSED).parent / 'objective_summary.xlsx', index=False)
    save_multiple_sheets_with_chart(objective, def_df, Path(BASE_DIR) / "reports/objective_results.xlsx")

        # 그룹별(성별, 연령대, 소속) 객관식 통계: 
    for group in ['gender','age','affiliation']:
        obj_grp = summarize_by(df_processed, group, summarize_objective, def_df)
        save_grouped_summaries(obj_grp, def_df, group, Path(PROCESSED).parent)

        # 주관식 / 기타 문항
            # 주관식 전처리 1차 - 불필요 응답 분류
    df_clean = mark_noise(df_processed, def_df)
    
    # 주관식 각 문항별 처리
    nos = ['5', '13', '14', '15', '16']
    mapping = dict(
        zip(
            def_df['no'],
            def_df['column_id']
        )
    )

    df_split = {
        no: df_clean[df_clean['column_id'] == mapping[no]].reset_index(drop=True)
        for no in nos if no in mapping
    }
    
    qh = importlib.import_module("question_handlers.question_handlers")

    first_oe_summaries = {}
    for no, subdf in df_split.items():
        col_id = def_df.loc[def_df['no'].astype(str) == str(no), 'column_id'].iat[0]

        # 함수 이름 조합 (no는 두 자리 0패딩)
        func_name = f"summarize_q{int(no):02d}_{col_id}"
        try:
            summary_func = getattr(qh, func_name)
        except AttributeError:
            raise RuntimeError(f"요약 함수가 없습니다: {func_name}")

        # 동적으로 함수 호출
        df_sum = summary_func(subdf)
        first_oe_summaries[no] = df_sum

        # 저장  
        out = Path(PROCESSED).parent / f"open_ended_summary{no}.xlsx"
        df_sum.to_excel(out, index=False)
        print(f"[1차 저장] 문항 {no} -> {out}")
        
    mapped_needed = {
        '14': ['mapped_domain', 'mapped_ai']
    }
    
    all_open_summaries = []
    for no, df_sum in first_oe_summaries.items():
        opts_list = mapped_needed.get(no, [None])
        
        for opt in opts_list:
            kwargs = {'mapped_col': opt} if opt else {}
            summary = summarize_open_ended(df_sum, def_df, **kwargs)
            
            summary.insert(0, 'question_no', no)
            if opt:
                summary.insert(1, 'mapped_col', opt)
            
            all_open_summaries.append(summary)
            suffix = f", {opt}" if opt else ""
            print(f"[문항 {no}{suffix}] → columns: {summary.columns.tolist()}")

    # 4) 한 번에 결합
    all_open = pd.concat(all_open_summaries, ignore_index=True)

    # 5) 저장
    out_path = Path(PROCESSED).parent / 'analysis_open_ended_summary.xlsx'
    all_open.to_excel(out_path, index=False)
    save_multiple_sheets_with_chart(all_open, def_df, Path(BASE_DIR) / "reports/open_ended_results.xlsx")
    print(f"[최종 저장] {out_path}")

    print("----------- 분석 완료")
    print("- 객관식:", objective.shape)
    print("- 주관식/기타:", all_open.shape)

if __name__ == '__main__':
    main()
