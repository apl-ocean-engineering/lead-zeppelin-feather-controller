# generic class for tasks
class Task:
    # initializes a new task with arguments
    def __init__(self, *args): # if replaced, don't forget to run super().__init__()
        self.stop = False 

    # runs once per loop (loops are as fast as possible)
    def loop(self): 
        pass

    # runs once per tick (tick rate defined in settings)
    def tick(self): 
        pass

    # whether or not a task is a core function
    def core(self): 
        return False

    # whether or not a task has expired. expired tasks will be removed from the task list
    def expired(self):
        return self.stop

    # expires a certain task. needs cooperation from the task itself
    def expire(self):
        if not self.core():
            self.stop = True

    # allows a task to wrap up. called after all tasks have executed in the loop
    def finish(self):
        pass
    
    # modifies an existing task with arguments
    def modify(self, *args):
        pass