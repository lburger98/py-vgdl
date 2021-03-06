from vgdl.state import StateObserver, KeyValueObservation
import math

from typing import Union, List, Dict


class AvatarOrientedObserver(StateObserver):

    def _get_distance(self, s1, s2):
        return math.hypot(s1.rect.x - s2.rect.x, s1.rect.y - s2.rect.y)


    def get_observation(self):
        avatars = self.game.get_avatars()
        assert avatars
        avatar = avatars[0]

        avatar_pos = avatar.rect.topleft
        resources = [avatar.resources[r] for r in self.game.domain.notable_resources]

        sprite_distances = []
        for key in self.game.sprite_registry.sprite_keys:
            dist = 100
            for s in self.game.get_sprites(key):
                dist = min(self._get_distance(avatar, s)/self.game.block_size, dist)
            sprite_distances.append(dist)

        obs = KeyValueObservation(
            position=avatar_pos, speed=avatar.speed, resources=resources,
            distances=sprite_distances
        )
        return obs


class NotableSpritesObserver(StateObserver):
    """
    TODO: There is still a problem with games where the avatar
    transforms into a different type
    """
    def __init__(self, game, notable_sprites: Union[List, Dict] = None):
        super().__init__(game)
        self.notable_sprites = list(notable_sprites or game.sprite_registry.groups())


    def get_observation(self):
        state = {'avatar': [('avatar.1.position', (-1, -1))], 'angry': [('angry.1.position', (-1, -1))]}

        sprite_keys = self.notable_sprites
        num_classes = len(sprite_keys)
        resource_types = self.game.domain.notable_resources

        for i, key in enumerate(sprite_keys):
            if key[0] == 'floor' or key[0] == 'wall' or key[0] == 'A':
                continue
            class_one_hot = [float(j==i) for j in range(num_classes)]

            # TODO this code is currently unsafe as getSprites does not
            # guarantee the same order for each call (Python < 3.6),
            # meaning observations will have inconsistent ordering of values
            for s in key[1]:

                position = self._rect_to_pos(s.rect)

                state[key[0]] = [
                    (s.id + '.position', position),
                ]

        return KeyValueObservation(state['angry'] + state['avatar'])
