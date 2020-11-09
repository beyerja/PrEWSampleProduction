#include <SingleW/SingleWProcessor.h>

void SingleWProcessor::save_tree() {
  /** Save the output tree and close the file.
   **/
  m_file->cd(); // go to output file
  
  streamlog_out(DEBUG) << "Writing tree." << std::endl; 
  m_tree->Write();
  
  streamlog_out(DEBUG) << "Closing file." << std::endl; 
  m_file->Close();
   
}