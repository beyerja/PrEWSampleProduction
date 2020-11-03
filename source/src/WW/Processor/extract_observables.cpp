#include <Utils/MC.h>
#include <WW/WWProcessor.h>

// Includes from iLCSoft
#include "streamlog/streamlog.h"

void WWProcessor::extract_observables(const EVENT::MCParticleVec &mcps) {
  /** Extract the relevant generator level observables.
   **/
  // Find the first lepton (skip the initial e+e- and ISR -> skip 8)
  auto l = Utils::MC::find_first_lepton(mcps, 8);
  streamlog_out(DEBUG) << "Found l: " << Utils::MC::print(*l) << std::endl; 

  m_observables.l_charge = int(l->getCharge());
  if (Utils::MC::is_mu(*l))
    m_observables.decay_to_mu = true;
  if (Utils::MC::is_tau(*l))
    m_observables.decay_to_tau = true;

  // First try to see if W's are explicitely listed in MC list
  auto W_l = Utils::MC::find_first_W(mcps, m_observables.l_charge);
  auto W_h = Utils::MC::find_first_W(mcps, -1 * m_observables.l_charge);

  // If W's weren't explicitely found, look for their decay products
  IMPL::MCParticleImpl W_l_tech;
  if (W_l == NULL) {
    W_l_tech = Utils::MC::determine_W(mcps, m_observables.l_charge);
    W_l = &W_l_tech;
  }
  IMPL::MCParticleImpl W_h_tech;
  if (W_h == NULL) {
    W_h_tech = Utils::MC::determine_W(mcps, -1 * m_observables.l_charge);
    W_h = &W_h_tech;
  }

  streamlog_out(DEBUG) << "Found W_l: " << Utils::MC::print(*W_l) << std::endl; 
  streamlog_out(DEBUG) << "Found W_h: " << Utils::MC::print(*W_h) << std::endl; 

  // Which one is W+, which one W-?
  auto Wplus = W_l;
  auto Wminus = W_h;
  if (m_observables.l_charge == -1) {
    Wplus = W_h;
    Wminus = W_l;
  }

  // Extract observables in detector rest frame
  this->extract_lab_observables(*l);

  // Extract observables in ee rest frame
  this->extract_ee_observables(*Wminus);

  // Extract lepton angles in W_lep system
  this->extract_Wl_observables(*W_l, *l);
}