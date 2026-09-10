#pragma once
#include <SFML/Graphics.hpp>
#include "Animation.hpp"
#include <vector>

enum class animationState{
    Idle,
    Run,
    Jump,
    Attack
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
        bool attackFacingRight;
        Animation idleAnimation;
        Animation runAnimation;
        Animation jumpAnimation;
        Animation* currentAnimation;
        Animation attackAnimation;
        float coyoteTime;
        bool attacking;
        float coyoteTimer;
        float jumpBufferTime;
        float jumpBufferTimer;
        float attackCooldown;
        float attackCooldownTimer;
        float attackMoveSpeed;
        sf::RectangleShape attackHitbox;
        std::vector<int> hitEnemies;
        int health;
        int maxHealth;
        float knockbackSpeed;
        float knockbackDistance;
        float invincibilityTime;
        float invincibilityTimer;
        sf::Shader* hitShader;
        float hitFlashTimer;
        float hitFlashDuration;
        float nextHitFlashTime;
        bool dead;

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
                const sf::Texture& jump,
                const sf::Texture& attack
                 );
        void updateTimers(float dt);
        void startAttack();
        bool isAttacking() const;
        void updateAttackCooldown(float dt);
        const sf::RectangleShape& getAttackHitbox() const; 
        void updateAttackHitbox();
        bool hasHitEnemy(int id) const;
        void addHitEnemy(int id);
        void clearHitEnemies();
        void takeDamage(int damage);
        int getHealth() const;
        int getMaxHealth() const;
        bool isDead() const;
        void applyKnockback(float distance);
        void updateInvincibility(float dt);
        bool isInvincible() const;
        void setHitShader(sf::Shader& shader);
        sf::Shader* getHitShader() const;
        bool isHitFlashing() const;
        void respawn(const sf::Vector2f& position);
};
