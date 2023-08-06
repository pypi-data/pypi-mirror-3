project(python-accounts-sso)

cmake_minimum_required(VERSION 2.6)
set(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake/Macros
                      ${CMAKE_MODULE_PATH})

find_package(PythonLibs REQUIRED)
find_package(GeneratorRunner REQUIRED)
find_package(Shiboken REQUIRED)
find_package(Qt4 REQUIRED)
find_package(PySide REQUIRED)
find_package(PkgConfig REQUIRED)

# binding dependences
pkg_check_modules(ACCOUNTS REQUIRED accounts-qt)
pkg_check_modules(ACCOUNT_SETUP REQUIRED AccountSetup)
pkg_check_modules(SIGNON REQUIRED libsignon-qt)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE ${SHIBOKEN_BUILD_TYPE})
endif()

set(BINDING_NAME accountsSSO)
set(BINDING_API_MAJOR_VERSION "0")
set(BINDING_API_MINOR_VERSION "0")
set(BINDING_API_MICRO_VERSION "1")
set(BINDING_API_RELEASE_LEVEL "0m6")
set(BINDING_API_VERSION "${BINDING_API_MAJOR_VERSION}.${BINDING_API_MINOR_VERSION}.${BINDING_API_MICRO_VERSION}"
	CACHE STRING "PySide version"
	FORCE
)

configure_file("${CMAKE_CURRENT_SOURCE_DIR}/__init__.py.in" 
               "${CMAKE_CURRENT_BINARY_DIR}/__init__.py" 
               @ONLY
)

include(${QT_USE_FILE})

if(NOT SITE_PACKAGE)
    execute_process(
        COMMAND ${SHIBOKEN_PYTHON_INTERPRETER} -c "from distutils import sysconfig; \\
            print sysconfig.get_python_lib(1,0)"
        OUTPUT_VARIABLE SITE_PACKAGE
        OUTPUT_STRIP_TRAILING_WHITESPACE)
    if (NOT SITE_PACKAGE)
        message(FATAL_ERROR "Could not detect Python module installation directory.")
    endif()
endif()

if(CMAKE_HOST_UNIX)
    option(ENABLE_GCC_OPTIMIZATION "Enable specific GCC flags to optimization library size and performance. Only available on Release Mode" 0)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -fvisibility=hidden -Wno-strict-aliasing")
    set(CMAKE_CXX_FLAGS_DEBUG "-g")
    if(ENABLE_GCC_OPTIMIZATION)
        set(CMAKE_BUILD_TYPE Release)
        set(CMAKE_CXX_FLAGS_RELEASE "-DNDEBUG -Os -Wl,-O1")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wl,--hash-style=gnu")
    endif()
endif()

set(GENERATOR_EXTRA_FLAGS --generator-set=shiboken --enable-parent-ctor-heuristic --enable-pyside-extensions --enable-return-value-heuristic)
add_subdirectory(accounts)
add_subdirectory(signon)
add_subdirectory(providers)

# install
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/__init__.py"
        DESTINATION "${SITE_PACKAGE}/${BINDING_NAME}${pyside_SUFFIX}")

