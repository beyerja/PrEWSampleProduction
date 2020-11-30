#include <Difermion/DifermionProcessor.h>
#include <Utils/MC.h>

void DifermionProcessor::extract_lab_observables(
    const EVENT::MCParticle &f, const EVENT::MCParticle &fbar) {
  /** Extract the observables in the lab/detector rest frame.
   **/
  auto f_tlv_lab = Utils::MC::get_tlv(f);
  auto fbar_tlv_lab = Utils::MC::get_tlv(fbar);
  
  // --- Find observables ------------------------------------------------------
  m_observables.costh_f = f_tlv_lab.CosTheta();
  m_observables.costh_fbar = fbar_tlv_lab.CosTheta();
  // ---------------------------------------------------------------------------
}