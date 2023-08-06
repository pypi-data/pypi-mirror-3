import random, bisect
from math import exp, log1p, log

def get_weights(dataset, score, **kwargs):
    """Computes weights for all vertices and their potential parents"""
    weights = {}
    for node in dataset.vertices:
        # determine possible parents of the node
        parents = dataset.get_potential_parents(node)
        # compute parents' weights for this node
        pweights = parents_weights(dataset, score, node, parents, **kwargs)
        # add all weights to a dictionary
        for par, w in zip(parents, pweights):
            weights[node, par] = w
    return weights

def parents_weights(dataset, score, node, parents, **kwargs):
    """Weights for given dataset, score function, node and its parents."""
    thres, no_el = thresholds(dataset, score, node, parents, **kwargs)

    weights = [z_k - score.graph_score(len(parents),node,[],no_el,parents) for z_k in thres]
    if any(w < 0.0 for w in weights):
        # print "negative weights !"
        weights = [max(w, 0.0) for w in weights]
    return weights

def thresholds(dataset, score, X, Y, alpha=0.05):
    
    n_parents=len(Y)
    if n_parents < 1:
        return [], 0

    # Determine beta value and threshold values.
    beta = bonferroni_correction(alpha, n_parents)
    # changed from 1e-10 to 1e-5 because now no_tries depends on it
    beta = max(beta, 1e-5)

    no_tries = int(round(max(100, 1.0 / beta)))

    no_el, data = dataset.sel_data(X.index) 
    prs = [shuffled_distribution(data, score, X, Y_k, no_tries) for Y_k in Y]
    models = [cumulative(pr) for pr in prs]

    values = [cm_threshold(beta, model) for model in models]
    return values, no_el

def cm_threshold(beta, cm):
    """
    Return threshold z such that P(Z > z | H0) ~= beta holds.
    """
    xs, ys = zip(*cm)
    # negate values to get proper order
    k = bisect.bisect_left([-y for y in ys], -log(beta))
    if k < len(xs):
        # return (xs[k - 1] + xs[k]) / 2.0
        z = (log(beta) - ys[k - 1]) / (ys[k] - ys[k - 1])
        return xs[k - 1] + (xs[k] - xs[k - 1]) * z
    else:
        return xs[k - 1] + 0.1  # +0.1 is important here !


def bonferroni_correction(alpha, parents_num):
    return alpha / parents_num

# Waszczuk version
def cumulative(points):
    M_INF = float('-inf')

    def log_is_zero(x):
        return x == M_INF

    def log_add(x, y):
        if log_is_zero(x):
            return y
        if x > y:
            return x + log1p(exp(y - x))
        else:
            return y + log1p(exp(x - y))

    def logsum(w):
        """[log(w1), ..., log(wn)] -> log(w1 + ... + wn)"""
        return reduce(log_add, sorted(w), M_INF)

    def partial_sums(l, add, init):
        s = init
        r = []
        for x in l:
            s = add(s, x)
            r.append(s)
        return r

    # flatten
    points.sort()
    old = map(lambda x: (x, 0.0), points)
    points = []
    i = 0
    while i < len(old):
        part = []
        x = old[i][0]
        while i < len(old) and old[i][0] == x:
            part.append(old[i][1])
            i += 1
        points.append((x, logsum(part)))

    # rest
    X = map(lambda x: x[0], points)
    Y = map(lambda x: x[1], points)
    Y = reversed(Y)
    Y = partial_sums(Y, log_add, M_INF)
    maxy = Y[-1]
    Y = [y - maxy for y in Y]
    Y.reverse()
    return zip(X, Y)

def shuffle_data(data, ind, values):
    """Shuffles data from experiments for specified node index (shifted by no of variables)
    parameter data denotes a list of experiments data as in class experiment"""

    random.shuffle(values)

    for i, d in enumerate(data):
        d[ind] = values[i]

def shuffled_distribution(data, score, X, Y, no_tries):
    """Shuffles no_tries times X column and returns z_i values
    we assume, that data is just a copy and can be lost after this operation
    """
    # result distribution as a list of scores
    P = []
    # number of variables / genes
    var_no = len(data[0]) / 2 # due to dynamic/static networks stuff, data in experiments are kept in two copies

    empty_score = score.data_score(X, [], data)
    # compute list of values for variable X
    x_values = [d[X.index + var_no] for d in data]

    # pnum times shuffle X data and add score to the distribution
    for i in range(no_tries):
        shuffle_data(data, X.index + var_no, x_values)
        stat_value = empty_score - score.data_score(X, [Y], data)
        P.append(stat_value)

    return P
