"""Battle City-inspired pixel-art PyGame UI for the existing Tank Battle AI engine.

All art is locally generated and included under assets/pixel; no internet or
third-party artwork is required. This module changes presentation, not search.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import csv
from datetime import datetime
import pygame
from tankbattle.engine.model import Action, GameState, initial_state, WIDTH, HEIGHT
from tankbattle.engine.game import apply_action
from tankbattle.engine.maps import MAP_NAMES, get_map, spawn_state
from tankbattle.agents.search import SearchAgent, SearchStats
from tankbattle.agents.registry import ExternalAgent

SCREEN_W, SCREEN_H = 1240, 818
TILE = 40
BOARD_X, BOARD_Y = 43, 126
BOARD_W, BOARD_H = WIDTH * TILE, HEIGHT * TILE
SIDE_X, SIDE_Y, SIDE_W, SIDE_H = 679, 126, 516, 600
ART = Path(__file__).resolve().parents[2] / 'assets' / 'pixel'

BG = (9, 13, 21)
BLACK = (2, 3, 5)
PANEL = (19, 28, 41)
PANEL_LIGHT = (28, 42, 58)
BORDER = (62, 77, 89)
TEXT = (233, 241, 239)
MUTED = (138, 160, 171)
CYAN = (97, 212, 233)
GOLD = (255, 201, 77)
GREEN = (103, 220, 144)
ORANGE = (247, 141, 69)
MODES_UI = ['Heuristic Alpha-Beta', 'Heuristic Minimax', 'Alpha-Beta', 'Minimax', 'Human', 'External']


@dataclass
class UIButton:
    rect: pygame.Rect
    key: str
    label: str


class BattleApp:
    def __init__(self, depth=3, p0='Heuristic Alpha-Beta', p1='Heuristic Minimax',
                 external_module='tankbattle.external_agents.example_agent',
                 starting_state=None, scenario_name='Opening', gameplay_tactics=True,
                 spawn_mode='balanced', spawn_seed=2026):
        pygame.init()
        pygame.display.set_caption('TANK BATTLE | Battle City Pixel UI | Task 2')
        # Co gian canvas theo kich thuoc cua so
        display = pygame.display.Info()
        scale = min(1.0, (display.current_w - 80) / SCREEN_W,
                    (display.current_h - 100) / SCREEN_H)
        scale = max(0.65, scale)
        self.window = pygame.display.set_mode((int(SCREEN_W * scale),
                                               int(SCREEN_H * scale)), pygame.RESIZABLE)
        self.screen = pygame.Surface((SCREEN_W, SCREEN_H)).convert()
        self.clock = pygame.time.Clock()
        self.fonts: dict[tuple[int, bool], pygame.font.Font] = {}
        self.art = self._load_art()
        self.starting_state = starting_state if starting_state is not None else initial_state()
        self.scenario_name = scenario_name
        self.map_name = 'Classic Battlefield' if scenario_name == 'Opening' else scenario_name
        self.state = self.starting_state
        self.depth = depth
        self.gameplay_tactics = gameplay_tactics
        self.spawn_mode = spawn_mode
        self.spawn_seed = spawn_seed
        self.external_modules = (external_module if isinstance(external_module, tuple)
                                 else (external_module, external_module))
        self.modes = [p0, p1]
        self.agents = [None, None]
        self._refresh_agents()
        self.paused = True
        self.interval = 600
        self.last_tick = pygame.time.get_ticks()
        self.last_actions = ['-', '-']
        self.stats: list[SearchStats | None] = [None, None]
        self.notice = f'{self.scenario_name} | SPACE to play, N to step'
        self.flash = None
        self.history = [self.state]
        self.records = []
        self.replay_mode = False
        self.replay_index = 0
        self.buttons = self._make_buttons()

    def _load_art(self):
        names = ['brick', 'steel', 'flash', 'base_blue', 'base_gold']
        names += [f'forest_{i}' for i in range(4)]
        names += [f'tank_{side}_{direction}' for side in ('blue', 'gold')
                  for direction in ('up', 'down', 'left', 'right')]
        images = {}
        for name in names:
            path = ART / f'{name}.png'
            images[name] = pygame.transform.scale(pygame.image.load(str(path)).convert_alpha(), (TILE, TILE))
        return images

    def _font(self, size, bold=False):
        key = (size, bold)
        if key not in self.fonts:
            self.fonts[key] = pygame.font.SysFont('consolas', size, bold=bold)
        return self.fonts[key]

    def _text(self, value, x, y, size=18, color=TEXT, bold=False):
        rendered = self._font(size, bold).render(str(value), True, color)
        self.screen.blit(rendered, (x, y))
        return rendered.get_width()

    def _box(self, rect, fill=PANEL, edge=BORDER, radius=5, line=1):
        pygame.draw.rect(self.screen, fill, rect, border_radius=radius)
        if edge is not None:
            pygame.draw.rect(self.screen, edge, rect, line, border_radius=radius)

    def _make_buttons(self):
        x = SIDE_X + 21
        return [
            UIButton(pygame.Rect(x, 206, SIDE_W - 42, 34), 'map', ''),
            UIButton(pygame.Rect(x, 389, SIDE_W - 42, 41), 'p0', 'P1'),
            UIButton(pygame.Rect(x, 451, SIDE_W - 42, 41), 'p1', 'P2'),
            UIButton(pygame.Rect(x, 515, 147, 40), 'pause', 'PLAY / PAUSE'),
            UIButton(pygame.Rect(x + 162, 515, 147, 40), 'step', 'STEP'),
            UIButton(pygame.Rect(x + 324, 515, 150, 40), 'reset', 'RESET'),
            UIButton(pygame.Rect(x, 563, 230, 33), 'slower', '-  SLOWER'),
            UIButton(pygame.Rect(x + 244, 563, 230, 33), 'faster', '+  FASTER'),
            UIButton(pygame.Rect(x, 697, SIDE_W - 42, 26), 'replay', 'BATTLE LOG / REPLAY'),
            UIButton(pygame.Rect(x, 630, 146, 39), 'prev', '< PREVIOUS'),
            UIButton(pygame.Rect(x + 164, 630, 146, 39), 'next', 'NEXT >'),
            UIButton(pygame.Rect(x + 328, 630, 146, 39), 'exit_replay', 'BACK'),
            UIButton(pygame.Rect(x, 682, SIDE_W - 42, 39), 'save_log', 'EXPORT LOG CSV'),
        ]

    @property
    def display_state(self):
        # Replay chi hien thi state cu, khong thay doi tran dau that
        return self.history[self.replay_index] if self.replay_mode else self.state

    def _refresh_agents(self):
        self.agents = []
        for player, mode in enumerate(self.modes):
            if mode == 'Human':
                self.agents.append(None)
            elif mode == 'External':
                self.agents.append(ExternalAgent(self.external_modules[player]))
            else:
                self.agents.append(SearchAgent(mode, self.depth, gameplay_tactics=self.gameplay_tactics))

    def _reset(self):
        self.state = self.starting_state
        self.history = [self.state]
        self.records = []
        self.replay_index = 0
        self.replay_mode = False
        self.last_actions = ['-', '-']
        self.stats = [None, None]
        self.flash = None
        self.paused = True
        self.notice = f'{self.scenario_name} | NEW MATCH READY'
        self.last_tick = pygame.time.get_ticks()

    def _change_map(self):
        current = MAP_NAMES.index(self.map_name) if self.map_name in MAP_NAMES else -1
        self.map_name = MAP_NAMES[(current + 1) % len(MAP_NAMES)]
        self.scenario_name = self.map_name
        self.starting_state = spawn_state(self.map_name, getattr(self, 'spawn_mode', 'balanced'),
                                          getattr(self, 'spawn_seed', 2026))
        self._reset()

    def _new_random_spawn(self):
        # G: tao tran moi voi vi tri spawn moi va seed co the tai lap.
        self.spawn_mode = 'random'
        self.spawn_seed = getattr(self, 'spawn_seed', 2026) + 1
        self.starting_state = spawn_state(self.map_name, 'random', self.spawn_seed)
        self._reset()
        self.notice = f'RANDOM SPAWN | seed={self.spawn_seed} | G for new spawn'

    def _open_replay(self):
        self.paused = True
        self.replay_mode = True
        self.replay_index = len(self.history) - 1

    def _save_log(self):
        folder = Path(__file__).resolve().parents[2] / 'results' / 'battle_logs'
        folder.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        target = folder / f'battle_{stamp}.csv'
        with target.open('w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=('map', 'ply', 'player', 'action',
                                                     'events', 'p1_tank_hp', 'p2_tank_hp',
                                                     'p1_base_hp', 'p2_base_hp', 'winner'))
            writer.writeheader()
            for rec, state in zip(self.records, self.history[1:]):
                writer.writerow({
                    'map': self.scenario_name,
                    'ply': state.ply, 'player': rec['player'] + 1,
                    'action': rec['action'].value,
                    'events': ' | '.join(rec['events']),
                    'p1_tank_hp': state.tanks[0].hp, 'p2_tank_hp': state.tanks[1].hp,
                    'p1_base_hp': state.bases[0].hp, 'p2_base_hp': state.bases[1].hp,
                    'winner': state.winner if state.terminal else '',
                })
        self.notice = f'Saved log: {target.name}'

    def _cycle(self, player):
        index = MODES_UI.index(self.modes[player]) if self.modes[player] in MODES_UI else 0
        self.modes[player] = MODES_UI[(index + 1) % len(MODES_UI)]
        try:
            self._refresh_agents()
        except (ImportError, TypeError, ValueError) as exc:
            self.modes[player] = 'Heuristic Alpha-Beta'
            self._refresh_agents()
            self._reset()
            self.notice = f'External error: {str(exc)[:40]}'
            return
        self._reset()

    def _step(self, human_action: Action | None = None):
        if self.replay_mode:
            self.replay_index = min(self.replay_index + 1, len(self.history) - 1)
            return
        if self.state.terminal:
            self.paused = True
            return
        player = self.state.turn
        if self.agents[player] is None:
            if human_action is None:
                self.notice = f'P{player + 1} HUMAN: WASD move, F fire, X stay'
                return
            action = human_action
        else:
            try:
                action = self.agents[player].choose_action(self.state)
            except (ValueError, TypeError, ImportError) as exc:
                self.paused = True
                self.notice = f'Agent error: {str(exc)[:43]}'
                return
            self.stats[player] = getattr(self.agents[player], 'stats', None)
        if action == Action.FIRE:
            tank = self.state.tanks[player]
            self.flash = (tank.x, tank.y, pygame.time.get_ticks() + 180)
        # Ghi lai state va su kien de xem replay
        events = []
        self.state = apply_action(self.state, action, events=events)
        self.history.append(self.state)
        self.records.append({'player': player, 'action': action, 'events': events})
        self.last_actions[player] = action.value.replace('MOVE_', '')
        self.notice = f'P{player + 1}  >  {action.value}'
        self.last_tick = pygame.time.get_ticks()
        if self.state.terminal:
            self.paused = True
            who = 'DRAW' if self.state.winner == -1 else f'PLAYER {self.state.winner + 1} WINS'
            self.notice = f'{who}  |  {self.state.reason}'

    def _handle_button(self, key):
        if key == 'map':
            self._change_map()
        elif key in ('p0', 'p1'):
            self._cycle(0 if key == 'p0' else 1)
        elif key == 'replay':
            self._open_replay()
        elif key == 'exit_replay':
            self.replay_mode = False
            self.paused = True
        elif key == 'prev':
            self.replay_index = max(0, self.replay_index - 1)
        elif key == 'next':
            self.replay_index = min(len(self.history) - 1, self.replay_index + 1)
        elif key == 'save_log':
            self._save_log()
        elif key == 'pause':
            if self.replay_mode:
                self.replay_mode = False
            self.paused = not self.paused
        elif key == 'step':
            self.paused = True
            self._step()
        elif key == 'reset':
            self._reset()
        elif key == 'slower':
            self.interval = min(2200, self.interval + 150)
        elif key == 'faster':
            self.interval = max(80, self.interval - 150)

    def _events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                self.window = pygame.display.set_mode((max(720, event.w),
                                                       max(480, event.h)), pygame.RESIZABLE)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                window_w, window_h = self.window.get_size()
                point = (int(event.pos[0] * SCREEN_W / window_w),
                         int(event.pos[1] * SCREEN_H / window_h))
                available = self.buttons[9:] if self.replay_mode else self.buttons[:9]
                for button in available:
                    if button.rect.collidepoint(point):
                        self._handle_button(button.key)
                        break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key in (pygame.K_SPACE, pygame.K_p):
                    self._handle_button('pause')
                elif event.key == pygame.K_n:
                    self.paused = True
                    self._step()
                elif event.key == pygame.K_r:
                    self._reset()
                elif event.key == pygame.K_m:
                    self._handle_button('map')
                elif event.key == pygame.K_g:
                    self._new_random_spawn()
                elif event.key == pygame.K_l:
                    self._open_replay()
                elif event.key == pygame.K_LEFTBRACKET and self.replay_mode:
                    self._handle_button('prev')
                elif event.key == pygame.K_RIGHTBRACKET and self.replay_mode:
                    self._handle_button('next')
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self._handle_button('slower')
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                    self._handle_button('faster')
                else:
                    human = {
                        pygame.K_w: Action.MOVE_UP, pygame.K_UP: Action.MOVE_UP,
                        pygame.K_s: Action.MOVE_DOWN, pygame.K_DOWN: Action.MOVE_DOWN,
                        pygame.K_a: Action.MOVE_LEFT, pygame.K_LEFT: Action.MOVE_LEFT,
                        pygame.K_d: Action.MOVE_RIGHT, pygame.K_RIGHT: Action.MOVE_RIGHT,
                        pygame.K_f: Action.FIRE, pygame.K_RETURN: Action.FIRE,
                        pygame.K_x: Action.STAY,
                    }.get(event.key)
                    if human and not self.replay_mode and not self.state.terminal and self.modes[self.state.turn] == 'Human':
                        self._step(human)
        return True

    def _draw_board(self):
        state = self.display_state
        pygame.draw.rect(self.screen, (124, 131, 135),
                         (BOARD_X - 5, BOARD_Y - 5, BOARD_W + 10, BOARD_H + 10), 3)
        pygame.draw.rect(self.screen, BLACK, (BOARD_X, BOARD_Y, BOARD_W, BOARD_H))
        # Ve cay trang tri, khong can duong di
        for y in range(4, 9):
            for x in range(5, 10):
                if any(w.x == x and w.y == y for w in state.walls):
                    continue
                self.screen.blit(self.art[f'forest_{(x * 5 + y * 3) % 4}'],
                                 (BOARD_X + x * TILE, BOARD_Y + y * TILE))
        # Ve tuong theo HP hien tai
        for wall in state.walls:
            px, py = BOARD_X + wall.x * TILE, BOARD_Y + wall.y * TILE
            self.screen.blit(self.art['steel' if wall.kind == 'steel' else 'brick'], (px, py))
            if wall.hp < 3:
                # Vet nut chi de hien thi
                crack = (9, 10, 13) if wall.kind == 'steel' else (34, 15, 10)
                cx, cy = px + TILE // 2, py + TILE // 2
                pygame.draw.line(self.screen, crack, (cx - 8, cy - 8), (cx + 2, cy), 3)
                pygame.draw.line(self.screen, crack, (cx + 2, cy), (cx - 3, cy + 9), 3)
                if wall.hp == 1:
                    pygame.draw.line(self.screen, crack, (cx + 2, cy), (cx + 11, cy - 4), 3)
        for i, base in enumerate(state.bases):
            px, py = BOARD_X + base.x * TILE, BOARD_Y + base.y * TILE
            if base.hp > 0:
                self.screen.blit(self.art['base_blue' if i == 0 else 'base_gold'], (px, py))
        for i, tank in enumerate(state.tanks):
            if tank.hp <= 0:
                continue
            if tank.dx == 1:
                direction = 'right'
            elif tank.dx == -1:
                direction = 'left'
            elif tank.dy == 1:
                direction = 'down'
            else:
                direction = 'up'
            px, py = BOARD_X + tank.x * TILE, BOARD_Y + tank.y * TILE
            self.screen.blit(self.art[f'tank_{"blue" if i == 0 else "gold"}_{direction}'], (px, py))
            if state.turn == i and not state.terminal:
                # Danh dau player dang toi luot
                c = CYAN if i == 0 else GOLD
                pygame.draw.line(self.screen, c, (px + 1, py + 1), (px + 9, py + 1), 2)
                pygame.draw.line(self.screen, c, (px + 1, py + 1), (px + 1, py + 9), 2)
        for bullet in state.bullets:
            px = BOARD_X + bullet.x * TILE + TILE // 2
            py = BOARD_Y + bullet.y * TILE + TILE // 2
            pygame.draw.rect(self.screen, ORANGE, (px - 4, py - 4, 8, 8))
            pygame.draw.rect(self.screen, (255, 255, 223), (px - 2, py - 2, 4, 4))
        if not self.replay_mode and self.flash and pygame.time.get_ticks() < self.flash[2]:
            x, y, _ = self.flash
            self.screen.blit(self.art['flash'], (BOARD_X + x * TILE, BOARD_Y + y * TILE))
        if self.replay_mode:
            pygame.draw.rect(self.screen, (25, 37, 45), (BOARD_X + 7, BOARD_Y + 7, 212, 31))
            self._text(f'REPLAY {self.replay_index}/{len(self.records)}',
                       BOARD_X + 16, BOARD_Y + 13, 16, GOLD, True)
        if state.terminal:
            overlay = pygame.Surface((BOARD_W, 100), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 210))
            self.screen.blit(overlay, (BOARD_X, BOARD_Y + BOARD_H // 2 - 50))
            result = 'DRAW' if state.winner == -1 else f'PLAYER {state.winner + 1} WINS'
            title = self._font(36, True).render(result, True, GOLD)
            self.screen.blit(title, (BOARD_X + (BOARD_W - title.get_width()) // 2,
                                     BOARD_Y + BOARD_H // 2 - 23))

    def _hp_bar(self, x, y, value, maximum, color, label):
        self._text(label, x, y, 16, MUTED, True)
        self._text(f'{value} / {maximum}', x + 365, y - 1, 18, color, True)
        bx, by, bw, bh = x, y + 24, 464, 11
        pygame.draw.rect(self.screen, (42, 55, 67), (bx, by, bw, bh))
        if value > 0:
            pygame.draw.rect(self.screen, color, (bx, by, round(bw * value / maximum), bh))
        pygame.draw.rect(self.screen, BORDER, (bx, by, bw, bh), 1)

    def _draw_button(self, button: UIButton, active=False):
        self._box(button.rect, (35, 66, 63) if active else PANEL_LIGHT, BORDER, 4)
        f = self._font(13 if button.key in ('pause', 'replay', 'save_log') else 15, True)
        r = f.render(button.label, True, TEXT)
        self.screen.blit(r, (button.rect.centerx - r.get_width() // 2,
                             button.rect.centery - r.get_height() // 2))

    def _draw_replay_sidebar(self):
        self._box(pygame.Rect(SIDE_X, SIDE_Y, SIDE_W, SIDE_H))
        x = SIDE_X + 21
        self._text('BATTLE LOG / REPLAY', x, 145, 21, ORANGE, True)
        self._text(f'{self.scenario_name}  |  PLY {self.replay_index}/{len(self.records)}',
                   x, 180, 15, MUTED)
        pygame.draw.line(self.screen, BORDER, (x, 213), (x + 474, 213))
        state = self.display_state
        self._text(f'P1 Tank {state.tanks[0].hp}/6   Base {state.bases[0].hp}/9', x, 225, 15, CYAN)
        self._text(f'P2 Tank {state.tanks[1].hp}/6   Base {state.bases[1].hp}/9', x, 248, 15, GOLD)
        # Hien cac su kien gan vi tri replay dang xem
        start = max(0, self.replay_index - 10)
        end = min(len(self.records), start + 10)
        for i in range(start, end):
            rec = self.records[i]
            y = 291 + (i - start) * 30
            selected = (i + 1) == self.replay_index
            if selected:
                self._box(pygame.Rect(x - 5, y - 3, 474, 28), PANEL_LIGHT, None, 3)
            self._text(f'{i+1:03d} P{rec["player"]+1} {rec["action"].value}',
                       x, y, 14, GOLD if selected else TEXT)
            event = next((e for e in reversed(rec['events']) if 'hit ' in e or 'GAME OVER' in e), '')
            if event:
                self._text(event[:27], x + 215, y, 12, ORANGE if selected else MUTED)
        if not self.records:
            self._text('No actions yet. Play or STEP first.', x, 302, 16, MUTED)
        for button in self.buttons[9:]:
            self._draw_button(button)

    def _draw_sidebar(self):
        if self.replay_mode:
            self._draw_replay_sidebar()
            return
        self._box(pygame.Rect(SIDE_X, SIDE_Y, SIDE_W, SIDE_H))
        x = SIDE_X + 21
        self._text('MATCH CONTROL', x, 145, 19, ORANGE, True)
        self._text('TURN-BASED / 2 PLAYERS / 3 MAPS / ' +
                   ('TACTICAL AI' if self.gameplay_tactics else 'STRICT AI'),
                   x, 174, 15, MUTED)
        self._draw_button(self.buttons[0])
        self._text(f'MAP: {self.map_name}', x + 12, 215, 15, CYAN, True)
        self._text('>', x + 447, 215, 18, ORANGE, True)
        status = 'FINISHED' if self.state.terminal else ('PAUSED' if self.paused else 'RUNNING')
        self._text(f'STATUS  {status}', x, 254, 18, GREEN if status == 'RUNNING' else GOLD, True)
        self._text(f'PLY {self.state.ply:03d}', x + 370, 254, 18, TEXT, True)
        self._hp_bar(x, 287, self.state.tanks[0].hp, 6, CYAN, 'P1 TANK')
        self._hp_bar(x, 337, self.state.tanks[1].hp, 6, GOLD, 'P2 TANK')
        for i, y in enumerate((389, 451)):
            button = self.buttons[i + 1]
            self._box(button.rect, PANEL_LIGHT, BORDER, 4)
            color = CYAN if i == 0 else GOLD
            self._box(pygame.Rect(x + 9, y + 8, 34, 25),
                      (36, 65, 80) if i == 0 else (80, 62, 34), None, 3)
            self._text(f'P{i + 1}', x + 14, y + 12, 14, color, True)
            self._text(self.modes[i], x + 55, y + 10, 19, TEXT, True)
            self._text('>', x + 447, y + 11, 21, ORANGE, True)
            self._text(f'BASE HP {self.state.bases[i].hp}/9   |   LAST: {self.last_actions[i]}',
                       x + 6, y + 43, 13, MUTED)
        for button in self.buttons[3:9]:
            self._draw_button(button, button.key == 'pause' and not self.paused)
        self._text(f'SPEED: {self.interval} ms / turn', x, 603, 15, MUTED)
        self._text(f'SEARCH DEPTH: {self.depth}', x + 280, 603, 15, MUTED)
        pygame.draw.line(self.screen, BORDER, (x, 629), (x + 474, 629))
        self._text('LAST SEARCH', x, 635, 16, ORANGE, True)
        for i, y in enumerate((658, 679)):
            stats = self.stats[i]
            color = CYAN if i == 0 else GOLD
            line = (f'P{i + 1}   waiting for AI search' if stats is None else
                    f'P{i + 1}   {stats.nodes} nodes   {stats.elapsed_ms:.1f} ms   {stats.prunes} cuts')
            self._text(line, x, y, 14, color)
        self._draw_button(self.buttons[8])

    def _draw(self):
        self.screen.fill(BG)
        self._text('TANK BATTLE', 42, 29, 39, TEXT, True)
        self._text('BATTLE CITY STYLE  /  ADVERSARIAL SEARCH', 44, 79, 16, MUTED, True)
        self._text('MINIMAX  //  ALPHA-BETA  //  HEURISTIC', SIDE_X + 2, 54, 19, ORANGE, True)
        self._draw_board()
        self._draw_sidebar()
        self._text('SPACE Play/Pause   N Step   R Reset   M Map   G Random   L Replay', 44, 758, 16, MUTED)
        self._text('HUMAN: WASD move  |  F fire  |  X stay  |  ESC quit', 44, 784, 15, MUTED)
        self._text(self.notice[:54], SIDE_X + 1, 762, 15, GOLD)
        scaled = pygame.transform.scale(self.screen, self.window.get_size())
        self.window.blit(scaled, (0, 0))
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self._events()
            now = pygame.time.get_ticks()
            if not self.paused and not self.state.terminal and now - self.last_tick >= self.interval:
                self._step()
            self._draw()
            self.clock.tick(60)
        pygame.quit()


def run_app(depth=3, p0='Heuristic Alpha-Beta', p1='Heuristic Minimax',
            external_module='tankbattle.external_agents.example_agent',
            starting_state=None, scenario_name='Opening', gameplay_tactics=True,
            spawn_mode='balanced', spawn_seed=2026):
    BattleApp(depth, p0, p1, external_module,
              starting_state=starting_state, scenario_name=scenario_name,
              gameplay_tactics=gameplay_tactics,
              spawn_mode=spawn_mode, spawn_seed=spawn_seed).run()
