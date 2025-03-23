import pickle

def pickledump(item, path):
    with open(path, 'wb') as file:
        pickle.dump(item, file)
        
def pickleload(path):
    with open(path, 'rb') as file:
        item = pickle.load(file)
    return item