#include "assetManager.hpp"
#include <iostream>

void assetManager::loadTexture(const std::string& name, const std::string& filename)
{
    sf::Texture texture;
    if(!texture.loadFromFile(filename))
    {
        std::cout<<"Failed to load "<<name<<" texture\n";
    }
    textures[name]=texture;
}

const sf::Texture& assetManager::getTexture(const std::string& name) const
{
    return textures.at(name);
}


