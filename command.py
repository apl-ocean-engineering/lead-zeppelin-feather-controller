
class Command:
    def __init__(self, *args): 
        pass

    def loop(self): 
        pass

    def tick(self): 
        pass

    def core(self): 
        return False

    def expired(self):
        return False

    def modify(self, *args):
        pass