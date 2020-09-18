#include <Utils/MC.h>
#include <WW/WWProcessor.h>

// includes from MarlinHelp
#include <MarlinHelp/Root/LorentzVec.h>

void WWProcessor::extract_lab_observables(const EVENT::MCParticle &l) {
  /** Extract the observables in the lab/detector rest frame.
   **/
  // Lorentz vectors in lab frame
  auto l_tlv_lab = Utils::MC::get_tlv(l);

  // --- Find observables ------------------------------------------------------
  m_observables.costh_l = l_tlv_lab.CosTheta();
  // ---------------------------------------------------------------------------
}