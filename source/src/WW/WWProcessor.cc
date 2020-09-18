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

  // Register a parameter
  registerProcessorParameter("OutputFilePath", "Path of the output ROOT file",
                             m_file_path, std::string("./output.root"));
  registerProcessorParameter("OutputTreeName", "Name of the output TTree",
                             m_tree_name, std::string("WWObservables"));
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

  // Read the header info
  m_header.read(*event);

  // Reset the observables
  m_observables.reset();

  // Read the observables
  auto mcps =
      Utils::Collections::read<EVENT::MCParticle>(event, m_mcCollectionName);
  for (const auto mcp_ptr : mc_particles) {
    auto tlv = Utils::MC::get_tlv(*mcp_ptr);
  }
  
  // Fill the event data into the tree
  m_tree->Fill();
}

//------------------------------------------------------------------------------

void WWProcessor::end() { this->save_tree(); }
