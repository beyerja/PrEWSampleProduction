#ifndef LIB_SINGLEW_SINGLEWOBSERVABLES_H
#define LIB_SINGLEW_SINGLEWOBSERVABLES_H 1

namespace SingleW {

struct SingleWObservables {
  /** Helper struct to keep all the variables that will be connected with the
    *TTree branches in the SingleW analysis.
   **/

  // Boost-independent observables
  int e_charge{};

  // Observables in the (outgoing) electron-neutrino rest frame
  // -> z axis should be along combined flight direction
  double costh_e_star{};

  // Observables in the ee rest frame
  // -> Detector coordinate system (expecting no significant x-y boost)
  double costh_Whad_star{};
  double m_enu{};

  // Observables in detector rest frame

  void reset() {
    /** Reset all observables to their default value.
     **/
    e_charge = 0;
    costh_e_star = 9e9;
    costh_Whad_star = 9e9;
    m_enu = 9e9;
  }
};

} // namespace SingleW

#endif