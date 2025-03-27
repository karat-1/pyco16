import copy

from engine.core.engine_core_funcs import *
from engine.state.finitestate import FiniteState
from engine.core.engine_dataclasses import PLAYERSTATES


class FiniteIdleState(FiniteState):
    """
    A state defining the Players behaviour idle behaviour
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = PLAYERSTATES.idle_state

    def enter_state(self) -> None:
        super().enter_state()
        self.e.set_animation('idle', True, "samurai")
        self.e.reset_fractions()
        self.e.velocity -= self.e.velocity
        self.e.can_enter_cutscene = True
        if self.state_machine.get_prev_state() == PLAYERSTATES.airborne_state:
            self.e.jump_particles.spawn_particle_group(20)

    def exit_state(self) -> None:
        super().exit_state()
        self.e.can_enter_cutscene = False

    def logic_update(self, dt) -> None:
        super().logic_update(dt)
        if self.e.h_dir != 0:
            self.state_machine.change_state(self.e.run_state)
            return

        elif self.e.input_jump:
            if not (self.e.on_oneway and self.e.v_dir == 1):
                self.state_machine.change_state(self.e.jump_state)
                return

        elif self.e.input_attack and self.e.playerprogress.attack_unlocked and self.e.can_attack:
            self.state_machine.change_state(self.e.attack_state)

        elif not self.e.on_ground:
            self.state_machine.change_state(self.e.airborne_state)
            return

        elif self.e.ref_ladder and self.e.v_dir == -1:
            self.state_machine.change_state(self.e.ladder_state)
            return

        elif self.e.collectable_ref:
            self.state_machine.change_state(self.e.collected_state)
            return

        elif self.e.input_grappling_hook and self.e.can_grapple and self.e.playerprogress.grapplehook_unlocked:
            self.state_machine.change_state(self.e.grapple_state)
            return

    def physics_update(self, dt) -> None:
        super().physics_update(dt)
        if not self.e.movement_suspended:
            self.e.horizontal_movement(0, 0)


class FiniteRunState(FiniteState):
    """
    A state defining the Players run behaviour
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = PLAYERSTATES.run_state

    def enter_state(self) -> None:
        super().enter_state()
        self.e.set_animation('run', True, "samurai")
        self.e.reset_fractions()
        self.e.velocity = self.e.velocity
        self.e.can_enter_cutscene = True
        if self.state_machine.get_prev_state() == PLAYERSTATES.airborne_state:
            self.e.jump_particles.spawn_particle_group(3)

    def exit_state(self) -> None:
        super().exit_state()
        self.e.can_enter_cutscene = False

    def logic_update(self, dt) -> None:
        super().logic_update(dt)
        if self.e.h_dir == 0:
            self.state_machine.change_state(self.e.idle_state)
            return

        elif self.e.input_attack and self.e.playerprogress.attack_unlocked and self.e.can_attack:
            self.state_machine.change_state(self.e.attack_state)

        elif self.e.input_jump:
            if not (self.e.on_oneway and self.e.v_dir == 1):
                self.state_machine.change_state(self.e.jump_state)
                return

        elif not self.e.on_ground:
            self.state_machine.change_state(self.e.airborne_state)
            return

        elif self.e.collectable_ref:
            self.state_machine.change_state(self.e.collected_state)
            return

        elif self.e.input_grappling_hook and self.e.can_grapple and self.e.playerprogress.grapplehook_unlocked:
            self.state_machine.change_state(self.e.grapple_state)
            return

    def physics_update(self, dt) -> None:
        super().physics_update(dt)
        self.e.horizontal_movement(self.e.run_speed, self.e.run_acceleration)


class FiniteJumpState(FiniteState):
    """
    A state defining the Players jump behaviour
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = PLAYERSTATES.jump_state

    def enter_state(self) -> None:
        super().enter_state()
        self.e.velocity[1] = self.e.jump_force
        self.e.can_jump = False
        self.e.coyote_counter = 10000
        self.e.stretch_entity(1, 1)

    def exit_state(self) -> None:
        super().exit_state()
        self.e.reset_jump_buffer()

    def logic_update(self, dt) -> None:
        super().logic_update(dt)
        self.state_machine.change_state(self.e.airborne_state)
        self.e.position.y -= 1

    def physics_update(self, dt) -> None:
        super().physics_update(dt)


class FiniteAttackState(FiniteState):

    def __init__(self, entity_obj, state_machine):
        super().__init__(entity_obj, state_machine)
        self.name = PLAYERSTATES.attack_state
        self.attack_acceleration = 0.25

    def enter_state(self) -> None:
        super().enter_state()
        self.e.velocity.x = self.e.attack_speed * self.e.face[0]
        self.e.velocity.y = 0
        self.e.attack_timer = 0
        self.e.lock_face = True
        self.e.can_attack = False

    def exit_state(self) -> None:
        super().exit_state()
        self.e.lock_face = False
        self.e.velocity.x = 0
        self.e.attack_timer = 0
        self.e.hit_entities.clear()

    def logic_update(self, dt) -> None:
        super().logic_update(dt)
        self.e.attack_timer += dt
        if self.e.attack_timer >= self.e.attack_duration:
            if self.e.on_ground and self.e.h_dir == 0:
                self.state_machine.change_state(self.e.idle_state)
                return
            elif self.e.on_ground and self.e.h_dir != 0:
                self.state_machine.change_state(self.e.run_state)
                return
            elif not self.e.on_ground:
                self.state_machine.change_state(self.e.airborne_state)
                return

        _entities = self.e.em.get_spatial_entities(self.e.get_chunk_location())
        _entities = [e for e in _entities if e.flags.damageable and self.e.attack_rect.colliderect(e.rect)]
        for e in _entities:
            if e not in self.e.hit_entities:
                e.damage(1)
                self.e.hit_entities.append(e)
                if e.flags.sliceable:
                    self.e.velocity.x = self.e.attack_speed * self.e.face[0]
                else:
                    self.state_machine.change_state(self.e.bounceback_state)
                    return

        if self.e.velocity.x == 0:
            self.state_machine.change_state(self.e.bounceback_state)

    def physics_update(self, dt) -> None:
        super().physics_update(dt)
        self.e.velocity.x = approach(self.e.velocity.x, 0.1, 0.1)

    def print_state(self) -> None:
        super().print_state()

    def render_state(self, surf, offset) -> None:
        super().render_state(surf, offset)


class FinitePushbackState(FiniteState):

    def __init__(self, entity_obj, state_machine):
        super().__init__(entity_obj, state_machine)
        self.name = PLAYERSTATES.pushback_state

    def enter_state(self) -> None:
        super().enter_state()
        self.e.velocity.x = self.e.pushback_speed.x * self.e.face[0] * -1
        self.e.velocity.y = self.e.pushback_speed.y
        self.e.pushback_timer = self.e.pushback_duration
        self.e.lock_face = True

    def exit_state(self) -> None:
        super().exit_state()
        self.e.lock_face = False
        self.e.velocity.x = 0
        self.e.pushback_timer = 0

    def logic_update(self, dt) -> None:
        super().logic_update(dt)
        self.e.pushback_timer -= dt

        if self.e.pushback_timer <= 0:
            if self.e.on_ground:
                self.state_machine.change_state(self.e.idle_state)
                return
            elif not self.e.on_ground:
                self.state_machine.change_state(self.e.airborne_state)
                return

    def physics_update(self, dt) -> None:
        super().physics_update(dt)
        self.e.vertical_movement(dt)

    def print_state(self) -> None:
        super().print_state()

    def render_state(self, surf, offset) -> None:
        super().render_state(surf, offset)


class FiniteGrappleJumpState(FiniteState):

    def __init__(self, entity_obj, state_machine):
        super().__init__(entity_obj, state_machine)
        self.name = PLAYERSTATES.grapplejump_state

    def enter_state(self) -> None:
        super().enter_state()
        self.e.velocity.y = self.e.jump_force * 1.25

    def exit_state(self) -> None:
        super().exit_state()

    def logic_update(self, dt) -> None:
        super().logic_update(dt)
        self.state_machine.change_state(self.e.airborne_state)

    def physics_update(self, dt) -> None:
        super().physics_update(dt)

    def print_state(self) -> None:
        super().print_state()

    def render_state(self, surf, offset) -> None:
        super().render_state(surf, offset)


class FiniteBubbleJumpState(FiniteState):

    def __init__(self, entity_obj, state_machine):
        super().__init__(entity_obj, state_machine)
        self.name = PLAYERSTATES.bubblejump_state

    def enter_state(self) -> None:
        super().enter_state()
        self.e.velocity.y = -1.5
        self.e.bubble_ref.alive = False

    def exit_state(self) -> None:
        super().exit_state()

    def logic_update(self, dt) -> None:
        super().logic_update(dt)
        self.state_machine.change_state(self.e.airborne_state)

    def physics_update(self, dt) -> None:
        super().physics_update(dt)

    def print_state(self) -> None:
        super().print_state()

    def render_state(self, surf, offset) -> None:
        super().render_state(surf, offset)


class FiniteWalljumpState(FiniteState):

    def __init__(self, entity_obj, state_machine):
        super().__init__(entity_obj, state_machine)
        self.timer = 0
        self.name = PLAYERSTATES.walljump_state
        self.is_locked = True

    def enter_state(self) -> None:
        super().enter_state()
        _xspeed = 0
        _yspeed = 0
        if self.e.on_wall_right and not self.e.on_wall_left:
            _xspeed = -1.05
            self.e.position.x -= 0
        elif self.e.on_wall_left and not self.e.on_wall_right:
            self.e.position.x += 0
            _xspeed = 1.05
        self.e.velocity = pygame.Vector2(_xspeed, -1.25)
        self.e.can_walljump = False

    def exit_state(self) -> None:
        super().exit_state()
        self.timer = 0

    def logic_update(self, dt) -> None:
        super().logic_update(dt)
        if abs(self.e.velocity.x) < 0.1:
            self.state_machine.change_state(self.e.airborne_state)
            return
        if self.e.velocity.x == 0:
            self.state_machine.change_state(self.e.airborne_state)
            return
        if (self.e.on_wall_left or self.e.on_wall_right) and self.timer >= 10:
            self.state_machine.change_state(self.e.airborne_state)
            return

    def physics_update(self, dt) -> None:
        super().physics_update(dt)
        self.e.vertical_movement(dt)
        self.timer += dt
        self.e.velocity[0] = approach(self.e.velocity[0], 0, 0.06)


class FiniteAirborneState(FiniteState):
    """
    A state defining the Players airborne behaviour
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = PLAYERSTATES.airborne_state
        self.fastfall_applied = False
        self.changed_animation = False
        self.prev_state = None

    def enter_state(self) -> None:
        super().enter_state()
        if self.e.velocity.y > 0:
            self.e.set_animation('falling', True, "samurai")

            self.changed_animation = True
        else:
            self.e.set_animation('jump', True, "samurai")

        self.prev_state = self.state_machine.get_prev_state()

    def exit_state(self) -> None:
        super().exit_state()
        self.fastfall_applied = False
        self.changed_animation = False

    def logic_update(self, dt) -> None:
        super().logic_update(dt)
        if self.e.velocity.y > 0 and not self.changed_animation:
            self.e.set_animation('falling', True, "samurai")

            self.changed_animation = True

        self.e.coyote_counter += dt
        if self.e.on_ground and self.e.velocity[0] == 0:
            self.state_machine.change_state(self.e.idle_state)
            return

        elif self.e.input_attack and self.e.playerprogress.attack_unlocked and self.e.can_attack:
            self.state_machine.change_state(self.e.attack_state)

        elif self.e.on_ground and self.e.velocity[0] != 0:
            self.state_machine.change_state(self.e.run_state)
            return

        elif self.e.velocity.y >= 0 and self.e.check_for_bubblejump():
            self.state_machine.change_state(self.e.bubblejump_state)
            return

        elif self.e.ref_ladder and self.e.v_dir == -1:
            self.state_machine.change_state(self.e.ladder_state)
            return

        elif (
                self.e.on_wall_left or self.e.on_wall_right) and self.e.input_jump and self.e.can_walljump and self.e.playerprogress.walljump_unlocked:
            self.state_machine.change_state(self.e.walljump_state)

        elif (self.e.input_jump and self.e.coyote_counter < self.e.coyote_time
              or (self.e.can_jump and self.e.input_jump)):
            self.state_machine.change_state(self.e.jump_state)
            return

        elif self.e.input_grappling_hook and self.e.can_grapple and self.e.playerprogress.grapplehook_unlocked:
            self.state_machine.change_state(self.e.grapple_state)
            return

    def physics_update(self, dt) -> None:
        super().physics_update(dt)
        if not self.e.input_jump_hold and self.e.velocity[
            1] < 0 and not self.fastfall_applied and self.prev_state == 'Jump':
            self.fastfall_applied = True
            self.e.velocity.y *= 0.4
        if not self.e.movement_suspended:
            self.e.horizontal_movement(self.e.run_acceleration, 3)
            self.e.vertical_movement(dt, ignore_mult=self.state_machine.get_prev_state() != 'Jump')


class FiniteDamagedState(FiniteState):

    def __init__(self, entity_obj, state_machine):
        super().__init__(entity_obj, state_machine)
        self.name = PLAYERSTATES.damaged_state

    def enter_state(self) -> None:
        super().enter_state()
        self.e.velocity.x = self.e.pushback_speed.x * self.e.face[0] * -1
        self.e.velocity.y = self.e.pushback_speed.y
        self.e.pushback_timer = self.e.pushback_duration
        self.e.lock_face = True

    def exit_state(self) -> None:
        super().exit_state()
        self.e.lock_face = False
        self.e.velocity.x = 0
        self.e.pushback_timer = 0

    def logic_update(self, dt) -> None:
        super().logic_update(dt)
        self.e.pushback_timer -= dt

        if self.e.pushback_timer <= 0:
            self.state_machine.change_state(self.e.idle_state)

    def physics_update(self, dt) -> None:
        super().physics_update(dt)
        self.e.vertical_movement(dt)

    def print_state(self) -> None:
        super().print_state()

    def render_state(self, surf: pygame.Surface, offset) -> None:
        super().render_state(surf, offset)
        _white_sprite = self.e.img.copy()
        _white_sprite.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_ADD)
        offset = self.e.calculate_render_offset(offset)
        surf.blit(_white_sprite, (self.e.position.x - offset[0], self.e.position.y - offset[1]))


class FiniteHookState(FiniteState):

    def __init__(self, entity_obj, state_machine):
        super().__init__(entity_obj, state_machine)
        self.name = PLAYERSTATES.hook_state
        self.y_cache = 0

    def enter_state(self) -> None:
        super().enter_state()
        self.e.velocity.x = self.e.hook_speed * self.e.face[0]
        self.y_cache = copy.deepcopy(self.e.velocity.y)
        self.e.velocity.y = 0
        self.e.lock_face = True
        self.e.movement_suspended = True

    def exit_state(self) -> None:
        super().exit_state()
        self.e.lock_face = False
        self.e.movement_suspended = False
        self.e.velocity.y = self.y_cache

    def logic_update(self, dt) -> None:
        super().logic_update(dt)
        _a = self.e.em.get_spatial_entities(self.e.get_chunk_location())
        _a = [anchor for anchor in _a if anchor.flags.anchorpoint]

        for anchor in _a:
            if self.e.rect.colliderect(anchor.rect):
                self.e.can_grapple = True
                self.state_machine.change_state(self.e.grapplejump_state)

        if self.e.input_jump:
            self.state_machine.change_state(self.e.grapplejump_state)
            return

        if self.e.on_wall_right or self.e.on_wall_left:
            self.state_machine.change_state(self.e.wallstuck_state)
            return

    def physics_update(self, dt) -> None:
        super().physics_update(dt)

    def print_state(self) -> None:
        super().print_state()

    def render_state(self, surf, offset) -> None:
        super().render_state(surf, offset)


class FiniteWallstuckState(FiniteState):
    def __init__(self, entity_obj, state_machine):
        super().__init__(entity_obj, state_machine)
        self.name = PLAYERSTATES.wallstuck_state

    def enter_state(self) -> None:
        super().enter_state()
        self.e.velocity.x = 0
        self.e.velocity.y = 0
        self.e.lock_face = True
        self.e.movement_suspended = True

    def exit_state(self) -> None:
        super().exit_state()
        self.e.lock_face = False
        self.e.movement_suspended = False

    def logic_update(self, dt) -> None:
        super().logic_update(dt)
        if self.e.input_jump:
            self.state_machine.change_state(self.e.jump_state)
            return

    def physics_update(self, dt) -> None:
        super().physics_update(dt)

    def print_state(self) -> None:
        super().print_state()

    def render_state(self, surf, offset) -> None:
        super().render_state(surf, offset)


class FiniteGrapplingState(FiniteState):

    def __init__(self, entity_obj, state_machine):
        super().__init__(entity_obj, state_machine)
        self.name = PLAYERSTATES.grappling_state
        self.y_cache = 0

    def enter_state(self) -> None:
        super().enter_state()
        self.e.lock_face = True
        self.e.can_grapple = False
        self.e.velocity.x = 0
        self.y_cache = copy.deepcopy(self.e.velocity.y)
        self.e.velocity.y = 0
        self.e.hook_start_position.x = self.e.rect.right if self.e.face[0] == 1 else self.e.rect.left
        self.e.hook_start_position.y = self.e.rect.y + (self.e.rect.height // 2)
        self.e.movement_suspended = True

    def exit_state(self) -> None:
        super().exit_state()
        self.e.hook_length = 0
        self.e.lock_face = False
        self.e.movement_suspended = False
        self.e.velocity.y = self.y_cache

    def logic_update(self, dt) -> None:
        super().logic_update(dt)

        # calculate check position
        if self.e.face[0] == 1:
            _check_pos = pygame.Vector2(self.e.hook_start_position.x + self.e.hook_length, self.e.hook_start_position.y)
        elif self.e.face[0] == -1:
            _check_pos = pygame.Vector2(self.e.hook_start_position.x - self.e.hook_length, self.e.hook_start_position.y)
        else:
            _check_pos = pygame.Vector2(0, 0)

        # get all important colliders
        _td = self.e.tile_data.get_surround_tiles(_check_pos)
        entity_colliders = self.e.em.get_spatial_entities(self.e.get_chunk_location())
        collideable_entities = [entity for entity in entity_colliders if entity.flags.collideable or
                                entity.flags.anchorpoint]
        _td.extend(collideable_entities)

        # iterate over colliders and change state once collided with anything that can be collided with
        for collider in _td:
            if collider.rect.collidepoint(_check_pos):
                self.e.hook_position = _check_pos
                self.state_machine.change_state(self.e.hooked_state)
                return

        if self.e.hook_length <= self.e.hook_max_length:
            self.e.hook_length += self.e.hook_speed * dt

        if self.e.on_ground and self.e.hook_length > self.e.hook_max_length:
            self.state_machine.change_state(self.e.idle_state)
            return
        elif not self.e.on_ground and self.e.hook_length > self.e.hook_max_length:
            self.state_machine.change_state(self.e.airborne_state)
            return

    def physics_update(self, dt) -> None:
        super().physics_update(dt)

    def print_state(self) -> None:
        super().print_state()

    def render_state(self, surf, offset) -> None:
        super().render_state(surf, offset)
        if self.e.face[0] == 1:
            pygame.draw.circle(surf, (255, 255, 255),
                               (self.e.hook_start_position.x + self.e.hook_length - offset[0],
                                self.e.hook_start_position.y - offset[1]), 1)
        elif self.e.face[0] == -1:
            pygame.draw.circle(surf, (255, 255, 255),
                               (self.e.hook_start_position.x - self.e.hook_length - offset[0],
                                self.e.hook_start_position.y - offset[1]), 1)


class FiniteLadderState(FiniteState):
    def __init__(self, entity_obj, state_machine):
        super().__init__(entity_obj, state_machine)
        self.name = PLAYERSTATES.ladder_state

    def enter_state(self) -> None:
        super().enter_state()
        self.e.position.x = copy.deepcopy(self.e.ref_ladder.position.x) + 3
        self.e.velocity.x = 0

    def exit_state(self) -> None:
        super().exit_state()

    def logic_update(self, dt) -> None:
        super().logic_update(dt)

        if self.e.input_jump and self.e.v_dir <= 0:
            self.state_machine.change_state(self.e.jump_state)
            return
        elif not self.e.ref_ladder:
            self.state_machine.change_state(self.e.idle_state)

    def physics_update(self, dt) -> None:
        super().physics_update(dt)
        if self.e.v_dir == -1:
            self.e.velocity.y = -self.e.run_speed * 0.7
        elif self.e.v_dir == 1:
            self.e.velocity.y = -self.e.run_speed * 0.7
        elif self.e.v_dir == 0:
            self.e.velocity.y = 0

    def print_state(self) -> None:
        super().print_state()

    def render_state(self, cam, surf) -> None:
        super().render_state(cam, surf)


class FiniteCollectedState(FiniteState):

    def __init__(self, entity_obj, state_machine):
        super().__init__(entity_obj, state_machine)
        self.name = PLAYERSTATES.collected_state

    def enter_state(self) -> None:
        super().enter_state()
        self.e.collectable_ref.pickup_item()
        self.e.velocity.x = 0
        self.e.velocity.y = 0

    def exit_state(self) -> None:
        super().exit_state()
        self.e.collectable_ref.collect_item()
        self.e.collectable_ref = None

    def logic_update(self, dt) -> None:
        super().logic_update(dt)
        if self.e.input_jump:
            self.state_machine.change_state(self.e.idle_state)

    def physics_update(self, dt) -> None:
        super().physics_update(dt)

    def print_state(self) -> None:
        super().print_state()

    def render_state(self, surf, offset) -> None:
        super().render_state(surf, offset)
        surf.blit(self.e.collectable_ref.inventory_image,
                  (self.e.position.x - offset[0], self.e.position.y - offset[1] - 5))


class FiniteCutsceneState(FiniteState):
    def __init__(self, entity_obj, state_machine):
        super().__init__(entity_obj, state_machine)
        self.name = PLAYERSTATES.cutscene_state

    def enter_state(self) -> None:
        super().enter_state()
        self.e.velocity.x = 0
        self.e.velocity.y = 0
        self.e.can_enter_cutscene = False

    def exit_state(self) -> None:
        super().exit_state()
        self.e.reset_jump_buffer()

    def logic_update(self, dt) -> None:
        super().logic_update(dt)

    def physics_update(self, dt) -> None:
        super().physics_update(dt)

    def print_state(self) -> None:
        super().print_state()

    def render_state(self, surf, offset) -> None:
        super().render_state(surf, offset)


class FiniteSuddenDeathState(FiniteState):

    def __init__(self, entity_obj, state_machine):
        super().__init__(entity_obj, state_machine)
        self.name = PLAYERSTATES.suddendeath_state

    def enter_state(self) -> None:
        super().enter_state()

    def exit_state(self) -> None:
        super().exit_state()
        self.e.position = self.e.respawnpoint_position

    def logic_update(self, dt) -> None:
        super().logic_update(dt)
        self.e.suddendeath_counter += dt

        if self.e.suddendeath_duration >= self.e.suddendeath_counter:
            self.state_machine.change_state(self.e.idle_state)

    def physics_update(self, dt) -> None:
        super().physics_update(dt)

    def print_state(self) -> None:
        super().print_state()

    def render_state(self, surf, offset) -> None:
        super().render_state(surf, offset)


class FiniteDeathState(FiniteState):
    def __init__(self, entity_obj, state_machine):
        super().__init__(entity_obj, state_machine)
        self.name = PLAYERSTATES.death_state

    def enter_state(self) -> None:
        super().enter_state()

    def exit_state(self) -> None:
        super().exit_state()
        self.e.position = self.e.bonfire.spawn_position - (0, 2)

    def logic_update(self, dt) -> None:
        super().logic_update(dt)
        self.e.death_counter += dt

        if self.e.death_counter >= self.e.death_duration:
            self.state_machine.change_state(self.e.idle_state)
