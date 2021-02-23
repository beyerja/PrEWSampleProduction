#include <Difermion/DifermionProcessor.h>
#include <Utils/MC.h>

// includes from MarlinHelp
#include <MarlinHelp/Root/LorentzVec.h>

void DifermionProcessor::extract_ff_observables(const EVENT::MCParticle &f,
                                                const EVENT::MCParticle &fbar) {
  /** Extract the observables in the ffbar rest frame.
   **/
  // Lorentz vectors in lab frame
  auto f_tlv_lab = Utils::MC::get_tlv(f);
  auto fbar_tlv_lab = Utils::MC::get_tlv(fbar);

  auto ffbar_tlv_lab = f_tlv_lab + fbar_tlv_lab;
  
  // Lorentz vectors in ff frame
  auto f_tlv_ff =
      MarlinHelp::Root::LorentzVec::boost_tlv(f_tlv_lab, ffbar_tlv_lab);

  // --- Find observables ------------------------------------------------------
  m_observables.costh_f_star = f_tlv_ff.CosTheta();
  // ---------------------------------------------------------------------------
}