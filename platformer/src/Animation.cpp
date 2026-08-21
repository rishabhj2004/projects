#include "Animation.hpp"

Animation::Animation()
    : texture(nullptr),
      frameWidth(0),
      frameHeight(0),
      frameCount(0),
      currentFrame(0),
      frameTime(0.f),
      timer(0.f)
{
}

void Animation::setTexture(const sf::Texture& texture)
{
    this->texture = &texture;
}

    
void Animation::setFrames(
    int width,
    int height,
    int count,
    float frameTime)
{
    frameWidth=width;
    frameHeight=height;
    frameCount=count;
    this->frameTime=frameTime;
    currentFrame=0;
    timer=0.f;
}

void Animation::update(float dt)
{
    timer+=dt;
    while(timer>=frameTime)
    {
        timer-=frameTime;
        currentFrame++;
        if(currentFrame>=frameCount)
        {
            currentFrame=0;
        }
    }
}

sf::IntRect Animation::getTextureRect() const
{
    return sf::IntRect(
        currentFrame * frameWidth,
        0,
        frameWidth,
        frameHeight
    );
}

void Animation::reset()
{
    currentFrame=0;
    timer=0.f;
}

const sf::Texture& Animation::getTexture() const
{
    return *texture;
}
