#pragma once

#include <vector>
#include <memory>

#include "Enemy.hpp"
#include "Leveltmx.hpp"
#include "assetManager.hpp"
#include "Player.hpp"

class EnemyManager
{
private:
    std::vector<std::unique_ptr<Enemy>> enemies;
    void resolveHorizontalCollisions(
        Enemy& enemy,
        const Leveltmx& level
    );

    void resolveVerticalCollisions(
        Enemy& enemy,
        const Leveltmx& level
    );
    bool hasGroundAhead(
        const Enemy& enemy,
        const Leveltmx& level
    );

public:
    EnemyManager();

    void loadFromLevel(
        const Leveltmx& level,
        assetManager& assets
    );
    void render(sf::RenderWindow& window) const;
    void update(float dt, const Leveltmx& level, float gravity);
    void checkPlayerAttack(Player& player);
    void checkEnemyPlayerCollision(Player& player);
    void reset(
        const Leveltmx& level,
        assetManager& assets
    );
};
