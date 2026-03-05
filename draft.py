if checks:
    column_names = list(checks[0].keys())
    table = doc.add_table(rows=len(checks) + 1, cols=len(column_names), style="Light Grid")
    for _cell, name in zip(table.rows[0].cells, column_names):
        _cell.text = name.title().replace("_", " ")
    for idx, row_data in enumerate(checks, start=1):
        for _cell, val in zip(table.rows[idx].cells, row_data.values()):
            _cell.text = str(val)
