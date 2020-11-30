#include <Difermion/DifermionProcessor.h>
#include <Utils/MC.h>

// Includes from iLCSoft
#include "streamlog/streamlog.h"

// Standard library
#include <cmath>

void DifermionProcessor::extract_observables(const EVENT::MCParticleVec &mcps) {
  /** Extract the relevant generator level observables.
   **/
  // Find the first after-collision fermion
  // (skip the initial e+e- and ISR -> skip 8)
  auto f = Utils::MC::find_first_fermion(mcps, 8);
  auto fbar = Utils::MC::find_anti_partner(*f);
  streamlog_out(DEBUG) << "Found f: " << Utils::MC::print(*f) << std::endl;
  streamlog_out(DEBUG) << "Found fbar: " << Utils::MC::print(*fbar)
                       << std::endl;

  // Save fermion PDG ID
  m_observables.f_pdg = std::abs(f->getPDG());

  // Extract observables in detector rest frame
  this->extract_lab_observables(*f, *fbar);

  // Extract observables in ee rest frame
  this->extract_ee_observables(*f, *fbar);
}