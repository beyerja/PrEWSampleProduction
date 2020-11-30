#include <Utils/MC.h>

// Includes from iLCSoft
#include "streamlog/streamlog.h"

// Standard library
#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <string>

namespace Utils {

//------------------------------------------------------------------------------

TLorentzVector MC::get_tlv(const lcio::MCParticle &mcp) {
  /** Return the four-momentum of the MC particle as a TLorentzVector.
   **/
  return TLorentzVector(mcp.getMomentum(), mcp.getEnergy());
}

//------------------------------------------------------------------------------

bool MC::fits_id(const EVENT::MCParticle &mcp,
                 const std::vector<int> &pdg_ids) {
  /** Check if the particle fits any of the given IDs;
   **/
  auto mcp_id = mcp.getPDG();
  bool fits = false;
  for (int id : pdg_ids) {
    if (mcp_id == id) {
      fits = true;
      break;
    }
  }
  return fits;
}

//------------------------------------------------------------------------------

bool MC::is_type(const EVENT::MCParticle &mcp, const std::vector<int> &ids_plus,
                 const std::vector<int> &ids_minus, int sign) {
  /** Check if the given particle is of a type.
      The type has a plus and a minus sign option (sign can be charge or
   particle/antiparticle). If sign not specified than either one is checked.
   **/
  std::vector<int> ids{};
  if ((sign == 0) || (sign == 1)) {
    ids.insert(ids.end(), ids_plus.begin(), ids_plus.end());
  }
  if ((sign == 0) || (sign == -1)) {
    ids.insert(ids.end(), ids_minus.begin(), ids_minus.end());
  }
  if ((sign != 0) && (std::abs(sign) != 1)) {
    throw std::invalid_argument("Looking for invalid sign: " +
                                std::to_string(sign));
  }

  return MC::fits_id(mcp, ids);
}

//------------------------------------------------------------------------------

bool MC::is_e(const EVENT::MCParticle &mcp, int charge) {
  /** Check if the particle is an electron/positron.
      Charge can be specified, if not (0) either is considered.
   **/
  return MC::is_type(mcp, {-11}, {11}, charge);
}
bool MC::is_mu(const EVENT::MCParticle &mcp, int charge) {
  /** Check if the particle is a muon/anti-muon.
      Charge can be specified, if not (0) either is considered.
   **/
  return MC::is_type(mcp, {-13}, {13}, charge);
}
bool MC::is_tau(const EVENT::MCParticle &mcp, int charge) {
  /** Check if the particle is a tau/anti-tau.
      Charge can be specified, if not (0) either is considered.
   **/
  return MC::is_type(mcp, {-15}, {15}, charge);
}

//------------------------------------------------------------------------------

bool MC::is_nu_e(const EVENT::MCParticle &mcp, int sign) {
  /** Check if the particle is an electron/positron.
      Sign can be specified, if not (0) either is considered.
      Sign: +1 particle, -1 antiparticle (NOTE: opposite to charge leptons!)
   **/
  return MC::is_type(mcp, {12}, {-12}, sign);
}
bool MC::is_nu_mu(const EVENT::MCParticle &mcp, int sign) {
  /** Check if the particle is a muon/anti-muon.
      Sign can be specified, if not (0) either is considered.
      Sign: +1 particle, -1 antiparticle (NOTE: opposite to charge leptons!)
   **/
  return MC::is_type(mcp, {14}, {-14}, sign);
}
bool MC::is_nu_tau(const EVENT::MCParticle &mcp, int sign) {
  /** Check if the particle is a tau/anti-tau.
      Sign can be specified, if not (0) either is considered.
      Sign: +1 particle, -1 antiparticle (NOTE: opposite to charge leptons!)
   **/
  return MC::is_type(mcp, {16}, {-16}, sign);
}

//------------------------------------------------------------------------------

bool MC::is_uptype(const EVENT::MCParticle &mcp, int sign) {
  /** Check if the quark is uptype.
      If sign given, then quark (+1) or antiquark (-1) is searched for.
   **/
  return MC::is_type(mcp, {2, 4, 6}, {-2, -4, -6}, sign);
}

bool MC::is_downtype(const EVENT::MCParticle &mcp, int sign) {
  /** Check if the quark is downtype.
      If sign given, then quark (+1) or antiquark (-1) is searched for.
   **/
  return MC::is_type(mcp, {1, 3, 5}, {-1, -3, -5}, sign);
}

//------------------------------------------------------------------------------

bool MC::is_W_compatible(const EVENT::MCParticle &mcp1,
                         const EVENT::MCParticle &mcp2, int charge) {
  /** Check if the two given MC particles are potentially decay products of a
   charged W. The charge of the W can be given, if set to 0 the charge won't be
   checked.
   **/
  bool fits = false;

  if (mcp1.getPDG() * mcp2.getPDG() > 0) {
    // Not a particle antiparticle pair, definitely not a W
    streamlog_out(DEBUG) << "Pair not charge compatible with W." << std::endl;
    fits = false;
  } else if (charge == 1) {
    fits =
        // Is it qqbar?
        (MC::is_uptype(mcp1, +1) && MC::is_downtype(mcp2, -1)) ||
        (MC::is_uptype(mcp2, +1) && MC::is_downtype(mcp1, -1)) ||
        // Is it l-nu pair?
        (MC::is_e(mcp1, +1) && MC::is_nu_e(mcp2, +1)) ||
        (MC::is_e(mcp2, +1) && MC::is_nu_e(mcp1, +1)) ||
        (MC::is_mu(mcp1, +1) && MC::is_nu_mu(mcp2, +1)) ||
        (MC::is_mu(mcp2, +1) && MC::is_nu_mu(mcp1, +1)) ||
        (MC::is_tau(mcp1, +1) && MC::is_nu_tau(mcp2, +1)) ||
        (MC::is_tau(mcp2, +1) && MC::is_nu_tau(mcp1, +1));
    if (!fits) {
      streamlog_out(DEBUG) << "Pair not W+ compatible." << std::endl;
    } else {
      streamlog_out(DEBUG) << "Pair W+ compatible." << std::endl;
    }
  } else if (charge == -1) {
    fits =
        // Is it qqbar?
        (MC::is_uptype(mcp1, -1) && MC::is_downtype(mcp2, +1)) ||
        (MC::is_uptype(mcp2, -1) && MC::is_downtype(mcp1, +1)) ||
        // Is it l-nu pair?
        (MC::is_e(mcp1, -1) && MC::is_nu_e(mcp2, -1)) ||
        (MC::is_e(mcp2, -1) && MC::is_nu_e(mcp1, -1)) ||
        (MC::is_mu(mcp1, -1) && MC::is_nu_mu(mcp2, -1)) ||
        (MC::is_mu(mcp2, -1) && MC::is_nu_mu(mcp1, -1)) ||
        (MC::is_tau(mcp1, -1) && MC::is_nu_tau(mcp2, -1)) ||
        (MC::is_tau(mcp2, -1) && MC::is_nu_tau(mcp1, -1));
    if (!fits) {
      streamlog_out(DEBUG) << "Pair not W- compatible." << std::endl;
    } else {
      streamlog_out(DEBUG) << "Pair W- compatible." << std::endl;
    }
  } else if (charge == 0) {
    // Look for either one
    fits = MC::is_W_compatible(mcp1, mcp2, 1) ||
           MC::is_W_compatible(mcp1, mcp2, -1);
  } else {
    throw std::invalid_argument("Unknown W charge: " + std::to_string(charge));
  }

  return fits;
}

//------------------------------------------------------------------------------

EVENT::MCParticle *MC::find_first(const EVENT::MCParticleVec &vec,
                                  std::vector<int> pdg_ids, int skip, int end) {
  /** Return the first particle in the vector that fits any of the given IDs.
      Optional:
       - Skip the first N elements of the vector (e.g. to skip initial
   particles).
       - End search at given particle (give index!, -1 means whole vector)
   **/

  // Lambda that checks if any ID fits for a given particle
  auto id_lambda = [pdg_ids](EVENT::MCParticle *mcp) {
    return fits_id(*mcp, pdg_ids);
  };

  // Check that we're not skipping past the last vector element
  int n_mcps = int(vec.size());
  if (skip >= n_mcps) {
    throw std::out_of_range("Trying to skip past vector end.");
  }

  // Check if given end point is valid
  if (!((end == -1) || ((end > skip) && (end < n_mcps)))) {
    throw std::out_of_range("Invalid end point " + std::to_string(end));
  }

  // Choose a valid endpoint for search
  auto end_ptr = std::end(vec);
  if (end != -1) {
    end_ptr = std::begin(vec) + end + 1;
  }

  // Try to find the first element
  auto iterator = std::find_if(std::begin(vec) + skip, end_ptr, id_lambda);

  // If element not in vector return a null pointer
  if (iterator == end_ptr) {
    streamlog_out(DEBUG) << "Couldn't find any fitting particle in MC vector: ";
    for (int id : pdg_ids)
      streamlog_out(DEBUG) << std::to_string(id) << " ";
    streamlog_out(DEBUG) << std::endl;
    return NULL;
  }

  return *iterator;
}

//------------------------------------------------------------------------------

EVENT::MCParticle *MC::find_first_fermion(const EVENT::MCParticleVec &vec,
                                      int skip, int end) {
  /** Return the first fermion (not specified if f or fbar) in the vector that
      fits any of the given IDs. Optional:
       - Skip the first N elements of the vector (e.g. to skip initial
         particles).
       - End search at given particle (-1 means whole vector)
   **/
  std::vector<int> fermion_ids{};
  for (int i = 1; i < 17; i++) {
    fermion_ids.push_back(i);
    fermion_ids.push_back(-i);
  }
  return MC::find_first(vec, fermion_ids, skip, end);
}

//------------------------------------------------------------------------------

EVENT::MCParticle *MC::find_first_lepton(const EVENT::MCParticleVec &vec,
                                         int skip, int end) {
  /** Return the first lepton in the vector that fits any of the given IDs.
      Optional:
       - Skip the first N elements of the vector (e.g. to skip initial
   particles).
       - End search at given particle (-1 means whole vector)
   **/
  auto lepton_ids = {11, -11, 13, -13, 15, -15};
  return MC::find_first(vec, lepton_ids, skip, end);
}

//------------------------------------------------------------------------------

EVENT::MCParticle *MC::find_first_W(const EVENT::MCParticleVec &vec,
                                    int charge) {
  /** Return the first W in the vector. If charge not specified (0) the first is
   *given independent of charge.
   **/
  std::vector<int> ids{};

  // Which W are we looking for
  if (charge == 0) {
    ids = {24, -24};
  } else if (charge == 1) {
    ids = {24};
  } else if (charge == -1) {
    ids = {-24};
  } else {
    throw std::invalid_argument("Looking for invalid W charge: " +
                                std::to_string(charge));
  }

  return MC::find_first(vec, ids);
}

//------------------------------------------------------------------------------

EVENT::MCParticle *MC::find_anti_partner(const EVENT::MCParticle &mcp) {
  /** Find the anti-partner (same parent, opposite sign PDG) to the given
   * particle.
   **/
  return MC::find_first(mcp.getParents().at(0)->getDaughters(),
                        {-1 * mcp.getPDG()});
}

//------------------------------------------------------------------------------

IMPL::MCParticleImpl MC::determine_W(const EVENT::MCParticleVec &vec,
                                     int charge) {
  /** Determine the W of the given charge (in a semileptonic 4-fermion process)
   using the ILD convention for the MCParticle list:
        - Look for qq pair or lnu pair that works with W hypothesis
   **/
  // First check if a valid charge is given
  if (std::abs(charge) != 1) {
    throw std::invalid_argument("Invalid W charge: " + std::to_string(charge));
  }

  // look for q/qbar pair or l/nu pair (should be indices 8-13 (11 if no
  // explicit Ws))
  auto q1 = MC::find_first(vec, {1, 2, 3, 4, 5}, 8, 13);
  auto q2 = MC::find_first(vec, {-1, -2, -3, -4, -5}, 8, 13);

  auto l = MC::find_first(vec, {11, 13, 15, -11, -13, -15}, 8, 13);
  auto nu = MC::find_first(vec, {12, 14, 16, -12, -14, -16}, 8, 13);

  // Check if any are compatible
  bool q_compatible = false;
  bool l_compatible = false;
  if (q1 != NULL && q2 != NULL) {
    q_compatible = MC::is_W_compatible(*q1, *q2, charge);
  }
  if (l != NULL && nu != NULL) {
    l_compatible = MC::is_W_compatible(*l, *nu, charge);
  }

  // There should never be a case when both are compatible
  if (q_compatible && l_compatible) {
    throw std::domain_error("Both l and q compatible W found!");
  } else if ((!q_compatible) && (!l_compatible)) {
    throw std::domain_error("No compatible W found!");
  }

  IMPL::MCParticleImpl res_W;

  // Create a W from the correct pair
  if (q_compatible) {
    res_W = MC::create_W(*q1, *q2);
  } else if (l_compatible) {
    res_W = MC::create_W(*l, *nu);
  }

  return res_W;
}

//------------------------------------------------------------------------------

EVENT::MCParticle *MC::incoming_eM_after_ISR(const EVENT::MCParticleVec &vec) {
  /** Return the incoming electron after ISR.
      ILD convention: First four elements in collection are before ISR
   **/
  return MC::find_first(vec, {11}, 4);
}

EVENT::MCParticle *MC::incoming_eP_after_ISR(const EVENT::MCParticleVec &vec) {
  /** Return the incoming positron after ISR.
      ILD convention: First four elements in collection are before ISR
   **/
  return MC::find_first(vec, {-11}, 4);
}

//------------------------------------------------------------------------------

IMPL::MCParticleImpl MC::create_W(const EVENT::MCParticle &mcp1,
                                  const EVENT::MCParticle &mcp2) {
  /** Create a W MCParticle from the given two particles.
   **/
  // First check if the particles are W-compatible.
  if (!MC::is_W_compatible(mcp1, mcp2)) {
    throw std::invalid_argument("The particles are not W compatible!");
  }

  IMPL::MCParticleImpl W_res;

  if (MC::is_W_compatible(mcp1, mcp2, +1)) {
    W_res.setPDG(+24);
  } else if (MC::is_W_compatible(mcp1, mcp2, -1)) {
    W_res.setPDG(-24);
  }
  auto E1 = mcp1.getEnergy();
  auto E2 = mcp2.getEnergy();
  auto mom1 = mcp1.getMomentum();
  auto mom2 = mcp2.getMomentum();

  auto E_W = E1 + E2;
  double p_W[3] = {mom1[0] + mom2[0], mom1[1] + mom2[1], mom1[2] + mom2[2]};
  auto m_W = std::sqrt(E_W * E_W -
                       (p_W[0] * p_W[0] + p_W[1] * p_W[1] + p_W[2] * p_W[2]));

  W_res.setMomentum(p_W);
  W_res.setMass(m_W);
  W_res.setCharge(mcp1.getCharge() + mcp2.getCharge());

  return W_res;
}

//------------------------------------------------------------------------------

std::string MC::print(const EVENT::MCParticle &mcp) {
  /** Return a string of some vital information of the MC particle.
   **/
  return std::string("E: ") + std::to_string(mcp.getEnergy()) +
         " Px: " + std::to_string(mcp.getMomentum()[0]) +
         " Py: " + std::to_string(mcp.getMomentum()[1]) +
         " Pz: " + std::to_string(mcp.getMomentum()[2]) +
         " Charge: " + std::to_string(mcp.getCharge());
}

//------------------------------------------------------------------------------

} // namespace Utils