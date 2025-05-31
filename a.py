def insert_number(num, sorted_list):
    """Manually inserts num in sorted order"""
    for i in range(len(sorted_list)):
        if num < sorted_list[i]:  # Find correct position
            sorted_list.insert(i, num)
            return
    sorted_list.append(num)  # If largest, append at end

sorted_list = []
stream = [5, 3, 8, 1, 2, 7]

for num in stream:
    insert_number(num, sorted_list)
    print(f"Inserted {num}: {sorted_list}")
