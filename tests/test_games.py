from generator.themes.space_shooter import targets as shooter_targets


def test_quiet_graph_gets_ghost_targets(ctx, bare_ctx):
    real, ghosts = shooter_targets(bare_ctx)
    assert real == [] and len(ghosts) == 24
    real, ghosts = shooter_targets(ctx)
    assert ghosts == [] and len(real) == ctx.data.active_days


def test_shooter_sweeps_left_to_right_bottom_up(ctx):
    real, _ = shooter_targets(ctx)
    keys = [(c.col, -c.row) for c in real]
    assert keys == sorted(keys)


# --- snake ------------------------------------------------------------------

from generator.themes.snake import route  # noqa: E402
from generator.themes.snake import targets as snake_targets  # noqa: E402


def test_route_eats_every_goal_in_single_steps():
    goals = [(3, 0), (0, 2), (5, 5)]
    path, eaten = route(goals)
    assert set(eaten) == set(goals)
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        assert abs(x1 - x2) + abs(y1 - y2) == 1
    assert eaten[(0, 2)] < eaten[(3, 0)]  # nearest first: 2 steps away vs 3


def test_route_eats_a_goal_on_the_start_cell_immediately():
    assert route([(0, 0)]) == ([(0, 0)], {(0, 0): 0})


def test_snake_gets_ghost_targets_on_a_quiet_graph(bare_ctx):
    goals, ghost_set = snake_targets(bare_ctx)
    assert len(goals) == len(ghost_set) == 24
