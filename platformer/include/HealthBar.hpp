#pragma once
#include <SFML/Graphics.hpp>
#include "Animation.hpp"
#include <vector>

class HealthBar
{
    private:
        const sf::Texture* fullHeartTexture;
        const sf::Texture* emptyHeartTexture;

        std::vector<sf::Sprite> hearts;

        Animation lossAnimation;
        sf::Sprite lossSprite;

        int maxHealth;
        int currentHealth;

        float x;
        float y;
        float heartSpacing;

        bool lossAnimationPlaying;
        int lossHeartIndex;

    public:
        HealthBar();
        void setTextures(
            const sf::Texture& fullTexture,
            const sf::Texture& emptyTexture,
            const sf::Texture& lossTexture
        );
        void setHealth(int health);
        void setMaxHealth(int health);
        void setPosition(float x, float y);
        void draw(sf::RenderWindow& window) const;
        void update(float dt);

};
