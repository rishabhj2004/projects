#pragma once
#include <vector>
#include <SFML/Graphics.hpp>
#include <tmxlite/Map.hpp>
#include <tmxlite/ObjectGroup.hpp>
#include <string>

struct TilesetData
{
    tmx::Tileset tileset;
    sf::Texture texture;
};

struct CollisionRect
{
    sf::FloatRect bounds;
};

class Leveltmx
{
private:
    tmx::Map map;
    std::vector<TilesetData> tilesets;
    std::vector<CollisionRect> collisions;

public:
    Leveltmx(const std::string& filename);
    void draw(sf::RenderWindow& window);

    float getWidth() const;
    float getHeight() const;
    sf::Vector2f getPlayerSpawn() const;
    const std::vector<CollisionRect>& getCollisions() const;
};
