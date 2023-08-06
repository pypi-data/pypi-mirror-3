__author__ = 'tunnell'


def print_to_screen(results):
    for E, l, angle in results:
        print 'E_mu: %g GeV\tL: %g km\tangle:%g rad' % (E, l, angle)


def create_plot(name, results, use_matplotlib=True):
    """Create plot with matplotlib"""

    try:
        import matplotlib.pyplot as plt
    except:
        print "Can't find matplotlib.  Just creating flux output."
        use_matplotlib = False

    for key in results.keys():
        plt.figure()
        par = results[key]

        x = []
        y = []
        for key2, val in par.iteritems():
            x.append(key2)
            y.append(val)

        if use_matplotlib:
            plt.plot(x, y, 'ro')
            plt.xlabel("Neutrino energy [GeV]")
            plt.ylabel(r'Flux /(m${}^2$ 100 MeV)')

            plt.savefig('avg_%s_%s.eps' % (name, key))

        x.sort()

        file_obj = open('raw_%s_%s' % (name, key), 'w')
        for sorted_x in x:
            file_obj.write('%f %f\n' % (sorted_x, par[sorted_x]))
        file_obj.close()
