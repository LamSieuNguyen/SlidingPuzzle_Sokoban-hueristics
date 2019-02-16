'''Contains heuristics for sliding puzzles and Sokoban.'''
import numpy as np
from scipy.optimize import linear_sum_assignment

class NullHeuristic:
    '''The heuristic function that always returns 0.'''
    def __init__(self, problem):
        pass

    def eval(self, state):
        return 0

class NumMisplacedHeuristic:
    '''Gives the number of misplaced tiles.'''
    def __init__(self, problem):
        self.problem = problem

    def eval(self, state):
        curState = self.problem.getState()
        self.problem.setState(state)
        
        bound = 0
        board = self.problem.getBoard()
        for r in range(self.problem.getDim()[0]):
            for c in range(self.problem.getDim()[1]):
                if board[r][c] != r*self.problem.getDim()[1]+c:
                    bound+=1

        self.problem.setState(curState)
        return bound

class ManhattanHeuristic:
    '''Gives the Manhattan distance each tile's position to its position in the goal state.'''
    def __init__(self, problem):
        self.problem = problem

    def eval(self, state):
        curState = self.problem.getState()
        self.problem.setState(state)
        
        bound = 0
        for r in range(self.problem.getDim()[0]):
            for c in range(self.problem.getDim()[1]):
                tidx = self.problem.getTile(r,c)
                if tidx != 0:
                    tr = tidx//self.problem.getDim()[1]
                    tc = tidx%self.problem.getDim()[1]
                    bound+=abs(r-tr)+abs(c-tc)


        self.problem.setState(curState)
        return bound

class GaschnigsHeuristic:
    '''Gives the number of moves to the goal if any tile may swap with the blank tile.'''
    def __init__(self, problem):
        self.problem = problem

    def findMisplaced(self,brd,target):    
        for r in range(self.problem.getDim()[0]):
            for c in range(self.problem.getDim()[1]):
                tidx = brd[r][c]            
                correct = target[r][c]
                if(tidx != correct):
                    return tidx
                
    def findCorrect(self,brd,blank,target):
        correct = target[blank[0]][blank[1]]
        for r in range(self.problem.getDim()[0]):
            for c in range(self.problem.getDim()[1]):
                check = brd[r][c]        
                if(check == correct):
                    correct = target[blank[0]][blank[1]]
                    return check
                
    def FindTile(self, tile,brd):
         for r in range(self.problem.getDim()[0]):
            for c in range(self.problem.getDim()[1]):
                check = brd[r][c]
                if (check == tile):
                    return (r,c)

    def eval(self, state):
        curState = self.problem.getState()
        self.problem.setState(state)
        
        bound = 0
        brd = self.problem.getBoard()

        blank = self.problem.getPos()
        target=[[x*self.problem.getDim()[1]+y for y in range(self.problem.getDim()[1])] for x in range(self.problem.getDim()[0])]
        while (brd != target):
            if (blank != (0,0) and brd!= target):
                # checks what correct tile should be at the blank tile.
                tile = self.findCorrect(brd,blank,target)
                blankr = blank[0]
                blankc = blank[1]
                r = self.FindTile(tile,brd)[0]
                c = self.FindTile(tile,brd)[1]
          
                brd[r][c] = 0
                brd[blankr][blankc] = tile
                blank = (r,c)
                bound+=1
              
            elif (blank == (0,0) and brd!= target):
                #checks for non sorted tiles then switches)
                tile = self.findMisplaced(brd,target)
                blankr = blank[0]
                blankc = blank[1]
                r = self.FindTile(tile,brd)[0]
                c = self.FindTile(tile,brd)[1]
                brd[r][c] = 0
                brd[blankr][blankc] = tile
                blank = (r,c)
                bound+=1


        self.problem.setState(curState)
        return bound

class ComboHeuristic:
    '''Gives the max of Manhattan and Gaschnig's.'''
    def __init__(self, problem):
        self.problem = problem
        self.manhattan = ManhattanHeuristic(problem)
        self.gaschnigs = GaschnigsHeuristic(problem)

    def eval(self, state):
        curState = self.problem.getState()
        self.problem.setState(state)
        
        g_bound = self.gaschnigs.eval(state)
        m_bound = self.manhattan.eval(state)
        bound = max(g_bound,m_bound)

        self.problem.setState(curState)
        return bound

class SokobanHeuristic:
    def __init__(self, problem):
        self.problem = problem
        self.deadends = []
        brd = [["e" for y in range(self.problem.getDim()[1])]for x in range(self.problem.getDim()[0])]
        for r in range(self.problem.getDim()[0]):
            for c in range(self.problem.getDim()[1]):
                if self.problem.getItem(r,c) not in ["*","#","."]:
                    brd[r][c] = "."
                else:
                    brd[r][c] = self.problem.getItem(r,c)
                if self.problem.getItem(r,c)==".":
                    n = [self.problem.getItem(r-1,c),self.problem.getItem(r,c+1),self.problem.getItem(r+1,c),self.problem.getItem(r,c-1)]
                    d=-1
                    for k in range(len(n)):
                        if n[d]=="#" and n[d+1]=="#":
                            brd[r][c] = "X"
                            self.deadends.append((r,c))
                        d+=1


        # scan for potential tunnels        
        for r in range(self.problem.getDim()[0]):
            for c in range(self.problem.getDim()[1]):
                if brd[r][c]==".":
                    n = [brd[r-1][c],brd[r][c+1],brd[r+1][c],brd[r][c-1]]
                    if "#" in n:
                        brd[r][c] = "$"

        # detect the deadend tonnels
        for deadend in self.deadends:
            r,c = deadend[0],deadend[1]
            n = [brd[r-1][c],brd[r][c+1],brd[r+1][c],brd[r][c-1]]
            offs = [[-1,0],[0,1],[1,0],[0,-1]]
            for i in range(len(offs)):
                if n[i]=="$":
                    # traverse this way
                    visited = []
                    stop = False
                    tr,tc =  r,c
                    while not stop:
                        tr+=offs[i][0]
                        tc+=offs[i][1]
                        if brd[tr][tc]=="X":
                            stop = True
                            for v in visited:
                                brd[v[0]][v[1]] = "X"
                                self.deadends.append((v[0],v[1]))
                        elif brd[tr][tc]!="$":
                            stop = True
                        visited.append((tr,tc))


        
    def eval(self, state):
        curState = self.problem.getState()
        self.problem.setState(state)

        bound = 0
        boxes = self.problem.getBoxes()
        goals = self.problem.getGoals()

        # if one of the boxes in a deadend, no solution possible 
        for box in boxes:
            if (box[0],box[1]) in self.deadends:
                return float('inf')

        # calculate the distances from each box to each goal 
        cost = []
        for box in boxes:
            dists = []
            for goal in goals:
                dists.append(abs(box[0]-goal[0])+abs(box[1]-goal[1]))
            cost.append(dists)
        # perform perfect bipartite matching using Hungarian Algorithm (polynomial time)
        cost_mat = np.array(cost)
        ridx, cidx = linear_sum_assignment(cost_mat)
        total_cost = cost_mat[ridx,cidx].sum()
        # add the shortest distances from each box to its corresponding goal according to the matching
        bound += 2*total_cost

        p_pos = self.problem.getPos()
        shortest_dist = float('inf')
        for box in boxes:
            d = abs(box[0]-p_pos[0])+abs(box[1]-p_pos[1])
            if d<shortest_dist:
                shortest_dist = d
        bound+=(shortest_dist-1)

        self.problem.setState(curState)
        return bound
