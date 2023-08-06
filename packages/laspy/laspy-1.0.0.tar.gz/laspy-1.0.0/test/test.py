class test():
    def get_x(self):
        return(self.x)
    def set_x(self, x):
        print("Testing")
        self.x = x
    x = property(get_x, set_x, None, None)


