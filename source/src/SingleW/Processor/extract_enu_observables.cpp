#include <SingleW/SingleWProcessor.h>
#include <Utils/MC.h>

// includes from MarlinHelp
#include <MarlinHelp/ILD/Machine.h>
#include <MarlinHelp/Root/LorentzVec.h>

void SingleWProcessor::extract_enu_observables(const EVENT::MCParticle &W_enu,
                                               const EVENT::MCParticle &e) {
  /** Extract the electron observables in the e-nu system.
      Need angles in e-nu rest frame and with z' axis along e-nu combined flight
      direction:
      1. Boost into e+e- system after ISR
      2. Rotate to be along enu axis
      3. Boost into enu system
      4. Extract angles
   **/
  // Lorentz vectors in lab frame
  auto e_tlv_lab = Utils::MC::get_tlv(e);
  auto enu_tlv_lab = Utils::MC::get_tlv(W_enu);

  // Lorentz vectors in e+e- frame (after removing crossing angle)
  auto energy = m_header.m_energy;
  auto eM_tlv_ee = TLorentzVector(0, 0, energy, energy); // e- in z direction

  auto e_tlv_ee = e_tlv_lab;
  auto enu_tlv_ee = enu_tlv_lab;
  if (m_unboost_xangle) {
    e_tlv_ee =
        MarlinHelp::ILD::Machine::unboost_crossing_angle(e_tlv_lab, energy);
    enu_tlv_ee =
        MarlinHelp::ILD::Machine::unboost_crossing_angle(enu_tlv_lab, energy);
  }

  // Rotate to be along e-nu flight direction (x in initial e- - e-nu plane,
  // z along e-nu flight)
  auto e_tlv_ee_rot = MarlinHelp::Root::LorentzVec::rotate_into(
      e_tlv_ee, enu_tlv_ee, eM_tlv_ee);
  auto enu_tlv_ee_rot = MarlinHelp::Root::LorentzVec::rotate_into(
      enu_tlv_ee, enu_tlv_ee, eM_tlv_ee);

  // Lorentz vectors in e-nu system
  auto e_tlv_enu_rot =
      MarlinHelp::Root::LorentzVec::boost_tlv(e_tlv_ee_rot, enu_tlv_ee_rot);

  // --- Find observables ------------------------------------------------------
  m_observables.costh_e_star = e_tlv_enu_rot.CosTheta();
  // ---------------------------------------------------------------------------
}