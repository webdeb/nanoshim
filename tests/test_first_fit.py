

def first_fit_pio(instructions_per_sm):
    free_instructions = [32, 32]
    sorted_sm = sorted(instructions_per_sm, key=lambda sm: sm[1], reverse=True)
    for (pio_idx, free) in enumerate(free_instructions):
        free_slots = 4
        for next_large in sorted_sm:
            if (free >= next_large[1] and len(next_large) == 3):
                sm_id = abs(free_slots - 4) + (pio_idx * 4)
                next_large.append(sm_id)
                free = free - next_large[1]
                free_slots = free_slots - 1

            if (free == 0 or free_slots == 0):
                break

    return sorted(sorted_sm, key=lambda sm: sm[0])

def group_list(list_to_group):
    last_pidx = list_to_group[-1][0]
    new_list = []
    for i in range(last_pidx + 1):
        ids = list(map(lambda i: [i[1], i[3]], sorted(filter(lambda l: l[0] == i, list_to_group), key=lambda i: i[2])))
        if (len(ids) == 1):
            new_list.append(ids[0][1])
        else:
            new_list.append(list(map(lambda i: i[1], ids)))
    
    return new_list

def test_first_fit_normal():
    data = [
        [0, 10, 0],
        [1, 10, 0],
    ]

    assert [
        [0, 10, 0, 0],
        [1, 10, 0, 1],
    ] == first_fit_pio(data)

def test_first_fit_normal_double():
    data = [
        [0, 10, 0],
        [0, 10, 1],
        [1, 10, 0],
    ]

    assert [
        [0, 10, 0, 0],
        [0, 10, 1, 1],
        [1, 10, 0, 2],
    ] == first_fit_pio(data)


def test_group():
        data = [    
        [0, 10, 0, 0],
        [0, 10, 1, 1],
        [1, 10, 0, 2],
        ]

        expected = [
             [0, 1],
             2,
        ]
        assert expected == group_list(data)
