#include "Enemy.hpp"

#include <cmath>

Enemy::Enemy()
    : velocity(0.f, 0.f),
      facingRight(true),
      health(10),
      id(-1),
      deathAnimationFinished(false),
      dying(false),
      onGround(false),
      deathTimer(0.f),
      deathDissolveTime(1.f),
      dissolveShader(nullptr),
      hitShader(nullptr),
      knockbackSpeed(150.f),
      knockbackDistance(0.f),
      hitFlashTimer(0.f),
      hitFlashDuration(0.1f),
      deathHoldTime(4.f)
{
    shape.setSize(sf::Vector2f(25.f, 20.f));
    shape.setFillColor(sf::Color::Red);
    shape.setPosition(100.f, 100.f);

    previousPosition = shape.getPosition();
}

sf::Vector2f Enemy::getVelocity() const
{
    return velocity;
}

const sf::RectangleShape& Enemy::getShape() const
{
    return shape;
}
sf::FloatRect Enemy::getBounds() const
{
    return shape.getGlobalBounds();
}


void Enemy::setPosition(const sf::Vector2f& position)
{
    shape.setPosition(position);
    sprite.setPosition(
        position.x + shape.getSize().x / 2.f,
        position.y + shape.getSize().y
    );
}

sf::Vector2f Enemy::getPosition() const
{
    return shape.getPosition();
}

void Enemy::updateHitFlash(float dt)
{
    if (hitFlashTimer > 0.f)
    {
        hitFlashTimer -= dt;

        if (hitFlashTimer < 0.f)
        {
            hitFlashTimer = 0.f;
        }
    }
}

bool Enemy::updateDeath(float dt)
{
    if (!dying)
        return false;

    if (!deathAnimation.isFinished())
    {
        deathAnimation.update(dt);

        sprite.setTextureRect(
            deathAnimation.getTextureRect()
        );
    }

    updateSpritePosition();

    if (deathAnimation.isFinished())
    {
        deathTimer += dt;

        if (deathTimer >= deathHoldTime + deathDissolveTime)
        {
            deathAnimationFinished = true;
        }
    }

    return true;
}

bool Enemy::updateKnockback(float dt)
{
    if (knockbackDistance == 0.f)
        return false;

    float direction =
        knockbackDistance > 0.f ? 1.f : -1.f;

    float movement = knockbackSpeed * dt;

    if (std::abs(knockbackDistance) < movement)
    {
        movement = std::abs(knockbackDistance);
    }

    shape.move(direction * movement, 0.f);

    knockbackDistance -= direction * movement;

    return true;
}

void Enemy::updateSpritePosition()
{
    sprite.setPosition(
        shape.getPosition().x + shape.getSize().x / 2.f,
        shape.getPosition().y + shape.getSize().y
    );

    if (facingRight)
        sprite.setScale(1.f, 1.f);
    else
        sprite.setScale(-1.f, 1.f);
}

const sf::Sprite& Enemy::getSprite() const
{
    return sprite;
}

void Enemy::applyGravity(float dt, float gravity)
{
    velocity.y += gravity * dt;

    float maxFallSpeed = 900.f;

    if (velocity.y > maxFallSpeed)
        velocity.y = maxFallSpeed;
}

void Enemy::moveVertical(float dt)
{
    previousPosition.y = shape.getPosition().y;
    shape.move(0.f, velocity.y * dt);
}

void Enemy::stopVerticalMovement()
{
    velocity.y = 0.f;
}

sf::Vector2f Enemy::getPreviousPosition() const
{
    return previousPosition;
}

void Enemy::stopHorizontalMovement()
{
    velocity.x = 0.f;
}

void Enemy::land()
{
    onGround = true;
}

void Enemy::leaveGround()
{
    onGround = false;
}

bool Enemy::isOnGround() const
{
    return onGround;
}

void Enemy::takeDamage(int damage)
{
    hitFlashTimer = hitFlashDuration;
    health -= damage;
    if (health <= 0)
    {
        dying = true;
        deathTimer=0.f;
        deathAnimationFinished = false;
        velocity.x = 0.f;
        velocity.y = 0.f;

        deathAnimation.reset();

        sprite.setTexture(
            deathAnimation.getTexture()
        );
    }
}

bool Enemy::isDead() const
{
    return health <= 0;
}

void Enemy::setId(int id)
{
    this->id=id;
}

int Enemy::getId() const
{
    return id;
}

bool Enemy::isDying() const
{
    return dying;
}

bool Enemy::isDeathAnimationFinished() const
{
    return deathAnimationFinished;
}

void Enemy::setDissolveShader(sf::Shader& shader)
{
    dissolveShader = &shader;
}

sf::Shader* Enemy::getDissolveShader() const
{
    return dissolveShader;
}

float Enemy::getDissolveProgress() const
{
    if (!dying)
        return 0.f;

    if (deathTimer <= deathHoldTime)
        return 0.f;

    float progress =
        (deathTimer - deathHoldTime)
        / deathDissolveTime;

    if (progress > 1.f)
        progress = 1.f;

    return progress;
}

void Enemy::applyKnockback(float distance)
{
    knockbackDistance = distance;
}

void Enemy::setHitShader(sf::Shader& shader)
{
    hitShader = &shader;
}

sf::Shader* Enemy::getHitShader() const
{
    return hitShader;
}

bool Enemy::isHitFlashing() const
{
    return hitFlashTimer > 0.f;
}
