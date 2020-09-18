#include <Utils/HeaderInfo.h>

namespace Utils {

//------------------------------------------------------------------------------

void HeaderInfo::connect(TTree *tree) {
  /** Create all the needed branches in the given TTree and connect them the
   *member variables of this HeaderInfo.
   **/
  tree->Branch("process_ID", &m_process_ID, "process_ID/I");
  tree->Branch("energy", &m_energy, "energy/D");
  tree->Branch("weight", &m_weight, "weight/D");
  tree->Branch("eM_chirality", &m_eM_chirality, "eM_chirality/I");
  tree->Branch("eP_chirality", &m_eP_chirality, "eP_chirality/I");
  tree->Branch("cross_section", &m_cross_section, "cross_section/D");
  tree->Branch("cross_section_err", &m_cross_section_err,
               "cross_section_err/D");
}

//------------------------------------------------------------------------------

void HeaderInfo::read(const EVENT::LCEvent &event) {
  /** Read the information from a given event.
   **/
  m_process_ID = event.getParameters().getIntVal("ProcessID");
  m_energy = event.getParameters().getFloatVal("Energy");
  m_weight = event.getParameters().getFloatVal("_weight");
  m_eM_chirality = event.getParameters().getFloatVal("beamPol1");
  m_eP_chirality = event.getParameters().getFloatVal("beamPol2");
  m_cross_section = event.getParameters().getFloatVal("crossSection");
  m_cross_section_err = event.getParameters().getFloatVal("crossSectionError");
}

//------------------------------------------------------------------------------

} // namespace Utils