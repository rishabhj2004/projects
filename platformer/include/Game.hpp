#pragma once
#include <SFML/Graphics.hpp>
#include "Player.hpp"
#include <vector>
#include "assetManager.hpp"
#include "Leveltmx.hpp"

class Game{
    private:
        sf::View camera;
        void processEvents();
        void update(float dt);
        void render();
        sf::RenderWindow window;
        Player player;
        float gravity;
        void resolveHorizontalCollisions();
        void resolveVerticalCollisions();
        void updateCamera(float dt);
        assetManager assets;
        sf::Sprite bgSprite;
        Leveltmx level;
    public:
        Game();
        void run();
};
