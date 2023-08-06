project(signon)

set(SignOn_SRC
    ${CMAKE_CURRENT_BINARY_DIR}/SignOn/signon_module_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/SignOn/signon_authservice_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/SignOn/signon_identityinfo_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/SignOn/signon_error_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/SignOn/signon_sessiondata_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/SignOn/signon_identity_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/SignOn/signon_authsession_wrapper.cpp

)

set(SignOn_INCLUDE_DIRECTORIES
    ${SIGNON_INCLUDE_DIRS}
    ${PYTHON_INCLUDE_DIRS}
    ${SHIBOKEN_INCLUDE_DIR}
    ${PYSIDE_INCLUDE_DIR}
    ${PYSIDE_INCLUDE_DIR}/QtCore
    )

string(REGEX REPLACE ";" ":" SignOn_INCLUDE_DIRECTORIES_FIX_COLON "${SignOn_INCLUDE_DIRECTORIES}")

set(SignOn_LINK_LIBRARIES
    ${PYTHON_LIBRARIES}
    ${SHIBOKEN_LIBRARY}
    ${PYSIDE_LIBRARY}
    ${QT_QTCORE_LIBRARY}
    ${SIGNON_LIBRARIES}
)

set(SignOn_LIBRARY_DIRS
    ${SIGNON_LIBRARY_DIRS}
    ${PYSIDE_LIBRARY_DIR}
    ${SHIBOKEN_LIBRARY_DIR}
)

link_directories(${SignOn_LIBRARY_DIRS})
include_directories(SignOn ${SignOn_INCLUDE_DIRECTORIES})
add_library(SignOn MODULE ${SignOn_SRC})
set_property(TARGET SignOn PROPERTY PREFIX "")
target_link_libraries(SignOn ${SignOn_LINK_LIBRARIES})

add_custom_command(OUTPUT ${SignOn_SRC}
                   COMMAND ${GENERATORRUNNER_BINARY}
                   ${GENERATOR_EXTRA_FLAGS}
                   ${CMAKE_CURRENT_SOURCE_DIR}/global.h
                   --include-paths=${QT_INCLUDE_DIR}:${SignOn_INCLUDE_DIRECTORIES_FIX_COLON}
                   --typesystem-paths=${typesystem_path}:${PYSIDE_TYPESYSTEMS}
                   --output-directory=${CMAKE_CURRENT_BINARY_DIR}
                   --api-version=${BINDING_API_MAJOR_VERSION}.${BINDING_API_MINOR_VERSION}
                   ${CMAKE_CURRENT_SOURCE_DIR}/typesystem_signon.xml
                   WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                   COMMENT "Running generator for SignOn..."
)


install(FILES ${CMAKE_CURRENT_BINARY_DIR}/SignOn${CMAKE_DEBUG_POSTFIX}.so 
        DESTINATION "${SITE_PACKAGE}/${BINDING_NAME}")
