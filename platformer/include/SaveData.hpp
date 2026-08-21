#pragma once

#include <SFML/System/Vector2.hpp>
#include <string>

struct SaveData
{
    std::string currentRoom;
    sf::Vector2f checkpoint;
    bool doubleJump;
    bool dash;
    bool attack;
};

