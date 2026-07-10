#pragma once
#include <vector>

enum class Direction
{
    North,
    East,
    South,
    West
};

struct Cell{
    bool north=false;
    bool south=false;
    bool east=false;
    bool west=false;
};

class Maze{
    private:
        std::vector<std::vector<Cell>> cells;
    public:
        Maze();
        int getRows() const;
        int getCols() const;
        Cell& getCell(int row,int col);//we are creating a new datatype Cell
        const Cell& getCell(int row,int col) const;
        void addWall(int row,int col, Direction direction);
        bool hasWall(int row, int col, Direction direction) const;
        void print() const;
};
