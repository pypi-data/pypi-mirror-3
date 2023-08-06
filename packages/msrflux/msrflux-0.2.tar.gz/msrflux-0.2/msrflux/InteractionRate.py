__author__ = 'tunnell'

from Constants import AVOGADROS_NUMBER

def CC(fluxes):
    xsec = {}
    xsec['nubar'] = 0.34 * 10 ** -42 # units of m^2
    xsec['nu'] = 0.67 * 10 ** -42     # units of m^2

    interactions = {}
    for flavor, value in fluxes.iteritems():
        for energy, flux in value.iteritems():
            for nu_or_nubar in ['nu', 'nubar']:
                key = (flavor, nu_or_nubar)
                if key not in interactions:
                    interactions[key] = 0.0

                my_int = 10 ** 9 * AVOGADROS_NUMBER * xsec[nu_or_nubar]
                my_int *= energy * flux

                interactions[key] += my_int

    return interactions


