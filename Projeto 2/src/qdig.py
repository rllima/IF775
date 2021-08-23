import math
import csv
import sys
import argparse
import time


class Node:
    def __init__(self):
        self.w = 0
        self.child = [None, None]

    def tree_weight(self):
        rank = self.w
        for c in self.child:
            rank += c.tree_weight() if c else 0
        return rank

# e = erro permitido
# U = universo
# Certifica-se que o valor de (U,e) > (0,0)
# Aplica o log2(U) para facilitar calculo da capacidade
# Arredonda valor de U


class Q_digest:
    def __init__(self, e, U):
        assert(U > 0)
        assert(e > 0)
        self.root = Node()  # iniciado com valor 0 e sem filhos
        self.W = 0
        self.e = e
        self.log_u = math.ceil(math.log2(U))
        self.U = 2 ** int(self.log_u)

# Certifica-se que (x,w) >= (0,0) e x < U
# Soma w ao peso total
    def update(self, x, w):
        assert(x >= 0 and w >= 0 and x < self.U)
        self.W += w
        C = int((self.e*self.W)/self.log_u)
        v = self.root
        l, r = 0, self.U
        # enquanto w != 0 e ainda houver nodes para checar (nao chegou numa folha)
        while(w and (r - l) > 1):
            # peso disponivel para adicionar no node
            avail = C - v.w
            # peso que vai ser adicionado no node
            added = min(w, avail)
            v.w += added
            w -= added
            mid = (l+r)//2
            if x < mid:
                next_v = 0
                r = mid
            else:
                next_v = 1
                l = mid
            # ate aqui ele escolheu o lado da arvore para seguir
            # se o node nao existir, eh criado
            if not v.child[next_v]:
                v.child[next_v] = Node()
            # o v muda pra o seu filho e tudo se repete
            v = v.child[next_v]
        assert(w == 0 or (r-l) == 1)
        # se sobrou peso e ele chegou numa folha, adiciona tudo que restou na folha
        v.w += w

    def rank(self, x):
        if x < 0 or self.U <= x:
            return None
        v = self.root
        l, r = 0, self.U
        rank = 0
        # enquanto nao chega numa folha
        while(v and (r-l) > 1):
            mid = (l+r)//2
            if x < mid:
                r = mid
                v = v.child[0]
            else:
                # se estiver do lado direito da arvore soma no rank o peso de todos os nodes do lado esquerdo da arvore, se estiver do lado esquerdo nao soma nada ainda
                rank += v.child[0].tree_weight() if v.child[0] else 0
                v = v.child[1]
                l = mid
        return rank

    # recebe um rank e retorna o elemento do rank
    def rank_element(self, rank):
        v = self.root
        l, r = 0, self.U
        while v and (r-l) > 1:
            mid = (l+r)//2
            # se a soma dos pesos da esquerda for menor que o rank, vai pra a direita
            # se nao, vai pra a esquerda
            if v.child[0]:  # se existe filho à esquerda
                # peso da arvore do filho à esquerda
                u = v.child[0].tree_weight()
                if u < rank:
                    if v.child[1]:
                        v = v.child[1]
                        rank -= u  # diminui do rank o q já foi visto
                        l = mid
                    else:  # se u < rank mas n tiver filho na direita
                        return mid
                else:
                    v = v.child[0]
                    r = mid
            elif v.child[1]:  # se n existe nada à esquerda, só vai pra a direita e o resto continua igual
                v = v.child[1]
                l = mid
            else:
                return mid
        # end while
        return mid

    # definição da função quant:
    # Given a fraction q from [0, 1], the quantile query is about to find the value whose rank in a sorted sequence of the n values is q * n.

    def _compress(self, root, C, avail_up):
        assert(root)
        # peso que vai subir
        move_up = 0
        for i in range(2):
            child = root.child[i]
            if child:
                # quantidade disponivel no node raiz que pode ser pega de nodes abaixo
                avail_here = C - root.w
                new_child, move_up_from_child = self._compress(
                    child, C, avail_up + avail_here)
                # o filho pode ser o mesmo ou pode ter sido apagado, entao seria nulo
                root.child[i] = new_child
                # valor que sera colocado no node
                put_here = min(avail_here, move_up_from_child)
                root.w += put_here
                # valor que sera colocado no node acima desse, que eh o que sobrou
                move_up += (move_up_from_child - put_here)
        # move o peso disponivel no node para cima ou uma parte do peso
        move_up_from_here = min(avail_up, root.w)
        move_up += move_up_from_here
        root.w -= move_up_from_here

        if root.w == 0 and root.child[0] == None and root.child[1] == None:
            # se o peso do node for zero e ele for uma folha pode ser deletado
            return (None, move_up)
        else:
            # se o peso do node n for zero, ele continua sendo filho do pai dele
            return (root, move_up)

    def compress(self):
        C = int(self.e*self.W/self.log_u)
        self._compress(self.root, C, 0)

    # def _print(self, root, level, l, r):
    #     if root:
    #         mid = (l+r)//2
    #         self._print(root.child[0], level+1, l, mid)
    #         print("%s[range=(%d,%d) weight=%d]" % (level*"  ", l, r, root.w))
    #         self._print(root.child[1], level+1, mid, r)

    # def print_tree(self):
    #     print()
    #     print("-------------------------------")
    #     print("total_weight=%d" % (self.W))
    #     self._print(self.root, 0, 0, self.U)
    #     print("-------------------------------")


def main():

    inicio = time.time()
    # ---------------------- definição de variáveis INÍCIO ----------------------
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--val", required=True,
                    help="column number to be used to feed the sketch")
    ap.add_argument("-e", "--eps", required=True, help="error bound")
    ap.add_argument("-u", "--univ", nargs='*', required=True,
                    help="universe value + file_path + rank/quant decision + possible query.args")
    ap.add_argument("-i", "--in", required=False,
                    help="optional: file for query.args")
    args = vars(ap.parse_args())

    # se existe arquivo query.args e tem valores query.args antes dele
    if args['in'] and len(args['univ']) > 3:
        print("ERROR: if you're including an --in file, don't put any query.args before. Use -h/--help for more")
        sys.exit(2)

    if len(args['univ']) < 3:
        print("ERROR: missing values. Use -h/--help for more")
        sys.exit(2)

    # se n existe arquivo query.args e nem valores query.args
    if not args['in'] and len(args['univ']) == 3:
        print("ERROR: missing query.args. Use -h/--help for more")
        sys.exit(2)

    # se a decision n for rank ou quant
    if str(args['univ'][2]) not in ('rank', 'quant'):
        print("ERROR: invalid entry. Use -h/--help for more")
        sys.exit(2)

    # se o arquivo da tree n for .csv
    if str(args['univ'][1]).split('.')[-1] != 'csv':
        print("ERROR: invalid entry. Use -h/--help for more")
        sys.exit(2)

    # se o valor de univ n for um inteiro
    try:
        univ = int(args['univ'][0])
    except:
        print("ERROR: univ should be an integer. Use -h/--help for more")
        sys.exit(2)

    # se o valor de val n for um inteiro
    try:
        val = int(args['val'])
    except:
        print("ERROR: val should be an integer. Use -h/--help for more")
        sys.exit(2)

    # se o valor de eps n for um float
    try:
        eps = float(args['eps'])
    except:
        print("ERROR: eps should be a float number. Use -h/--help for more")
        sys.exit(2)

    # definição de variáveis de entrada
    val = int(args['val'])
    eps = float(args['eps'])
    univ = int(args['univ'][0])

    # se a decision for rank, os valores devem ser inteiros do universo separados por espaco
    if str(args['univ'][2]) == 'rank':
        if len(args['univ']) > 3:
            for i in range(len(args['univ'])):
                if i > 2:
                    try:
                        aux = int(args['univ'][i])
                    except:
                        print("ERROR: query.args has invalid input.")
                        sys.exit(2)
    # se for quant, os valores devem ser numeros decimais entre 0 e 1 separados por espaço
    else:
        if len(args['univ']) > 3:
            for i in range(len(args['univ'])):
                if i > 2:
                    try:
                        aux = float(args['univ'][i])
                    except:
                        print("ERROR: query.args has invalid input.")
                        sys.exit(2)

    # ---------------------- definição de variáveis FIM ----------------------

    sketch = Q_digest(eps, univ)
    w = 1

    # ---------------------- UPDATE ----------------------
    with open(str(args['univ'][1])) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            x = int(row[val])
            if x < univ:
                sketch.update(x, w)
    # ---------------------- UPDATE FIM ----------------------

    sketch.compress()

    # se o tamanho do vetor univ for maior que 3 quer dizer que tem query.args
    # ent preciso usar esses args para fazer as queries
    # eu sei que se o arquivo in existe, o vetor univ tem tamanho 3

    # ---------------------- QUERIES ----------------------
    # tratando primeiro o caso de existir arquivo in
    if args['in']:
        with open(str(args['in'])) as f:
            contents = f.readlines()
            for content in contents:
                if (str(args['univ'][2]) == 'rank'):
                    x = int(content)
                    if x >= 0 and x < univ:
                        rank = sketch.rank(x)
                        print(rank)
                        # print("x original = ", x)
                        # rankx = sketch.rank_element(rank)
                        # print("x = ", rankx)
                    else:
                        print("ERROR: query.args file has invalid values.")
                        sys.exit(2)
                else:
                    q = float(content)
                    # print("q = ", q)
                    # print("q*total_weight = ", q*sketch.W)
                    if q < 0 or q > 1:
                        print("ERROR: query.args file has invalid values.")
                        sys.exit(2)
                    rank_q = int(q*sketch.W)
                    rank_x = sketch.rank_element(rank_q)
                    print(rank_x)
            # end for

    else:  # query.args sem arquivo in
        for i in range(len(args['univ'])):
            if i > 2:
                if (str(args['univ'][2]) == 'rank'):
                    x = int(args['univ'][i])
                    if x >= 0 and x < univ:
                        rank = sketch.rank(x)
                        print(rank)
                        # rankx = sketch.rank_element(rank)
                        # print("x = ", rankx)
                    else:
                        print("ERROR: query.args has invalid input.")
                        sys.exit(2)
                else:
                    q = float(args['univ'][i])
                    if q < 0 or q > 1:
                        print("ERROR: query.args has invalid input.")
                        sys.exit(2)
                    rank_q = int(q*sketch.W)
                    rank_x = sketch.rank_element(rank_q)
                    print(rank_x)
            # end if
        # end for

    fim = time.time()
    #print("tempo = ", fim - inicio)
    # ---------------------- QUERIES FIM ----------------------


if __name__ == "__main__":
    main()
