import pygame
import math
import random

from src.utils.util import Utils
import src.engine.sounds as sounds
import src.engine.window as window
import src.engine.inputs as inputs

import src.engine.sprites as sprites
import src.engine.renderengine as renderengine
import src.engine.layers as layers
import src.engine.spritesheets as spritesheets

import src.game.spriteref as spriteref
import src.game.globalstate as gs
import src.game.gamestate as gamestate

DEFAULT_SCREEN_SIZE = (800, 600)
MINIMUM_SCREEN_SIZE = (800, 600)


def init(name_of_game):
    print("INFO: pygame version: " + pygame.version.ver)
    print("INFO: initializing sounds...")
    pygame.mixer.pre_init(44100, -16, 1, 2048)

    pygame.mixer.init()
    pygame.init()

    window_icon = pygame.image.load(Utils.resource_path("assets/icon.png"))
    pygame.display.set_icon(window_icon)

    window.create_instance(window_size=DEFAULT_SCREEN_SIZE, min_size=MINIMUM_SCREEN_SIZE)
    window.get_instance().set_caption(name_of_game)
    window.get_instance().show()

    render_eng = renderengine.create_instance()
    render_eng.init(*DEFAULT_SCREEN_SIZE)
    render_eng.set_min_size(*MINIMUM_SCREEN_SIZE)

    sprite_atlas = spritesheets.create_instance()

    spriteref.MAIN_SHEET = sprite_atlas.add_sheet(spriteref.MainSheet())

    atlas_surface = sprite_atlas.create_atlas_surface()

    # uncomment to save out the full texture atlas
    # pygame.image.save(atlas_surface, "texture_atlas.png")

    texture_data = pygame.image.tostring(atlas_surface, "RGBA", 1)
    width = atlas_surface.get_width()
    height = atlas_surface.get_height()
    render_eng.set_texture(texture_data, width, height)

    # REPLACE with whatever layers you need
    COLOR = True
    SORTS = True
    render_eng.add_layer(layers.ImageLayer(spriteref.LAYER_SCENE_BG, 0, False, COLOR))
    render_eng.add_layer(layers.ImageLayer(spriteref.LAYER_SCENE_ENVIRONMENT, 5, False, COLOR))
    render_eng.add_layer(layers.ImageLayer(spriteref.LAYER_SCENE_FG, 10, False, COLOR))

    render_eng.add_layer(layers.ImageLayer(spriteref.LAYER_UI_BG, 12, SORTS, COLOR))
    render_eng.add_layer(layers.ImageLayer(spriteref.LAYER_UI_FG, 15, SORTS, COLOR))
    render_eng.add_layer(layers.ImageLayer(spriteref.LAYER_UI_TOOLTIP, 20, SORTS, COLOR))

    gs.create_instance()

    gs.get_instance().set_game_state(gamestate.GameState())

    inputs.create_instance()

    px_scale = _calc_pixel_scale(DEFAULT_SCREEN_SIZE)
    render_eng.set_pixel_scale(px_scale)


def _calc_pixel_scale(screen_size, px_scale_opt=-1, max_scale=4):
    global DEFAULT_SCREEN_SIZE
    default_w = DEFAULT_SCREEN_SIZE[0]
    default_h = DEFAULT_SCREEN_SIZE[1]
    default_scale = 1

    screen_w, screen_h = screen_size

    if px_scale_opt <= 0:

        # when the screen is large enough to fit this quantity of (minimal) screens at a
        # particular scaling setting, that scale is considered good enough to switch to.
        # we choose the largest (AKA most zoomed in) "good" scale.
        step_up_x_ratio = 1.0
        step_up_y_ratio = 1.0

        best = default_scale
        for i in range(default_scale + 1, max_scale + 1):
            if (default_w / default_scale * i * step_up_x_ratio <= screen_w
                    and default_h / default_scale * i * step_up_y_ratio <= screen_h):
                best = i
            else:
                break

        return best
    else:
        return int(px_scale_opt)


def run():
    clock = pygame.time.Clock()
    running = True

    ignore_resize_events_next_tick = False

    while running:
        # processing user input events
        all_resize_events = []
        toggled_fullscreen = False

        input_state = inputs.get_instance()
        for py_event in pygame.event.get():
            if py_event.type == pygame.QUIT:
                running = False
                continue
            elif py_event.type == pygame.KEYDOWN:
                input_state.set_key(py_event.key, True)
            elif py_event.type == pygame.KEYUP:
                input_state.set_key(py_event.key, False)

            elif py_event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                scr_pos = window.get_instance().window_to_screen_pos(py_event.pos)
                game_pos = Utils.round(Utils.mult(scr_pos, 1 / renderengine.get_instance().get_pixel_scale()))
                input_state.set_mouse_pos(game_pos)

                if py_event.type == pygame.MOUSEBUTTONDOWN:
                    input_state.set_mouse_down(True, button=py_event.button)
                elif py_event.type == pygame.MOUSEBUTTONUP:
                    input_state.set_mouse_down(False, button=py_event.button)

            elif py_event.type == pygame.VIDEORESIZE:
                all_resize_events.append(py_event)

            if py_event.type == pygame.KEYDOWN and py_event.key == pygame.K_F4:
                toggled_fullscreen = True

            if not pygame.mouse.get_focused():
                input_state.set_mouse_pos(None)

        ignore_resize_events_this_tick = ignore_resize_events_next_tick
        ignore_resize_events_next_tick = False

        if toggled_fullscreen:
            # print("INFO {}: toggled fullscreen".format(gs.get_instance().tick_counter))
            win = window.get_instance()
            win.set_fullscreen(not win.is_fullscreen())

            new_size = win.get_display_size()
            new_pixel_scale = _calc_pixel_scale(new_size)
            if new_pixel_scale != renderengine.get_instance().get_pixel_scale():
                renderengine.get_instance().set_pixel_scale(new_pixel_scale)
            renderengine.get_instance().resize(new_size[0], new_size[1], px_scale=new_pixel_scale)

            # when it goes from fullscreen to windowed mode, pygame sends a VIDEORESIZE event
            # on the next frame that claims the window has been resized to the maximum resolution.
            # this is annoying so we ignore it. we want the window to remain the same size it was
            # before the fullscreen happened.
            ignore_resize_events_next_tick = True

        if not ignore_resize_events_this_tick and len(all_resize_events) > 0:
            last_resize_event = all_resize_events[-1]

            print("INFO: resizing to {}, {}".format(last_resize_event.w, last_resize_event.h))

            window.get_instance().set_window_size(last_resize_event.w, last_resize_event.h)

            display_w, display_h = window.get_instance().get_display_size()
            new_pixel_scale = _calc_pixel_scale((last_resize_event.w, last_resize_event.h))

            renderengine.get_instance().resize(display_w, display_h, px_scale=new_pixel_scale)

        input_state.update(gs.get_instance().tick_count)
        sounds.update()

        if gs.get_instance().is_dev() and input_state.was_pressed(pygame.K_F1):
            # used to help find performance bottlenecks
            import src.utils.profiling as profiling
            profiling.get_instance().toggle()

        if input_state.was_pressed(pygame.K_F5):
            current_scale = gs.get_instance().px_scale
            options = gs.get_instance().px_scale_options
            if current_scale in options:
                new_scale = (options.index(current_scale) + 1) % len(options)
            else:
                print("WARN: illegal pixel scale={}, reverting to default".format(current_scale))
                new_scale = options[0]
            gs.get_instance().px_scale = new_scale

            display_size = window.get_instance().get_display_size()
            new_pixel_scale = _calc_pixel_scale(display_size, px_scale_opt=new_scale)
            renderengine.get_instance().set_pixel_scale(new_pixel_scale)

        renderengine.get_instance().set_clear_color((0, 0, 0))

        gs.get_instance().update_all()

        renderengine.get_instance().render_layers()
        pygame.display.flip()

        slo_mo_mode = gs.get_instance().is_dev() and input_state.is_held(pygame.K_TAB)
        if slo_mo_mode:
            clock.tick(15)
        else:
            clock.tick(60)

        gs.get_instance().tick_count += 1

        if gs.get_instance().tick_count % 60 == 0:
            if clock.get_fps() < 55 and gs.get_instance().is_dev() and not slo_mo_mode:
                print("WARN: fps drop: {} ({} sprites)".format(round(clock.get_fps() * 10) / 10.0,
                                                               renderengine.get_instance().count_sprites()))

    print("INFO: quitting game")
    pygame.quit()
