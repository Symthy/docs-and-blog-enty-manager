from typing import List

from domain.blog.blog_entry import BlogEntry, BlogEntries
from domain.doc.doc_entry import DocEntries
from file.blog_config import BlogConfig
from file.category_group_def import CategoryGroupDef
from file.dump.blog_to_doc_mapping import BlogDocEntryMapping
from file.dump.dump_entry_list import DumpEntryList
from service.external.blog_entry_index_updater import update_blog_entry_summary_index_file
from service.external.blog_entry_pusher import push_blog_and_photo_entry
from service.local.doc_entry_pusher import push_documents_to_docs


def push_entry_to_docs_and_blog(blog_config: BlogConfig, category_group_def: CategoryGroupDef,
                                target_dir_names: List[str] = None):
    doc_entries = push_documents_to_docs(category_group_def, target_dir_names)
    __push_entry_from_docs_to_blog(blog_config, category_group_def, doc_entries)


def push_entry_from_docs_to_blog(blog_config: BlogConfig, category_group_def: CategoryGroupDef,
                                 target_doc_entry_ids: List[str]):
    doc_entries = DocEntries.init_by_entry_ids(target_doc_entry_ids)
    __push_entry_from_docs_to_blog(blog_config, category_group_def, doc_entries)


def __push_entry_from_docs_to_blog(blog_config: BlogConfig, category_group_def: CategoryGroupDef,
                                   doc_entries: DocEntries):
    blog_doc_mapping = BlogDocEntryMapping()
    dump_blog_entry_list = DumpEntryList.init_blog_entry_list()
    updated_blog_entry_list: List[BlogEntry] = []
    for doc_entry in doc_entries.entry_list:
        blog_entry_id_opt = blog_doc_mapping.get_blog_entry_id(doc_entry.id)
        old_blog_entry_opt = None if blog_entry_id_opt is None else BlogEntry.deserialize_entry_data(blog_entry_id_opt)
        new_blog_entry_opt = push_blog_and_photo_entry(blog_config, doc_entry, old_blog_entry_opt)
        if new_blog_entry_opt is None:
            print(f'[Info] blog push skip. (dir: {doc_entry.dir_path})')
            continue
        updated_blog_entry_list.append(new_blog_entry_opt)
        dump_blog_entry_list.push_entry(new_blog_entry_opt)
        blog_doc_mapping.push_entry_pair(new_blog_entry_opt.id, doc_entry.id)
    # dump to file
    updated_blog_entries = BlogEntries(updated_blog_entry_list)
    updated_blog_entries.dump_all_data()
    dump_blog_entry_list.dump_file()
    blog_doc_mapping.dump_file()
    update_blog_entry_summary_index_file(category_group_def, updated_blog_entries)
