from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Dict

from common.constant import NON_CATEGORY_GROUP_NAME
from domain.blog.photo_entry import PhotoEntries
from domain.interface import IEntries, IEntry
from dump.entry_data_dumper import resolve_dump_str_field
from ltime.time_resolver import convert_datetime_to_entry_time_str, \
    convert_datetime_to_month_day_str, convert_entry_time_str_to_datetime


class BlogEntry(IEntry):
    FIELD_ID = 'id'
    FIELD_TITLE = 'title'
    FIELD_CONTENT = 'content'
    FIELD_PAGE_URL = 'page_url'
    FIELD_TOP_CATEGORY = 'top_category'
    FIELD_CATEGORIES = 'categories'
    FIELD_UPDATED_AT = 'updated_at'
    FIELD_ORIGINAL_DOC_ID = 'original_doc_id'
    FIELD_DOC_IMAGES = 'doc_images'

    def __init__(self, entry_id: str, title: str, content: str, page_url: str, last_updated: Optional[datetime],
                 categories: List[str], doc_id: Optional[str] = None, doc_images: Optional[PhotoEntries] = None):
        self.__id = entry_id
        self.__title = title
        self.__content = content  # No dump
        self.__page_url = page_url
        self.__updated_at: Optional[datetime] = last_updated  # Make it optional just in case
        self.__top_category = categories[0] if not len(categories) == 0 else NON_CATEGORY_GROUP_NAME
        self.__categories = categories
        self.__original_doc_id = doc_id
        self.__doc_images: PhotoEntries = PhotoEntries() if doc_images is None else doc_images

    @property
    def id(self):
        return self.__id

    @property
    def title(self):
        return self.__title

    @property
    def content(self):
        return self.__content

    @property
    def page_url(self):
        return self.__page_url

    @property
    def updated_at(self) -> str:
        return convert_datetime_to_entry_time_str(self.__updated_at)

    @property
    def updated_at_month_day(self) -> str:
        return convert_datetime_to_month_day_str(self.__updated_at)

    @property
    def categories(self) -> List[str]:
        return self.__categories

    @property
    def top_category(self) -> str:
        return self.__top_category

    @property
    def original_doc_id(self):
        return self.__original_doc_id

    def register_doc_id(self, doc_entry_id: str):
        self.__original_doc_id = doc_entry_id

    @property
    def doc_images(self) -> PhotoEntries:
        return self.__doc_images

    def is_images_empty(self) -> bool:
        return self.__doc_images.is_empty()

    def add_photo_entries(self, photo_entries: Optional[PhotoEntries] = None):
        if photo_entries is None:
            return
        self.__doc_images.merge(photo_entries)

    def build_id_to_title(self) -> Dict[str, str]:
        return {self.id: self.title}

    def convert_md_line(self) -> str:
        return f'- [{self.title}]({self.page_url}) ({self.updated_at_month_day})'

    def build_dump_data(self, json_data: Optional[object] = None) -> object:
        return {
            BlogEntry.FIELD_ID: resolve_dump_str_field(self, json_data, BlogEntry.FIELD_ID),
            BlogEntry.FIELD_TITLE: resolve_dump_str_field(self, json_data, BlogEntry.FIELD_TITLE),
            BlogEntry.FIELD_PAGE_URL: resolve_dump_str_field(self, json_data, BlogEntry.FIELD_PAGE_URL),
            BlogEntry.FIELD_TOP_CATEGORY: resolve_dump_str_field(self, json_data, BlogEntry.FIELD_TOP_CATEGORY),
            BlogEntry.FIELD_CATEGORIES: resolve_dump_str_field(self, json_data, BlogEntry.FIELD_CATEGORIES),
            BlogEntry.FIELD_UPDATED_AT: resolve_dump_str_field(self, json_data, BlogEntry.FIELD_UPDATED_AT),
            BlogEntry.FIELD_ORIGINAL_DOC_ID: resolve_dump_str_field(self, json_data, BlogEntry.FIELD_ORIGINAL_DOC_ID),
            BlogEntry.FIELD_DOC_IMAGES: self.__doc_images.build_dump_data(),
        }

    @classmethod
    def restore_from_json_data(cls, dump_data: Dict[str, any]) -> BlogEntry:
        return BlogEntry(
            dump_data[BlogEntry.FIELD_ID],
            dump_data[BlogEntry.FIELD_TITLE],
            '',  # content is not dump
            dump_data[BlogEntry.FIELD_PAGE_URL],
            convert_entry_time_str_to_datetime(dump_data[BlogEntry.FIELD_UPDATED_AT]),
            dump_data[BlogEntry.FIELD_CATEGORIES],
            dump_data[BlogEntry.FIELD_ORIGINAL_DOC_ID],
            PhotoEntries.init_from_dump_data(dump_data[BlogEntry.FIELD_DOC_IMAGES])
        )


class BlogEntries(IEntries):
    def __init__(self, entries: List[BlogEntry] = None):
        # Todo: examination. use dict? see
        self.__entries: List[BlogEntry] = []
        if entries is not None:
            self.__entries: List[BlogEntry] = entries

    @property
    def entry_list(self) -> List[BlogEntry]:
        return self.__entries

    def is_empty(self) -> bool:
        return len(self.__entries) == 0

    def is_contains(self, target_entry_id: str) -> bool:
        for entry in self.__entries:
            if entry.id == target_entry_id:
                return True
        return False

    def add_entry(self, blog_entry: BlogEntry):
        self.__entries.append(blog_entry)

    def merge(self, blog_entries: BlogEntries):
        if blog_entries.is_empty():
            return
        # existed entry is overwrite
        self.__entries.extend(blog_entries.entry_list)

    def convert_md_lines(self) -> List[str]:
        return [entry.convert_md_line() for entry in self.__entries]

    @classmethod
    def new_instance(cls, entry_list: List[BlogEntry]) -> BlogEntries:
        return BlogEntries(entry_list)
