# Quick computer art

How am I doing artwork right now?

- `Game.art` is just a list of lines to draw.
- The `points` that become the lines are in `Entity.artwork`.
    - The `Game` has a dict of entities, each with their own `artwork`.


```
+----------+  +---------------------------+
|     Game |  |              Art          |
+----------+  +---------------------------+
|          |  | draw_lines(points, color) | <-- points, color
|          |  |                           |     Art knows how to draw lines from points
|          |  |                           |
|          |  |                     lines | <-- list[Line2D]
|          |  |                           |     Art stores the lines it draws in 'lines'
|          |  +---------------------------+
|          |
| entities | <-- dict[str, Entity]
+----------+
                        +---------+
                        |  Entity |
                        +---------+
                        |         |     +-----------------+
                        | artwork | <-- |     Artwork     |
                        |         |     +-----------------+
                        |         |     |          entity | <-- Access to its entity's data
                        |         |     |          color  | <-- An enum from Colors
                        |         |     |         points  | <-- list[Point2D]
                        |         |     | animated_points | <-- list[Point2D]
                        |         |     |                 |     Animated point = point + offset
                        |         |     |                 |     point_offsets: list[Vec2D]
                        |         |     +-----------------+
                        |         |
                        |  draw() | <-- Draw by calling Art.draw_lines(points, color)
                        +---------+
```

`Entity.draw(art)` gives its `points` and `color` to `Art`. The "shape" that is
drawn is defined when the Entity animates itself: in
`entity.artwork.animate()`, the points are reset. The random offsets to the
points are updated each period. The period is set by the
`entity.clocked_event_name`: the name of the `Game.timing` frame counter the
entity uses.

```
    +--------------+    +-------------------------+
    |              |    |                         |    +-----------------------------------+
    | Game.loop()  +--->| self.update_entities()  +--->| for each entity in Game.entities: |
    |              |    |                         |    +------------+----------------------+
    +-------+------+    +-------------------------+                 |
                                                                    v
                                                            +-----------------+     +-------------------------+
                                             Game.timing -->| entity.update() +---->| movement.update_speed() |
                                                            +-------+---------+     |                         |    +--------------------+
                                                                    |               | .update_position()      +--->| .origin += .speed  |
                                                                    |               +-----------+-------------+    +--------------------+
                                                                    |                           |
                                                                    |                           v
                                                                    |                  +--------------------+
                                                                    |                  |                    |       +-------------------------+
                                                                    |   Game.timing -->| artwork.animate()  +------>| ._reset_points()        |
                                                                    |                  |                    |       |                         |
                                                                    |                  +--------------------+       | If it is time, get new  |
                                                                    |                                               | random point offsets.   |
                                                                    |                                               +-------------------------+
                                                                    v
                                                            +---------------+
                                                            | entity.draw() |
                                                            +-------+-------+
                                                                    |
                                                                    v
                                                                +------------------+
                                              artwork.color, -->| Art.draw_lines() |
                                     artwork.animated_points()  +------------------+
                                                        ^
                                                        |
                             .points + .point_offsets ---
```

`_reset_points` uses the `entity.origin` to set the location of the shape to draw.
