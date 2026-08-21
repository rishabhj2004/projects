cmake_minimum_required(VERSION 3.20)

project(platformer)

set(CMAKE_CXX_STANDARD 20)
find_package(SFML 2.6 REQUIRED COMPONENTS graphics)
add_executable(platformer
    src/main.cpp
    src/Game.cpp
    src/Player.cpp
    src/assetManager.cpp
    src/Animation.cpp
    src/Leveltmx.cpp
    src/SaveManager.cpp
)
add_subdirectory(external/tmxlite/tmxlite)
target_include_directories(platformer PRIVATE include)
target_link_libraries(platformer 
    PRIVATE
    sfml-graphics
    tmxlite
)
