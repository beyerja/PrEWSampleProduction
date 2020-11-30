# -------------------------------------------------
# include directories
include_directories( include )

# -------------------------------------------------
# build the project library
# This compiles everything in the src directory and build a library
# called lib%(repository)s.so, that with be install in the lib directory
# in the top level directory of your project 
aux_source_directory( src/Utils SRC_FILES )
aux_source_directory( src/Difermion SRC_FILES )
aux_source_directory( src/Difermion/Processor SRC_FILES )
aux_source_directory( src/WW SRC_FILES )
aux_source_directory( src/WW/Processor SRC_FILES )
aux_source_directory( src/SingleW SRC_FILES )
aux_source_directory( src/SingleW/Processor SRC_FILES )
add_shared_library( ${PROJECT_NAME} ${SRC_FILES} )

# Link external libraries
target_link_libraries(${PROJECT_NAME} PUBLIC 
  ${MarlinHelp}
)

install( TARGETS ${PROJECT_NAME} LIBRARY DESTINATION lib )
