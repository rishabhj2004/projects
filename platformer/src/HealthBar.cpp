#include "HealthBar.hpp"

HealthBar::HealthBar()
    : maxHealth(3),
      currentHealth(0),
      fullHeartTexture(nullptr),
      emptyHeartTexture(nullptr),
      x(0.f),
      y(0.f),
      heartSpacing(40.f),
      lossAnimationPlaying(false),
      lossHeartIndex(-1)
{
}

void HealthBar::setTextures(
    const sf::Texture& fullTexture,
    const sf::Texture& emptyTexture,
    const sf::Texture& lossTexture
)
{
    fullHeartTexture = &fullTexture;
    emptyHeartTexture = &emptyTexture;

    lossAnimation.setTexture(lossTexture);
    lossAnimation.setFrames(32, 32, 5, 0.1f);

    lossSprite.setTexture(lossTexture);
    lossSprite.setTextureRect(
        lossAnimation.getTextureRect()
    );

    setHealth(currentHealth);
}

void HealthBar::setHealth(int health)
{
    if (health == currentHealth)
        return;

    int previousHealth = currentHealth;

    currentHealth = health;

    if (currentHealth < 0)
        currentHealth = 0;

    if (currentHealth > maxHealth)
        currentHealth = maxHealth;

    if (currentHealth < previousHealth)
    {
        lossHeartIndex = currentHealth;

        lossAnimation.reset();
        lossAnimationPlaying = true;

        lossSprite.setPosition(
            x + lossHeartIndex * heartSpacing,
            y
        );
    }

    hearts.clear();

    for (int i = 0; i < maxHealth; i++)
    {
        sf::Sprite heart;

        if (i < currentHealth)
        {
            heart.setTexture(*fullHeartTexture);
        }
        else
        {
            heart.setTexture(*emptyHeartTexture);
        }

        heart.setPosition(
            x + i * heartSpacing,
            y
        );

        hearts.push_back(heart);
    }
}

void HealthBar::setMaxHealth(int health)
{
    maxHealth = health;

    if (maxHealth <= 0)
        maxHealth = 1;

    setHealth(currentHealth);
}

void HealthBar::setPosition(float x, float y)
{
    this->x = x;
    this->y = y;

    setHealth(currentHealth);
}

void HealthBar::update(float dt)
{
    if (!lossAnimationPlaying)
        return;

    lossAnimation.update(dt);

    lossSprite.setTextureRect(
        lossAnimation.getTextureRect()
    );

    if (lossAnimation.isFinished())
    {
        lossAnimationPlaying = false;
        lossHeartIndex = -1;
    }
}

void HealthBar::draw(sf::RenderWindow& window) const
{
    for (const auto& heart : hearts)
    {
        window.draw(heart);
    }

    if (lossAnimationPlaying && lossHeartIndex >= 0)
    {
        window.draw(lossSprite);
    }
}
