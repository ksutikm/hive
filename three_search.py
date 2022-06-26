import math
# from turtle import tiles
from copy import deepcopy, copy

import pieces
from game_state import Game_State
from move_checker import is_valid_move, player_has_no_moves, game_is_over
import random

from settings import PIECE_WHITE, PIECE_BLACK, HEIGHT, WIDTH

# there is random bug choice
from tile import initialize_grid, Tile


# there is random bug choice
def random_move(state):
    tiles = gen_figures(state)
    moves = [tile for tile in tiles if len(tile) != 0]
    return random.choice(moves)


def gen_figures(state):
    # check tiles on field
    tiles = state.get_tiles_with_pieces(include_inventory=True)
    gen_tiles = []
    if state.turn % 2 == 1:
        color = PIECE_WHITE
    else:
        color = PIECE_BLACK
    board_tiles = board(state)
    for tile in tiles:
        if tile.color == color:
            # we need an abstract bug to implement game logic
            state.add_moving_piece(tile.pieces[-1])
            gen_tiles.append(moves_piece(state, tile, board_tiles))
    return gen_tiles


# movements title generation
def moves_piece(state, piece_title, board_tiles):
    pull_titles = []
    for title in board_tiles:
        if is_valid_move(state, piece_title, title):
            # pull_titles.append((copy_tile(piece_title), copy_tile(title)))
            pull_titles.append((piece_title, title))
    return pull_titles


def nearest_to_queen_hex(available_steps, state):
    # for step in available_steps:
    #     # print(step[0].pieces, step[1])
    #     print(step[1].__dict__)
    # print("choosen:", choosen[1].__dict__)
    tiles = state.get_tiles_with_pieces(include_inventory=False)
    for tile in tiles:
        # find the white queen
        if type(tile.pieces[0]).__name__ == "Queen" and tile.pieces[0].color == PIECE_WHITE:
            # find distances to white queen
            qx, qy = tile.axial_coords
            distance_to_queen = []
            for step in available_steps:
                x, y = step[1].axial_coords
                distance_to_queen.append(((qx - x)**2 + (qy - y)**2)**(1/2))
            # put the piece on the nearest hex
            nearest = distance_to_queen.index(min(distance_to_queen))
            return available_steps[nearest]
    return random.choice(available_steps)


def board(state):
    if state.turn < 1:
        min_x, min_y, max_x, max_y = 0, 0, 0, 0
    else:
        min_x, min_y, max_x, max_y = math.inf, math.inf, -math.inf, -math.inf
        for title in state.get_tiles_with_pieces():
            min_x = min(min_x, title.axial_coords[0])
            min_y = min(min_y, title.axial_coords[1])
            max_x = max(max_x, title.axial_coords[0])
            max_y = max(max_y, title.axial_coords[1])

    min_x, min_y, max_x, max_y = min_x - 2, min_y - 2, max_x + 2, max_y + 2
    tiles = []
    for title in state.board_tiles:
        coords = title.axial_coords
        if min_x <= coords[0] <= max_x and min_y <= coords[1] <= max_y:
            tiles.append(title)
    return tiles


def minimax(state, depth, alpha, beta, player=True):
    if depth <= 0 or game_is_over(state):
        # evaluation function value
        return None, evaluation_offensive(state)

    new_state = copy_state(state)
    tiles = gen_figures(new_state)
    moves = [tile for tile in tiles if len(tile) != 0]
    maximizing = new_state.turn % 2 != 0
    f = max if maximizing else min
    evaluations = {}
    # result = -math.inf if maximizing else math.inf
    for move in moves:
        new_state = do_move(state, move)
        # print('tiles', new_state.get_tiles_with_pieces())
        _, minmax = minimax(new_state, depth - 1, alpha, beta, not player)
        if maximizing:
            alpha = f(alpha, minmax)
        else:
            beta = f(beta, minmax)
        move[1].move_piece(move[0])
        evaluations[move] = minmax
        if beta <= alpha:
            break
    # if player:
    #     result = -math.inf
    #     for move in moves:
    #         new_state = do_move(state, move)
    #
    #         result = max(result, minimax(new_state, depth - 1, False))
    # else:
    #     result = math.inf
    #     for move in moves:
    #         new_state = do_move(state, move)
    #         result = min(result, minimax(new_state, depth - 1, True))

    if evaluations:
        best_move = f(evaluations, key=evaluations.get)
        return best_move, evaluations[best_move]
    else:
        return None, 0


def evaluation_offensive(state):
    if state.turn-1 % 2 == 1:
        color = PIECE_WHITE
        color2 = PIECE_BLACK
    else:
        color = PIECE_BLACK
        color2 = PIECE_WHITE
    tiles_pieces = state.get_tiles_with_pieces()

    value = 0
    # points for the piece on the board
    for tile in tiles_pieces:
        if tile.color == color:
            piece = tile.pieces[-1]
            if type(piece) is pieces.Queen:
                if 2 >= state.turn >= 1:
                    value += 0
                else:
                    value += 50
            if type(piece) is pieces.Grasshopper:
                value += 20
            if state.turn < 9:
                if type(piece) is pieces.Beetle:
                    value += 40
                elif type(piece) is pieces.Ant:
                    value += 40
                elif type(piece) is pieces.Spider:
                    value += 40
            else:
                if type(piece) is pieces.Beetle:
                    value += 20
                elif type(piece) is pieces.Ant:
                    value += 30
                elif type(piece) is pieces.Spider:
                    value += 10

            # if tile.adjacent_tiles)
            # adjacent_tiles_pieces = [tile for tile in tile.adjacent_tiles if tile.has_pieces()]
            # if len(adjacent_tiles_pieces) > 2
            # for adj_tile in tile.adjacent_tiles:
            #     if adj_tile.has_pieces() and adj_tile.color == color2:
            #         moves = moves_piece(state, adj_tile, color2)
            #         if len(moves) == 0:
            #             value += 5 * adj_tile

        for piece in tile.pieces:
            if type(piece) is pieces.Queen and piece.color == color2:
                for adj_tile in tile.adjacent_tiles:
                    if len(adj_tile.pieces) > 0:
                        value += 50

    return value


def do_move(state, step):
    new_state = state
    # state.add_moving_piece(step[1].pieces[-1])
    new_state.add_moving_piece(step[0].pieces[-1])
    step[0].move_piece(step[1])
    new_state.next_turn()
    if player_has_no_moves(state) and state.turn > 7:
        state.open_popup()
    new_state.remove_moving_piece()
    return new_state


def copy_state(state):
    new_state = Game_State(initialize_grid(HEIGHT - 200, WIDTH, radius=18))
    new_state.running = copy(state.running)
    new_state.menu_loop = copy(state.menu_loop)
    new_state.main_loop = copy(state.main_loop)
    new_state.end_loop = copy(state.end_loop)
    new_state.play_new_game = copy(state.play_new_game)
    new_state.move_popup_loop = copy(state.move_popup_loop)
    new_state.board_tiles = state.board_tiles[:]
    new_state.turn_panel = deepcopy(state.turn_panel)
    new_state.clicked = copy(state.clicked)
    new_state.moving_piece = copy(state.moving_piece)
    new_state.turn = copy(state.turn)
    new_state.winner = copy(state.winner)
    new_state.comp = copy(state.comp)
    return new_state


def copy_tile(tile):
    new_tile = Tile((0, 0), (0, 0), 0, PIECE_WHITE)
    new_tile.coords = copy(tile.coords)
    new_tile.axial_coords = copy(tile.axial_coords)
    new_tile.radius = copy(tile.radius)
    new_tile.hex = copy(tile.hex)
    new_tile.hex_select = copy(tile.hex_select)
    new_tile.color = copy(tile.color)
    new_tile.adjacent_tiles = tile.adjacent_tiles[:]
    new_tile.pieces = tile.pieces[:]
    return new_tile

