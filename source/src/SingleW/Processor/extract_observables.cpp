#include <SingleW/SingleWProcessor.h>
#include <Utils/MC.h>

// Includes from iLCSoft
#include "streamlog/streamlog.h"

void SingleWProcessor::extract_observables(const EVENT::MCParticleVec &mcps) {
  /** Extract the relevant generator level observables.
   **/
  // Find the first after-collision lepton (should be e-/e+)
  // (skip the initial e+e- and ISR -> skip 8)
  auto e = Utils::MC::find_first_lepton(mcps, 8);
  streamlog_out(DEBUG) << "Found e: " << Utils::MC::print(*e) << std::endl;

  if (!Utils::MC::is_e(*e)) {
    throw std::domain_error("First found lepton isn't e, PDG: " +
                            std::to_string(e->getPDG()));
  }

  m_observables.e_charge = int(e->getCharge());
  if (Utils::MC::is_mu(*e))
    m_observables.decay_to_mu = true;
  if (Utils::MC::is_tau(*e))
    m_observables.decay_to_tau = true;

  // First try to see if W's are explicitely listed in MC list
  auto W_enu = Utils::MC::find_first_W(mcps, m_observables.e_charge);
  auto W_h = Utils::MC::find_first_W(mcps, -1 * m_observables.e_charge);

  // If W's weren't explicitely found, look for their decay products
  IMPL::MCParticleImpl W_enu_tech;
  if (W_enu == NULL) {
    W_enu_tech = Utils::MC::determine_W(mcps, m_observables.e_charge);
    W_enu = &W_enu_tech;
  }
  IMPL::MCParticleImpl W_h_tech;
  if (W_h == NULL) {
    W_h_tech = Utils::MC::determine_W(mcps, -1 * m_observables.e_charge);
    W_h = &W_h_tech;
  }

  streamlog_out(DEBUG) << "Found W_enu: " << Utils::MC::print(*W_enu)
                       << std::endl;
  streamlog_out(DEBUG) << "Found W_h: " << Utils::MC::print(*W_h) << std::endl;

  // Extract observables in detector rest frame
  this->extract_lab_observables(*e);

  // Extract observables in ee rest frame
  this->extract_ee_observables(*W_enu);

  // Extract lepton angles in W_lep system
  this->extract_Wl_observables(*W_enu, *e);
}