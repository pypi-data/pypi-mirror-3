import info

def add():
    print("Current names:",info.names)
    print("Enter a name like verge.info.tm you want to make special.")
    name = raw_input(">").strip()
    if len(name)==0: return
    if raw_input("Is '"+name+"' OK? y/n").startswith('y'):
        info.names += (name,)
        info.save()

if __name__ == '__main__': add()
