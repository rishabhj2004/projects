#include <SFML/Graphics.hpp>
#include "Player.hpp"
#include <iostream>
#include <cmath>
Player::Player()
    :moveSpeed(170.0f),
     velocity(0.0f,0.0f),
     jumpSpeed(400.0f),
     onGround(false),
     facingRight(true),
     currentAnimation(nullptr),
     jumpHeld(false),
     attacking(false),
     attackFacingRight(true),
     coyoteTime(0.1f),
     coyoteTimer(0.f),
     attackCooldown(0.07f),
     attackCooldownTimer(0.f),
     attackMoveSpeed(50.0f),
     jumpBufferTime(0.1f),
     maxHealth(5),
     health(5),
     jumpBufferTimer(0.f),
     invincibilityTime(1.f),
     invincibilityTimer(0.f),
     knockbackSpeed(100.f),
     knockbackDistance(0.f),
     hitFlashTimer(0.f),
     hitFlashDuration(0.1f),
     nextHitFlashTime(0.f),
     dead(false),
     hitShader(nullptr)
{
    shape.setSize(sf::Vector2f(10,30)); 
    shape.setFillColor(sf::Color::Blue); 
    shape.setPosition(sf::Vector2f(100,100));
    previousPosition=shape.getPosition();
    attackHitbox.setSize(sf::Vector2f(30.f, 25.f));
    attackHitbox.setFillColor(sf::Color::Transparent);
    attackHitbox.setOutlineColor(sf::Color::Red);
    attackHitbox.setOutlineThickness(2.f);
}

const sf::RectangleShape& Player::getShape() const
{
    return shape;
}

void Player::moveLeft()
{
    velocity.x=-moveSpeed;
    facingRight=false;
}

void Player::moveRight()
{
    velocity.x=moveSpeed;
    facingRight=true;
}

void Player::applyGravity(float dt,float gravity)
{       
    float gravityMultiplier = 1.0f;
    if (velocity.y > 0.f || !jumpHeld)
    {
        gravityMultiplier = 2.0f; 
    }
    velocity.y += gravity * gravityMultiplier * dt;
    float maxFallSpeed = 900.0f;
    if (velocity.y > maxFallSpeed)
    {
        velocity.y = maxFallSpeed;
    }
}

void Player::moveHorizontal(float dt)
{
    previousPosition.x = shape.getPosition().x;

    if (knockbackDistance != 0.f)
    {
        float direction =
            knockbackDistance > 0.f ? 1.f : -1.f;

        float movement = knockbackSpeed * dt;

        if (std::abs(knockbackDistance) < movement)
        {
            movement = std::abs(knockbackDistance);
        }

        shape.move(direction * movement, 0.f);

        knockbackDistance -= direction * movement;
    }
    else
    {
        shape.move(velocity.x * dt, 0.f);
    }
}

void Player::moveVertical(float dt)
{
    previousPosition.y = shape.getPosition().y;
    shape.move(0.f, velocity.y * dt);
}

void Player::stopHorizontalMovement()
{
    velocity.x=0;
}

void Player::stopVerticalMovement()
{
    velocity.y=0;
}

sf::FloatRect Player::getBounds() const
{
    return shape.getGlobalBounds();
}

void Player::land()
{
    onGround=true;
    jumpHeld=false;
}

void Player::setPosition(const sf::Vector2f& position)
{
    shape.setPosition(position);
}

sf::Vector2f Player::getPosition() const
{
    return shape.getPosition();
}

void Player::startJump()
{
    jumpHeld = true;
    jumpBufferTimer = jumpBufferTime;
}

void Player::stopJump()
{
    jumpHeld = false;
    if (velocity.y < 0.f)
    {
        velocity.y *= 0.5f; 
    }
}


sf::Vector2f Player::getPreviousPosition() const
{
    return previousPosition;
}

void Player::leaveGround(){
    onGround=false;
}

bool Player::isOnGround() const
{
    return onGround;
}

bool Player::isFacingRight()
{
    return facingRight;
}

void Player::updateSpritePosition()
{
    sprite.setPosition(
        shape.getPosition().x + shape.getSize().x / 2.f - 2.f,
        shape.getPosition().y + shape.getSize().y
    );

    if (attacking)
    {
        if (attackFacingRight)
            sprite.setScale(1.f, 1.f);
        else
            sprite.setScale(-1.f, 1.f);
    }
    else
    {
        if (facingRight)
            sprite.setScale(1.f, 1.f);
        else
            sprite.setScale(-1.f, 1.f);
    }
}

void Player::updateAnimation(float dt)
{
    if (attacking)
    {
        attackAnimation.update(dt);

        sprite.setTextureRect(
            attackAnimation.getTextureRect()
        );

        if (attackAnimation.isFinished())
        {
            attacking = false;
            attackCooldownTimer = attackCooldown;
        }

        return;
    }
    Animation* newAnimation;

    if (!onGround)
    {
        if (currentAnimation != &jumpAnimation)
        {
            currentAnimation = &jumpAnimation;
            sprite.setTexture(jumpAnimation.getTexture());
        }

        if (velocity.y < -50.f)
        {
            sprite.setTextureRect(sf::IntRect(0,0,64,64));
        }   
        else if (velocity.y < 50.f)
        {
            sprite.setTextureRect(sf::IntRect(0,0,64,64));
        }
        else
        {
            sprite.setTextureRect(sf::IntRect(64,0,64,64));
        }

        return;
    }

    else if (velocity.x == 0.f)
    {
        newAnimation = &idleAnimation;
    }
    else
    {
        newAnimation = &runAnimation;
    }

    if (newAnimation != currentAnimation)
    {
        currentAnimation = newAnimation;
        currentAnimation->reset();
        sprite.setTexture(currentAnimation->getTexture());
    }

    currentAnimation->update(dt);

    sprite.setTextureRect(
        currentAnimation->getTextureRect()
    );
}


const sf::Sprite& Player::getSprite() const
{
    return sprite;
}

void Player::setTextures(const sf::Texture& idle,
                 const sf::Texture& run,
                 const sf::Texture& jump,
                 const sf::Texture& attack
                 )
{
    idleAnimation.setTexture(idle);
    idleAnimation.setFrames(64, 64, 2, 0.2f);
    runAnimation.setTexture(run);
    runAnimation.setFrames(64, 64, 5, 0.07f);
    jumpAnimation.setTexture(jump);
    jumpAnimation.setFrames(64,64,2,0.2f);
    attackAnimation.setTexture(attack);
    attackAnimation.setFrames(64, 64, 5, 0.05f);
    currentAnimation = &idleAnimation;
    sprite.setTexture(currentAnimation->getTexture());
    sprite.setTextureRect(currentAnimation->getTextureRect());
    sprite.setTextureRect(sf::IntRect(0, 0, 64, 64));
    sprite.setOrigin(32.f, 64.f);
    sprite.setScale(1.f, 1.f);
}

void Player::updateTimers(float dt)
{
    if (onGround)
    {
        coyoteTimer = coyoteTime;
    }
    else
    {
        coyoteTimer -= dt;
        if (coyoteTimer < 0.f)
        {
            coyoteTimer = 0.f;
        }
    }
    if (jumpBufferTimer > 0.f)
    {
        jumpBufferTimer -= dt;

        if (jumpBufferTimer < 0.f)
        {
            jumpBufferTimer = 0.f;
        }
    }
    if (jumpBufferTimer > 0.f && coyoteTimer > 0.f)
    {
        velocity.y = -jumpSpeed;
        onGround = false;

        jumpBufferTimer = 0.f;
        coyoteTimer = 0.f;
    }
}

void Player::startAttack()
{
    if (attacking || attackCooldownTimer > 0.f)
        return;
    attacking = true;
    attackFacingRight = facingRight;
    clearHitEnemies();
    if (onGround)
    {
        if (attackFacingRight)
            velocity.x = attackMoveSpeed;
        else
            velocity.x = -attackMoveSpeed;
    }
    currentAnimation = &attackAnimation;
    currentAnimation->reset();

    sprite.setTexture(attackAnimation.getTexture());
}

bool Player::isAttacking() const
{
    return attacking;
}

void Player::updateAttackCooldown(float dt)
{
    if (attackCooldownTimer > 0.f)
    {
        attackCooldownTimer -= dt;

        if (attackCooldownTimer < 0.f)
        {
            attackCooldownTimer = 0.f;
        }
    }
}

void Player::updateAttackHitbox()
{
    if (!attacking)
    {
        attackHitbox.setPosition(-1000.f, -1000.f);
        return;
    }
    sf::FloatRect playerBounds = getBounds();

    bool facingRightNow = attackFacingRight;

    float x;

    if (facingRightNow)
    {
        x = playerBounds.left + playerBounds.width;
    }
    else
    {
        x = playerBounds.left - attackHitbox.getSize().x;
    }

    float y =
        playerBounds.top
        + playerBounds.height / 2.f
        - attackHitbox.getSize().y / 2.f;

    attackHitbox.setPosition(x, y);
}

const sf::RectangleShape& Player::getAttackHitbox() const
{
    return attackHitbox;
}

bool Player::hasHitEnemy(int id) const
{
    for (int hitId : hitEnemies)
    {
        if (hitId == id)
        return true;
    }
    return false;
}

void Player::addHitEnemy(int id)
{
    hitEnemies.push_back(id);
}

void Player::clearHitEnemies()
{
    hitEnemies.clear();
}

void Player::takeDamage(int damage)
{
    if (isInvincible() || dead)
        return;

    health -= damage;

    if (health <= 0)
    {
        health = 0;
        dead = true;
        velocity = sf::Vector2f(0.f, 0.f);
        knockbackDistance = 0.f;
    }

    invincibilityTimer = invincibilityTime;
    hitFlashTimer = hitFlashDuration;
    nextHitFlashTime = 0.35f;
}

int Player:: getHealth() const
{
    return health;
}

int Player:: getMaxHealth() const
{
    return maxHealth;
}

bool Player::isDead() const
{
    return dead;
}
void Player::applyKnockback(float distance)
{
    knockbackDistance = distance;
}

void Player::updateInvincibility(float dt)
{
    if (invincibilityTimer > 0.f)
    {
        invincibilityTimer -= dt;

        if (invincibilityTimer < 0.f)
        {
            invincibilityTimer = 0.f;
        }
    }

    if (hitFlashTimer > 0.f)
    {
        hitFlashTimer -= dt;

        if (hitFlashTimer < 0.f)
        {
            hitFlashTimer = 0.f;
        }
    }

    if (invincibilityTimer > 0.f &&
        nextHitFlashTime > 0.f)
    {
        nextHitFlashTime -= dt;

        if (nextHitFlashTime <= 0.f)
        {
            hitFlashTimer = hitFlashDuration;

            if (invincibilityTimer > 0.35f)
            {
                nextHitFlashTime = 0.35f;
            }
            else
            {
                nextHitFlashTime = 0.f;
            }
        }
    }
}
bool Player::isInvincible() const
{
    return invincibilityTimer > 0.f;
}

void Player::setHitShader(sf::Shader& shader)
{
    hitShader = &shader;
}

sf::Shader* Player::getHitShader() const
{
    return hitShader;
}

bool Player::isHitFlashing() const
{
    return hitFlashTimer > 0.f;
}

void Player::respawn(const sf::Vector2f& position)
{
    health = maxHealth;
    dead = false;

    velocity = sf::Vector2f(0.f, 0.f);
    knockbackDistance = 0.f;

    invincibilityTimer = 0.f;
    hitFlashTimer = 0.f;
    nextHitFlashTime = 0.f;

    setPosition(position);
}
