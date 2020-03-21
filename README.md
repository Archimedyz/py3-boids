# py3-boids
Programming Boids in Python 3
This project was inspired by a video by **Sebastian Lague**: [Coding Adventure: Boids](https://www.youtube.com/watch?v=bqtqltqcQhw)
In his video, Sebastian moes up to 3D boids. I will stick with 2D boids for this project, as this is mainly a learning experience to familiarize myself with python 3.

## What's a boid?
Good question. Here's a [wikipedia article](https://en.wikipedia.org/wiki/Boids) explaining the origin of the term.
Basically, it's a bird/bee like object that follows s flocking/swarming behaviour.

## Rules
Boids follow three main rules: (I've borrowed these from Sebastian's video linked above.):
#### 1. Separation
Boids will try to avoid colliding with other boids
#### 2. Alignment
Boids will try to align their trajectory with surrounding Boids
#### 3. Cohesion
Boids will try to move to the center of the local group.

## Technical Details
I'll fill these out as the implementation becomes clearer and cleaner.
