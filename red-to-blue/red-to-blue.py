import copy
import multiprocessing as mp
import os
import re
import time


def get_pint(msg):
    s = input(msg + "\n> ")
    try:
        s = float(s)
    except ValueError:
        return get_pint("The entered string is not a valid NUMBER.")
    i = int(s)
    if s != i:
        return get_pint("You must enter an INTEGER.")
    if i <= 0:
        return get_pint("The entered integer must be POSITIVE.")

    return i


def get_mat(x_size, y_size, msg):
    if x_size <= 0 or y_size <= 0:
        return []

    size = x_size * y_size
    s = ""

    print(msg)

    while len(s) != size:
        r = ''.join([i if i == '0' or i == '1' else '' for i in input("> ").replace('r', '0').replace('b', '1')])
        if len(r) == x_size or (len(r) == size and len(s) == 0):
            s += r

    m = re.findall('.' * x_size, s)
    for i in range(len(m)):
        c = [j for j in m[i]]
        for j in range(len(c)):
            c[j] = c[j] == '1'
        m[i] = c

    return m


def trigger_node(mat, coord):
    y_size = len(mat)
    x_size = len(mat[0])
    size = x_size * y_size

    flat_mat = [j for i in mat for j in i]
    coords_to_toggle = [coord, coord - x_size, coord + x_size]
    if coord % x_size != 0:
        coords_to_toggle.append(coord - 1)
    if coord % x_size != x_size - 1:
        coords_to_toggle.append(coord + 1)

    for i in coords_to_toggle:
        if 0 <= i < size:
            flat_mat[i] = not flat_mat[i]
    for i in range(y_size):
        for j in range(x_size):
            mat[i][j] = flat_mat[0]
            del flat_mat[0]


def is_solved(mat):
    flat_mat = [j for i in mat for j in i]
    return True if sum(flat_mat) == len(flat_mat) else False


def try_solution(current_mat, combination):
    binary_combination = f"{combination:b}"
    binary_combination = '0' * (len(current_mat) * len(current_mat[0]) - len(binary_combination)) + binary_combination

    trigger_map = binary_combination[::-1]

    for i in range(len(trigger_map)):
        if trigger_map[i] == '1':
            trigger_node(current_mat, i)

    return binary_combination


def try_combinations(initial_mat, max_combination, offset, increment, solved, queue):
    x_size = len(initial_mat[0])
    i = offset
    while i <= max_combination and not solved.is_set():
        current_mat = copy.deepcopy(initial_mat)
        binary_combination = try_solution(current_mat, i)

        if is_solved(current_mat):
            solved.set()
            print_solution(binary_combination[::-1], x_size, queue)
        i += increment


def solve_linear(initial_mat):
    x_size = len(initial_mat[0])
    max_combination = 2 ** (len(initialMat) * x_size)
    combination = 0

    while combination < max_combination:
        current_mat = copy.deepcopy(initial_mat)

        binary_combination = try_solution(current_mat, combination)

        if is_solved(current_mat):
            s = binary_combination[::-1]
            print_solution(s, x_size)

            break

        combination += 1


def solve_mp_div(initial_mat, queue):
    max_combination = 2 ** (len(initialMat) * len(initialMat[0]))

    is_solved = mp.Event()
    processes = []

    process_count = os.cpu_count()

    for i in range(process_count):
        p = mp.Process(target=try_combinations,
                       args=(initial_mat, max_combination, i, process_count, is_solved, queue))
        p.start()
        p.join()
        processes.append(p)

    is_solved.wait()

    for i in processes:
        i.kill()
        # i.terminate()


def print_solution(solution, x_size, queue=None):
    global computationStartTime

    if queue is not None:
        computationStartTime = queue.get()

    end_time = time.time()
    time_taken = end_time - computationStartTime
    
    rows = [solution[i:i + x_size] for i in range(0, len(solution), x_size)]

    print("\n\nMulti-line solution: ")
    print('\n'.join(rows))
    print("\nSingle-line solution:")
    print(' '.join(rows))

    print(f"\nStart time: {computationStartTime}")
    print(f"End time: {end_time}")
    print(f"Time taken: {time_taken}")


if __name__ == "__main__":
    mp.freeze_support()

    while True:
        s = input("Enter a method of solution. (lin, mp)\n> ").lower()
        while s != "lin" and s != "mp":
            s = input("You have entered an invalid option.\n> ").lower()

        xSize = get_pint("Enter the WIDTH of the puzzle.")
        ySize = get_pint("Enter the HEIGHT of the puzzle.")
        initialMat = get_mat(xSize, ySize, "Enter, in matrix form, the puzzle to be solved.")

        print("\nSolving...", end='')

        if s == "lin":
            computationStartTime = time.time()
            solve_linear(initialMat)
        if s == "mp":
            q = mp.Queue()
            q.put(time.time())
            solve_mp_div(initialMat, q)

        s = input("\nWould you like to solve another puzzle? (y/n)\n> ").lower()
        while s != "y" and s != "n" and s != "yes" and s != "no":
            s = input("You have entered an invalid option.\n> ").lower()

        if s[0] == 'n':
            input("\nPress enter to exit...")
            break

