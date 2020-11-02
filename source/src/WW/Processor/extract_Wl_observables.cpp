#include <Utils/MC.h>
#include <WW/WWProcessor.h>

// includes from MarlinHelp
#include <MarlinHelp/ILD/Machine.h>
#include <MarlinHelp/Root/LorentzVec.h>

void WWProcessor::extract_Wl_observables(const EVENT::MCParticle &Wl,
                                         const EVENT::MCParticle &l) {
  /** Extract the lepton observables in the leptonically decaying W system.
      Need angles in W rest frame and with z' axis along W_l flight direction:
      1. Boost into e+e- system after ISR
      2. Boost into W_l system
      3. Rotate to be along W_l axis
      4. Extract angles
   **/
  // Lorentz vectors in lab frame
  auto l_tlv_lab = Utils::MC::get_tlv(l);
  auto Wl_tlv_lab = Utils::MC::get_tlv(Wl);

  // Lorentz vectors in e+e- frame (after removing crossing angle)
  auto energy = m_header.m_energy;
  auto eM_tlv_ee = TLorentzVector(0, 0, energy, energy); // e- in z direction

  auto l_tlv_ee = l_tlv_lab;
  auto Wl_tlv_ee = Wl_tlv_lab;
  if (m_unboost_xangle) {
    l_tlv_ee =
        MarlinHelp::ILD::Machine::unboost_crossing_angle(l_tlv_lab, energy);
    Wl_tlv_ee =
        MarlinHelp::ILD::Machine::unboost_crossing_angle(Wl_tlv_lab, energy);
  }

  // Rotate to be along W flight direction (x in e-W plane, z along W flight)
  auto l_tlv_ee_rot =
      MarlinHelp::Root::LorentzVec::rotate_into(l_tlv_ee, Wl_tlv_ee, eM_tlv_ee);
  auto Wl_tlv_ee_rot = MarlinHelp::Root::LorentzVec::rotate_into(
      Wl_tlv_ee, Wl_tlv_ee, eM_tlv_ee);

  // Lorentz vectors in W_l system
  auto l_tlv_Wl_rot =
      MarlinHelp::Root::LorentzVec::boost_tlv(l_tlv_ee_rot, Wl_tlv_ee_rot);

  // --- Find observables ------------------------------------------------------
  m_observables.costh_l_star = l_tlv_Wl_rot.CosTheta();
  m_observables.phi_l_star = l_tlv_Wl_rot.Phi();
  // ---------------------------------------------------------------------------
}