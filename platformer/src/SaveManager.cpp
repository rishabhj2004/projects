#include "SaveManager.hpp"
#include <fstream>
#include <iostream>

void SaveManager::save(const SaveData& data)
{
    std::ofstream file("save.txt");
    if(!file)
    {
        std::cerr<<"Failed to open Save file"<<"\n";
        return;
    }
    file << data.currentRoom << "\n";
    file << data.checkpoint.x << " " << data.checkpoint.y << "\n";
    file << data.doubleJump << '\n';
    file << data.dash << '\n';
    file << data.attack << '\n';
    std::cout << "Game saved!\n";
}

SaveData SaveManager::load()
{
    SaveData data;
    std::ifstream file("save.txt");
    if(!file)
    {
        std::cout<<"No save file found... Starting fresh\n";
        data.currentRoom="level1.tmx";
        data.checkpoint=sf::Vector2f(100.f,100.f);
        data.doubleJump = false;
        data.dash = false;
        data.attack = false;

        return data;
    }
    file >> data.currentRoom;
    file >> data.checkpoint.x >> data.checkpoint.y;
    file >> data.doubleJump;
    file >> data.dash;
    file >> data.attack;
    std::cout << "Game loaded!\n";
    return data;
}
