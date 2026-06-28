#include <iostream>
#include "Maze.hpp"

int main()
{
    Maze maze;
    maze.addWall(5,7,Direction::North);
    std::cout<<maze.hasWall(5,7,Direction::North)<<"\n";
    std::cout<<maze.hasWall(4,7,Direction::South)<<"\n";
    return 0;
}
