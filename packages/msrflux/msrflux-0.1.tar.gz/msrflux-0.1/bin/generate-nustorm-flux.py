"""Compute nustorm neutrino fluxes"""

__author__ = 'tunnell'

from msrflux.Sampler import Sampler
from msrflux.Output import print_to_screen, create_plot
from msrflux.DecayKinematics import compute_neutrino_flux

#  Do we want fluxes at the near detector rather than the far detector?
is_near_detector = True

#  What is the mean stored muon energy in the decay ring?
energy_muon = 3.8  # GeV

#  Set the baseline between the accelerator and detector.
baseline = 2.0  # km
if is_near_detector:
    baseline = 0.1 # km

#  Sampler performs the MC integration by sampling points in the detector and
#  accelerator volumes.
x = Sampler(energy_muon, baseline)

###########################
##  OPTIONAL SET METHODS ##
###########################

# Smear the stored muon energy by 10% uniform spread
#x.set_accelerator_energy(spread=0.1*energy_muon) # GeV

#  Integrate over the detector volume

x.set_detector(radius=2.5, # m
    mass=1.0, # kt
    density=1.4)  # g/cm^3

#  Integrate over the detector straight
x.set_accelerator_length(0.15) # km

#  Set the Twiss parameters (ie. accelerator optics)
x.set_accelerator_twiss(emittance=2.1e-06,
    beta=0.04) # km, km

#  Sample N points
results = x.sample(N=100)

# Print to screen
print_to_screen(results)

# Compute the fluxes
results = compute_neutrino_flux(results, N_mu=1.8e18) # 1/m2

#  Create plots and flux files
if is_near_detector:
    create_plot('nustorm_near', results)
else:
    create_plot('nustorm', results)
