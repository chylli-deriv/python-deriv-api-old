try:
    raise Exception()
except BaseException as err:
    print(f"{err}")