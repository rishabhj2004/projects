#pragma once

#include <SFML/Graphics.hpp>
#include "Animation.hpp"

class Enemy
{
protected:
    sf::Sprite sprite;
    sf::RectangleShape shape;

    sf::Vector2f velocity;
    sf::Vector2f previousPosition;

    bool facingRight;
    bool onGround;

    int health;
    int id;

    bool dying;
    bool deathAnimationFinished;

    Animation deathAnimation;

    float deathTimer;
    float deathHoldTime;
    float deathDissolveTime;

    sf::Shader* dissolveShader;
    sf::Shader* hitShader;

    float knockbackSpeed;
    float knockbackDistance;

    float hitFlashTimer;
    float hitFlashDuration;
    bool updateDeath(float dt);
    void updateHitFlash(float dt);
    bool updateKnockback(float dt);
    void updateSpritePosition();

public:
    Enemy();
    virtual ~Enemy() = default;

    virtual void update(float dt) = 0;

    const sf::RectangleShape& getShape() const;
    sf::FloatRect getBounds() const;

    void setPosition(const sf::Vector2f& position);
    sf::Vector2f getPosition() const;

    const sf::Sprite& getSprite() const;

    void applyGravity(float dt, float gravity);
    void moveVertical(float dt);
    void stopVerticalMovement();

    sf::Vector2f getPreviousPosition() const;
    sf::Vector2f getVelocity() const;

    void stopHorizontalMovement();

    void land();
    void leaveGround();
    bool isOnGround() const;

    void takeDamage(int damage);
    bool isDead() const;

    bool isDeathAnimationFinished() const;

    void setId(int id);
    int getId() const;

    bool isDying() const;

    void setDissolveShader(sf::Shader& shader);
    sf::Shader* getDissolveShader() const;
    float getDissolveProgress() const;

    void applyKnockback(float distance);

    void setHitShader(sf::Shader& shader);
    sf::Shader* getHitShader() const;
    bool isHitFlashing() const;

    virtual void turnAround() = 0;
};
