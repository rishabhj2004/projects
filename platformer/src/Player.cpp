#include <SFML/Graphics.hpp>
#include "Player.hpp"

Player::Player()
    :moveSpeed(250.0f),
     velocity(0.0f,0.0f),
     jumpSpeed(600.0f),
     onGround(false),
     facingRight(true),
     currentAnimation(nullptr),
     jumpHeld(false),
     coyoteTime(0.1f),
     coyoteTimer(0.f),
     jumpBufferTime(0.1f),
     jumpBufferTimer(0.f)
{
    shape.setSize(sf::Vector2f(20,50)); 
    shape.setFillColor(sf::Color::Blue); 
    shape.setPosition(sf::Vector2f(100,100));
    previousPosition=shape.getPosition();
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
    shape.move(velocity.x * dt, 0.f);
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

    if (facingRight)
        sprite.setScale(1.f, 1.f);
    else
        sprite.setScale(-1.f, 1.f);
}

void Player::updateAnimation(float dt)
{
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
            sprite.setTextureRect(sf::IntRect(64,0,64,64));
        }
        else
        {
            sprite.setTextureRect(sf::IntRect(128,0,64,64));
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
                 const sf::Texture& jump)
{
    idleAnimation.setTexture(idle);
    idleAnimation.setFrames(64, 64, 3, 0.15f);
    runAnimation.setTexture(run);
    runAnimation.setFrames(64, 64, 8, 0.1f);
    jumpAnimation.setTexture(jump);
    jumpAnimation.setFrames(64,64,3,0.2f);
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
