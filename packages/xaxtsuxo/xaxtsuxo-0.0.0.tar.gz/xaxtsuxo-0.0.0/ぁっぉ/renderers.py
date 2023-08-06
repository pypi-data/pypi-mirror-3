from .words import branch, katsuo_words

def build_string_list(chain, ctx):
    retval = []
    for component in chain:
        if isinstance(component, branch):
            retval += build_string_list(component(ctx), ctx)
        else:
            retval += component(ctx)
    return retval

if __name__ == '__main__':
    from .words import markov_chains
    print(build_string_list(markov_chains, katsuo_words))
