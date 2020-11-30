#ifndef LIB_DIFERMIONPROCESSOR_H
#define LIB_DIFERMIONPROCESSOR_H 1

#include <Difermion/DifermionObservables.h>
#include <Utils/HeaderInfo.h>

// Includes from iLCSoft
#include "EVENT/MCParticle.h"
#include "marlin/Processor.h"

// Includes from ROOT
#include <TFile.h>
#include <TTree.h>

// Standard library
#include <memory>

class DifermionProcessor : public marlin::Processor {
public:
  /**
   *  @brief  Factory method to create a processor
   *
   *  This method is called internally by Marlin to create an instance of your
   * processor
   */
  marlin::Processor *newProcessor() { return new DifermionProcessor(); }

  /**
   *  @brief  Constructor
   *
   *  Regiter your parameters in there. See DifermionProcessor.cc
   */
  DifermionProcessor();

  // These two lines avoid frequent compiler warnings when using -Weffc++
  DifermionProcessor(const DifermionProcessor &) = delete;
  DifermionProcessor &operator=(const DifermionProcessor &) = delete;

  /**
   *  @brief  Called once at the begin of the job before anything is read.
   *
   *  Use to initialize the processor, e.g. book histograms. The parameters that
   *  you have registered in the constructor are initialized
   */
  void init();

  /**
   *  Called for every run read from the file.
   *
   *  If you use simulation data output from ddsim (e.g from production data on
   * grid), this will be called before the first event and only once in the job.
   */
  void processRunHeader(EVENT::LCRunHeader *run);

  /**
   *  @brief  Called for every event - the working horse.
   *
   *  Analyze your reconstructed particle objects from the event object here.
   *  See DifermionProcessor.cc for an example
   */
  void processEvent(EVENT::LCEvent *event);

  /**
   *  @brief  Called after data processing for clean up.
   *
   *  You have allocated memory somewhere in your code ?
   *  This is the best place to clean your mess !
   */
  void end();

private:
  // Initialize your members in the class definition to
  // be more efficient and avoid compiler warnings

  // --- Input parameters ------------------------------------------------------
  std::string m_mcCollectionName = {""};

  bool m_unboost_xangle{true};

  std::string m_file_path{""};
  std::string m_tree_name{""};

  // ---------------------------------------------------------------------------

  // TFile and TTree with result output
  std::unique_ptr<TFile> m_file{};
  TTree *m_tree{}; // Needs to be pure pointer, belongs to file

  // Output information
  Utils::HeaderInfo m_header{};
  Difermion::DifermionObservables m_observables{};

  // Internal functions
  void create_tree();
  void save_tree();

  void extract_observables(const EVENT::MCParticleVec &mcps);
  void extract_lab_observables(const EVENT::MCParticle &f,
                               const EVENT::MCParticle &fbar);
  void extract_ee_observables(const EVENT::MCParticle &f,
                              const EVENT::MCParticle &fbar);
};

#endif