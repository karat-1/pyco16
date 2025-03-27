import pygame


class HitBox:
    def __init__(self, entity, position, size, game, duration=15, decrement=0.5, on_timer=True, offset=(0, 0),
                 on_hit=[]):
        self.game = game
        self.position = position
        self.entity = entity
        self.creator_id = entity.id
        self.size = size
        self.hit_entities = []
        self.dmg = 1
        self.duration = duration
        self.timer = 0
        self.decrement = decrement
        self.alive = True
        self.on_timer = on_timer
        self.offset: pygame.Vector2 = offset
        self.on_hit: list = on_hit  # list of callbacks

    @property
    def rect(self):
        return pygame.Rect(self.position.x, self.position.y, self.size.x, self.size.y)

    def __add_hit_entity(self, entity):
        self.hit_entities.append(entity.id)

    def check_collision(self, entity):
        if self.rect.colliderect(entity.rect) and entity.id not in self.hit_entities and entity.id != self.creator_id:
            entity.damage(self.dmg, creator=self.entity, collided_entity=self.entity)
            if self.on_hit:
                for callback in self.on_hit:
                    callback(entity)
            self.__add_hit_entity(entity)

    def update(self, dt):
        horizontal_difference = self.entity.position.x - self.position.x + self.offset[0]
        vertical_difference = self.entity.position.y - self.position.y + self.offset[1]
        self.position.x += horizontal_difference
        self.position.y += vertical_difference
        self.timer += dt
        if self.timer >= self.duration and self.on_timer:
            self.alive = False

    def set_alive(self, alive: bool) -> None:
        self.alive = alive


class HitboxManager:
    def __init__(self, game):
        self.game = game
        self.hitboxes_list: list[HitBox] = []
        self.entity_manager = None
        self.debug = True

    def init_manager(self):
        self.entity_manager = self.game.world.entities
        self.hitboxes_list = []

    def create_hitbox(self, entity, position, size, duration=15, on_timer=True, offset=(0, 0), on_hit=None):
        hitbox = HitBox(entity, position, size, self.game, duration=duration, on_timer=on_timer, offset=offset,
                        on_hit=on_hit)
        self.hitboxes_list.append(hitbox)
        return hitbox

    def update(self, dt):
        for i, hitbox in enumerate(self.hitboxes_list):
            if hitbox.alive:
                hitbox.update(dt)
            else:
                self.hitboxes_list.pop(i)
                print("popped hitbox")
        self.check_for_collisions()

    def check_for_collisions(self):
        for hitbox in self.hitboxes_list:
            for entity in self.entity_manager.get_all_entities():
                # TODO: This check needs to be replaced by a single flag as the project handles the collision
                if entity.flags.actor or entity.flags.projectile or entity.flags.hitable_prop or entity.flags.wallsword_prop:
                    hitbox.check_collision(entity)

    def render(self, surf, offset):
        if self.debug:
            for hitbox in self.hitboxes_list:
                rect = (
                    hitbox.position.x - offset[0], hitbox.position.y - offset[1], hitbox.rect.width, hitbox.rect.height)
                pygame.draw.rect(surf, (255, 0, 0), rect)
