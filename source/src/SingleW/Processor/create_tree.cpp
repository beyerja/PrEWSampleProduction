#include <SingleW/SingleWProcessor.h>

void SingleWProcessor::create_tree() {
  /** Open the output file, create the needed TTree, create its branches and
      connect them to the observable variables.
   **/
  // Open the output file
  m_file = std::make_unique<TFile>(m_file_path.c_str(), "recreate");

  // Create the tree
  m_tree = new TTree(m_tree_name.c_str(), m_tree_name.c_str());

  // Connect header info
  m_header.connect(m_tree);

  // Create and connect the observable branches
  m_tree->Branch("e_charge", &m_observables.e_charge, "e_charge/I");
  m_tree->Branch("phi_e_star", &m_observables.phi_e_star, "phi_e_star/D");
  m_tree->Branch("costh_e_star", &m_observables.costh_e_star, "costh_e_star/D");
  m_tree->Branch("m_enu", &m_observables.m_enu, "m_enu/D");
}