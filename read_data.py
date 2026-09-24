import importlib.util
import pathlib

_module_path = pathlib.Path(__file__).resolve().parent / 'tools' / 'data-validation' / 'originalRead_Data.py'
_spec = importlib.util.spec_from_file_location('read_data_impl', _module_path)
if _spec is None or _spec.loader is None:
    raise ImportError(f'Unable to load data module from {_module_path}')
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

for _name in [
    'get_sheet_names',
    'read_excel_file',
    'read_all_sheets',
    'clean_data',
    'clean_all_sheets',
    'calculate_totals',
    'get_numeric_columns',
    'preview_sheet',
    'preview_all_sheets',
    'summarize_sheets',
    'plot_null_summary',
    'plot_numeric_distribution',
    'plot_sheet_comparison',
    'generate_all_visualizations',
]:
    globals()[_name] = getattr(_module, _name)
