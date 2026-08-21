#pragma once
#include <vector>
#include "Direction.hpp"

class Mouse{
    private:
        int row;
        int col;
        Direction direction;

    public:
        Mouse(int row, int col, Direction direction);
        bool checkForwardWall();
        bool checkWallLeft();
        bool checkWallRight();
        void moveForward();
        void turnLeft();
        void turnRight();
}

