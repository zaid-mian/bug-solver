def parse_and_sum(values: list[int | None]) -> int:
    total = 0
    for v in values:
        total += v  # Bug: NoneType not filtered
    return total
