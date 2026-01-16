```
update_entities()
    |
    \--> for each entity:
            |
            v
            entity.update()
            |
            \-> npc_update():
            |       |   If left of player, go right, stop going left.
            |       |   If right of player, go left, stop going right.
            |       |   If aligned with player, stop going left and stop going right.
            |       v
            |   move():
            |       |
            |       \-> update_speed():
            |       |       If going left, add speed.accel to speed.left
            |       |       If not going left, sub speed.slide from speed.left
            |       |       If going right, add speed.accel to speed.right
            |       |       If not going right, sub speed.slide from speed.right
            |       |
            |       \-> update_position()
            |       |
            |       \-> update_is_moving()
            |       |
            |       v
            |   animate():
            |       |
            |       \-> reset_points()
            |       |
            |       \-> if it is time, calculate new point offsets
            |       |
            |       v
            v
            entity.draw():
                set color
                draw lines
```
