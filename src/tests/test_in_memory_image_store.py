from src.in_memory_storage import InMemoryStorage
from src.in_memory_storage import StorageItem


def test_get_random_index_when_one_item():
    storage = InMemoryStorage()
    storage.add(StorageItem(
        image_content_type="text/plain",
        image_bytes=b"not important",
        secret_word="cat",
    ))
    # when there's only one item, the only index we can get from the method is 0
    assert storage.get_random_item_index() == 0


def test_is_empty():
    storage = InMemoryStorage()  # create empty storage
    assert storage.is_empty()  # verify it's empty when it's just created
