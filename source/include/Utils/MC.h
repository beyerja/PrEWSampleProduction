#ifndef LIB_UTILS_MC_H
#define LIB_UTILS_MC_H 1

// Includes from ROOT
#include "TLorentzVector.h"

// Includes from iLCSoft
#include "lcio.h"
#include <EVENT/MCParticle.h>

namespace Utils {
namespace MC {
/** LCIO helper functions related to MC particles.
 **/

TLorentzVector get_tlv(const lcio::MCParticle &mcp);

}
} // namespace Utils

#endif