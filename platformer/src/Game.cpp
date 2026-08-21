#include "Game.hpp"
#include <SFML/Graphics.hpp>
#include <iostream>

Game::Game()
    :window(sf::VideoMode(1280,720),"Platformer"),
    gravity(980.0f),
    level("assets/levels/level1.tmx"),
    camera(sf::FloatRect(0.f,0.f,1280.f,720.f))
{
    window.setFramerateLimit(60);
    window.setKeyRepeatEnabled(false);
    assets.loadTexture("bg","assets/textures/background.png");
    assets.loadTexture("player_idle","assets/textures/player_idle.png");
    assets.loadTexture("player_run", "assets/textures/player_run.png");
    assets.loadTexture("player_jump","assets/textures/player_jump.png");
    bgSprite.setTexture(assets.getTexture("bg"));
    player.setTextures(assets.getTexture("player_idle"),assets.getTexture("player_run"),assets.getTexture("player_jump"));
    sf::Vector2f spawn = level.getPlayerSpawn();

    player.setPosition(spawn);

    camera.setCenter(
        spawn.x + 250.f,
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
    player.stopHorizontalMovement();

    if (sf::Keyboard::isKeyPressed(sf::Keyboard::Right))
    {
        player.moveRight();
    }

    if (sf::Keyboard::isKeyPressed(sf::Keyboard::Left))
    {
        player.moveLeft();
    }

    //horizontal movement
    player.moveHorizontal(dt);
    resolveHorizontalCollisions();
    player.updateTimers(dt);
    //vertical movement
    player.applyGravity(dt,gravity);
    player.moveVertical(dt);
    resolveVerticalCollisions();
    
    //camera movement
    updateCamera(dt);
    player.updateSpritePosition();
    player.updateAnimation(dt);
}

void Game::render()
{
    window.clear();
    window.setView(window.getDefaultView());
    //window.draw(bgSprite);
    window.setView(camera);
    level.draw(window);
    window.draw(player.getSprite());
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
    float lookAhead=0;
    if(player.isFacingRight()==true)
    {
        lookAhead=250.f;
    }
    else
    {
        lookAhead=-250.f;
    }
    float targetX = player.getPosition().x + lookAhead;
    float currentX=camera.getCenter().x;
    float currentY=camera.getCenter().y;
    float cameraSpeed=2.f;
    float horizontalDeadZone=100.f;
    float verticalDeadZone=100.f;

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
