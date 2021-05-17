#include <Difermion/DifermionProcessor.h>
#include <Utils/MC.h>

// includes from MarlinHelp
#include <MarlinHelp/Root/LorentzVec.h>

void DifermionProcessor::extract_ff_true_observables(
    const EVENT::MCParticle &f, const EVENT::MCParticle &fbar,
    const EVENT::MCParticle &eM_after_ISR,
    const EVENT::MCParticle & /*eP_after_ISR*/) {
  /** Extract the observables in the cheated ffbar frame where it is assumed
   *that ISR of both e+ and e- are exactly known.
   **/
  // Lorentz vectors in lab frame
  auto f_tlv_lab = Utils::MC::get_tlv(f);
  auto fbar_tlv_lab = Utils::MC::get_tlv(fbar);
  auto eM_ISR_tlv_lab = Utils::MC::get_tlv(eM_after_ISR);
  // auto eP_ISR_tlv_lab = Utils::MC::get_tlv(eP_after_ISR);

  auto ffbar_tlv_lab = f_tlv_lab + fbar_tlv_lab;

  // Boost into ff frame
  auto f_tlv_ff =
      MarlinHelp::Root::LorentzVec::boost_tlv(f_tlv_lab, ffbar_tlv_lab);
  auto eM_ISR_tlv_ff =
      MarlinHelp::Root::LorentzVec::boost_tlv(eM_ISR_tlv_lab, ffbar_tlv_lab);

  // --- Find observables ------------------------------------------------------
  m_observables.costh_f_star_true =
      MarlinHelp::Root::LorentzVec::cos_theta(f_tlv_ff, eM_ISR_tlv_ff);
  // ---------------------------------------------------------------------------
}