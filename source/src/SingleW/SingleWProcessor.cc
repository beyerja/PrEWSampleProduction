// -- your process header
#include "SingleW/SingleWProcessor.h"

// Custom headers
#include <Utils/Collections.h>
#include <Utils/MC.h>

// -- lcio headers
#include "EVENT/LCCollection.h"
#include "UTIL/LCTOOLS.h"

// This line allows to register your processor in marlin when calling "Marlin
// steeringFile.xml"
SingleWProcessor anSingleWProcessor;

//------------------------------------------------------------------------------

SingleWProcessor::SingleWProcessor() : marlin::Processor("SingleWProcessor") {
  // _description comes from marlin::Processor
  _description = "Processor for extracting the single-W (semilep) observables";

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
                             m_tree_name, std::string("SingleWObservables"));
}

//------------------------------------------------------------------------------

void SingleWProcessor::init() {
  // Usually a good idea to print parameters
  printParameters(); // method from marlin::Processor

  // Set up the output tree
  this->create_tree();
}

//------------------------------------------------------------------------------

void SingleWProcessor::processRunHeader(EVENT::LCRunHeader *run) {
  streamlog_out(MESSAGE) << "Starting run no " << run->getRunNumber()
                         << std::endl;
  // LCRunHeader objects can be printed using LCTOOLS class
  UTIL::LCTOOLS::dumpRunHeader(run);
}

//------------------------------------------------------------------------------

void SingleWProcessor::processEvent(EVENT::LCEvent *event) {
  streamlog_out(DEBUG) << "Processing event no " << event->getEventNumber()
                       << " - run " << event->getEventNumber() << std::endl;

  // Read the header info
  m_header.read(*event);

  // Reset the observables
  m_observables.reset();

  // Read the observables
  auto mcps =
      Utils::Collections::read<EVENT::MCParticle>(event, m_mcCollectionName);
  this->extract_observables(mcps);

  // Fill the event data into the tree
  m_tree->Fill();
}

//------------------------------------------------------------------------------

void SingleWProcessor::end() { this->save_tree(); }
