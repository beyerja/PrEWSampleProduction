#ifndef LIB_DIFERMION_DIFERMIONOBSERVABLES_H
#define LIB_DIFERMION_DIFERMIONOBSERVABLES_H 1

namespace Difermion {

struct DifermionObservables {
  /** Helper struct to keep all the variables that will be connected with the
    *TTree branches in the Difermion analysis.
   **/

  // Boost-independent observables
  int f_pdg{};

  // Observables in the ee rest frame
  // -> Detector coordinate system (expecting no significant x-y boost)
  double costh_f_star{};
  double m_ff{};

  // Observables in detector rest frame
  double costh_f{};
  double costh_fbar{};

  void reset() {
    /** Reset all observables to their default value.
     **/
    f_pdg = 0;
    costh_f_star = 9e9;
    m_ff = 9e9;
    costh_f = 9e9;
    costh_fbar = 9e9;
  }
};

} // namespace Difermion

#endif