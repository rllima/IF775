import getopt
import sys
import csv
import time
import math
import numpy as np


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
        self._min = np.inf
        self._max = -np.inf
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
                
            if value < self._min:
                self._min = value
            if value > self._max:
                self._max = value
            if self._count % self._compress_threshold == 0:
                    self.compress()
    

                 
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
        if not (0 <= q <= 1):
            raise ValueError("q must be a value in [0, 1].")

        if self._count == 0:
            raise ValueError("GK sketch does not contain values.")

        rank = int(q * (self._count))
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
        
        quantiles = np.arange(0, 1, 0.1).tolist()
        for quant in quantiles:
            print(f'Query quantile: {quant},result: { gk.quantile(quant)}')

    #test()
    argv = sys.argv[1:]
    val = 0
    eps = 0.0
    path = ""
    input_path = ""
    query_type = ""
    params = []
    gt = []
    try:
        opts, args = getopt.gnu_getopt(argv,'v:e:t:f:pih',['val=',"type=",'eps=','file=','params=','input=','help',])
        for opt, arg in opts:
            if opt in ('--v', '--val'):
                val = int(arg)
            elif opt in ('--e', '--eps'):
                eps = float(arg)
            elif opt in ('--t', '--type'):
                query_type = arg
            elif opt in ('--f','--file'):
                path = str(arg)
            elif opt in ('--p','--params'):
                params = str(arg).split(" ")
            elif opt in ('--i','--input'):
                input_path = str(arg)
            elif opt == 'help':
                help()
    except getopt.GetoptError as e:
        print('Something went wrong! Use help to see acepted arguments')
        sys.exit(2)

    gk = GK(eps)
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            gk.update(int(row[val]))
            gt.append(int(row[val]))
    print("Summary Read")
    for i in gk.entries[:100]:
        print(i)
    gt = sorted(gt)
    if params:
        for i in params:
            query = int(i)
            if query_type == "rank":
                if query in gt:
                    rank = gk.rank(query)
                    real_rank = gt.index(query)
                    error = abs(rank - real_rank)
                    print(f'Query: {i} ,Estimated_rank: {gk.rank(query)}, Real_rank: {real_rank}, error: {error}, Max erro: {gk.eps * gk._count}')
            elif query_type == "quant":
                print(f'Query quantile: {row},result: { gk.quantile(row)}')  
    print(input_path) 
    if input_path:
        with open(input_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                if query_type == "rank":
                    if i in gt:
                        rank = gk.rank(float(row))
                        real_rank = gt.index(float(row))
                        error = abs(rank - real_rank)
                        print(f'Query: {i} ,Estimated_rank: {gk.rank(float(row))}, Real_rank: {real_rank}, error: {error}')
                elif query_type == "quant":
                    print(f'Query quantile: {float(row)},result: { gk.quantile(float(row))}')   


    

                
    
 
    
if __name__ == "__main__":
    main()



