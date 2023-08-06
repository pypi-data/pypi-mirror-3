class dictionary():
    def __init__(self):
        self.dict = {}
    def add(self,function,keywords,priority):
        match = 0
        for each in self.dict:
            if function == self.dict:
                match = 1
        if match == 0:
            self.dict[function] = [priority,keywords]
            return True
        else:
            return False
    def remove(self,function):
        x = 0
        match = 0
        rem = 0
        for each in self.dict:
            if each == function:
                rem = each
                match = 1
            x += 1
        self.dict.pop(rem)
        if match == 1:
            return True
        else:
            return False

    def run(self,string):
        cur = 0
        func = 0
        cPri = 0
        match = 0
        for each in self.dict:
            x = 0
            for key in self.dict[each][1]:
                if key in string:
                    x = x + 1
            if x > cur:
                cur = x
                cPri = self.dict[each][0]
                func = each
                match = 1
            elif x == cur and self.dict[each][0] < cPri:
                cur = x
                cPri = self.dict[each][0]
                func = each
                match = 1
        if match == 1:
            return func
        else:
            return False
    def funcs(self):
        return self.dict
