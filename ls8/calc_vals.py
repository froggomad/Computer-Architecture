dict = {
  "cat": "bob",
  "dog": 23,
  19: 18,
  90: "fish"
}

value = 0

for i, val in dict.items():
    if type(val) is int:
        value += val

print(value)