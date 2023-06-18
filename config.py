import random

with open("keys.txt", "r") as f:
    keys = [row.strip() for row in f]
    random.shuffle(keys)


''' настройка перерыва между кошельками от и до в секундах'''
delay = (0, 100)