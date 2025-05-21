🎮 Catch Game — Reinforcement Learning Agent

This project implements a custom reinforcement learning agent to play a classic Catch game, where the objective is to move a paddle and catch falling objects. The game was built from scratch, and a PPO-based RL model was trained using Stable Baselines3.

--------------------------------------------------------------------------------------------------------

🕹 Game Overview

In Catch, the player controls a paddle fixed at the bottom of the screen. Objects fall from the top, and the player must move left or right to catch them. The difficulty increases over time with:

-More objects on screen.

-Faster falling speed.

-Variable drop timing to challenge reaction time and decision-making.

--------------------------------------------------------------------------------------------------------

🧠 Reinforcement Learning Agent

    Frameworks Used
        -Stable Baselines3

        -gym - custom environment for Catch

        -SubprocVecEnv - for parallelized training

    Algorithm
        -Proximal Policy Optimization (PPO)

    Observation Space
        -The agent receives:
            --Player’s x coordinate

            --Up to 10 projectiles' x, y coordinates

            --A binary mask indicating active projectiles

    Action Space
        -Move left, right, or stay still

    Reward Shaping
        -Positive reward for aligning with falling objects

        -Bonus for proactive positioning

        -Penalty for unnecessary movement

        -Large reward for successfully catching a projectile

--------------------------------------------------------------------------------------------------------

🧪 Training Setup

Multiple environments for faster sampling

Adaptive difficulty: Object count and speed increase based on performance

Logging via TensorBoard and custom callback

Periodic model checkpointing

--------------------------------------------------------------------------------------------------------

📊 Results

After ~20 million timesteps:

    -Agent performs well at lower difficulties

    -Struggles at high object counts and speeds

    -Model used for experimentation in curriculum learning and reward shaping