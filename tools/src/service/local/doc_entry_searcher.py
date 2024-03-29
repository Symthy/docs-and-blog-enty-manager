from __future__ import annotations

from typing import List, Optional

import unicodedata

from common.constant import NON_CATEGORY_GROUP_NAME
from docs.docs_grouping_data_deserializer import DocsGroupingDataDeserializer
from domain.doc.doc_entry import DocEntries, DocEntry
from domain.group_to_categories import GroupToCategorizedEntriesMap
from domain.interface import IEntry, IEntries
from dump.blog_to_doc_mapping import BlogDocEntryMapping
from dump.interface import IDumpEntriesAccessor
from files.conf.category_group_def import CategoryGroupDef


class EntrySearchResults:
    LINE_FORMAT = '{0:<15} {1:<{title_width}} {2:<15} {3:<15} {4:<11}'
    DEFAULT_TITLE_WIDTH = 48

    class EntrySearchResult:
        def __init__(self, entry_id, title, group, category, blog_id: Optional[str] = None):
            self.__id = entry_id
            self.__title = title
            self.__group = group
            self.__category = category
            self.__is_blog_posted = 'True' if blog_id is not None else 'False'

        def print_entry_search_result(self):
            double_byte_char_count = 0
            for char in self.__title:
                if unicodedata.east_asian_width(char) in "FWA":
                    double_byte_char_count += 1
            title_width = EntrySearchResults.DEFAULT_TITLE_WIDTH - double_byte_char_count
            print(EntrySearchResults.LINE_FORMAT.format(
                self.__id, self.__title[:EntrySearchResults.DEFAULT_TITLE_WIDTH], self.__group, self.__category,
                self.__is_blog_posted, title_width=title_width))

    def __init__(self):
        self.__results: List[EntrySearchResults.EntrySearchResult] = []

    @classmethod
    def print_header_line(cls):
        hyphen = '-'
        print(EntrySearchResults.LINE_FORMAT
              .format('Doc Entry ID', 'Doc Entry Title', 'Group Name', 'Category Name', 'Blog Posted',
                      title_width=EntrySearchResults.DEFAULT_TITLE_WIDTH))
        print(f'{hyphen:->15} {hyphen:->32} {hyphen:->15} {hyphen:->15} {hyphen:->11}')

    @classmethod
    def init_by_single_group(cls, group: str, entries: List[IEntry]) -> EntrySearchResults:
        blog_doc_mapping = BlogDocEntryMapping()
        self = EntrySearchResults()
        for entry in entries:
            blog_id_opt = blog_doc_mapping.get_blog_entry_id(entry.id)
            self.__results.append(
                EntrySearchResults.EntrySearchResult(entry.id, entry.title, group, entry.top_category, blog_id_opt))
        return self

    @classmethod
    def init_by_multi_groups(cls, category_group_def: CategoryGroupDef, entries: IEntries) -> EntrySearchResults:
        blog_doc_mapping = BlogDocEntryMapping()
        self = EntrySearchResults()
        for entry in entries.entry_list:
            group = category_group_def.get_belongs_group(entry.top_category)
            blog_id_opt = blog_doc_mapping.get_blog_entry_id(entry.id)
            self.__results.append(
                EntrySearchResults.EntrySearchResult(entry.id, entry.title, group, entry.top_category, blog_id_opt))
        return self

    def __print_entry_search_results(self):
        for result in self.__results:
            result.print_entry_search_result()

    def print_search_results(self):
        EntrySearchResults.print_header_line()
        self.__print_entry_search_results()


def search_doc_entry_by_group(category_group_def: CategoryGroupDef,
                              grouping_doc_entries_deserializer: DocsGroupingDataDeserializer, group: str):
    grouping_data: GroupToCategorizedEntriesMap = grouping_doc_entries_deserializer.execute()
    if not category_group_def.has_group_case_insensitive(group):
        print(f'[Info] Nothing specified group: {group}')
        return
    entries: List[IEntry] = grouping_data.get_entries(group)
    EntrySearchResults.init_by_single_group(group, entries).print_search_results()


def search_doc_entry_by_category(category_group_def: CategoryGroupDef,
                                 grouping_doc_entries_deserializer: DocsGroupingDataDeserializer, category: str):
    def print_entries_in_category(group_name: str, category_name: str):
        entries: List[IEntry] = grouping_data.get_entries(group_name, category_name)
        if len(entries) == 0:
            print(f'[Info] Nothing docs of specified category: {category_name}')
        EntrySearchResults.init_by_single_group(group_name, entries).print_search_results()

    grouping_data: GroupToCategorizedEntriesMap = grouping_doc_entries_deserializer.execute()
    is_exist_category = category_group_def.has_category(category)
    group = category_group_def.get_belongs_group(category)
    if not is_exist_category and group == NON_CATEGORY_GROUP_NAME:
        # Docs with no categories in the definition are under NON_CATEGORY_GROUP_NAME
        print_entries_in_category(NON_CATEGORY_GROUP_NAME, category)
        return
    if is_exist_category:
        print_entries_in_category(group, category)
        return
    print(f'[Info] Nothing specified category: {category}')


def search_doc_entry_by_title(dump_doc_data_accessor: IDumpEntriesAccessor[DocEntries, DocEntry],
                              category_group_def: CategoryGroupDef, keyword: str):
    target_entry_ids = dump_doc_data_accessor.search_entry_id(keyword)
    if len(target_entry_ids) == 0:
        print(f'[Warn] Nothing partially matched doc title: {keyword}')
    doc_entries: DocEntries = dump_doc_data_accessor.load_entries(target_entry_ids)
    EntrySearchResults.init_by_multi_groups(category_group_def, doc_entries).print_search_results()
