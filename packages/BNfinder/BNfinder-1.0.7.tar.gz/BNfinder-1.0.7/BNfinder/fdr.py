from math import log

def get_weights(dataset, score, alpha=0.05):
    """Computes weights for all vertices and their potential parents"""
    weights = {}
    for node in dataset.vertices:
        selected_data = dataset.select_1(node)
        parents = selected_data.parents
        n_parents = len(parents)
        n_data = len(selected_data)
        
        if n_parents:

            # Determine beta value and threshold values.
            beta = alpha / n_parents
            # changed from 1e-10 to 1e-5 because now no_tries depends on it
            beta = max(beta, 1e-5)
            no_tries = int(round(max(100, log(2+n_parents) / beta)))
            
            selected_data_empty = selected_data.subset()
            empty_score = score.data_score(selected_data_empty) + score.graph_score(n_parents,node,[],n_data,[])
            sample_scores = [[score.lower_bound_for_data_score(selected_data_empty)]*n_parents]
            
            # no_tries times shuffle vertex data and add scores to the distributions
            perm_data = selected_data.subset(selected_data.parents) # create a copy
            for i in range(no_tries):
                perm_data.permute()
                sample_scores.append([score.data_score(perm_data.subset([par]))  for par in perm_data.parents])
            distributions = [sorted(scores) for scores in zip(*sample_scores)]
            
            # compute data_score thresholds
            thr_ind = beta*no_tries
            a,b = divmod(thr_ind,1)
            ds_thrs = [(1-b)*scores[int(round(a))] + b*scores[int(round(a))+1] for scores in distributions]

            # compute required parents' graph_scores
            g_scores = [max(0, empty_score - thr)   for thr in ds_thrs]
            
            #compute parents' weights
            pweights = []
            for g in g_scores:
                r = 2
                while score.graph_score(n_parents,node,[r],n_data,[]) < g:
                    r*=2
                l=r/2.
                while r-l>1e-3:
                    w=(l+r)/2
                    if score.graph_score(n_parents,node,[w],n_data,[]) < g:
                        l=w
                    else:
                        r=w
                pweights.append(w)
        
            # add all weights to a dictionary
            for par, w in zip(selected_data.parents, pweights):
                weights[(node.name, par.name)] = w
    return weights

