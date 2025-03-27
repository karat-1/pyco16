from pygame import Surface

from engine.state.finitestatemachine import FiniteStateMachine
from engine.entities.base.particle_emitter import ParticleEmitter
from engine.entities.base.particle_presets import PlayerJumpParticles
from project.player_entities.player_states_samurai import *
from engine.core.engine_core_funcs import *
from engine.entities.base.actor import Actor
from engine.core.engine_dataclasses import DEBUGCONFIG
from pygame import Vector2


class Player(Actor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flags.player = 1
        self.centered = False
        self.ref_ladder = False
        self.wallstuck_ref = False
        self.collectable_ref = False
        self.drone = False
        self.bubble_ref = False
        self.flags.damaged = 0

        # inputs
        self.h_dir = 0
        self.h_dir_single = 0
        self.v_dir = 0
        self.v_dir_single = 0
        self.input_jump = 0
        self.input_jump_buffer = 0
        self.input_jump_buffer_duration = 0.15
        self.input_jump_hold = 0
        self.input_attack = 0
        self.input_drone = 0
        self.input_special_gun = 0
        self.input_accept = 0
        self.input_grappling_hook = 0
        self.map = None

        # physics
        self.apply_gravity = True
        self.collision_types = None
        self.max_y_velocity = 55
        self.run_speed = 28.5
        self.normalrun_speed = self.run_speed
        self.run_acceleration = 6
        self.water_run_speed = self.run_speed // 2
        self.normaljump_force = -61
        self.waterjump_force = self.normaljump_force / 2
        self.jump_force = -61
        self.dash_speed = pygame.Vector2(4, 0)
        self.grav_mult = 0
        self.grav_threshold = 0.5
        self.gravity = 4
        self.fractals = pygame.Vector2(0, 0)
        self.velocity_cache = pygame.Vector2(0, 0)

        # gameplay relative
        self.health = 100
        self.coyote_time = 20
        self.coyote_counter = 0
        self.counter = 0
        self.walljump_dir = 0
        self.attack_timer = 0
        self.attack_duration = 0.05
        self.attack_cooldown = 0.5
        self.attack_cooldown_timer = 0
        self.attack_speed = 132
        self.can_attack = False
        self.movement_suspended = False
        self.lock_face = False
        self.projectile_cooldown = 10
        self.projectile_timer = 15
        self.projectile_duration = 0
        self.can_jump = False
        self.can_grapple = True
        self.can_enter_cutscene = False
        self.hook_max_length = 24
        self.hook_length = 0
        self.windup_force = 0
        self.hook_speed = 90
        self.hook_start_position = pygame.Vector2(0, 0)
        self.hook_position = pygame.Vector2(0, 0)
        self.hit_entities = []
        self.can_walljump = True
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 1
        self.pushback_timer = 0
        self.pushback_duration = 0.1
        self.pushback_speed = pygame.Vector2(40, -10)
        self.suddendeath_counter = 0
        self.suddendeath_duration = 2
        self.respawnpoint_position = pygame.Vector2(0, 0)
        self.checkpoint = None
        self.bonfire = None
        self.death_counter = 0
        self.death_duration = 2

        # Entities
        self.jump_particles = ParticleEmitter(game=self.game, position=self.position, parent=self, width=0, height=0)
        self.jump_particles.apply_config(PlayerJumpParticles())
        self.em.add_entity(self.jump_particles)

        # Ability related
        self.playerprogress = self.game.savegame.get_player_progress()

        # Statemachine and States
        self.state_machine = FiniteStateMachine(debug=True)

        # ninja rework soon
        self.idle_state = FiniteIdleState(self, self.state_machine)
        self.run_state = FiniteRunState(self, self.state_machine)
        self.jump_state = FiniteJumpState(self, self.state_machine)
        self.airborne_state = FiniteAirborneState(self, self.state_machine)
        self.ladder_state = FiniteLadderState(self, self.state_machine)
        self.collected_state = FiniteCollectedState(self, self.state_machine)
        self.cutscene_state = FiniteCutsceneState(self, self.state_machine)
        self.bubblejump_state = FiniteBubbleJumpState(self, self.state_machine)
        self.grapple_state = FiniteGrapplingState(self, self.state_machine)
        self.hooked_state = FiniteHookState(self, self.state_machine)
        self.grapplejump_state = FiniteGrappleJumpState(self, self.state_machine)
        self.wallstuck_state = FiniteWallstuckState(self, self.state_machine)
        self.attack_state = FiniteAttackState(self, self.state_machine)
        self.bounceback_state = FinitePushbackState(self, self.state_machine)
        self.walljump_state = FiniteWalljumpState(self, self.state_machine)
        self.damaged_state = FiniteDamagedState(self, self.state_machine)
        self.suddendeath_state = FiniteSuddenDeathState(self, self.state_machine)
        self.death_state = FiniteDeathState(self, self.state_machine)

        self.state_machine.init_statemachine(self.idle_state)

    @property
    def img(self) -> Surface:
        return super().img

    @property
    def attack_rect(self):
        return pygame.Rect(self.position.x - 2, self.position.y - 1, 9, 7)

    def init_entity(self):
        pass

    def update(self, dt) -> bool:
        r = super().update(dt)
        if not r:
            return r

        self.parse_input(dt)
        self.check_for_direction()
        self.state_machine.current_state.logic_update(dt)
        self.state_machine.current_state.physics_update(dt)
        self.resolve_stretching(dt)
        self.resolve_attack(dt)
        self.collision_types = self.move(dt)
        self.check_for_boundary_collisions()
        self.check_for_projectile(dt)
        self.deal_with_collisions(dt)
        self.check_water_collisions()
        self.check_rope_collisions()
        self.check_for_ladders()
        self.check_for_collectibles()
        self.check_for_checkpoints()
        self.resolve_oneway()
        self.resolve_invincibility(dt)
        self.jump_particles.update_position(
            Vector2(self.position.x + self.size.x // 2, self.position.y + self.size.y - 1))

        # project is alive
        return True

    def deal_with_collisions(self, dt):
        if not self.on_ground:
            self.coyote_counter += dt
        if self.collision_types['top']:
            self.velocity[1] = 0
        if self.collision_types['bottom']:
            self.stretch_entity(1, 1)
            self.can_walljump = True
        if self.on_ground:
            self.coyote_counter = 0
            self.can_grapple = True

    def resolve_attack(self, dt):
        if not self.can_attack:
            self.attack_cooldown_timer += dt
        if self.attack_cooldown_timer >= self.attack_cooldown:
            self.can_attack = True
            self.attack_cooldown_timer = 0

    def transition_to_cutscene(self):
        self.state_machine.change_state(self.cutscene_state)

    def resolve_invincibility(self, dt):
        if self.invincible_timer > 0:
            self.invincible_timer -= dt
        else:
            self.invincible = False

    def resolve_oneway(self):
        if self.input_jump and self.v_dir == 1 and self.on_oneway:
            left_edge_tile = self.tile_data.get_tile_cell_pixel(self.rect.left, self.rect.bottom + 2)
            right_edge_tile = self.tile_data.get_tile_cell_pixel(self.rect.right - 1, self.rect.bottom + 2)
            if not left_edge_tile and not right_edge_tile:
                self.position.y += 3
                self.input_jump = False
                self.input_jump_buffer = 0

    def check_for_boundary_collisions(self):
        if self.position.x <= 0:
            self.position.x = 0
        elif self.position.x >= self.game.world.room_size_px.x * 16 - self.size.x:
            self.position = self.game.world.room_size_px.x * 16 - self.size.x

        if self.position.y <= 0:
            self.position.y = 0
        elif self.position.y >= self.game.world.room_size_px.y * 8 - self.size.y:
            self.position.y = self.game.world.room_size_px.y * 8 - self.size.y

    def stretch_entity(self, x=1, y=1):
        self.scale = [x, y]

    def change_checkpoint(self, new_checkpoint):
        if self.checkpoint:
            self.checkpoint.is_active = False
        self.checkpoint = new_checkpoint

    def change_bonfire(self, new_bonfire):
        if self.bonfire:
            self.bonfire.is_active = False
        self.bonfire = new_bonfire

    def resolve_stretching(self, dt):
        self.scale[0] = approach(self.scale[0], 1, 0.1 * dt)
        self.scale[1] = approach(self.scale[1], 1, 0.07 * dt)

    def check_for_ladders(self):
        _ladders = self.em.get_entities_by_type('Ladder')
        _ladder_hit = False
        _ladder_ref = None
        for ladder in _ladders:
            if self.rect.colliderect(ladder.rect):
                _ladder_hit = True
                _ladder_ref = ladder
                break
        if _ladder_hit:
            self.ref_ladder = _ladder_ref
        else:
            self.ref_ladder = None

    def check_for_checkpoints(self):
        _respawnpoints = self.em.get_entities_by_type('RespawnPoint')
        for rsp in _respawnpoints:
            if self.rect.colliderect(rsp.rect):
                self.respawnpoint_position = rsp.spawn_position

    def check_for_attack_collision(self):
        pass

    def check_for_collectibles(self):
        _collectibles = self.em.get_spatial_entities(self.get_chunk_location())
        _collectibles = [item for item in _collectibles if item.flags.collectible]
        for entity in _collectibles:
            if self.rect.colliderect(entity.rect) and not entity.collected:
                self.collectable_ref = entity
                break

    def apply_windup(self, force: int = 0, dt: float = 0):
        if not self.on_ground and not self.movement_suspended:
            self.velocity.y += force * dt

    def check_for_direction(self):
        if not self.lock_face:
            if self.h_dir == 1:
                self.flip[0] = 0
                self.face[0] = 1
            elif self.h_dir == -1:
                self.flip[0] = 1
                self.face[0] = -1

    def check_for_bubblejump(self):
        _list = self.em.get_spatial_entities(self.get_chunk_location())
        _list = [v for v in _list if v.flags.bubblejump_collider]
        for e in _list:
            if self.rect.colliderect(e.rect) and self.rect.bottom < e.rect.centery:
                return True
        return False

    def check_for_projectile(self, dt):
        if self.input_special_gun and self.playerprogress.swordthrow_unlocked:
            if self.bubble_ref:
                self.bubble_ref.alive = False
            self.shoot_special_gun()
            self.projectile_duration = 0
        if self.projectile_duration < self.projectile_cooldown:
            self.projectile_duration += 0.5 * dt

    def horizontal_movement(self, acceleration, decceleration) -> None:
        # calculating the velocity
        if self.h_dir == 1:
            self.velocity.x = approach(self.velocity.x, self.run_speed, acceleration)
        elif self.h_dir == -1:
            self.velocity.x = approach(self.velocity.x, -self.run_speed, acceleration)
        elif self.h_dir == 0 or self.velocity[0] > 0:
            self.velocity.x = approach(self.velocity[0], 0, decceleration)

    def vertical_movement(self, dt, ignore_mult=False) -> None:
        # if we are airborne because we are falling/running off a ledge then do this
        if not self.on_ground:
            self.velocity.y = approach(self.velocity[1], self.max_y_velocity, self.gravity)
        if self.velocity[1] > self.max_y_velocity:
            self.velocity.y = clamp(self.velocity.y, -self.max_y_velocity, self.max_y_velocity)

    def set_pos(self, position):
        self.position = position

    def suspend_movement(self):
        self.velocity_cache = self.velocity
        self.velocity = pygame.Vector2(0, 0)
        self.movement_suspended = True

    def continue_movement(self):
        self.velocity = self.velocity_cache
        self.movement_suspended = False

    def damage(self, amount: int = 1, **kwargs):

        if not self.invincible:
            self.health -= amount
            if self.health <= 0:
                self.state_machine.change_state(self.death_state)
                return
            self.state_machine.change_state(self.damaged_state)
            self.invincible = True
            self.invincible_timer = self.invincible_duration


    def check_water_collisions(self):
        super().check_water_collisions()
        water_objs = self.em.get_entities_by_type('Wave')
        for wave in water_objs:
            if self.rect.colliderect(wave.rect) and wave.wave_type == "WATER":
                self.jump_force = self.waterjump_force
                self.run_speed = self.water_run_speed
                return
            elif self.rect.colliderect(wave.rect) and wave.wave_type == "LAVA":
                self.state_machine.change_state(self.suddendeath_state)
        self.jump_force = self.normaljump_force
        self.run_speed = self.normalrun_speed

    def shoot_prjectile(self):
        if self.v_dir == 0:
            _rotation = 0 if self.face[0] == 1 else 180
        else:
            _rotation = 270 if self.v_dir == -1 else 90

        # self.game.world.invoke_screenshake(5, pygame.Vector2(5, 0))
        self.stretch_entity(1, 1)
        self.em.add_entity(Projectile(game=self.game,
                                      width=4,
                                      height=1,
                                      rotation=_rotation,
                                      creator=self,
                                      speed=2.5,
                                      position=self.position))

    def shoot_special_gun(self):
        self.bubble_ref = self.em.add_entity(JumpPad(game=self.game,
                                                     width=5,
                                                     height=5, tile_data=self.tile_data,
                                                     creator=self,
                                                     position=self.position,
                                                     velocity=pygame.Vector2(2.5, 0) * self.face[0]))

    def render(self, surf: pygame.Surface, offset=(0, 0)) -> None:
        """
        most of the stuff here is just for debugging purposes
        :param surf:
        :param offset:
        :return:
        """
        # offset is the offset of the actual position
        # render offset takes sprite origin into account, whenever I want to render the image sprite
        # then render offset has to be used
        super().render(surf, offset)
        self.state_machine.current_state.render_state(surf, offset)

        if DEBUGCONFIG.player_show_wallcollider:
            pygame.draw.rect(surf, (0, 255, 0),
                             pygame.Rect(self.position.x - 2 - offset[0], self.position.y - offset[1], 2,
                                         self.size.y), 1)
            pygame.draw.rect(surf, (0, 255, 0),
                             pygame.Rect(self.rect.right - offset[0], self.position.y - offset[1], 2,
                                         self.size.y), 1)

        if DEBUGCONFIG.player_show_collision_box:
            pygame.draw.rect(surf, (255, 0, 0),
                             pygame.Rect(self.position.x - offset[0], self.position.y - offset[1], self.size.x,
                                         self.size.y), 1)

        if DEBUGCONFIG.player_show_surround_tiles:
            for tile in self.tiles:
                rect = pygame.Rect(tile.rect.x - offset[0], tile.rect.y - offset[1], tile.size.x, tile.size.y)
                pygame.draw.rect(surf, (0, 255, 0), rect, 1)

        if DEBUGCONFIG.player_show_hitbox:
            _rect = self.attack_rect
            pygame.draw.rect(surf, (255, 255, 255), pygame.Rect(_rect.x - offset[0], _rect.y - offset[1], 8, 8), 1)

    def parse_input(self, dt):
        if self.game.input.input_method == 'gamepad':
            self.h_dir = self.game.input.dpad[0]
            self.v_dir = self.game.input.dpad[1] * -1

            self.h_dir_single = self.game.input.dpad_single[0]
            self.v_dir_single = self.game.input.dpad_single[1] * -1
        else:
            self.h_dir = self.game.input.states['move_right'] - self.game.input.states['move_left']
            self.v_dir = self.game.input.states['move_down'] - self.game.input.states['move_up']

        print(self.h_dir)

        # Jump-Buffer Logic
        if self.game.input.states['A'] or self.game.input.states["jump"]:
            self.input_jump_buffer = self.input_jump_buffer_duration

        if self.input_jump_buffer > 0:
            self.input_jump_buffer -= dt
            self.input_jump = True
        else:
            self.input_jump = False

        self.input_jump_hold = self.game.input.states['A_hold']
        self.input_attack = self.game.input.states['X'] or self.game.input.states["attack"]
        self.input_drone = self.game.input.states['LB']
        self.input_grappling_hook = self.game.input.states['Y']
        self.input_special_gun = self.game.input.states['B']
        self.input_accept = self.game.input.states['A']

    def reset_jump_buffer(self):
        self.input_jump = False
        self.input_jump_buffer = 0
