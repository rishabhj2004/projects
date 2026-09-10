#include "Game.hpp"
#include <SFML/Graphics.hpp>
#include <iostream>

Game::Game()
    :window(sf::VideoMode(1280,720),"Platformer"),
    gravity(700.0f),
    respawnTimer(0.f),
    respawnDelay(1.5f),
    level("assets/levels/level1.tmx"),
    camera(sf::FloatRect(0.f,0.f,1280.f,720.f)),
    cameraLookAhead(0.f)
{
    window.setFramerateLimit(60);
    window.setKeyRepeatEnabled(false);
    camera.zoom(0.5f);

    assets.loadShader("dissolve","assets/shaders/dissolve.frag");
    assets.loadShader("hit","assets/shaders/hit.frag");

    assets.loadTexture("player_idle","assets/textures/player_idle.png");
    assets.loadTexture("player_run", "assets/textures/player_run.png");
    assets.loadTexture("player_jump","assets/textures/player_jump.png");
    assets.loadTexture("player_attack","assets/textures/player_attack1.png");
    assets.loadTexture("snail_walk","assets/textures/snail_walk.png");
    assets.loadTexture("snail_death","assets/textures/snail_death.png");
    assets.loadTexture("heart", "assets/textures/heart.png");
    assets.loadTexture("empty_heart","assets/textures/empty_heart.png");
    assets.loadTexture("heart_loss","assets/textures/heart_loss.png");

    player.setTextures(assets.getTexture("player_idle"),assets.getTexture("player_run"),assets.getTexture("player_jump"), assets.getTexture("player_attack"));
    player.setHitShader(
        assets.getShader("hit")
    );
    healthBar.setTextures(
        assets.getTexture("heart"),
        assets.getTexture("empty_heart"),
        assets.getTexture("heart_loss")
    );
    healthBar.setPosition(30.f, 30.f);
    healthBar.setMaxHealth(player.getMaxHealth());
    healthBar.setHealth(player.getHealth());

    saveData=SaveManager::load();
    if(SaveManager::hasSave())
    {
        player.setPosition(saveData.checkpoint);
    }
    else
    {
        player.setPosition(level.getPlayerSpawn());
    }
    sf::Vector2f spawn=player.getPosition();
    enemyManager.loadFromLevel(level, assets);
    camera.setCenter(
        spawn.x + 200.f,
        spawn.y + 100.f
    );
}

void Game::run()
{
    sf::Clock clock;
    while(window.isOpen())
    {
        float dt=clock.restart().asSeconds();
        processEvents();
        update(dt);
        render();
    }
}

void Game::processEvents()
{
    sf::Event event;
    while(window.pollEvent(event))
    {
        if(event.type==sf::Event::Closed)
        {
            window.close();
        }
        if(event.type==sf::Event::KeyPressed)
        {
            if(event.key.code==sf::Keyboard::Space)
            {
                player.startJump();
            }
            if(event.key.code==sf::Keyboard::D && !player.isInvincible())
            {
                player.startAttack();
            }
            if(event.key.code==sf::Keyboard::F5)
            {
                saveGame();
            }
        }
        if(event.type==sf::Event::KeyReleased)
        {
           if (event.key.code == sf::Keyboard::Space)
            {
                player.stopJump();
            }
        }
    }
}

void Game::update(float dt)
{
    if (player.isDead())
    {
        respawnTimer += dt;
        healthBar.update(dt);

        if (respawnTimer >= respawnDelay)
        {
            sf::Vector2f spawn;

            if (SaveManager::hasSave())
            {
                saveData = SaveManager::load();
                spawn = saveData.checkpoint;
            }
            else
            {
                spawn = level.getPlayerSpawn();
            }

            player.respawn(spawn);
            enemyManager.reset(level, assets);
            respawnTimer = 0.f;

            camera.setCenter(
                spawn.x + 200.f,
                spawn.y + 100.f
            );
        }

        return;
    }
    if (!(player.isAttacking() && player.isOnGround()))
    {
        player.stopHorizontalMovement();

        if (sf::Keyboard::isKeyPressed(sf::Keyboard::Right))
        {
            player.moveRight();
        }

        if (sf::Keyboard::isKeyPressed(sf::Keyboard::Left))
        {
            player.moveLeft();
        }
    } 

    //horizontal movement
    player.moveHorizontal(dt);
    resolveHorizontalCollisions();
    player.updateTimers(dt);
    player.updateAttackCooldown(dt);
    player.updateInvincibility(dt);
    //vertical movement
    player.applyGravity(dt,gravity);
    player.moveVertical(dt);
    resolveVerticalCollisions();
    
    //camera movement
    updateCamera(dt);
    player.updateSpritePosition();
    player.updateAttackHitbox();
    player.updateAnimation(dt);

    //enemy collisions
    enemyManager.update(dt, level, gravity);
    enemyManager.checkPlayerAttack(player);
    enemyManager.checkEnemyPlayerCollision(player);
    healthBar.setHealth(player.getHealth());
    healthBar.update(dt);
}

void Game::render()
{
    window.clear();

    // World
    window.setView(camera);

    level.draw(window);

    if (player.isHitFlashing())
    {
        sf::Shader* shader = player.getHitShader();

        if (shader)
        {
            window.draw(player.getSprite(), shader);
        }
        else
        {
            window.draw(player.getSprite());
        }
    }
    else
    {
        window.draw(player.getSprite());
    }

    enemyManager.render(window);

    float totalTime = absoluteClock.getElapsedTime().asSeconds();
    level.drawPlatforms(window, totalTime);

    // UI
    window.setView(window.getDefaultView());

    healthBar.draw(window);

    window.display();
}

void Game::resolveHorizontalCollisions()
{
    for (const auto& collision : level.getCollisions())
    {
        if (player.getBounds().intersects(collision.bounds))
        {
            if(player.getPreviousPosition().x+player.getBounds().width<=collision.bounds.left)
            {
                player.setPosition(
                        sf::Vector2f(
                            collision.bounds.left-player.getBounds().width-0.1,
                            player.getPosition().y
                            )
                        );
                player.stopHorizontalMovement();
                break;
            }
            else if(player.getPreviousPosition().x>=collision.bounds.left+collision.bounds.width)
            {
                player.setPosition(
                        sf::Vector2f(
                            collision.bounds.left+collision.bounds.width,
                            player.getPosition().y
                            )
                        );
                player.stopHorizontalMovement();
                break;
            }
        }
    }
}

void Game::resolveVerticalCollisions()
{
    bool grounded = false;

    for (const auto& collision : level.getCollisions())
    {
        if (!player.getBounds().intersects(collision.bounds))
        {
            continue;
        }

        if (player.getPreviousPosition().y + player.getBounds().height
            <= collision.bounds.top+5.f)
        {
            grounded=true;

            player.setPosition(
                sf::Vector2f(
                    player.getPosition().x,
                    collision.bounds.top - player.getBounds().height
                )
            );

            break;
        }
        else if(player.getPreviousPosition().y>=collision.bounds.top+collision.bounds.height)
        {
            player.setPosition(
                    sf::Vector2f(
                        player.getPosition().x,
                        collision.bounds.top+collision.bounds.height
                        )
                    );
            player.stopVerticalMovement();
            break;
        }
    }
    if(grounded)
    {
        player.stopVerticalMovement();
        player.land();
    }
    else{
        player.leaveGround();
    }
}

void Game::updateCamera(float dt)
{
    float targetLookAhead;

    if (player.isFacingRight())
        targetLookAhead = 200.f;
    else
        targetLookAhead = -200.f;

    float lookAheadSpeed = 300.f;

    if (cameraLookAhead < targetLookAhead)
    {
        cameraLookAhead += lookAheadSpeed * dt;

        if (cameraLookAhead > targetLookAhead)
            cameraLookAhead = targetLookAhead;
    }
    else if (cameraLookAhead > targetLookAhead)
    {
        cameraLookAhead -= lookAheadSpeed * dt;

        if (cameraLookAhead < targetLookAhead)
            cameraLookAhead = targetLookAhead;
    }

    float targetX = player.getPosition().x + cameraLookAhead;

    float currentX = camera.getCenter().x;
    float currentY = camera.getCenter().y;

    float cameraSpeed = 1.5f;

    float horizontalDeadZone = 100.f;
    float verticalDeadZone = 100.f;

    if (targetX > currentX + horizontalDeadZone)
    {
        currentX += (targetX - (currentX + horizontalDeadZone)) * cameraSpeed * dt;
    }
    else if (targetX < currentX - horizontalDeadZone)
    {
        currentX += (targetX - (currentX - horizontalDeadZone)) * cameraSpeed * dt;
    }

    float targetY = player.getPosition().y+50.f;

    if (targetY > currentY)
    {
        currentY += (targetY - currentY) * cameraSpeed * dt;
    }
    else if (targetY < currentY)
    {
        currentY += (targetY - (currentY)) * cameraSpeed * dt;
    }

    float halfWidth = camera.getSize().x / 2.f;
    if (currentX < halfWidth)
    {
        currentX = halfWidth;
    }

    if (currentX > level.getWidth() - halfWidth)
    {
        currentX = level.getWidth() - halfWidth;
    }

    float halfHeight = camera.getSize().y / 2.f;
    if (currentY < halfHeight)
    {
        currentY = halfHeight;
    }

    if (currentY > level.getHeight() - halfHeight)
    {
        currentY = level.getHeight() - halfHeight;
    }

    camera.setCenter(currentX, currentY);
}

void Game::saveGame()
{
    saveData.currentRoom = "level1.tmx";
    saveData.checkpoint = player.getPosition();

    SaveManager::save(saveData);
}
