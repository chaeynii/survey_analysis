import pandas as pd
from config.logging_config import setup_logging

logger = setup_logging("logs.log")

def save_multiple_sheets_with_chart(df: pd.DataFrame, def_df: pd.DataFrame, output_path: str):
    no_map = def_df.set_index('column_id')['no'].to_dict()
    # 정렬
    def sort_key(cid):
        v = no_map.get(cid, None)
        try:
            return float(v)
        except:
            return float('inf')

    sorted_cols = sorted(df['column_id'].unique(), key=sort_key)

    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        workbook  = writer.book

        for col_id in sorted_cols:
            grp = df[df['column_id']==col_id]
            no = no_map.get(col_id, '')
            
            sheet_name = f"{no}. {col_id}"
            sheet_name = sheet_name[:31]

            grp.to_excel(writer, sheet_name=sheet_name, index=False)

            worksheet = writer.sheets[sheet_name]
            chart     = workbook.add_chart({'type': 'column'})

            # 표 헤더 이후 데이터 시작 행, 열 인덱스 계산
            # 'option' 컬럼이 D, 'count' 컬럼이 E에 있다고 가정
            start_row = 1
            end_row   = len(grp)
            cols = list(grp.columns)
            opt_col_idx   = cols.index('option')
            count_col_idx = cols.index('count')
            
            # 카테고리(가로축) / 값(세로축) 좌표 설정
            categories = [sheet_name, start_row, opt_col_idx, end_row, opt_col_idx]
            values     = [sheet_name, start_row, count_col_idx, end_row, count_col_idx]

            chart.add_series({
                'name':       '응답 수',
                'categories': categories,
                'values':     values,
            })
            
            # 차트 스타일 및 축 레이블
            chart.set_title ({'name': '응답 분포 (count)'})
            chart.set_x_axis({'name': 'Option'})
            chart.set_y_axis({'name': 'Count'})
            chart.set_legend({'position': 'none'})
            chart.set_style(10)

            # 차트 삽입 (크기 조절)
            worksheet.insert_chart('H2', chart, {'x_scale': 1.2, 'y_scale': 1.2})

    logger.info(f"-----'{output_path}'에 {df['column_id'].nunique()}개 시트 생성 완료")