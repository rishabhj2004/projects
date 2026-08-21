#pragma once
#include <SFML/Graphics.hpp>
#include <string>
#include <map>

class assetManager
{
    private:
        std::map<std::string, sf::Texture> textures;
    public:
        void loadTexture(const std::string& name,const std::string& filename);
        const sf::Texture& getTexture(const std::string& name) const;
};

