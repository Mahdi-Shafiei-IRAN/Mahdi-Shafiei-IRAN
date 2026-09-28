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
