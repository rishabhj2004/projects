#include <iostream>
#include "Maze.hpp"

int main()
{
    Maze maze;
    maze.addWall(0,0,Direction::North);
    maze.addWall(0,0,Direction::West);
    maze.addWall(0,0,Direction::East);
    maze.addWall(0,0,Direction::South);
    maze.print();
    return 0;
}
