import numpy as np
import xxhash


class HLL():
    
    def __get_alpha(self,p):
        if not (4 <= p <= 16):
            raise ValueError("p=%d should be in range [4 : 16]" % p)

        if p == 4:
            return 0.673

        if p == 5:
            return 0.697

        if p == 6:
            return 0.709

        return 0.7213 / (1.0 + 1.079 / (1 << p))

    def __init__(self, error_bound, error_probability):
        self.p = int(np.ceil(np.log2((1.04 / error_bound) ** 2)))
        self.m = 1 << self.p
        self.alpha = self.__get_alpha(self.p)
        self.M = np.zeros((self.m,),dtype = np.int8)


    
        


x = HLL(0.01,0.01)
print(x.p,x.alpha)
        