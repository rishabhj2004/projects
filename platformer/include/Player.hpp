#pragma once
#include <SFML/Graphics.hpp>
#include "Animation.hpp"

enum class animationState{
    Idle,
    Run
};
class Player
{
    private:
        sf::RectangleShape shape;
        sf::Sprite sprite;
        float moveSpeed;
        sf::Vector2f velocity;
        float jumpSpeed;
        bool jumpHeld;
        bool onGround;
        sf::Vector2f previousPosition;
        bool facingRight;
        Animation idleAnimation;
        Animation runAnimation;
        Animation jumpAnimation;
        Animation* currentAnimation;
        float coyoteTime;
        float coyoteTimer;
        float jumpBufferTime;
        float jumpBufferTimer;

    public:
        Player();
        const sf::RectangleShape& getShape() const;
        void moveLeft();
        void moveRight();
        void applyGravity(float dt, float gravity);
        void moveHorizontal(float dt);
        void moveVertical(float dt);
        void stopHorizontalMovement();
        void stopVerticalMovement();
        sf::FloatRect getBounds() const;
        void setPosition(const sf::Vector2f& position);
        sf::Vector2f getPosition() const;
        void startJump();
        void stopJump();
        void land();
        sf::Vector2f getPreviousPosition() const;
        void leaveGround();
        bool isOnGround() const;
        bool isFacingRight();
        void updateSpritePosition();
        void updateAnimation(float dt);
        const sf::Sprite& getSprite() const;
        void setTextures(
                const sf::Texture& idle,
                 const sf::Texture& run, 
                 const sf::Texture& jump);
        void updateTimers(float dt);
};
