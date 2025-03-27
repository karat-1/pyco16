from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class PLAYERSTATES:
    idle_state: str = 'player_idle_state'
    run_state: str = 'player_run_state'
    jump_state: str = 'player_jump_state'
    airborne_state: str = 'player_airborne_state'
    attack_state: str = 'player_attack_state'
    walljump_state: str = 'player_walljump_state'
    pushback_state: str = 'player_pushback_state'
    grapplejump_state: str = 'player_grapplejump_state'
    hook_state: str = 'player_hook_state'
    bubblejump_state: str = 'player_bubblejump_state'
    damaged_state: str = 'player_damaged_state'
    wallstuck_state: str = 'player_wallstuck_state'
    grappling_state: str = 'player_grappling_state'
    ladder_state: str = 'player_ladder_state'
    collected_state: str = 'player_collected_state'
    cutscene_state: str = 'player_cutscene_state'
    suddendeath_state: str = 'player_suddendeath_state'
    death_state: str = 'player_death_state'


class MINERBOSSSTATES:
    init_state: str = 'minerboss_init_state'
    wait_state: str = 'minerboss_wait_state'
    laser_state: str = 'minerboss_laser_state'
    molotov_state: str = 'minerboss_molotov_state'
    move_state: str = 'minerboss_move_state'
    v_state: str = 'minerboss_v_state'
    death_state: str = 'minerboss_death_state'
    dying_state: str = 'minerboss_dying_state'


@dataclass()
class ENTITYTYPES:
    default: bool = False
    actor: bool = False
    particle_system: bool = False
    oneway_collider: bool = False
    collideable: bool = False
    projectile: bool = False
    hitable_prop: bool = False
    burnable_prop: bool = False
    sliceable_prop: bool = False
    curseable_prop: bool = False
    elemental_source: bool = False
    wallsword_prop: bool = False
    player: bool = False
    collectible: bool = False
    currency: bool = False
    rope: bool = False
    miner_rock: bool = False
    ground_block: bool = False
    destroys_itself: bool = False
    boss_navigational_node: bool = False
    bubblejump_collider: bool = False
    is_drone: bool = False
    is_toggle_button: bool = False
    rope_can_impact: bool = False
    damageable: bool = False
    sliceable: bool = False
    anchorpoint: bool = False
    interactable: bool = False
    respawn_point: bool = False

    def __post_init__(self):
        # asserts that the fields are only booleans
        for field_name, value in self.__dict__.items():
            if not isinstance(value, bool):
                raise ValueError(f"{field_name} has to be a boolean value, but {value} was used")


@dataclass(frozen=True)
class DEBUGCONFIG:
    player_show_collision_box: bool = False
    player_show_surround_tiles: bool = False
    player_show_wallcollider: bool = False
    player_show_hitbox: bool = False
    drone_show_hurtbox: bool = False
    drone_show_surround_tiles: bool = False
    misc_show_wallstuck_collider: bool = False
    misc_show_respawnpoint_collider: bool = True
    misc_show_bonfire_collider: bool = False
    rope_show_points: bool = False
    questminer_debug_statemachine: bool = False
    questminer_show_collision_rect: bool = True
    questminer_show_interaction_rect: bool = False
    minerboss_show_nav_nodes: bool = False
    ladder_show_collider: bool = False

    def __post_init__(self):
        # asserts that the fields are only booleans
        for field_name, value in self.__dict__.items():
            if not isinstance(value, bool):
                raise ValueError(f"{field_name} has to be a boolean value, but {value} was used")


@dataclass(frozen=True)
class Dialogue:
    content: List = field(default_factory=lambda: [
        "default_text"
    ])


@dataclass
class ColorPalette:
    colors: list = field(default_factory=lambda: [
        "#be4a2f", "#d77643", "#ead4aa", "#e4a672", "#b86f50", "#733e39", "#3e2731", "#a22633",
        "#e43b44", "#f77622", "#feae34", "#fee761", "#63c74d", "#3e8948", "#265c42", "#193c3e",
        "#124e89", "#0099db", "#2ce8f5", "#ffffff", "#c0cbdc", "#8b9bb4", "#5a6988", "#3a4466",
        "#262b44", "#181425", "#ff0044", "#68386c", "#b55088", "#f6757a", "#e8b796", "#c28569"
    ])
    brown_tones: list = field(default_factory=lambda: ["#e4a672", "#b86f50", "#733e39", "#3e2731"])

    def __getitem__(self, key):
        return getattr(self, key, None)


@dataclass
class PlayerProgress:
    default: bool = True
    attack_unlocked: bool = False
    grapplehook_unlocked: bool = False
    swordthrow_unlocked: bool = False
    walljump_unlocked: bool = False

    def __post_init__(self):
        # asserts that the fields are only booleans
        for field_name, value in self.__dict__.items():
            if not isinstance(value, bool):
                raise ValueError(f"{field_name} has to be a boolean value, but {value} was used")

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Key '{key}' not found.")


@dataclass
class CollectableProgress:
    default: bool = True
    pickaxe_collected: bool = False

    def __post_init__(self):
        # asserts that the fields are only booleans
        for field_name, value in self.__dict__.items():
            if not isinstance(value, bool):
                raise ValueError(f"{field_name} has to be a boolean value, but {value} was used")

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Key '{key}' not found.")


@dataclass
class QuestProgress:
    default: bool = True
    miner_freed: bool = False
    miner_obtained_axe: bool = False
    miner_vine_severed: bool = False
    miner_boss_defeated: bool = False

    def __post_init__(self):
        # asserts that the fields are only booleans
        for field_name, value in self.__dict__.items():
            if not isinstance(value, bool):
                raise ValueError(f"{field_name} has to be a boolean value, but {value} was used")

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Key '{key}' not found.")
