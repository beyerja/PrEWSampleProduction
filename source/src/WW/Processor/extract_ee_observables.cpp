#include <Utils/MC.h>
#include <WW/WWProcessor.h>

// includes from MarlinHelp
#include <MarlinHelp/ILD/Machine.h>

void WWProcessor::extract_ee_observables(const EVENT::MCParticle &Wminus) {
  /** Extract the observables in the e+e- rest frame.
   **/
  // Lorentz vectors in lab frame
  auto Wminus_tlv_lab = Utils::MC::get_tlv(Wminus);

  // Lorentz vectors in e+e- frame (after removing crossing angle)
  auto Wminus_tlv_ee = MarlinHelp::ILD::Machine::unboost_crossing_angle(
      Wminus_tlv_lab, m_header.m_energy);

  // --- Find observables ------------------------------------------------------
  m_observables.costh_Wminus_star = Wminus_tlv_ee.CosTheta();
  // ---------------------------------------------------------------------------
}