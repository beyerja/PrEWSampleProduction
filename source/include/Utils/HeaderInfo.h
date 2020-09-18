#ifndef LIB_UTILS_HEADERINFO_H
#define LIB_UTILS_HEADERINFO_H 1

// Includes from iLCSoft
#include "lcio.h"
#include <EVENT/LCEvent.h>

// Includes from ROOT
#include "TTree.h"

namespace Utils {

struct HeaderInfo {
  /** Header class for simple extraction of LCIO event header info (in ILD 
      convention: particle1 = e-, particle2 = e+).
   **/
  
  int m_process_ID {};
  double m_energy {};
  double m_weight {};
  int m_eM_chirality {};
  int m_eP_chirality {};
  double m_cross_section {};
  double m_cross_section_err {};
  
  void connect(TTree * tree);
  void read(const EVENT::LCEvent & event);
};

} // namespace Utils

#endif