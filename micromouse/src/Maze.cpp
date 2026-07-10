#include "Maze.hpp"
#include <iostream>

Maze::Maze(){ //The :: means a scope resolution operator
    cells.resize(16);
    for(int row=0;row<16;row++){
        cells[row].resize(16);
    }
}

int Maze::getRows() const
{
    return cells.size();
}

int Maze::getCols() const
{
    return cells[0].size();
}

Cell& Maze::getCell(int row,int col)
{
    return cells[row][col];
}

const Cell& Maze::getCell(int row,int col) const
{
    return cells[row][col];
}

void Maze::addWall(int row,int col,Direction direction)
{
    switch(direction)
    {
        case Direction::North:
        {
            cells[row][col].north=true;
            if(row>0)
            {
            cells[row-1][col].south=true;
            }
            break;
        }
        case Direction::South:
        {
            cells[row][col].south=true;
            if(row<getRows()-1)
            {
            cells[row+1][col].north=true;
            }
            break;
        }
        case Direction::East:
        {
            cells[row][col].east=true;
            if(col<getCols()-1)
            {
                cells[row][col+1].west=true;
            }
            break;
        }
        case Direction::West:
        {
            cells[row][col].west=true;
            if(col>0)
            {
                cells[row][col-1].east=true;
            }
            break;
        }
        default:
            break;
    }
}

bool Maze::hasWall(int row, int col, Direction direction) const
{
    switch(direction)
    {
        case Direction::North:
            return cells[row][col].north;
        case Direction::South:
            return cells[row][col].south;
        case Direction::East:
            return cells[row][col].east;
        case Direction::West:
            return cells[row][col].west;
        default:
            return false;
    }
}

void Maze::print() const
{
    for(int row=0;row<getRows();row++)
    {
        for(int col=0;col<getCols();col++)
        {
            std::cout<<"+";            
            if(hasWall(row,col,Direction::North))
            {
                std::cout<<"---";
            }
            else
            {
                std::cout<<"   ";
            }
        }
        std::cout<<"+\n";
        for(int col=0;col<getCols();col++)
        {
            if(hasWall(row,col,Direction::West))
            {
                std::cout<<"|   ";
            }
            else
            {
                std::cout<<"    ";
            }
        }
        if(hasWall(row,getCols()-1,Direction::East))
        {
            std::cout<<"|\n";
        }
        else
        {
            std::cout<<" \n";
        }
    }
    for(int col=0;col<getCols();col++)
    {
        std::cout<<"+";
        if(hasWall(getRows()-1,col,Direction::South))
        {
            std::cout<<"---";
        }
        else
        {
            std::cout<<"   ";
        }
    }
    std::cout<<"+\n";
}

