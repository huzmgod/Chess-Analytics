from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import re
import chess
import chess.pgn
import io
from stockfish import Stockfish
from selenium.webdriver.chrome.service import Service
stockfish = Stockfish("<your stockfish path>")

######### CONSTANTS ##########

d = {
    'WHITE_KNIGHT': 'N',
    'WHITE_BISHOP': 'B',
    'WHITE_ROOK': 'R',
    'WHITE_QUEEN': 'Q',
    'WHITE_KING': 'K',
    'WHITE_PAWN': '',
    'BLACK_KNIGHT': 'N',
    'BLACK_BISHOP': 'B',
    'BLACK_ROOK': 'R',
    'BLACK_QUEEN': 'Q',
    'BLACK_KING': 'K',
    'BLACK_PAWN': '',
    'NO_CAPTURE': '',
    'DIRECT_CAPTURE': 'x',
    'CHECK': '+',
    'CHECKMATE': '#',
    'EN_PASSANT': 'e.p.',
    'CASTLE_KINGSIDE': 'O-O',
    'CASTLE_QUEENSIDE': 'O-O-O',
    'PAWN_PROMOTION': '=',
}

########## FUNCTIONS ##########
def array2Fen(moves):
    pgn = ''
    move_num = 1
    for move in moves:
        pgn += str(move_num) + '. '
        pgn += move + ' '
        move_num += 1
    pgn_ = pgn
    pgn = io.StringIO(pgn)
    try:
        game = chess.pgn.read_game(pgn)
        board = chess.Board()
        for move in game.mainline_moves():
            board.push(move)
        return board.fen(), pgn_
    except:
        return "Error"

def getMovePgnFormat(top_moves_info):

    prettyMoves = []
    for i, topMoves in enumerate(top_moves_info):
        move = getOneMovePgnFormat(topMoves['Move'])
        prettyMoves.append(move)
    return prettyMoves

def getOneMovePgnFormat(mateSequenceMove):
    someMove = mateSequenceMove
    pieceOrigin = someMove[:2]
    pieceDestiny = someMove[2:]
    if(stockfish.will_move_be_a_capture(someMove) == stockfish.Capture.DIRECT_CAPTURE):
        if(stockfish.get_what_is_on_square(pieceOrigin) == stockfish.Piece.WHITE_PAWN or \
            stockfish.get_what_is_on_square(pieceOrigin) == stockfish.Piece.BLACK_PAWN):
            pieceOrigin = pieceOrigin[0] + d['DIRECT_CAPTURE']
        else:
            pieceOrigin = d[str(stockfish.get_what_is_on_square(pieceOrigin)).replace('Piece.', '')] + d['DIRECT_CAPTURE']
    # elif(stockfish.will_move_be_a_capture(someMove) == stockfish.Capture.EN_PASSANT):
    #    pieceOrigin = d[str(stockfish.get_what_is_on_square(pieceOrigin)).replace('Piece.', '')] + d['EN_PASSANT']
    elif(stockfish.will_move_be_a_capture(someMove) == stockfish.Capture.NO_CAPTURE):
        pieceOrigin = d[str(stockfish.get_what_is_on_square(pieceOrigin)).replace('Piece.', '')] + d['NO_CAPTURE']
        if(pieceOrigin == 'K' and someMove == 'e1g1'):
            pieceOrigin,pieceDestiny = d['CASTLE_KINGSIDE'], ''
        elif(pieceOrigin == 'K' and someMove == 'e1c1'):
            pieceOrigin,pieceDestiny = d['CASTLE_QUEENSIDE'], ''
        elif(pieceOrigin == 'K' and someMove == 'e8g8'):
            pieceOrigin,pieceDestiny = d['CASTLE_KINGSIDE'], ''
        elif(pieceOrigin == 'K' and someMove == 'e8c8'):
            pieceOrigin,pieceDestiny = d['CASTLE_QUEENSIDE'], ''
    move = f"{pieceOrigin}{pieceDestiny}"
    return move

def getEval(fen,variations = 3):
    mateSequence = []

    if stockfish.is_fen_valid(fen):
        stockfish.set_fen_position(fen)
        # Get top moves in the current position
        top_moves_info = stockfish.get_top_moves(variations)
        # Look for a forced mate situation
        for i, move_info in enumerate(top_moves_info):
            stockfish.set_fen_position(fen)
            # Check if there is a mate in one move
            mate = []
            mate_move_index = move_info['Mate']
            if isinstance(move_info['Mate'],int):
                while(mate_move_index >= 1):
                # Find index of forced mating move in principal variation list
                    mate.append(getOneMovePgnFormat(move_info['Move']))
                    if (mate_move_index == 1):
                        break
                    stockfish.make_moves_from_current_position([move_info['Move']])
                    move_info = stockfish.get_top_moves(1)[0]
                    mate_move_index = move_info['Mate']
                mateSequence.append(mate)
        stockfish.set_fen_position(fen)
        # Get moves in PGN format
        prettyMoves = getMovePgnFormat(top_moves_info)
    for k in range(len(top_moves_info)):
        top_moves_info[k]['Move'] = prettyMoves[k]
    # If no forced mate was found or input FEN is invalid, return an empty list
    return top_moves_info, mateSequence


def checkIfValidMoves(htmlStoragedmoves):
    moves = []
    previousDataPly = 0
    missingDataPly, lastDataPly = None, None

    for item in htmlStoragedmoves:
        divs = item.split('<div')
        for div in divs[1:]:
            if "timestamp" in div or "data-tooltip" in div: # skip divs with timestamp
                continue
            dataPly = int(div.split('"')[1])
            if dataPly != previousDataPly + 1 and dataPly != previousDataPly:
                missingDataPly = previousDataPly + 1
            previousDataPly = dataPly

        if dataPly is not None:
            lastDataPly = dataPly

        value = splitHtml(item)
        moves.append(value)

    if missingDataPly:
        print(f'Missing move for data-ply {missingDataPly}')
        raise Exception(f'Missing move {missingDataPly}... RECALCULATING')

    return moves, lastDataPly

def splitHtml(html):

    # Parse the HTML string with BeautifulSoup
    htmlText = BeautifulSoup(html, 'html.parser')

    # Find the div elements with the classes "white" and "black"
    white_div = htmlText.find('div', {'class': 'white node'})
    white_div_selected = htmlText.find('div', {'class': 'white node selected'})
    black_div = htmlText.find('div', {'class': 'black node'})
    black_div_selected = htmlText.find('div', {'class': 'black node selected'})

    # Initialize dictionary with null values
    game_dict = {'moveNumber': '', 'whiteMove': '', 'whiteFigure': '', 'blackMove': '', 'blackFigure': ''}

    # Get the move number from the HTML text using regular expressions
    move_number = re.search(r'^\d+', html)
    if move_number:
        game_dict['moveNumber'] = move_number.group()
    # print(game_dict)
    # Get the white move text
    if white_div:
        game_dict['whiteMove'] = white_div.text.strip()
        # Find the span element with class "icon-font-chess" and get the "data-figurine" attribute value
        white_span = white_div.find('span', {'class': 'icon-font-chess'})
        if white_span and 'circle-info' not in white_span.get('class', []):
            game_dict['whiteFigure'] = white_span['data-figurine']

    elif white_div_selected:
        game_dict['whiteMove'] = white_div_selected.text.strip()
        # Find the span element with class "icon-font-chess" and get the "data-figurine" attribute value
        white_span = white_div_selected.find('span', {'class': 'icon-font-chess'})
        if white_span and 'circle-info' not in white_span.get('class', []):
            game_dict['whiteFigure'] = white_span['data-figurine']
    # print(game_dict)
    # Get the black move text
    if black_div:
        game_dict['blackMove'] = black_div.text.strip()
        # Find the span element with class "icon-font-chess" and get the "data-figurine" attribute value
        black_span = black_div.find('span', {'class': 'icon-font-chess'})
        if black_span and 'circle-info' not in black_span.get('class', []):
            game_dict['blackFigure'] = black_span['data-figurine']
    elif black_div_selected:
        game_dict['blackMove'] = black_div_selected.text.strip()
        # Find the span element with class "icon-font-chess" and get the "data-figurine" attribute value
        black_span = black_div_selected.find('span', {'class': 'icon-font-chess'})
        if black_span and 'circle-info' not in black_span.get('class', []):
            game_dict['blackFigure'] = black_span['data-figurine']
    # Print the resulting dictionary

    # handle pawn promotion
    if('=' in game_dict['whiteMove']):
        builtMove = game_dict['whiteMove'] + \
            game_dict['whiteFigure'] + ' ' + game_dict['blackFigure'] + game_dict['blackMove']
    elif('=' in game_dict['blackMove']):
        builtMove = game_dict['whiteFigure'] + \
            game_dict['whiteMove'] + ' ' + game_dict['blackMove'] + game_dict['blackFigure']
    else:
        builtMove = game_dict['whiteFigure'] + \
        game_dict['whiteMove'] + ' ' + game_dict['blackFigure'] + game_dict['blackMove']

    if '+' in builtMove:
        singleSpace = builtMove[-1]
        builtMove = builtMove.replace('+', '').strip()
        builtMove += '+'
        if singleSpace == ' ':
            builtMove += ' '
    # print(builtMove)
    return builtMove

def main():
    currentPos = []
    lastFen, lastPgn = "", ""
    moveNumber = 0
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(service=Service('<your chromedriver path>'), options=options)

    # Set up Firefox webdriver
    #driver = webdriver.Firefox()

    # Open the webpage
    driver.get("http://chess.com")
    lastEval = None

    while True:
        htmlStoragedMoves = []
        try:
            elements = WebDriverWait(driver, 10, 0.1).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "move"))
        )
            for elem in elements:
                htmlStoragedMoves.append(elem.get_attribute('innerHTML'))

            currentPos, lastMoveNumberChecked = checkIfValidMoves(htmlStoragedMoves)

            if lastMoveNumberChecked == 1 and moveNumber > 1:
                with open('games.txt', 'a') as f:
                    f.write(f"GAME: {lastPgn}\n")
                lastFen = ""
                moveNumber = 0

            if lastMoveNumberChecked > moveNumber:
                moveNumber = lastMoveNumberChecked
                fen, lastPgn = array2Fen(currentPos)
                if fen == "Error":
                    lastFen = ""
                    moveNumber = 0
                    currentPos = []
                    continue

                if lastFen != fen:
                    c = ['WHITE', 'BLACK']
                    color = 0
                    if(moveNumber%2 == 0):
                        color = 1

                    lastEval, mateSequence = getEval(fen)

                    if (lastEval == []):
                        print("NO EVALUATION")
                        continue
                    else:
                        data = []
                        for i, topMoves in enumerate(lastEval):
                            score, mateMoves = '', ''
                            if (isinstance(topMoves['Centipawn'], int)): score = f"{topMoves['Centipawn']/100}"
                            elif (isinstance(topMoves['Mate'], int)):
                                score = f"{d['CHECKMATE']}{topMoves['Mate']}"
                                for elem in mateSequence:
                                    mateMoves = " ".join(elem)
                                    break

                            data.append({'move': topMoves['Move'], 'eval': score, 'mate': mateMoves})
                        lastFen = fen

        except:
            pass
            # If there's an error, print it out
            # print("Error retrieving elements")

if __name__ == "__main__":
    main()
