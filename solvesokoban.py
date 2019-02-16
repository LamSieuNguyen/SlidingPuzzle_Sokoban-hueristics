from sokoban import *
from heuristics import *
import search
import time
import signal
import argparse

class timeout:
    def __init__(self, seconds=1):
        self.seconds = seconds

    def timeoutCallback(self, signum, frame):
        raise TimeoutError("Timed out after " + str(self.seconds) + " seconds")

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.timeoutCallback)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)    
        
def main():
    parser = argparse.ArgumentParser(description='Solve Sokoban puzzles automatically or by hand.')
    parser.add_argument('puzzle_file', help='file containing the puzzle layout.')
    parser.add_argument('-p', '--playable', action='store_true', default=False, help='make the puzzle human-playable using the arrow keys')
    parser.add_argument('-nd', '--nodisplay', action='store_true', default=False, help='do not display the solution (has no effect with -p)')
    parser.add_argument('-n', '--null', action='store_true', default=False, help='use the null heuristic (has no effect with -p)')

    args = parser.parse_args()
    
    fin = open(args.puzzle_file)
    stateStr = fin.read()
    p = SokobanPuzzle(stateStr)
    print(p, end="")
    initState = p.getState()

    if not args.nodisplay or args.playable:
        display = SokobanDisplay(p)   

    if args.playable:
        turtle.onkey(display.moveNorth, "Up")
        turtle.onkey(display.moveSouth, "Down")
        turtle.onkey(display.moveWest, "Left")
        turtle.onkey(display.moveEast, "Right")
        print("Make sure the main window has focus.")
        print("Use the arrow keys to move.")
        print("If you get stuck, close the window to exit.")
        turtle.Screen().listen()
        turtle.mainloop()
    else:
        startT = time.time()
        with timeout(15):
            if args.null:
                h = NullHeuristic(p)
            else:
                h = SokobanHeuristic(p)
            path,cost,numExpanded = search.aStarSearch(p, h)    
        endT = time.time()

        print("Time spent: " + str(endT-startT) + " seconds")
        print("Nodes expanded: " + str(numExpanded))
        if path == [] and not p.isSolved():
            print("No solution found!")
            quit()
        else:     
            actionSeq = ""
            actions = {(0, 1):"E", (0, -1):"W", (1, 0):"S", (-1, 0):"N"}
            for a in path:
                actionSeq += actions[a]+" "       
            print("Action sequence: " + actionSeq)
            if args.nodisplay:
                print("Total cost: " + str(cost))
            else:
                p.setState(initState)
                for m in path:
                    display.move(m)
                    time.sleep(0.2)
    
if __name__ == "__main__":
    main()
