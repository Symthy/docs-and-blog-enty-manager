from common.constant import LOCAL_DOCS_ENTRY_GROUPING_PATH, LOCAL_DOCS_ENTRY_INDEX_RESULT_PATH
from docs.docs_data_deserializer import deserialize_doc_entry_grouping_data
from domain.doc_entry import DocEntries
from file.category_group_def import CategoryGroupDef
from file.file_accessor import write_text_lines


def update_entry_grouping_and_index(category_group_def: CategoryGroupDef, add_docs_entries: DocEntries):
    entry_index_result_map = deserialize_doc_entry_grouping_data(category_group_def, add_docs_entries)
    entry_index_result_map.dump_all_data(LOCAL_DOCS_ENTRY_GROUPING_PATH)
    write_text_lines(LOCAL_DOCS_ENTRY_INDEX_RESULT_PATH, entry_index_result_map.convert_md_lines())