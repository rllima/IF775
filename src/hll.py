import numpy as np
import xxhash
import random
import getopt
import sys
import csv


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
        self.seed = random.randrange(0, 1 << self.p)
        self.M = np.zeros((self.m,),dtype = np.int8)
        

    def insert(self,value):
        x = xxhash.xxh32(bytes(value),seed=self.seed).intdigest()
        j = x & ((1 << self.p) - 1)
        # Remove those p bits
        w = x >> self.p
        # Find the first 0 in the remaining bit pattern
        self.M[j] = max(self.M[j], self.__get_rho(w, self.p))


    def __get_rho(self, w, p):
        mask = 1 << p
        lsb = 0
        while (w & mask) == 0:
            lsb += 1
            w =  w << 1
        return lsb + 1

    def estimate(self):
        """ Returns the estimate of the cardinality """
        E = self.alpha * float(self.m ** 2) / np.power(2.0, - self.M).sum()
        if E <= 2.5 * self.m:             # Small range correction
            V = self.m - np.count_nonzero(self.M)
            if V > 0:
                return self.__linear_counting(V)
            else:
                return int(E) 
    
        elif E <= float(int(1) << 32) / 30.0:
            return int(E)
        else:
            return - (1 << self.p) * np.log(1.0 - E / (1 << self.p))

    def __linear_counting(self, V):
        return self.m * np.log(self.m / float(V))


def main():
    argv = sys.argv[1:]
    target = str
    eps = float
    delta = float
    path = str
    try:
        opts, args = getopt.gnu_getopt(argv,'t:e:d:fh',['target=','eps=','delta=','file=','help',])
        for opt, arg in opts:
            if opt in ('--t', '--target'):
                target = int(arg)
            elif opt in ('--e', '--eps'):
                eps = float(arg)
            elif opt in ('--d','--delta'):
                delta = float(arg)
            elif opt in ('--f','--file'):
                path = arg
            elif opt == 'help':
                print("USAGE")
    except getopt.GetoptError as e:
        print('Something went wrong!')
        sys.exit(2)

    #unique = {}
    hll = HLL(eps,delta)
    print("Stating insertion...")  
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            #if row[8] not in unique:
              #  unique[row[target]] = "a"
            hll.insert(int(row[target]))
    print("Finish insertion\nEstimating...")
    estimate = int(hll.estimate())
   # real = len(unique)
    print(f'HLL estimation: {estimate}\nReal Counting:')


if __name__ == "__main__":
    main()






