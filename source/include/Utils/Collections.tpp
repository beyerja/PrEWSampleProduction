#ifndef LIB_UTILS_COLLECTIONS_TPP
#define LIB_UTILS_COLLECTIONS_TPP 1

#include <Utils/Collections.h>

// Standard library
#include <string>

namespace Utils {

//------------------------------------------------------------------------------

template <class T>
std::vector<T *> Collections::read(EVENT::LCEvent *event,
                                  const std::string &name) {
  /** Read the given collection into a vector of the template particle type.
   **/
  std::vector<T *> output{};

  // Get the collection from the event
  LCCollection *collection = event->getCollection(name);
  streamlog_out(DEBUG) << "Number of particles in '" << name
                       << "': " << std::to_string(collection->getNumberOfElements())
                       << std::endl;

  for (int e = 0; e < collection->getNumberOfElements(); e++) {
    // Get an object from the collection and convert it to a particle
    T *particle = static_cast<T *>(collection->getElementAt(e));

    // If the collection type is wrong you end up with a null pointer here.
    // Always check it !
    if (nullptr == particle) {
      streamlog_out(ERROR) << "Wrong object type in collection '" << name << "'"
                           << std::endl;
      continue;
    }

    output.push_back(particle);
  }

  return output;
}

//------------------------------------------------------------------------------

} // namespace Utils

#endif