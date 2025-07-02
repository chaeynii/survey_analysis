from config.common_imports import *
from utils.reporting_utils import save_multiple_sheets_with_chart
from config.logging_config import setup_logging

logger = setup_logging("logs.log")

def summarize_by(df, group_field, summary_func, *args, **kwargs):
    import pandas as pd

    out = []
    for grp_val, subdf in df.groupby(group_field):
        summary = summary_func(subdf, *args, **kwargs)

        if isinstance(summary, pd.Series):
            summary = summary.to_frame().T

        summary.insert(0, group_field, grp_val)

        out.append(summary)

    result = pd.concat(out, ignore_index=True)
    return result

def save_grouped_summaries(
    summary_df: pd.DataFrame,
    def_df: pd.DataFrame,
    group_field: str,
    output_base: str
) -> None:
    group_path = Path(output_base) /  f"objective_by_{group_field}"
    group_path.mkdir(parents=True, exist_ok=True)
    summary_df.to_excel(group_path / f"objective_by_{group_field}.xlsx", index=False)

    for grp_val, subdf in summary_df.groupby(group_field):
        safe_val = str(grp_val).replace(" ", "_")
        file_name = f"{group_field}_{safe_val}_summary.xlsx"
        file_path = group_path / file_name

        subdf.to_excel(file_path, index=False)
        logger.info(f"[저장] {file_path}")
        
        file_report_name = f"{group_field}_{safe_val}_문항별_시트_생성.xlsx"
        file_report_path = Path(BASE_DIR) / "reports/groups"
        file_report_path.mkdir(parents=True, exist_ok=True)
        save_multiple_sheets_with_chart(subdf, def_df, file_report_path / file_report_name)
        logger.info(f"[저장] {file_report_path}")

