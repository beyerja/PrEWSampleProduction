#include <SingleW/SingleWProcessor.h>
#include <Utils/MC.h>

// includes from MarlinHelp
#include <MarlinHelp/ILD/Machine.h>

void SingleWProcessor::extract_ee_observables(const EVENT::MCParticle &W_enu,
                                              const EVENT::MCParticle &W_h) {
  /** Extract the observables in the e+e- rest frame.
   **/
  // Lorentz vectors in lab frame
  auto enu_tlv_lab = Utils::MC::get_tlv(W_enu);
  auto Wh_tlv_lab = Utils::MC::get_tlv(W_h);

  // Lorentz vectors in e+e- frame (after removing crossing angle)
  auto enu_tlv_ee = enu_tlv_lab;
  auto Wh_tlv_ee = Wh_tlv_lab;
  if (m_unboost_xangle) {
    enu_tlv_ee = MarlinHelp::ILD::Machine::unboost_crossing_angle(
        enu_tlv_lab, m_header.m_energy);
    Wh_tlv_ee = MarlinHelp::ILD::Machine::unboost_crossing_angle(
        Wh_tlv_lab, m_header.m_energy);
  }

  // --- Find observables ------------------------------------------------------
  m_observables.costh_Whad_star = Wh_tlv_ee.CosTheta();
  m_observables.m_enu = enu_tlv_ee.M();
  // ---------------------------------------------------------------------------
}