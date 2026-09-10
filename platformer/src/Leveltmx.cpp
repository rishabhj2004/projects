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
    if (sf::Shader::isAvailable())
    {
        platformShader.loadFromFile("assets/shaders/wind.frag", sf::Shader::Fragment);
    
        if (noiseTexture.loadFromFile("assets/textures/noise.png"))
        {
            // THIS IS VITAL for scrolling a texture indefinitely 
            noiseTexture.setRepeated(true);
            noiseTexture.setSmooth(true);
        }
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
        if(layer->getName() == "Platforms" || layer->getName() == "Ground")
            continue;
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

void Leveltmx::drawPlatforms(sf::RenderWindow& window, float totalTime)
{
    // Update global shader uniforms
    if (sf::Shader::isAvailable())
    {
        platformShader.setUniform("time", totalTime);
        platformShader.setUniform("texture", sf::Shader::CurrentTexture);
        platformShader.setUniform("noiseTex", noiseTexture);
    }

    const unsigned int tileW = map.getTileSize().x;
    const unsigned int tileH = map.getTileSize().y;
    const unsigned int mapW = map.getTileCount().x;
    const unsigned int mapH = map.getTileCount().y;

    // Grab the "Ground" layer to use as skeleton
    const tmx::TileLayer* groundLayer = nullptr;
    for (const auto& layer : map.getLayers())
    {
        if (layer->getType() == tmx::Layer::Type::Tile && layer->getName() == "Ground")
        {
            groundLayer = &layer->getLayerAs<tmx::TileLayer>();
            break;
        }
    }

    // Iterate through the "Platforms" layer
    for (const auto& layer : map.getLayers())
    {
        if (layer->getType() != tmx::Layer::Type::Tile || layer->getName() != "Platforms") continue;
        
        const auto& tileLayer = layer->getLayerAs<tmx::TileLayer>();
        const auto& platformTiles = tileLayer.getTiles();
        
        const auto& skeletonTiles = groundLayer ? groundLayer->getTiles() : platformTiles;

        for (std::size_t i = 0; i < platformTiles.size(); ++i)
        {
            unsigned int gid = platformTiles[i].ID;
            if (gid == 0) continue; // Skip empty space

            unsigned int x = i % mapW;
            unsigned int y = i / mapW;

            // --- NEW CHECK: Skip if overlapping Ground ---
            if (groundLayer && skeletonTiles[y * mapW + x].ID != 0)
            {
                // This Platform tile sits on Ground → rigid
                const TilesetData* tsData = nullptr;
                for (const auto& data : tilesets) {
                    if (gid >= data.tileset.getFirstGID()) tsData = &data;
                }
                if (!tsData) continue;

                unsigned int idx = gid - tsData->tileset.getFirstGID();
                unsigned int cols = tsData->tileset.getColumnCount();

                sf::Sprite sprite;
                sprite.setTexture(tsData->texture);
                sprite.setTextureRect(sf::IntRect((idx % cols) * tileW, (idx / cols) * tileH, tileW, tileH));
                sprite.setPosition(x * tileW, y * tileH);

                window.draw(sprite); // rigid draw
                continue;
            }

            // --- BORDER DETECTION ---
            bool airTop    = (y == 0 || skeletonTiles[(y - 1) * mapW + x].ID == 0);
            bool airBottom = (y == mapH - 1 || skeletonTiles[(y + 1) * mapW + x].ID == 0);
            bool airLeft   = (x == 0 || skeletonTiles[y * mapW + (x - 1)].ID == 0);
            bool airRight  = (x == mapW - 1 || skeletonTiles[y * mapW + (x + 1)].ID == 0);

            bool isLeafTile = (airTop || airBottom || airLeft || airRight);

            // Fetch texture properties
            const TilesetData* tsData = nullptr;
            for (const auto& data : tilesets) {
                if (gid >= data.tileset.getFirstGID()) tsData = &data;
            }
            if (!tsData) continue;

            unsigned int idx = gid - tsData->tileset.getFirstGID();
            unsigned int cols = tsData->tileset.getColumnCount();
            
            sf::Sprite sprite;
            sprite.setTexture(tsData->texture);
            sprite.setTextureRect(sf::IntRect((idx % cols) * tileW, (idx / cols) * tileH, tileW, tileH));
            sprite.setPosition(x * tileW, y * tileH);

            // --- DRAWING LOGIC ---
            if (isLeafTile && sf::Shader::isAvailable())
            {
                platformShader.setUniform("tilePos", sprite.getPosition());
                platformShader.setUniform("borders", sf::Glsl::Vec4(
                    airTop ? 1.0f : 0.0f,
                    airBottom ? 1.0f : 0.0f,
                    airLeft ? 1.0f : 0.0f,
                    airRight ? 1.0f : 0.0f
                ));
// --- TEXTURE BLEED BOUNDARIES (HALF-PIXEL INSET) ---
                sf::Vector2u tSize = tsData->texture.getSize();
                
                // 1. Get the raw, exact mathematical boundaries
                float rawLeft   = (float)((idx % cols) * tileW) / tSize.x;
                float rawTop    = (float)((idx / cols) * tileH) / tSize.y;
                float rawRight  = rawLeft + ((float)tileW / tSize.x);
                float rawBottom = rawTop + ((float)tileH / tSize.y);

                // 2. Calculate exactly how large half a pixel is in UV space
                float halfU = 0.5f / tSize.x;
                float halfV = 0.5f / tSize.y;

                // 3. Shrink the bounds inward to build an unbreakable safety wall
                platformShader.setUniform("uvBounds", sf::Glsl::Vec4(
                    rawLeft   + halfU, 
                    rawTop    + halfV, 
                    rawRight  - halfU, 
                    rawBottom - halfV
                ));
                
                window.draw(sprite, &platformShader);
            }
            else
            {
                window.draw(sprite); // rigid
            }
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
                std::cout<<object.getPosition().x<<" "<<object.getPosition().y<<"\n";
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

std::vector<EnemySpawn> Leveltmx::getEnemySpawns() const
{
    std::vector<EnemySpawn> enemySpawns;

    for (const auto& layer : map.getLayers())
    {
        if (layer->getType() != tmx::Layer::Type::Object)
            continue;

        if (layer->getName() != "Enemies")
            continue;
        const auto& objectLayer =
            layer->getLayerAs<tmx::ObjectGroup>();

        for (const auto& object : objectLayer.getObjects())
        {
            EnemySpawn spawn;

            spawn.type = object.getName();

            spawn.position = sf::Vector2f(
                object.getPosition().x,
                object.getPosition().y
            );

            enemySpawns.push_back(spawn);
        }
    }

    return enemySpawns;
}
