# Quick computer art

How am I doing artwork right now?

- `Game.art` is just a list of lines to draw.
- The `points` that become the lines are in `Entity.artwork`.
    - The `Game` has a dict of entities, each with their own `artwork`.


```
+----------+
|     Game |
+----------+
|          |     +-------+
|      art | <-- | Art   |
|          |     +-------+
|          |     | lines | <-- list[Line2D]
|          |     +-------+
|          |
| entities | <-- dict[str, Entity]
+----------+


+---------+
|  Entity |
+---------+
|         |     +----------------+
| artwork | <-- |    Artwork     |
|         |     +----------------+
|         |     |        points  | <-- list[Point2D]
|         |     | point_offsets  | <-- list[Vec2D]
|         |     |         color  | <-- An enum from Colors
|         |     +----------------+
+---------+
```

