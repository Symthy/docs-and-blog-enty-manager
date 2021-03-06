from common.constant import LOCAL_DOCS_ENTRY_INDEX_RESULT_PATH
from docs.docs_grouping_deserializer import deserialize_doc_entry_grouping_data
from domain.doc.doc_entry import DocEntries
from files.conf.category_group_def import CategoryGroupDef
from files.file_accessor import write_text_lines


def update_entry_grouping_and_summary(category_group_def: CategoryGroupDef, add_docs_entries: DocEntries):
    entry_grouping_map = deserialize_doc_entry_grouping_data(category_group_def, add_docs_entries)
    entry_grouping_map.dump_docs_data()
    write_text_lines(LOCAL_DOCS_ENTRY_INDEX_RESULT_PATH, entry_grouping_map.convert_md_lines())
