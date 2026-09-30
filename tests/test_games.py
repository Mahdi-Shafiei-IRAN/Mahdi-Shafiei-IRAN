from generator.themes.snake_trail import route


def test_route_eats_every_goal_in_single_steps():
    goals = [(3, 0), (0, 2), (5, 5)]
    path, eaten = route(goals)
    assert set(eaten) == set(goals)
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        assert abs(x1 - x2) + abs(y1 - y2) == 1
    assert eaten[(0, 2)] < eaten[(3, 0)]  # nearest first: 2 steps away vs 3


def test_route_eats_a_goal_on_the_start_cell_immediately():
    assert route([(0, 0)]) == ([(0, 0)], {(0, 0): 0})
