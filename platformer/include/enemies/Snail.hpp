#pragma once

#include "Enemy.hpp"

class Snail : public Enemy
{
private:
    float moveSpeed;
    Animation walkAnimation;

public:
    Snail();

    void setTexture(
        const sf::Texture& walk,
        const sf::Texture& death
    );

    void update(float dt) override;

    void turnAround() override;
};
