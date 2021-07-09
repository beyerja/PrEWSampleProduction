// -- your process header
#include "WW/WWProcessor.h"

// Custom headers
#include <Utils/Collections.h>
#include <Utils/MC.h>

// -- lcio headers
#include "EVENT/LCCollection.h"
#include "UTIL/LCTOOLS.h"

// This line allows to register your processor in marlin when calling "Marlin
// steeringFile.xml"
WWProcessor anWWProcessor;

//------------------------------------------------------------------------------

WWProcessor::WWProcessor() : marlin::Processor("WWProcessor") {
  // _description comes from marlin::Processor
  _description = "An example processor for ILD analysis";

  // Register an input collection
  registerInputCollection(
      LCIO::MCPARTICLE, // The collection type. Checkout the LCIO documentation
                        // for other types
      "MCParticleCollection", // The parameter name to read from steering file
      "The Pandora PFO collection name", // A parameter description. Please fill
                                         // this correctly
      m_mcCollectionName, // Your variable to store the result after steering
                          // file parsing
      std::string("MCParticle")); // That's the default value, in case

  // Register input parameters
  registerProcessorParameter("UnboostCrossingAngle",
                             "Should the crossing angle be unboosted?",
                             m_unboost_xangle, bool(true));

  registerProcessorParameter("OutputFilePath", "Path of the output ROOT file",
                             m_file_path, std::string("./output.root"));
  registerProcessorParameter("OutputTreeName", "Name of the output TTree",
                             m_tree_name, std::string("WWObservables"));

  registerProcessorParameter("WeightFilePath", "Path to rescan weight file",
                             m_weights_path, std::string(""));
}

//------------------------------------------------------------------------------

void WWProcessor::init() {
  // Usually a good idea to print parameters
  printParameters(); // method from marlin::Processor

  // Set up the output tree
  this->create_tree();
}

//------------------------------------------------------------------------------

void WWProcessor::processRunHeader(EVENT::LCRunHeader *run) {
  streamlog_out(MESSAGE) << "Starting run no " << run->getRunNumber()
                         << std::endl;
  // LCRunHeader objects can be printed using LCTOOLS class
  UTIL::LCTOOLS::dumpRunHeader(run);
}

//------------------------------------------------------------------------------

void WWProcessor::processEvent(EVENT::LCEvent *event) {
  streamlog_out(DEBUG) << "Processing event no " << event->getEventNumber()
                       << " - run " << event->getEventNumber() << std::endl;

  // If weights were requested and not found for this event, skip the event.
  // Main reason this happens is a bug that causes the rescan to fail.
  if ((!m_weights_path.empty()) && (m_wfr.n_events() <= n_evt)) {
    n_evt++;
    return;
  }

  // Read the header info
  m_header.read(*event);

  // Reset the observables
  m_observables.reset();

  // Read the observables
  auto mcps =
      Utils::Collections::read<EVENT::MCParticle>(event, m_mcCollectionName);
  this->extract_observables(mcps);

  // Read the current weights if requested
  if (!m_weights_path.empty()) {
    // Way of copying must preserve the addresses of m_evt_weights
    for (size_t p = 0; p < m_wfr[n_evt].size(); p++) {
      m_evt_weights[p] = m_wfr[n_evt][p];
    }
  }

  // Fill the event data into the tree
  m_tree->Fill();

  // Count up the event number
  n_evt++;
}

//------------------------------------------------------------------------------

void WWProcessor::end() {
  this->save_tree();
  if ((!m_weights_path.empty()) && (m_wfr.n_events() != n_evt)) {
    streamlog_out(WARNING) << "Weights were requested and only the first "
                           << m_wfr.n_events() << " out of " << n_evt
                           << " events had weights assigned "
                           << "- remaining events were not computed.\n";
  }
}
