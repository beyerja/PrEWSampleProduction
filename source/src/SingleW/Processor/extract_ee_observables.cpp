#include <Utils/MC.h>
#include <SingleW/SingleWProcessor.h>

// includes from MarlinHelp
#include <MarlinHelp/ILD/Machine.h>

void SingleWProcessor::extract_ee_observables(const EVENT::MCParticle &W_enu) {
  /** Extract the observables in the e+e- rest frame.
   **/
  // Lorentz vectors in lab frame
  auto enu_tlv_lab = Utils::MC::get_tlv(W_enu);

  // Lorentz vectors in e+e- frame (after removing crossing angle)
  auto enu_tlv_ee = enu_tlv_lab;
  if (m_unboost_xangle) {
    enu_tlv_ee = MarlinHelp::ILD::Machine::unboost_crossing_angle(
        enu_tlv_lab, m_header.m_energy);
  }

  // --- Find observables ------------------------------------------------------
  m_observables.m_enu = enu_tlv_ee.M();
  // ---------------------------------------------------------------------------
}