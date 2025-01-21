# iterator.py
from typing import List
from observer import Iterator
from Classes.book import Book

class BookCollectionIterator(Iterator):
    def __init__(self, collection: List[Book]):
        self.collection = collection
        self.index = 0

    def hasNext(self) -> bool:
        return self.index < len(self.collection)

    def next(self) -> Book:
        if self.hasNext():
            book = self.collection[self.index]
            self.index += 1
            return book
        else:
            raise StopIteration("No more books in the collection.")
