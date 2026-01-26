# Discrete Time Physics

## Unity time step

Think of time as discrete steps where each step size is the period of the video
frame, whatever that happens to be. Count time in units of video frames. Call
this `n`. Then the step size, `Δn`, is always 1.

## Sum equations

On every frame, update state variables position and velocity (and acceleration
if force is not constant) using the difference equations:

* `v(n) = Δx(n)/Δn = Δx(n)`
* `a(n) = Δv(n)/Δn = Δv(n)`

I define the difference equations this way so that the connection to
derivatives (and analytical physics) is obvious. But the state variable updates
are actually done as **sum equations** (integrals), not as difference equations
(derivatives).

In other words, the calculations to update the state start with finding the
acceleration from the mass and the total forces, then updating the velocity
based on the acceleration, and finally updating the position based on the
velocity.

## State variable update

Take the simple case where the force is constant (e.g., simulating gravity).
Then acceleration is a constant and so we do not need to update acceleration,
only velocity and position:

```
// Update velocity
v(n) += a(n)

// Update position
x(n) += v(n)
```

In general, each update starts with force. Force drives all physics. Position
and velocity are just manifestations of how the forces play out.

## Examples of force

Some examples of force:

* The simplest is constant force, like gravity.
    * Imagine a platformer: the constant acceleration due to gravity acts on
      all entities. This is a constant force.
    * It is always present and always the same value (per unit mass).
* The player UI is an example of a quantized force.
    * A joystick or keyboard input determines the forces acting on the player
      entity  to tell the player which way to go. This is a quantized force
      because the UI is a logic input (up/down/left/right).
    * Even if I give the player controls like "double-push" runs faster in that
      direction, that still only adds another set of quantized values.
    * Contrast this with an analog UI like a steering wheel that gives the
      amount of left/right turning and a gas/brake that gives the amount of
      acceleration/deceleration.
    * Note that in either case, quantized or analog, the UI input does not
      directly control position; the UI input controls force, and then the game
      engine figures out how that force manifests as a change in velocity and
      position.
* The most complex is an analog force.
    * Imagine an NPC that follows the player. The NPC's displacement vector
      (the directed line segment from NPC to player) towards the
      player determines the force acting on the NPC entity.
    * This is an analog force because the NPC calculates its aim to be whatever
      vector takes it from its current position to the player's position. The
      "aim" is not locked to quantized amounts of up/down/left/right.
    * The "aiming force" is analogous to the restoring force of a stretched
      spring, where the equilibrium position is whatever distance the NPC
      wishes to have from the player. So the further the NPC is from that
      equilibrium distance, the stronger the force it feels pushing it towards
      the player entity.
    * The "aiming" force can be any linear combination of x and y components;
      it is not locked to the x and y components of 0 and 1.

## Unity mass

Acceleration is force divided by mass. Let all masses be one (for now). Then
acceleration is numerically equivalent to force.

## Example update under a constant force

Before trying anything out in code, it's easiest to play with parameters and
get a feel for what is happening using a spreadsheet and plotting position vs
time.

## Example where forces depend on position and velocity

This example simulates a mass on a spring.

Make a spreadsheet with the following columns:

```
    n | d(n)          | v(n)           | ft(n)         | fk(n)     | fb(n)     |
    = | =             | =              | =             | =         | =         |
IC  0 | 1             | 0              | -             | -         | -         |
    = | =             | =              | =             | =         | =         |
    1 | d(n-1) + v(n) | v(n-1) + ft(n) | fk(n) + fb(n) | -k*d(n-1) | -b*v(n-1) |
    2 | d(n-1) + v(n) | v(n-1) + ft(n) | fk(n) + fb(n) | -k*d(n-1) | -b*v(n-1) |
    ...
  200 | d(n-1) + v(n) | v(n-1) + ft(n) | fk(n) + fb(n) | -k*d(n-1) | -b*v(n-1) |
```

* `IC` initial conditions
    * In this simulation, entities have an initial position and velocity. The
      forces result from these initial conditions, so we do not have initial
      values for the forces. The forces depend on values of position and
      velocity at the previous timestep, so we cannot calculate values for the
      forces at video frame zero.
* `n` number of video frames (the discrete time variable)
* `d(n)` 1d "displacement" vector, using sign to indicate direction
    * `d(n) = d(n-1) + v(n)`
    * Since the timestep is unity, this is the sum equation (the inverse of the difference equation)
* `v(n)` 1d "velocity" vector, using sign to indicate direction
    * `v(n) = v(n-1) + ft(n)`
    * Since the timestep is unity, this is the sum equation (the inverse of the difference equation)
* `ft(n)` 1d "total force" vector, using sign to indicate direction
    * `ft(n) = fk(n) + fb(n)`
    * Since mass is unity, this total force column also plays the role of
      acceleration.
* `fk(n)` 1d "restoring (spring) force" vector, using sign to indicate direction
    * Spring constant is `k`
    * `fk(n) = -1*k*d(n-1)`
    * Note this is based on the value of displacement at the previous timestep
* `fb(n)` 1d "friction force" vector, using sign to indicate direction
    * Friction constant is `b`
    * `fb(n) = -1*b*v(n-1)`
    * Note this is based on the value of velocity at the previous timestep

Try:
    * IC `d(n) = 10, v(n) = 0`
    * spring constant `k=0.1`
    * damping constant `b=0.02`

# Comparison With Continuous Time Physics

For now, I am taking the simplest approach to game physics (though I suspect
I'll need to rethink this when I start accounting for collisions). As long as
I update position using a physics Δt that is less than or equal to my video
frame period, motion should appear to follow a smooth curve: I am updating
positions each time I visually "sample" my world. My brain will connect those
samples with a smooth curve.

Being as lazy as possible, I let one unit of time equal the period of one video
frame. That means I update position each video frame. I don't care how much
clock time actually elapsed (so if my frame rate tanks, my physics slows down
too, which is fine for now).

This choice of Δt means my time step size is 1, which means I am doing discrete
math where my difference equations (e.g., Δf(n)/Δn) all have denominators of
one, which means that the discrete time function 2^n plays the role of the
continuous time function e^t in that d(e^t)/dt = e^t and Δ(2^n)/Δn = 2^n, or
simply Δ(2^n) = 2^n.

Rather than come up with closed form solutions, I am updating my state
variables each frame. But I still want to see how my discrete time math ties
back to continuous time closed form solutions that I am familiar with, and so
much of the discussion below is from that motivation.

## A system where force is constant

Consider a continuous time problem: a projectile thrown straight up and then
falling back to the ground. It's acceleration due to gravity is constant, which
means its velocity is a linear function of time, which means its position is a
quadratic function of time.

## A system where forces depend on position and velocity

Consider a continuous time problem: a mass on a spring with friction. The
position of the mass is a result of the forces on the mass. The potential
energy of the compressed or stretched spring and the kinetic energy of the
moving mass are two energy storage elements that exchange energy while the
total energy in the system decreases due to heat loss to the force of friction.
Depending on the size of the mass, the spring constant of the spring, and the
friction of the surface, we might observe oscillatory behavior with an
exponentially decaying envelope or we might observe a decaying exponential
without any oscillatory behavior.
