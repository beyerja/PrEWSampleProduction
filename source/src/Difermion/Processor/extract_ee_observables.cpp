#include <Difermion/DifermionProcessor.h>
#include <Utils/MC.h>

// includes from MarlinHelp
#include <MarlinHelp/ILD/Machine.h>

void DifermionProcessor::extract_ee_observables(const EVENT::MCParticle &f,
                                                const EVENT::MCParticle &fbar) {
  /** Extract the observables in the e+e- rest frame.
   **/
  // Lorentz vectors in lab frame
  auto f_tlv_lab = Utils::MC::get_tlv(f);
  auto fbar_tlv_lab = Utils::MC::get_tlv(fbar);

  // Lorentz vectors in e+e- frame (after removing crossing angle)
  auto f_tlv_ee = f_tlv_lab;
  auto fbar_tlv_ee = fbar_tlv_lab;
  if (m_unboost_xangle) {
    f_tlv_ee = MarlinHelp::ILD::Machine::unboost_crossing_angle(
        f_tlv_lab, m_header.m_energy);
    fbar_tlv_ee = MarlinHelp::ILD::Machine::unboost_crossing_angle(
        fbar_tlv_lab, m_header.m_energy);
  }
  auto ffbar_tlv_ee = f_tlv_ee + fbar_tlv_ee;

  // --- Find observables ------------------------------------------------------
  m_observables.costh_f_star = f_tlv_ee.CosTheta();
  m_observables.m_ff = ffbar_tlv_ee.M();
  // ---------------------------------------------------------------------------
}