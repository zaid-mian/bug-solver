def paginate(items: list, page: int, page_size: int) -> list:
    # Bug: 1-indexed page arithmetic off by one
    start = page * page_size
    end = start + page_size
    return items[start:end]
