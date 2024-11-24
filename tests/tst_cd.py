def get_user_input() -> list:
    user_input_str = input("Enter a list of items separated by commas: ")
    user_input = user_input_str.split(',')
    return [float(item.strip()) for item in user_input]


data = get_user_input()

ln = len(data)

for _cntr_ in range(ln-1 ):
    i = 0
    pass
    while i<ln-1:
        if data[i]<data[i+1]:
            tmp = data[i]
            data[i] = data[i+1]
            data[i+1] = tmp
        else:
            pass
        pass
        i = i + 1
        pass
print(data)
pass