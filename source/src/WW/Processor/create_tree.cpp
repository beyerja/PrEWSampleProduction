#include <WW/WWProcessor.h>

void WWProcessor::create_tree() {
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
  m_tree->Branch("decay_to_mu", &m_observables.decay_to_mu, "decay_to_mu/O");
  m_tree->Branch("decay_to_tau", &m_observables.decay_to_tau, "decay_to_tau/O");
  m_tree->Branch("l_charge", &m_observables.l_charge, "l_charge/I");
  m_tree->Branch("phi_l_star", &m_observables.phi_l_star, "phi_l_star/D");
  m_tree->Branch("costh_l_star", &m_observables.costh_l_star,
                 "costh_l_star/D");
  m_tree->Branch("costh_Wminus_star", &m_observables.costh_Wminus_star,
                 "costh_Wminus_star/D");
  m_tree->Branch("costh_l", &m_observables.costh_l, "costh_l/D");
}