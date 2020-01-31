import pandas as pd
from itertools import groupby
import queue
import numpy as np
import time
import sys
import json
from bs4 import BeautifulSoup
import os
import lxml

""" This is a map finding program that uses BFS(Breadth First Search) algorithm. """


''' VALIDATING DOCUMENT, PATH, FORMAT AND CONTENT FOR MAP CREATION '''


def content_is_valid(content):
    # Validating content through tags
    err = "Error. Document content invalid or missing data."
    try:
        # start point
        sp_row = content.map.startpoint["row"]
        sp_col = content.map.startpoint["col"]
        # end point
        ep_row = content.map.endpoint["row"]
        ep_col = content.map.endpoint["col"]

        if not sp_col.isupper() or not ep_col.isupper:
            sys.exit(err)
        elif len(sp_col) != 1 or len(ep_col) != 1:
            sys.exit(err)
        elif len(sp_row) != 1 or len(ep_row) != 1:
            sys.exit(err)

        # start and end point coordinates
        start_point = [int(sp_row), sp_col]
        end_point = [int(ep_row), ep_col]

        # rows and columns coordinates
        rows = []
        cols = []
        for item in content.findAll('cell'):
            if not item["col"].isupper():
                sys.exit(err)
            elif len(item["col"]) != 1 or len(item["row"]) != 1:
                sys.exit(err)
            rows.append(int(item['row']))
            cols.append(item['col'])

    except AttributeError:
        sys.exit(err)
    except TypeError:
        sys.exit(err)
    except KeyError:
        sys.exit(err)
    except ValueError:
        sys.exit(err)

    return rows, cols, start_point, end_point


doc_input = str(input("Enter document's path for map description parameter: "))

start_time = time.time()

if doc_input == "":
    sys.exit("Error. Parameter unspecified.")
elif doc_input[-5:] != ".html" and doc_input[-4:] != ".xml":
    sys.exit("Error. Invalid document format.")
else:
    try:
        doc_open = open(doc_input, mode="r", encoding="utf-8")
        doc_read = doc_open.read().replace("-", "")

        soup = BeautifulSoup(doc_read, "lxml-xml")
        doc_open.close()

        Rows, Columns, StartPoint, EndPoint = content_is_valid(soup)

    except FileNotFoundError:
        sys.exit("Error. Document is not found or wrong document path.")


''' MAP CREATION '''


row_count = list({key: len(list(group)) for key, group in groupby(Rows)}.values())

rows_and_columns_array = []
c = 0
for b in row_count:
    rows_and_columns_array.append(Columns[c:b+c])
    c += b

# Making a dictionary for DataFrame insert
data = [dict.fromkeys(d, " ") for d in rows_and_columns_array]

ROW = sorted(set(Rows))
COL = sorted(set(Columns))

# Creating a map (DataFrame) with obstacles (#)
map_maze = pd.DataFrame(data, index=ROW, columns=COL)
map_maze = map_maze.replace(np.nan, "#")

# start and end point coordinates check and map insert
if map_maze.loc[StartPoint[0], StartPoint[1]] == "#" or map_maze.loc[EndPoint[0], EndPoint[1]] == "#":
    sys.exit("Invalid Start or End point coordinates.")
else:
    map_maze.loc[StartPoint[0], StartPoint[1]] = "S"
    map_maze.loc[EndPoint[0], EndPoint[1]] = "E"

# print(map_maze) # remove the number sign to print the map

''' MAIN SECTION '''

# Making a 2D array structure for Maze
Maze = []
for e in range(len(ROW)):
    f = []
    Maze.append(f)
    for g in range(len(COL)):
        f.append(map_maze.loc[ROW[e], COL[g]])


def moves_making(maze, moves):
    # Finding the start point
    for h in maze:
        if "S" in h:
            k = maze.index(h)
            starting = h.index("S")

    i = starting
    j = k
    position = []
    for move in moves:
        if move == "L":
            i -= 1

        elif move == "R":
            i += 1

        elif move == "U":
            j -= 1

        elif move == "D":
            j += 1
        position.append((j, i))
    return i, j, position


def print_maze(maze, ex_time,  path=""):
    i, j, position = moves_making(maze, path)

    # rows and  columns coordinates output and drawing a path with +
    cols = [StartPoint[1]]
    rws = [StartPoint[0]]
    for p in position:
        rws.append(p[0]+1)
        for num, item in enumerate(COL):
            if p[1] == num:
                cols.append(item)
                map_maze.at[p[0]+1, item] = "+"

    print(map_maze)
    # Task solution export
    export = ({'execution_time_in_ms: ': round(ex_time * 1000),
               "paths": [{"points": [{'row': k, 'col': v} for k, v in zip(rws, cols)]}]})

    with open("Task_Solution.json", "w") as outfile:
        json.dump(export, outfile, indent=4)
        print("Task solution path:", os.path.abspath('Task_Solution.json'))


def valid(maze, moves):
    i, j, pos = moves_making(maze, moves)

    # Move validation
    if not (0 <= i < len(maze[0]) and 0 <= j < len(maze)):
        return False
    elif maze[j][i] == "#":
        return False
    return True


def end_find(maze, moves, fail):
    i, j, pos = moves_making(maze, moves)

    if maze[j][i] == "E":
        # print("Moves: " + moves) # Remove the number sign to print the moves
        print_maze(maze, execution_time, moves)
        return True
    elif len(moves) == fail:
        sys.exit("Path cannot be found.")
    return False

# MAIN ALGORITHM


nums = queue.Queue()
nums.put("")
add = ""
execution_time = (time.time() - start_time)

while not end_find(Maze, add, len(Rows)):
    add = nums.get()
    # print(add) # Remove the number sign to print all combinations
    for r in ["L", "R", "U", "D"]:
        put = add + r
        if valid(Maze, put):
            nums.put(put)

