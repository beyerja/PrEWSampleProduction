#include <Difermion/DifermionProcessor.h>

void DifermionProcessor::create_tree() {
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
  m_tree->Branch("f_pdg", &m_observables.f_pdg, "f_pdg/I");
  m_tree->Branch("costh_f_star", &m_observables.costh_f_star, "costh_f_star/D");
  m_tree->Branch("costh_f_star_true", &m_observables.costh_f_star_true, "costh_f_star_true/D");
  m_tree->Branch("m_ff", &m_observables.m_ff, "m_ff/D");
  m_tree->Branch("pz_ff", &m_observables.pz_ff, "pz_ff/D");
  m_tree->Branch("costh_f", &m_observables.costh_f, "costh_f/D");
  m_tree->Branch("costh_fbar", &m_observables.costh_fbar, "costh_fbar/D");
}