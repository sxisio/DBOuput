result = ["Hello-World", "Foo", "Bar-Baz"]
new_result = []
for item in result:
    if '-' in item:
        new_item = f"`{item}`"
    else:
        new_item = item
    new_result.append(new_item)
print(new_result)