#ifndef LIB_WW_WWOBSERVABLES_H
#define LIB_WW_WWOBSERVABLES_H 1

namespace WW {
  
struct WWObservables {
  /** Helper struct to keep all the variables that will be connected with the TTree branches in the WW analysis.
   **/
  
  // Boost-independent observables
  bool decay_to_mu {};
  bool decay_to_tau {};
  int l_charge {};
  
  // Observables in the leptonic W rest frame
  // -> z axis should be along W flight direction
  double phi_l_star {};
  double costh_l_star {};
  
  // Observables in the WW rest frame
  // -> Detector coordinate system (expecting no significant x-y boost)
  double costh_Wminus_star {};
  
  // Observables in detector rest frame
  double costh_l {};
  
  void reset() {
    /** Reset all observables to their default value.
     **/
    decay_to_mu = false;
    decay_to_tau = false;
    l_charge = 0;
    phi_l_star = 9e9;
    costh_l_star = 9e9;
    costh_Wminus_star = 9e9;
    costh_l = 9e9;
  }
};
  
} // namespace WW

#endif