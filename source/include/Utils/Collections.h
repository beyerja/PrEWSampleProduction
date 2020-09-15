#ifndef LIB_UTILS_COLLECTIONS_H
#define LIB_UTILS_COLLECTIONS_H 1

// Includes from iLCSoft
#include "lcio.h"
#include <EVENT/LCEvent.h>
#include <EVENT/LCCollection.h>

// Standard library
#include <vector>

namespace Utils {
namespace Collections {
/** LCIO helper functions related to LCCollections.
 **/

template <class T>
std::vector<T *> read(EVENT::LCEvent *event, const std::string &name);

} // namespace Collections
} // namespace Utils

#include <Utils/Collections.tpp>
#endif