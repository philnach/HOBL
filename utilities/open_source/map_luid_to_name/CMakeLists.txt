cmake_minimum_required(VERSION 3.20)

project(map_luid_to_name LANGUAGES CXX)

# Ensure using a modern C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Windows-only
if (NOT WIN32)
    message(FATAL_ERROR "This project targets Windows.")
endif()

# Create executable
add_executable(map_luid_to_name map_luid_to_name.cpp)

target_link_libraries(map_luid_to_name PRIVATE dxcore.lib)

if(MSVC)
    target_compile_options(map_luid_to_name PRIVATE /W4 /permissive-)
endif()
