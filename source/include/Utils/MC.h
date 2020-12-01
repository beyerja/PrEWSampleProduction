#ifndef LIB_UTILS_MC_H
#define LIB_UTILS_MC_H 1

// Includes from ROOT
#include "TLorentzVector.h"

// Includes from iLCSoft
#include "lcio.h"
#include <EVENT/MCParticle.h>
#include <IMPL/MCParticleImpl.h>

// Standard library
#include <string>
#include <vector>

namespace Utils {
namespace MC {
/** LCIO helper functions related to MC particles.
 **/

// --- Observable related ------------------------------------------------------
TLorentzVector get_tlv(const EVENT::MCParticle &mcp);
bool fits_id(const EVENT::MCParticle &mcp, const std::vector<int> &pdg_ids);
bool is_type(const EVENT::MCParticle &mcp, const std::vector<int> &ids_plus,
             const std::vector<int> &ids_minus, int sign = 0);
bool is_e(const EVENT::MCParticle &mcp, int charge = 0);
bool is_mu(const EVENT::MCParticle &mcp, int charge = 0);
bool is_tau(const EVENT::MCParticle &mcp, int charge = 0);
bool is_nu_e(const EVENT::MCParticle &mcp, int sign = 0);
bool is_nu_mu(const EVENT::MCParticle &mcp, int sign = 0);
bool is_nu_tau(const EVENT::MCParticle &mcp, int sign = 0);
bool is_uptype(const EVENT::MCParticle &mcp, int sign = 0);
bool is_downtype(const EVENT::MCParticle &mcp, int sign = 0);
bool is_W_compatible(const EVENT::MCParticle &mcp1,
                     const EVENT::MCParticle &mcp2, int charge = 0);
// -----------------------------------------------------------------------------

// --- Vector related ----------------------------------------------------------
EVENT::MCParticle *find_first(const EVENT::MCParticleVec &vec,
                              std::vector<int> pdg_ids, int skip = 0,
                              int end = -1);
EVENT::MCParticle *find_first_fermion(const EVENT::MCParticleVec &vec,
                                      int skip = 0, int end = -1);
EVENT::MCParticle *find_first_lepton(const EVENT::MCParticleVec &vec,
                                     int skip = 0, int end = -1);
EVENT::MCParticle *find_first_W(const EVENT::MCParticleVec &vec,
                                int charge = 0);

EVENT::MCParticle *find_anti_partner(const EVENT::MCParticle &mcp);
// -----------------------------------------------------------------------------

// --- Elements according to ILD conventions -----------------------------------
IMPL::MCParticleImpl determine_W(const EVENT::MCParticleVec &vec, int charge);
EVENT::MCParticle *incoming_eM_after_ISR(const EVENT::MCParticleVec &vec);
EVENT::MCParticle *incoming_eP_after_ISR(const EVENT::MCParticleVec &vec);
// -----------------------------------------------------------------------------

// --- Create MCParticles ------------------------------------------------------
IMPL::MCParticleImpl create_W(const EVENT::MCParticle &mcp1,
                              const EVENT::MCParticle &mcp2);
// -----------------------------------------------------------------------------

// --- Print out related -------------------------------------------------------
std::string print(const EVENT::MCParticle &mcp);
// -----------------------------------------------------------------------------

} // namespace MC
} // namespace Utils

#endif