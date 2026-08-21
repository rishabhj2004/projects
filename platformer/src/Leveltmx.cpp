#include "Leveltmx.hpp"
#include <iostream>
#include <tmxlite/TileLayer.hpp>

Leveltmx::Leveltmx(const std::string& filename)
{
    if (!map.load(filename))
    {
        std::cerr << "Failed to load TMX map: "
                  << filename << '\n';
        return;
    }

    std::cout << "Loaded TMX map successfully!\n";

    std::cout << "Map size: "
              << map.getTileCount().x
              << " x "
              << map.getTileCount().y
              << '\n';

    std::cout << "Tile size: "
              << map.getTileSize().x
              << " x "
              << map.getTileSize().y
              << '\n';

    // Layers
    for (const auto& layer : map.getLayers())
    {
        std::cout << "Layer: "
                  << layer->getName()
                  << '\n';
    }

    // Tilesets
    for (const auto& ts : map.getTilesets())
    {
        std::cout << "\nTileset: "
                  << ts.getName()
                  << '\n';

        std::cout << "Tile size: "
                  << ts.getTileSize().x
                  << " x "
                  << ts.getTileSize().y
                  << '\n';

        std::cout << "Tile count: "
                  << ts.getTileCount()
                  << '\n';

        std::cout << "Columns: "
                  << ts.getColumnCount()
                  << '\n';

        std::cout << "Image: "
                  << ts.getImagePath()
                  << '\n';

        std::cout << "First GID: "
                  << ts.getFirstGID()
                  << '\n';


        // Create our TilesetData
        TilesetData data;
        data.tileset = ts;

        // Load the texture
        if (!data.texture.loadFromFile(ts.getImagePath()))
        {
            std::cerr << "Failed to load tileset texture: "
                      << ts.getImagePath()
                      << '\n';

            continue;
        }

        tilesets.push_back(std::move(data));

        for (const auto& layer : map.getLayers())
        {
            if (layer->getType() != tmx::Layer::Type::Tile)
                continue;

            if (layer->getName() != "Ground")
                continue;

            const auto& tileLayer =
                layer->getLayerAs<tmx::TileLayer>();

            const auto& tiles = tileLayer.getTiles();

            const unsigned int mapWidth = map.getTileCount().x;
            const unsigned int tileWidth = map.getTileSize().x;
            const unsigned int tileHeight = map.getTileSize().y;

            for (std::size_t i = 0; i < tiles.size(); ++i)
            {
                // Empty tile
                if (tiles[i].ID == 0)
                    continue;

                unsigned int x = i % mapWidth;
                unsigned int y = i / mapWidth;

                CollisionRect collision;

                collision.bounds = sf::FloatRect(
                    x * tileWidth,
                    y * tileHeight,
                    tileWidth,
                    tileHeight
                );

                collisions.push_back(collision);
            }
        }

        std::cout << "Collision tiles: "
          << collisions.size()
          << '\n';
    }
}

void Leveltmx::draw(sf::RenderWindow& window)
{
    const unsigned int tileWidth = map.getTileSize().x;
    const unsigned int tileHeight = map.getTileSize().y;
    const unsigned int mapWidth = map.getTileCount().x;

    for (const auto& layer : map.getLayers())
    {
        if (layer->getType() != tmx::Layer::Type::Tile)
            continue;
        /*
        if(layer->getName() == "Ground")
            continue;
        */
        const auto& tileLayer =
            layer->getLayerAs<tmx::TileLayer>();

        const auto& tiles = tileLayer.getTiles();

        for (std::size_t i = 0; i < tiles.size(); ++i)
        {
            unsigned int gid = tiles[i].ID;

            // Empty tile
            if (gid == 0)
                continue;

            // Find the tileset that owns this GID
            const TilesetData* tilesetData = nullptr;

            for (const auto& data : tilesets)
            {
                if (gid >= data.tileset.getFirstGID())
                {
                    tilesetData = &data;
                }
            }

            if (tilesetData == nullptr)
                continue;

            const auto& tileset = tilesetData->tileset;

            // Convert global GID to local tile index
            unsigned int tileIndex =
                gid - tileset.getFirstGID();

            unsigned int columns =
                tileset.getColumnCount();

            unsigned int column =
                tileIndex % columns;

            unsigned int row =
                tileIndex / columns;

            // Create sprite
            sf::Sprite sprite;

            sprite.setTexture(tilesetData->texture);

            sprite.setTextureRect(
                sf::IntRect(
                    column * tileWidth,
                    row * tileHeight,
                    tileWidth,
                    tileHeight
                )
            );

            // Position in the map
            unsigned int x = i % mapWidth;
            unsigned int y = i / mapWidth;

            sprite.setPosition(
                x * tileWidth,
                y * tileHeight
            );

            window.draw(sprite);
        }
    }
}

float Leveltmx::getWidth() const
{
    return map.getTileCount().x * map.getTileSize().x;
}

float Leveltmx::getHeight() const
{
    return map.getTileCount().y * map.getTileSize().y;
}

sf::Vector2f Leveltmx::getPlayerSpawn() const
{
    for (const auto& layer : map.getLayers())
    {
        if (layer->getType() != tmx::Layer::Type::Object)
            continue;

        const auto& objectLayer =
            layer->getLayerAs<tmx::ObjectGroup>();

        for (const auto& object : objectLayer.getObjects())
        {
            if (object.getName() == "PlayerSpawn")
            {
                return sf::Vector2f(
                    object.getPosition().x,
                    object.getPosition().y
                );
            }
        }
    }

    std::cerr << "PlayerSpawn not found!\n";

    return sf::Vector2f(100.f, 100.f);
}

const std::vector<CollisionRect>& Leveltmx::getCollisions() const
{
    return collisions;
}
