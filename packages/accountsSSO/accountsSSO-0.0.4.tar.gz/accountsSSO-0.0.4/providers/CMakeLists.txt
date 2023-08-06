project(providers)

set(Providers_SRC
    ${CMAKE_CURRENT_BINARY_DIR}/Providers/providers_module_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Providers/accountsetup_providerpluginprocess_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Providers/accountsetup_providerpluginproxy_wrapper.cpp
)

set(Providers_INCLUDE_DIRECTORIES
    ${ACCOUNT_SETUP_INCLUDE_DIRS}
    ${PYTHON_INCLUDE_DIRS}
    ${SHIBOKEN_INCLUDE_DIR}
    ${PYSIDE_INCLUDE_DIR}
    ${PYSIDE_INCLUDE_DIR}/QtCore
    )

string(REGEX REPLACE ";" ":" Providers_INCLUDE_DIRECTORIES_FIX_COLON "${Providers_INCLUDE_DIRECTORIES}")

set(Providers_LINK_LIBRARIES
    ${PYTHON_LIBRARIES}
    ${SHIBOKEN_LIBRARY}
    ${PYSIDE_LIBRARY}
    ${QT_QTCORE_LIBRARY}
    ${ACCOUNT_SETUP_LIBRARIES}
)

set(Providers_LIBRARY_DIRS
    ${ACCOUNT_SETUP_LIBRARY_DIRS}
    ${PYSIDE_LIBRARY_DIR}
    ${SHIBOKEN_LIBRARY_DIR}
)

link_directories(${Providers_LIBRARY_DIRS})
include_directories(Providers ${Providers_INCLUDE_DIRECTORIES})
add_library(Providers MODULE ${Providers_SRC})
set_property(TARGET Providers PROPERTY PREFIX "")
target_link_libraries(Providers ${Providers_LINK_LIBRARIES})

add_custom_command(OUTPUT ${Providers_SRC}
                   COMMAND ${GENERATORRUNNER_BINARY}
                   ${GENERATOR_EXTRA_FLAGS}
                   ${CMAKE_CURRENT_SOURCE_DIR}/global.h
                   --include-paths=${QT_INCLUDE_DIR}:${Providers_INCLUDE_DIRECTORIES_FIX_COLON}
                   --typesystem-paths=${typesystem_path}:${PYSIDE_TYPESYSTEMS}
                   --output-directory=${CMAKE_CURRENT_BINARY_DIR}
                   --api-version=${BINDING_API_MAJOR_VERSION}.${BINDING_API_MINOR_VERSION}
                   ${CMAKE_CURRENT_SOURCE_DIR}/typesystem_providers.xml
                   WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                   COMMENT "Running generator for Providers..."
)


install(FILES ${CMAKE_CURRENT_BINARY_DIR}/Providers${CMAKE_DEBUG_POSTFIX}.so 
        DESTINATION "${SITE_PACKAGE}/${BINDING_NAME}")
