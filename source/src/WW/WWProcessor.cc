// -- your process header
#include "WW/WWProcessor.h"

// -- lcio headers
#include "EVENT/LCCollection.h"
#include "EVENT/MCParticle.h"
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
  // registerProcessorParameter("PfoEnergyCut",
  //   "A cut on pfo energy to apply",
  //   m_pfoEnergyCut,
  //   0.f);
}

//------------------------------------------------------------------------------

void WWProcessor::init() {
  // Usually a good idea to print parameters
  printParameters(); // method from marlin::Processor
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

  // Collect MC collection
  EVENT::LCCollection *mc_collection{};
  try {
    mc_collection = event->getCollection(m_mcCollectionName);
  } catch (EVENT::DataNotAvailableException &) {
    streamlog_out(WARNING) << "MC collection '" << m_mcCollectionName
                           << "' is not available !" << std::endl;
  }
}

//------------------------------------------------------------------------------

void WWProcessor::end() {
  // Cleanup your mess here !
}
