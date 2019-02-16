from slidingpuzzle import *
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
    parser = argparse.ArgumentParser(description='Solve sliding puzzles automatically or by hand.')
    parser.add_argument('-f', '--file', type=str, help='display the puzzle using the image in FILE (must be a GIF). Has no effect if TRIALS > 1')
    parser.add_argument('-p', '--playable', action='store_true', default=False, help='make the puzzle human-playable using the mouse (requires an image file)')
    parser.add_argument('-r', '--rows', type=int, default=3, help='the puzzle will have ROWS rows (default 3)')
    parser.add_argument('-c', '--columns', type=int, default=3, help='the puzzle will have COLUMNS columns (default 3)')
    parser.add_argument('-d', '--depth', default=4, type=int, help='the solution depth -- the scrambled puzzle will take DEPTH steps to solve (default 4)')
    parser.add_argument('-t', '--trials', type=int, default=1, help='independently generate TRIALS puzzles to solve and report average results (default 1). Has no effect with -p')

    args = parser.parse_args()
       
    if args.playable:
        if args.file == None:
            raise FileNotFoundError("No image file specified. Use -f FILE to specify a filename.")
        p = SlidingPuzzle(args.rows, args.columns, args.depth)
        print(p, end="")
        initState = p.getState()    
        display = SlidingPuzzleDisplay(p, args.file)   
        print("Click to move tiles.")
        while(not p.isSolved()):
            display.clickMove()
    else:
        if args.trials > 1:
            random.seed(0)        
        p = SlidingPuzzle(args.rows, args.columns, 0)
        startStates = p.getScrambledStates(args.depth, args.trials)

        heuristics = [NullHeuristic(p), NumMisplacedHeuristic(p), ManhattanHeuristic(p), GaschnigsHeuristic(p), ComboHeuristic(p)]
        avgTimes = [0]*len(heuristics)
        avgExpanded = [0]*len(heuristics)
        for t in range(args.trials):
            initState = startStates[t]
            p.setState(initState)
            if args.trials > 1:
                print("Trial " + str(t+1))
            print(p, end="")

            if args.file != None and args.trials == 1:
                display = SlidingPuzzleDisplay(p, args.file)

            times = []
            expanded = []
            for h in range(len(heuristics)):
                p.setState(initState)
                startT = time.time()        
                with timeout(15):
                    path,cost,numExpanded = search.aStarSearch(p, heuristics[h])
                endT = time.time()
                avgTimes[h] += endT-startT
                avgExpanded[h] += numExpanded
                times.append("{0:.5f}".format(endT-startT))
                expanded.append(str(numExpanded))
            print("Heuristic:\tNull\t\t# Misplaced\tManhattan\tGaschnig's\tCombo")
            print("Time Taken:\t"+"\t\t".join(times))
            print("Nodes Expanded:\t" + "\t\t".join(expanded))
            if path == [] and not p.isSolved():
                print("No solution found!")
                quit()
            else:     
                actionSeq = ""
                actions = {(0, 1):"E", (0, -1):"W", (1, 0):"S", (-1, 0):"N"}
                for a in path:
                    actionSeq += actions[a]+" "       
                print("Action sequence: " + actionSeq)
                if args.file == None or args.trials != 1:
                    print("Total cost: " + str(cost))
                else:
                    p.setState(initState)
                    for m in path:
                        display.move(m)
                        time.sleep(0.2)
            print("-----------------------------")

        if args.trials > 1:
            avgTimes = ["{0:.5f}".format(avgTimes[i]/args.trials) for i in range(len(avgTimes))]
            avgExpanded = [str(avgExpanded[i]/args.trials) for i in range(len(avgExpanded))]
            print("Heuristic:\t\tNull\t\t# Misplaced\tManhattan\tGaschnig's\tCombo")
            print("Avg. Time Taken:\t"+"\t\t".join(avgTimes))
            print("Avg. Nodes Expanded:\t" + "\t\t".join(avgExpanded))
                                                
if __name__ == "__main__":
    main()
