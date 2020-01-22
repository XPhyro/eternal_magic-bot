import copy
import os
from multiprocessing import Process
import multiprocessing as mp
import re


def get_pint(msg):
    s = input(msg + "\n> ")
    try:
        s = float(s)
    except:
        s = get_pint("The entered string is not a valid number.")
    i = int(s)
    if s != i:
        i = get_pint("You must enter an integer.")
    if i <= 0:
        i = get_pint("The entered integer must be positive.")

    return i


def get_mat(x_size, y_size, msg):
    if x_size <= 0 or y_size <= 0:
        return []

    s = input(msg + "\n> ")
    s = s.replace('r', '0').replace('b', '1')
    s = ''.join([i if i == '0' or i == '1' else '' for i in s])
    if len(s) != x_size * y_size:
        s = get_mat(x_size, y_size, "The size of the interpreted matrix is inconsistent, try again.")

    m = re.findall('.' * x_size, s)
    for i in range(len(m)):
        c = [j for j in m[i]]
        for j in range(len(c)):
            c[j] = c[j] == '1'
        m[i] = c

    return m


def trigger_node(mat, coord):
    outer_size = len(mat)
    inner_size = len(mat[0])

    flat_mat = [j for i in mat for j in i]
    coords_to_toggle = [coord, coord - inner_size, coord + inner_size]
    if coord % inner_size != 0:
        coords_to_toggle.append(coord - 1)
    if coord % inner_size != inner_size - 1:
        coords_to_toggle.append(coord + 1)

    for i in coords_to_toggle:
        if 0 <= i < outer_size * inner_size:
            flat_mat[i] = not flat_mat[i]
    for i in range(outer_size):
        for j in range(inner_size):
            mat[i][j] = flat_mat[0]
            del flat_mat[0]
    return mat


def is_solved(mat):
    for i in [j for i in mat for j in i]:
        if not i:
            return False
    return True


# Used for multiprocessing (where each task gets a process)
def try_combination(x_size, size, initial_mat, combination, solved):
    current_mat = copy.deepcopy(initial_mat)

    binary_combination = f"{combination:b}";
    binary_combination = '0' * (size - len(binary_combination)) + binary_combination

    trigger_map = [True if i == '1' else False for i in binary_combination][::-1]
    for i in range(len(trigger_map)):
        if trigger_map[i]:
            current_mat = trigger_node(current_mat, i)

    if is_solved(current_mat):
        solved.set()
        s = binary_combination[::-1]
        print('\n\n' + '\n'.join(s[i:i + x_size] for i in range(0, len(s), x_size)))
        return


# Used for multiprocessing (where tasks are divided between few processes)
def try_combinations(x_size, size, initial_mat, combinations, solved):
    for combination in combinations:
        try_combination(x_size, size, initial_mat, combination, solved)


# # SERIAL PROCESSING START
# xSize = get_pint("Enter the WIDTH of the puzzle.")
# ySize = get_pint("Enter the HEIGHT of the puzzle.")
# initialMat = get_mat(xSize, ySize, "Enter, in matrix form, the puzzle to be solved.")
#
# size = ySize * xSize
# maxCombination = 2 ** size
#
# print("\nSolving...", end='')
#
# combination = 0
#
# while combination < maxCombination:
#     currentMat = copy.deepcopy(initialMat)
#
#     binaryCombination = f"{combination:b}";
#     binaryCombination = '0' * (size - len(binaryCombination)) + binaryCombination
#
#     triggerMap = [True if i == '1' else False for i in binaryCombination][::-1]
#     for i in range(len(triggerMap)):
#         if triggerMap[i]:
#             currentMat = trigger_node(currentMat, i)
#
#     if is_solved(currentMat):
#         s = binaryCombination[::-1]
#         print('\n\n' + '\n'.join(s[i:i + xSize] for i in range(0, len(s), xSize)))
#         break
#
#     combination += 1
#
# input("\nPress enter to exit . . .")
# # SERIAL PROCESSING END


# # MULTIPROCESSING (Each tasks gets a process)
# if __name__ == "__main__":
#     xSize = get_pint("Enter the WIDTH of the puzzle.")
#     ySize = get_pint("Enter the HEIGHT of the puzzle.")
#     initialMat = get_mat(xSize, ySize, "Enter, in matrix form, the puzzle to be solved.")
#
#     size = ySize * xSize
#     maxCombination = 2 ** size
#
#     print("\nSolving...", end='')
#
#     isSolved = mp.Event()
#     processes = []
#
#     for i in range(maxCombination):
#         p = Process(target=try_combination, args=(xSize, size, initialMat, i, isSolved))
#         p.start()
#         # p.join()
#         processes.append(p)
#
#     isSolved.wait()
#
#     for i in processes:
#         i.kill()
#         # i.terminate()
#         i.join()
#
#     input("\nPress enter to exit . . .")
# # MULTIPROCESSING (Each task gets a process)


# # MULTIPROCESSING START (Tasks are divided between few processes)
if __name__ == "__main__":
    xSize = get_pint("Enter the WIDTH of the puzzle.")
    ySize = get_pint("Enter the HEIGHT of the puzzle.")
    initialMat = get_mat(xSize, ySize, "Enter, in matrix form, the puzzle to be solved.")

    size = ySize * xSize
    maxCombination = 2 ** size

    print("\nSolving...", end='')

    isSolved = mp.Event()
    processes = []

    cpuCount = os.cpu_count()
    # TODO: This way, the code uses too much memory; find a better way to split the list between processes.
    # TODO: Use xrange(cpuCount)
    chunks = [[i for i in range(maxCombination)][i::cpuCount] for i in range(cpuCount)]

    for i in range(len(chunks)):
        p = Process(target=try_combinations, args=(xSize, size, initialMat, chunks[0], isSolved))
        p.start()
        # p.join()
        processes.append(p)
        chunks = chunks[1::]

    isSolved.wait()

    for i in processes:
        i.kill()
        # i.terminate()
        i.join()

    input("\nPress enter to exit . . .")
# # MULTIPROCESSING END (Tasks are divided between few processes)
