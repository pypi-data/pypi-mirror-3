

def objectAdded(object, event=None):
    print("object added, edited or deleted with the keywords:")
    try:
        print object.Subject()
    except:
        pass