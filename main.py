from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

import time
import chess
import stockfish

# TODO:
# scrape time and give to stockfish
# fix premove race condition breaking it. keep track of board.
# add chat insults

SF_THINK_TIME = 1000 # <-- TODO: Give sf real time from game.


# css selectors and scripts
S = {
    'bullet': 'div[data-id="1+0"]',
    'ai': '.color-submits [title="Black"]',
    'moves': 'u8t',
    'move_dest': '.move-dest',
    'piece': 'piece',
    'our_clock_running': '.rclock-bottom .running', # <-- use this when needed
    'your_turn': '.rclock-bottom .rclock-turn__text',
    'find_square': 'for(n of document.querySelectorAll("%s"))' \
                   + '{ if(n.cgKey === "%s"){return n} }',
}

# promotion selector index
P_PREFIX = '#promotion-choice'
P = {
    'q': '.queen',
    'n': 'knight',
    'b': 'bishop',
    'r': 'rook',
}


def get_board(d):
    # moves in form Nf6
    # POSSIBLE BUG: order may not be stable
    moves = [e.text for e in d.find_elements_by_css_selector(S['moves'])]

    b = chess.Board()

    for move in moves:
        b.push_san(move)

    return b


def find_move_dest(d, uci_move):
    dest = uci_move[2:4]
    return d.execute_script(S['find_square'] % (S['move_dest'], dest))


def find_piece(d, uci_move):
    src = uci_move[:2]
    return d.execute_script(S['find_square'] % (S['piece'], src))


def promote(d, choice):
    selector = P_PREFIX + ' ' + P[choice]
    elem = WebDriverWait(d, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
    )
    webdriver.ActionChains(d).move_to_element(elem).click().perform()


def make_move(d, uci_move):
    # 0.5. Wait for the piece to be clickable
    # (technically any piece, assume the board loads all at once.)
    WebDriverWait(d, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, S['piece']))
    )

    # 1. Find the piece we're moving
    piece = find_piece(d, uci_move)
    print('piece', piece)

    # 2. Click there
    webdriver.ActionChains(d).move_to_element(piece).click().perform()

    # 3.5. Wait for the click to be registered (for possible moves to be suggested)
    WebDriverWait(d, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, S['move_dest']))
    )

    # 3. Find the square/piece we're moving it to.
    dest = find_move_dest(d, uci_move)
    print('dest', piece)

    # 4. Click there
    webdriver.ActionChains(d).move_to_element(dest).click().perform()


    # 5. Deal with promotions if applicable
    if len(uci_move) > 4:
        promote(d, uci_move[-1])

    # 6. Wait for our move to go through (prevent race later on)
    WebDriverWait(d, 3).until(
        EC.invisibility_of_element((By.CSS_SELECTOR, S['your_turn']))
    )



def find_bullet_game(d):
    d.get('https://lichess.org')
    bullet = d.find_element_by_css_selector(S['bullet'])
    print('waiting for load...')
    bullet.click()
    time.sleep(3) # TODO: wait for load.
    print('done')


def find_computer_game(d):
    d.get('https://lichess.org/setup/ai')
    wait = WebDriverWait(d, 10)
    element = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, S['ai']))
    )
    e = d.find_element_by_css_selector(S['ai'])
    e.click()



def wait_for_turn(d):
    WebDriverWait(d, 1e7).until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, S['your_turn']), 'Your turn')
    )


def play_move(d, b, sf):
    sf.set_fen_position(b.fen())
    move = sf.get_best_move_time(SF_THINK_TIME)
    print('move', move)
    make_move(d, move)



def play_game(d, sf):
    SIDE = chess.BLACK

    while True:
        wait_for_turn(d)
        b = get_board(d)
        print(b)

        play_move(d, b, sf)


def main(d, sf):
    find_computer_game(d)
    play_game(d, sf)


d = webdriver.Chrome()
sf = stockfish.Stockfish()

# main(d, sf)
# print('[main] exited')

