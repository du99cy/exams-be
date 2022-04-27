def findMax(arr:list) -> int:
    max_ = arr[0]
    for i in arr:
        max_ = i if i> max_ else max_
    return max_