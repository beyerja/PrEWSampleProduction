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
  auto f1 = Utils::MC::find_first_fermion(mcps, 8);
  auto f2 = Utils::MC::find_anti_partner(*f1);
  streamlog_out(DEBUG) << "Found f1: " << Utils::MC::print(*f1) << std::endl;
  streamlog_out(DEBUG) << "Found f2: " << Utils::MC::print(*f2) << std::endl;

  // Assign which one is a fermion and which an anti-fermion
  auto f = f1;
  auto fbar = f2;
  if (f1->getPDG() < 0) {
    streamlog_out(DEBUG) << "f1 is anti-fermion and f2 is fermion" << std::endl;
    f = f2;
    fbar = f1;
  } else {
    streamlog_out(DEBUG) << "f1 is fermion and f2 is anti-fermion" << std::endl;
  }

  // Save fermion PDG ID
  m_observables.f_pdg = std::abs(f->getPDG());

  // Extract observables in detector rest frame
  this->extract_lab_observables(*f, *fbar);

  // Extract observables in ffbar rest frame
  this->extract_ff_observables(*f, *fbar);

  // --- Observables using truth level information that can't be reconstructed
  auto eM_after_ISR = Utils::MC::incoming_eM_after_ISR(mcps);
  auto eP_after_ISR = Utils::MC::incoming_eP_after_ISR(mcps);
  this->extract_ff_true_observables(*f, *fbar, *eM_after_ISR, *eP_after_ISR);
}