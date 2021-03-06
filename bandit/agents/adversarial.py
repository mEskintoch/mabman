__all__ = [
    'EXP3',
    'FPL'
]

from bandit.agents.base import Agent
from bandit.arms import Arm
import numpy as np
import math
from typing import Optional, Union, List


class EXP3(Agent):
    name = 'exponential-weight-bandit'

    def __init__(self,
                 arms: Optional[List[Arm]] = None,
                 episodes: int = 100,
                 reset_at_end: bool = False,
                 callbacks: Optional[list] = None,
                 gamma: float = 0.1
                 ):
        self._arm_vars_hook(weight=1)
        super().__init__(arms, episodes, reset_at_end, callbacks)
        self.gamma = gamma

    def _update_arm_weight(self, arm: Arm , reward: int):
        """
        update arm weights with the given reward.
        Parameters
        ----------
        arm: Arm
        reward: reward

        Returns
        -------
        None
        """
        estimate = reward / self._arm_proba(arm)
        arm.weight *= math.exp(estimate * self.gamma / len(self.active_arms))

    def _arm_proba(self, arm: Arm) -> float:
        """
        Calculate arm selection probability.
        Parameters
        ----------
        arm: Arm

        Returns
        -------
        selection probability (float)
        """
        return (1.0 - self.gamma) * (arm.weight / self._w_sum()) + (self.gamma / len(self.active_arms))

    def _w_sum(self) -> float:
        """
        Sum of weights
        Returns
        -------
        float
        """
        return sum([arm.weight for arm in self.active_arms])

    def selection_policy(self, context=None) -> str:
        w_dist = [self._arm_proba(arm) for arm in self.active_arms]
        chosen_arm = np.random.choice(self.active_arms, p=w_dist)
        chosen_arm.select()
        return chosen_arm.name

    def reward_policy(self, name: str, reward: Union[int, float]):
        arm = self.arm(name)
        self._update_arm_weight(arm, reward)
        arm.reward(reward)


class FPL(Agent):
    name = 'follow-perturbed-leader-bandit'

    def __init__(self,
                 arms: Optional[List[Arm]] = None,
                 episodes: int = 100,
                 reset_at_end: bool = False,
                 callbacks: Optional[list] = None,
                 noise_param: float = 5
                 ):
        super().__init__(arms, episodes, reset_at_end, callbacks)
        self.noise_param = noise_param

    def _noise(self) -> float:
        """
        get noise variable given the noise parameter.
        Returns
        -------
        noise (float)
        """
        return float(np.random.exponential(self.noise_param))

    def selection_policy(self) -> str:
        chosen_arm = max(self.active_arms, key=lambda x: x.rewards + self._noise())
        chosen_arm.select()
        return chosen_arm.name

    def reward_policy(self, name: str, reward: Union[int, float]):
        self.arm(name).reward(reward)
