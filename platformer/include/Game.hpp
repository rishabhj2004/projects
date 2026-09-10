#pragma once
#include <SFML/Graphics.hpp>
#include "Player.hpp"
#include <vector>
#include "assetManager.hpp"
#include "Leveltmx.hpp"
#include "SaveManager.hpp"
#include "EnemyManager.hpp"
#include "HealthBar.hpp"

class Game{
    private:
        sf::View camera;
        void processEvents();
        void update(float dt);
        void render();
        sf::RenderWindow window;
        Player player;
        EnemyManager enemyManager;
        float gravity;
        void resolveHorizontalCollisions();
        void resolveVerticalCollisions();
        void updateCamera(float dt);
        assetManager assets;
        sf::Sprite bgSprite;
        Leveltmx level;
        SaveData saveData;
        void saveGame();
        sf::Clock absoluteClock;
        float cameraLookAhead;
        float respawnTimer;
        float respawnDelay;
        HealthBar healthBar;
    public:
        Game();
        void run();
};
