import pickle
ids = []
filename = '2016_2017'
with open(filename, 'rb') as f:
    while 1:
        try:
            ids.append(pickle.load(f))
        except EOFError:
            break

print len(ids)
for list in ids:
    print list