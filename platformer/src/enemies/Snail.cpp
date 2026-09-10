#include "enemies/Snail.hpp"

Snail::Snail()
    : moveSpeed(50.f)
{
    velocity.x = moveSpeed;

    shape.setSize(sf::Vector2f(25.f, 20.f));
    shape.setFillColor(sf::Color::Red);
    shape.setPosition(100.f, 100.f);

    previousPosition = shape.getPosition();
}

void Snail::setTexture(
    const sf::Texture& walk,
    const sf::Texture& death
)
{
    walkAnimation.setTexture(walk);
    walkAnimation.setFrames(32, 32, 3, 0.15f);

    deathAnimation.setTexture(death);
    deathAnimation.setFrames(32, 32, 3, 0.15f);

    sprite.setTexture(
        walkAnimation.getTexture()
    );

    sprite.setTextureRect(
        walkAnimation.getTextureRect()
    );

    sprite.setOrigin(16.f, 32.f);
}

void Snail::turnAround()
{
    velocity.x = -velocity.x;
    facingRight = !facingRight;
}

void Snail::update(float dt)
{
    previousPosition.x = shape.getPosition().x;

    updateHitFlash(dt);

    if (updateDeath(dt))
        return;

    walkAnimation.update(dt);

    sprite.setTextureRect(
        walkAnimation.getTextureRect()
    );

    if (!updateKnockback(dt))
    {
        shape.move(velocity.x * dt, 0.f);
    }

    updateSpritePosition();
}

