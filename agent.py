import network
from build_graph import build_graph
import lightsaber.tensorflow.util as util
import numpy as np
import tensorflow as tf


class Agent(object):
    def __init__(self,
                 actor,
                 critic,
                 value,
                 obs_dim,
                 num_actions,
                 replay_buffer,
                 batch_size=4,
                 gamma=0.9):
        self.batch_size = batch_size
        self.num_actions = num_actions
        self.gamma = gamma
        self.obs_dim = obs_dim
        self.last_obs = None
        self.t = 0
        self.replay_buffer = replay_buffer

        self._act,\
        self._train_actor,\
        self._train_critic,\
        self._train_value,\
        self._update_target = build_graph(
            actor=actor,
            critic=critic,
            value=value,
            obs_dim=obs_dim,
            num_actions=num_actions,
            batch_size=batch_size,
            gamma=gamma
        )

    def act(self, obs, reward, training=True):
        obs = obs[0]
        action = self._act([obs])
        action = np.clip(action[0], -2, 2)

        if training and self.t > 10 * 200:
            # sample experiences
            obs_t,\
            actions,\
            rewards,\
            obs_tp1,\
            dones = self.replay_buffer.sample(self.batch_size)

            # update networks
            value_error = self._train_value(obs_t, actions)
            critic_error = self._train_critic(
                obs_t, actions, rewards, obs_tp1, dones)
            actor_error = self._train_actor(obs_t)

            # update target networks
            self._update_target()

        if training and self.last_obs is not None:
            self.replay_buffer.append(
                obs_t=self.last_obs,
                action=self.last_action,
                reward=reward,
                obs_tp1=obs,
                done=False
            )

        self.t += 1
        self.last_obs = obs
        self.last_action = action
        return action

    def stop_episode(self, obs, reward, training=True):
        obs = obs[0]
        if training:
            self.replay_buffer.append(
                obs_t=self.last_obs,
                action=self.last_action,
                reward=reward,
                obs_tp1=obs,
                done=True
            )
        self.last_obs = None
        self.last_action = []
