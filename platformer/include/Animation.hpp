#pragma once
#include <SFML/Graphics.hpp>

class Animation
{
    private:
        const sf::Texture* texture;
        int frameWidth;
        int frameHeight;
        int frameCount;
        int currentFrame;
        float frameTime;
        float timer;
    public:
        Animation();
        void setTexture(const sf::Texture& texture);
        void setFrames(
                int width,
                int height,
                int count,
                float frameTime);
        void update(float dt);
        sf::IntRect getTextureRect() const;
        void reset();
        const sf::Texture& getTexture() const;
};
