from utility import Utils
import xlsxwriter
import os


if __name__ == '__main__':
    analysis_xlsx = os.path.join(Utils.data_dir, "analysis_goldstandard.xlsx")
    workbook_analysis = xlsxwriter.Workbook(analysis_xlsx)

    worksheet_analysis = workbook_analysis.add_worksheet("DIRECT")
    direct_reasons_complete = Utils.load_json(os.path.join(Utils.data_dir, "direct_reasons_complete.json"))
    category_names = []
    for column, (cat, reasons) in enumerate(direct_reasons_complete.items()):
        category_names.append(cat)
        worksheet_analysis.set_column(column * 2, column * 2+1, 30)
        worksheet_analysis.write(0, column * 2, cat)
        for row, reason in enumerate(reasons):
            worksheet_analysis.write(row + 1, column * 2, reason["reason"])
            worksheet_analysis.write(row + 1, column * 2 + 1, reason["result"]["display"] + "|" + reason["result"]["code"])



    worksheet_analysis = workbook_analysis.add_worksheet("SEMI_DIRECT")

    semi_direct_reasons_complete = Utils.load_json(os.path.join(Utils.data_dir,
                                                                "semi_direct_reasons_complete.json"))
    extra_column = 0
    for (cat, reasons) in semi_direct_reasons_complete.items():
        if cat in category_names:
            column = category_names.index(cat)
        else:
            column = len(category_names) + extra_column
            extra_column += 1

        worksheet_analysis.set_column(column * 2, column * 2+1, 30)
        worksheet_analysis.write(0, column * 2, cat)
        for row, reason in enumerate(reasons):
            worksheet_analysis.write(row + 1, column * 2, reason["reason"])
            worksheet_analysis.write(row + 1, column * 2 + 1, reason["result"]["display"] + "|" + reason["result"]["code"])

    not_found = Utils.load_json(os.path.join(Utils.data_dir, "not_found.json"))


    worksheet_analysis = workbook_analysis.add_worksheet("FINAL")
    reasons_complete = Utils.merge(direct_reasons_complete, semi_direct_reasons_complete)
    cats_reason = Utils.read_cats_reason(os.path.join(Utils.data_dir, "Cats_Reasons.csv"))

    for column, (cat, reasons) in enumerate(reasons_complete.items()):
        worksheet_analysis.set_column(column * 2, column * 2+1, 30)
        worksheet_analysis.write(0, column * 2, cat)
        final_row = 0
        for row, reason in enumerate(reasons):
            worksheet_analysis.write(row + 1, column * 2, reason["reason"])
            worksheet_analysis.write(row + 1, column * 2 + 1, reason["result"]["display"] + "|" + reason["result"]["code"])
            final_row = row +1

        if cat in not_found:
            for reason in not_found[cat]:
                worksheet_analysis.write(final_row + 1, column * 2, reason)
                worksheet_analysis.write(final_row + 1, column * 2 + 1, "NaN")
                final_row += 1


        worksheet_analysis.write(0, column * 2 + 1, str(len(reasons)) + " out of " + str(len(cats_reason[cat].dropna())))





    workbook_analysis.close()




