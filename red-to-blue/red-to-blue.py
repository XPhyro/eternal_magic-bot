import copy
import os
from multiprocessing import Process
import multiprocessing as mp
import re
import time


def get_pint(msg):
    s = input(msg + "\n> ")
    try:
        s = float(s)
    except:
        s = get_pint("The entered string is not a valid NUMBER.")
    i = int(s)
    if s != i:
        i = get_pint("You must enter an INTEGER.")
    if i <= 0:
        i = get_pint("The entered integer must be POSITIVE.")

    return i


def get_mat(x_size, y_size, msg):
    if x_size <= 0 or y_size <= 0:
        return []

    s = input(msg + "\n> ")
    s = s.replace('r', '0').replace('b', '1')
    s = ''.join([i if i == '0' or i == '1' else '' for i in s])
    if len(s) != x_size * y_size:
        return get_mat(x_size, y_size, "The size of the interpreted matrix is inconsistent, try again.")

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
def try_combination(x_size, size, initial_mat, combination, solved, queue):
    current_mat = copy.deepcopy(initial_mat)

    binary_combination = f"{combination:b}"
    binary_combination = '0' * (size - len(binary_combination)) + binary_combination

    trigger_map = [True if i == '1' else False for i in binary_combination][::-1]
    for i in range(len(trigger_map)):
        if trigger_map[i]:
            current_mat = trigger_node(current_mat, i)

    if is_solved(current_mat):
        solved.set()
        s = binary_combination[::-1]
        print_solution(s, x_size, queue)
        return


# Used for multiprocessing (where tasks are divided between few processes)
def try_combinations(x_size, size, initial_mat, combinations, solved, queue):
    for combination in combinations:
        try_combination(x_size, size, initial_mat, combination, solved, queue)


def solve_linear(x_size, size, initial_mat):
    max_combination = 2 ** size

    combination = 0

    while combination < max_combination:
        current_mat = copy.deepcopy(initial_mat)

        binary_combination = f"{combination:b}";
        binary_combination = '0' * (size - len(binary_combination)) + binary_combination

        trigger_map = [True if i == '1' else False for i in binary_combination][::-1]
        for i in range(len(trigger_map)):
            if trigger_map[i]:
                current_mat = trigger_node(current_mat, i)

        if is_solved(current_mat):
            s = binary_combination[::-1]
            print_solution(s, x_size, None)

            break

        combination += 1


def solve_mp_per(x_size, size, initial_mat, queue):
    max_combination = 2 ** size

    is_solved = mp.Event()
    processes = []

    for i in range(max_combination):
        p = Process(target=try_combination, args=(x_size, size, initial_mat, i, is_solved, queue))
        p.start()
        # p.join()
        processes.append(p)

    is_solved.wait()

    for i in processes:
        i.kill()
        # i.terminate()
        i.join()


def solve_mp_div(x_size, size, initial_mat, queue):
    max_combination = 2 ** size

    is_solved = mp.Event()
    processes = []

    cpu_count = os.cpu_count()
    # TODO: This way, the code uses too much memory; find a better way to split the list between processes.
    # TODO: Use xrange(cpuCount)
    chunks = [[i for i in range(max_combination)][i::cpu_count] for i in range(cpu_count)]

    for i in range(len(chunks)):
        p = Process(target=try_combinations, args=(x_size, size, initial_mat, chunks[0], is_solved, queue))
        p.start()
        p.join()
        processes.append(p)
        chunks = chunks[1::]

    is_solved.wait()

    for i in processes:
        i.kill()
        # i.terminate()
        i.join()


def print_solution(solution, x_size, queue):
    global computationStartTime

    if queue is not None:
        computationStartTime = queue.get()

    end_time = time.time()
    time_taken = end_time - computationStartTime

    print('\n\n' + '\n'.join(solution[i:i + x_size] for i in range(0, len(solution), x_size)))

    print(f"\nStart time: {computationStartTime}")
    print(f"End time: {end_time}")
    print(f"Time taken: {time_taken}")


if __name__ == "__main__":
    mp.freeze_support()

    # firstRun = True
    while True:
        # if firstRun:
        #     s = input("Enter a method of solution. (lin, mp-per, mp-div)\n> ")
        #     while s != "lin" and s != "mp-per" and s != "mp-div":
        #         s = input("You have entered an invalid option.\n> ")
        # else:
        #     s = "lin"
        #     print("This is not the program's first solution; therefore, multiprocessing is disabled.")
        #     print("If you would like to solve using multiprocessing, restart the program.")
        #
        # firstRun = False

        s = input("Enter a method of solution. (lin, mp-per, mp-div)\n> ")
        while s != "lin" and s != "mp-per" and s != "mp-div":
            s = input("You have entered an invalid option.\n> ")

        xSize = get_pint("Enter the WIDTH of the puzzle.")
        ySize = get_pint("Enter the HEIGHT of the puzzle.")
        initialMat = get_mat(xSize, ySize, "Enter, in matrix form, the puzzle to be solved.")

        size = xSize * ySize

        print("\nSolving...", end='')

        if s == "lin":
            computationStartTime = time.time()
            solve_linear(xSize, size, initialMat)
        else:
            q = mp.Queue()
            q.put(time.time())

            if s == "mp-per":
                solve_mp_per(xSize, size, initialMat, q)
            if s == "mp-div":
                solve_mp_div(xSize, size, initialMat, q)

        s = input("\nWould you like to solve another puzzle? (y/n)\n> ").lower()
        while s != "y" and s != "n" and s != "yes" and s != "no":
            s = input("You have entered an invalid option.\n> ").lower()

        if s[0] == "n":
            input("Press enter to exit...")
            break
