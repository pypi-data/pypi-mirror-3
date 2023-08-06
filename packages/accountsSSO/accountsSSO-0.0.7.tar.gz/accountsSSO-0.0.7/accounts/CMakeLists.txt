project(accounts)

set(Accounts_SRC
    ${CMAKE_CURRENT_BINARY_DIR}/Accounts/accounts_module_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Accounts/accounts_account_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Accounts/accounts_manager_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Accounts/accounts_provider_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Accounts/accounts_service_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Accounts/accounts_error_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Accounts/accounts_servicetype_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Accounts/accounts_watch_wrapper.cpp
)

set(Accounts_INCLUDE_DIRECTORIES
    ${ACCOUNTS_INCLUDE_DIRS}
    ${PYTHON_INCLUDE_DIRS}
    ${SHIBOKEN_INCLUDE_DIR}
    ${PYSIDE_INCLUDE_DIR}
    ${PYSIDE_INCLUDE_DIR}/QtCore
    )

string(REGEX REPLACE ";" ":" Accounts_INCLUDE_DIRECTORIES_FIX_COLON "${Accounts_INCLUDE_DIRECTORIES}")

set(Accounts_LINK_LIBRARIES
    ${PYTHON_LIBRARIES}
    ${SHIBOKEN_LIBRARY}
    ${PYSIDE_LIBRARY}
    ${QT_QTCORE_LIBRARY}
    ${ACCOUNTS_LIBRARIES}
)

set(Accounts_LIBRARY_DIRS
    ${ACCOUNTS_LIBRARY_DIRS}
    ${PYSIDE_LIBRARY_DIR}
    ${SHIBOKEN_LIBRARY_DIR}
)

link_directories(${Accounts_LIBRARY_DIRS})
include_directories(Accounts ${Accounts_INCLUDE_DIRECTORIES})
add_library(Accounts MODULE ${Accounts_SRC})
set_property(TARGET Accounts PROPERTY PREFIX "")
target_link_libraries(Accounts ${Accounts_LINK_LIBRARIES})

add_custom_command(OUTPUT ${Accounts_SRC}
                   COMMAND ${GENERATORRUNNER_BINARY}
                   ${GENERATOR_EXTRA_FLAGS}
                   ${CMAKE_CURRENT_SOURCE_DIR}/global.h
                   --include-paths=${QT_INCLUDE_DIR}:${Accounts_INCLUDE_DIRECTORIES_FIX_COLON}
                   --typesystem-paths=${typesystem_path}:${PYSIDE_TYPESYSTEMS}
                   --output-directory=${CMAKE_CURRENT_BINARY_DIR}
                   --api-version=${BINDING_API_MAJOR_VERSION}.${BINDING_API_MINOR_VERSION}
                   ${CMAKE_CURRENT_SOURCE_DIR}/typesystem_accounts.xml
                   WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                   COMMENT "Running generator for Accounts..."
)


install(FILES ${CMAKE_CURRENT_BINARY_DIR}/Accounts${CMAKE_DEBUG_POSTFIX}.so 
        DESTINATION "${SITE_PACKAGE}/${BINDING_NAME}")
