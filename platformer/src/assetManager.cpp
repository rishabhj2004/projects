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

void assetManager::loadShader(
    const std::string& name,
    const std::string& filename
)
{
    auto [it, inserted] = shaders.try_emplace(name);

    if (!it->second.loadFromFile(
            filename,
            sf::Shader::Fragment))
    {
        std::cout << "Failed to load "
                  << name
                  << " shader\n";
    }
}

sf::Shader& assetManager::getShader(
    const std::string& name
)
{
    return shaders.at(name);
}
