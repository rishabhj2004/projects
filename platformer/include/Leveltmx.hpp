#pragma once
#include <vector>
#include <SFML/Graphics.hpp>
#include <tmxlite/Map.hpp>
#include <tmxlite/ObjectGroup.hpp>
#include <SFML/Graphics/Shader.hpp>
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

struct EnemySpawn
{
    std::string type;
    sf::Vector2f position;
};

class Leveltmx
{
private:
    tmx::Map map;
    std::vector<TilesetData> tilesets;
    std::vector<CollisionRect> collisions;
    sf::Shader platformShader;
    sf::Texture noiseTexture;

public:
    Leveltmx(const std::string& filename);
    void draw(sf::RenderWindow& window);
    void drawPlatforms(sf::RenderWindow& window, float totalTime);

    float getWidth() const;
    float getHeight() const;
    sf::Vector2f getPlayerSpawn() const;
    const std::vector<CollisionRect>& getCollisions() const;
    std::vector<EnemySpawn> getEnemySpawns() const;
};
