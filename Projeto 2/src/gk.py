import getopt
import sys
import csv
import time
import math
# import numpy as np


class Tuple():
    def __init__(self, val, g, delta):
        self.value  = val
        self.g = g
        self.delta = delta

    def __repr__(self):
        return 'Value: {} - ( g: {}, delta: {} )'.format(self.value, self.g, self.delta)

class GK():

    def __init__(self, eps = None):
        self.eps = eps
        self.entries = list()
        self._count = 0 
        self._min = 5000
        self._max = 0
        self._compress_threshold = int(1.0 / self.eps) + 1

    def __len__(self):
        return len(self.entries)
    
    def update(self, value):
        self._count += 1
        if not self.entries:
            self.entries.append(Tuple(value,1,0))
        else:
            self.entries = sorted(self.entries, key = lambda x: x.value)
            idx = 0
            for i, entry in enumerate(self.entries):
                if value < entry.value:
                    idx = i
                    break
            delta = 0
            #for first and last index - delta is  0
            
            delta = self.entries[idx].g + self.entries[idx].delta - 1
            # sanity check, if condition is true something went wrong. this should never happen
            if delta > int(math.floor(self.eps * float(self._count*2))): 
                print("Delta is greater than allowable error. This never should happen. Really.")
            xi = self.entries[idx]        
            if (xi.g + xi.delta + 1) < (2 * self.eps * self._count):
                self.entries[idx].g+=1
            else:
                self.entries.append(Tuple(value,1,delta))
                self.entries = sorted(self.entries, key = lambda x: x.value)
                self.compress()

            if value < self._min:
                self._min = value
            if value > self._max:
                self._max = value
        # if self._count % self._compress_threshold == 0:
        #     self.merge_compress()
                 
    def compress(self):
        remove_threshold = float(2.0 * self.eps * (self._count - 1))
        i = 0
        j = 1
        n_entries = len(self.entries) - 1
        while i < n_entries:
            xi = self.entries[i]
            xj = self.entries[j]
            if xi.g + xj.g + xj.delta <= remove_threshold:
                self.entries[j].g += self.entries[i].g
                self.entries.pop(i)
                break
            i+=1
            j+=1
        self.entries = sorted(self.entries, key = lambda x: x.value)
                                  
    def quantile(self, q):
        """Calculate quantile q."""
        if not (0 <= q <= 1):
            raise ValueError("q must be a value in [0, 1].")

        if self._count == 0:
            raise ValueError("GK sketch does not contain values.")

        rank = int(q * (self._count - 1) + 1)
        spread = int(self.eps * (self._count - 1))
        g_sum = 0.0
        i = 0

        n_entries = len(self.entries)
        while i < n_entries:
            g_sum += self.entries[i].g
            if g_sum + self.entries[i].delta > rank + spread:
                break
            i += 1
        if i == 0:
            return self._min
        return self.entries[i - 1].value

    def rank(self, value):
        g_sum = 0
        idx = 0
        for i, entry in enumerate(self.entries):
            if entry.value == value:
                idx = i
        if idx == 0:
            return self._max
        i = idx - 1
        j = 0
        while j <= i:
            g_sum+=self.entries[j].g
            j+=1 
        rank = g_sum - 1 + (self.entries[idx].g + self.entries[idx].delta)/2
        return rank

            
def main():
    test()
    # argv = sys.argv[1:]
    # val = str
    # eps = float
    # path = str
    # try:
    #     opts, args = getopt.gnu_getopt(argv,'v:e:d:fh',['val=','eps=','file=','help',])
    #     for opt, arg in opts:
    #         if opt in ('--v', '--val'):
    #             val = arg
    #         elif opt in ('--e', '--eps'):
    #             eps = float(arg)
    #         elif opt in ('--f','--file'):
    #             path = arg
    #         elif opt == 'help':
    #             help()
    # except getopt.GetoptError as e:
    #     print('Something went wrong! Use help to see acepted arguments')
    #     sys.exit(2)

        
    # print (val,eps)
    # gk = GK(eps)
    # with open(path) as csv_file:
    #     csv_reader = csv.reader(csv_file, delimiter=',')
    #     next(csv_reader)
    #     for row in csv_reader:
    #         print(row[val])
    #         gk.update(row[val])

    def test():
        eps = 0.2
        arr = [1, 4, 2, 8, 5, 7, 6, 7, 6, 7, 2, 1]
        test = list()
        gk = GK(eps)
        for i in arr:
            gk.update(i)
            test.append(i)
        for i in gk.entries:
            print(i)
        test = sorted(test)
        arr2 = [1,2,4,5,6,7,8]
        print(f'Total elements in Strem: {gk._count}, 2eN {len(gk.entries)}')
        for i in arr:
            rank = gk.rank(i)
            real_rank = test.index(i)
            error = abs(rank - real_rank)
            print(f'Query: {i} ,Rank: {gk.rank(i)}, Real_rank: {real_rank}, error: {error}')
            print("Real index:", test.index(i))

    
 
           
          
if __name__ == "__main__":
    main()



