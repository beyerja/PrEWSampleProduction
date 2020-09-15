#include <Utils/MC.h>

namespace Utils {
  
//------------------------------------------------------------------------------

TLorentzVector MC::get_tlv(const lcio::MCParticle &mcp) {
  /** Return the four-momentum of the MC particle as a TLorentzVector.
   **/
  return TLorentzVector( mcp.getMomentum(), mcp.getEnergy() );
}

//------------------------------------------------------------------------------

} // namespace Utils