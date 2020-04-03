from math import atan2, cos, pi, sin, sqrt
from sys import float_info
import sim_state
import config

HALF_PI = pi / 2

class ComputedValues:
    def __init__(self):
        self.computed = False
        self.diff_pos = None
        self.squared_distance = None
        self.adjusted_angle = None
        self.multiplier = 0

    def reset(self):
        self.computed = False
        self.diff_pos = None
        self.squared_distance = None
        self.adjusted_angle = None
        self.multiplier = None
# END class ComputedValues

class Boid:
    MAX_MAGNITUDE = 8
    VIEW_DISTANCE = 75
    SQUARED_VIEW_DISTANCE = VIEW_DISTANCE ** 2
    _VIEW_ANGLE = 0.75 * pi
    _D_THETA_PER_UPDATE = pi / 4
    _D_MAGNITUDE_PER_UPDATE = 0.075

    _NEUTRAL_COLOR = (0, 0, 0)
    _ACTIVE_COLOR = (228, 235, 26)

    _next_id = 0

    def __init__(self, init_position, init_magnitude, init_theta):        
        self._pos = [init_position[0], init_position[1]] # force to a list to allow reassignment.
        self._magnitude = min(max(init_magnitude, 0), Boid.MAX_MAGNITUDE)
        self._theta = _normalize_angle(init_theta)

        # "private" properties
        self._poly = [(8, 0), (-8, 6), (-4, 0), (-8, -6)]
        self._color = Boid._NEUTRAL_COLOR
        self._id = f'boid_{Boid._next_id}'

        # properties to help w/ computation
        self.relative_group_center = [0, 0]
        self.boids_in_view = 0
        self.d_theta = 0
        
        self._computation_color = False
        self._computed_values = {}

        # finally update the id counter
        Boid._next_id += 1


    def get_id(self):
        return self._id


    def get_pos(self):
        return self._pos


    def get_color(self):
        return self._color


    def get_vec(self):
        return (self._magnitude, self._theta)


    def get_poly(self):
        a = _rotate(self._poly[0], self._theta)
        b = _rotate(self._poly[1], self._theta)
        c = _rotate(self._poly[2], self._theta)
        d = _rotate(self._poly[3], self._theta)
        return _transpose([a, b, c, d], self._pos)


    def get_computed_values(self, other_id, other_color):
        if other_color != self._computation_color:
            return None

        if other_id in self._computed_values:
            return self._computed_values[other_id]

        return None


    def update(self, boid_groups):
        '''Update the boids speed, then position based on active rules'''

        self._color = Boid._NEUTRAL_COLOR
        self._computation_color = not self._computation_color

        # if the boid is not moving, it need not do anything to avoid the collision
        if self._magnitude == 0:
            return

        # read the state, in case it changes during execution.
        _separation = sim_state.SEPARATION
        _alignment = sim_state.ALIGNMENT
        _cohesion = sim_state.COHESION

        # if o rule is active, no need to do anything
        if not (_separation or _alignment or _cohesion):
            self._update_position()
            return

        # some computation is bound to take place, so we perpare
        self._reset_computation_properties()

        # iterate over each boid group
        for group in boid_groups:
            # iterate over each boid in the group
            for other in group:
                # don't check self
                if other.get_id() == self._id:
                    continue
                
                # see if the other boid already computed some variables
                computed_values = other.get_computed_values(self._id)
                if computed_values is None:
                    computed_values = ComputedValues()
                    self._computed_values[other.get_id()] = computed_values

                # If the other boid is not visible, we cannot act on it.
                if not self._can_see(other):
                    continue

                # follow the 3 rules if active
                if _separation:
                    self._avoid_collision(other)
                if _alignment:
                    self._align(other)

                # cohesion will try to go towards the center of the local group
                # however we will only compute the relative center
                if _cohesion:
                    self._adjust_relative_center()
            # end boid loop
        # end group loop

        if _cohesion:
            self._merge()

        self._theta += self.d_theta

        self._update_position()


    def _reset_computation_properties(self):
        self.relative_group_center = [0, 0]
        self.boids_in_view = 0
        self.d_theta = 0

        self._computed_values = {}


    def _enforce_bounds(self):
        # safety check: limit theta to +/- pi
        self._theta = _normalize_angle(self._theta)

        # safety check: limit magnitude to [0, 8]
        self._magnitude = min(max(self._magnitude, 0), Boid.MAX_MAGNITUDE)

        # wrapping behavior: wrap around to other end
        if self._pos[0] > config.SCREEN_SIZE[0] or self._pos[0] < 0:
            self._pos[0] %= config.SCREEN_SIZE[0] + 1
        if self._pos[1] > config.SCREEN_SIZE[1] or self._pos[1] < 0:
            self._pos[1] %= config.SCREEN_SIZE[1] + 1


    def _update_speed(self, d_megnitude, d_theta):
        # update theta
        self._theta += d_theta
        self._magnitude += d_megnitude
        

    def _can_see(self, other, comp_vals):
        # determine if the other's relative position to self
        o_pos = other.get_pos()
        if comp_vals.diff_pos is None:
            comp_vals.diff_pos = (o_pos[0]-self._pos[0], o_pos[1]-self._pos[1])

        # if the other is too far from self, we cannot see it
        if comp_vals.diff_pos[0] > Boid.VIEW_DISTANCE or \
            comp_vals.diff_pos[1] > Boid.VIEW_DISTANCE:
            return False

        # now we can compute and store the distance squared
        if comp_vals.squared_distance is None:
            comp_vals.squared_distance = comp_vals.diff_pos[0]**2 + comp_vals.diff_pos[1]**2
        
        if comp_vals.squared_distance > Boid.SQUARED_VIEW_DISTANCE:
            return False

        # determine the other boid's angle relative to self
        if comp_vals.diff_pos is None:
            if comp_vals.diff_pos[0] == 0:
                angle_from_boid = HALF_PI if comp_vals.diff_pos[1] >= 0 else -HALF_PI
            else:
                angle_from_boid = atan2(comp_vals.diff_pos[1], comp_vals.diff_pos[0])
                
            # adjust relative angle
            comp_vals.adjusted_angle = _normalize_angle(angle_from_boid - self._theta)
        else:
            comp_vals.adjusted_angle = _normalize_angle(comp_vals.adjusted_angle + pi - self._theta)
        

        # if we cannot see the other boid, do nothing
        if comp_vals.adjusted_angle >= Boid._VIEW_ANGLE or comp_vals.adjusted_angle <= -Boid._VIEW_ANGLE:
            return False

        # we can see the other boid!
        self.boids_in_view += 1
        self._color = Boid._ACTIVE_COLOR
        comp_vals.multiplier = 1 if comp_vals.squared_distance < 1 else 1 / sqrt(comp_vals.squared_distance)

        return True


    def _avoid_collision(self, other):
        # get the other's adjusted vector angle
        o_vec = other.get_vec()
        o_adjusted_theta = _normalize_angle(o_vec[1] - self._theta)

        ## first we consider some edge cases
        if _float_equals(self.adjusted_angle, 0):
            # case 1: boid is directly in front
            if o_vec[0] == 0:
                # case 1.1: stationary boid, move out of the way
                self.d_theta += Boid._D_THETA_PER_UPDATE * self.multiplier
                return
            elif _float_equals(o_adjusted_theta, 0):
                # case 1.2: moving away directly away. if too slow, dodge it otherwise no need to do anything
                if o_vec[0] < self._magnitude:
                    self.d_theta += Boid._D_THETA_PER_UPDATE * self.multiplier
                return
        # note, we do not need to consider a boids directly behind as we cannot see them
        # at this point, we know there is no boid directly in front, but if it's not moving, don't need to avoid it.
        if o_vec[0] == 0:
            return

        # last thing to check is if a collision will occur
        if not _in_range(o_adjusted_theta, (0, _normalize_angle(pi + self.adjusted_angle))):
            return
    
        # finally, since a collision may occur, we veer away from the other boid
        if self.adjusted_angle <= 0:
            self.d_theta += Boid._D_THETA_PER_UPDATE * self.multiplier
        else:
            self.d_theta -= Boid._D_THETA_PER_UPDATE * self.multiplier


    def _align(self, other):
        # we should only try to align with boids going in the same general direction
        # the rule will be that the angle difference cannot be more than pi/2
        o_vec = other.get_vec()
        angle_diff = o_vec[1] - self._theta

        # the absolute value must be less than pi/2
        if not -pi/2 <= angle_diff <= pi/2:
            return

        # optionally, if both boids are already going in the same direction, there is nothing to do.
        if _float_equals(angle_diff, 0):
            return

        # otherwise, we will try to fall into it's trajectory, but based on our distance to it.
        self.d_theta += angle_diff * self.multiplier


    def _adjust_relative_center(self):
        # we just add the values, no need to average as we want the angle in the end
        self.relative_group_center[0] += self.diff_pos[0]
        self.relative_group_center[1] += self.diff_pos[1]


    def _merge(self):
        if self.boids_in_view == 0:
            return

        # at this point, we want to move toward the relative group center
        relative_angle = atan2(self.relative_group_center[1], self.relative_group_center[0])
        self.d_theta += relative_angle * self.boids_in_view / 50


    def _update_position(self):
        # get update the position based on the speed
        delta = _to_vector(self._magnitude, self._theta)
        self._pos[0] += delta[0]
        self._pos[1] += delta[1]

        # enforce bounding
        self._enforce_bounds()
# END class Boid

def _to_vector(magnitude, theta):
    return [magnitude * cos(theta), magnitude * sin(theta)]


def _rotate(coord, theta):
    return [
        coord[0] * cos(theta) - coord[1] * sin(theta),
        coord[0] * sin(theta) + coord[1] * cos(theta)
        ]


def _transpose(coords, vec):
    updated_coords = []
    for point in coords:
        updated_coords.append([point[0] + vec[0], point[1] + vec[1]])
    return updated_coords


def _normalize_angle(theta):
    if theta > pi:
        theta -= 2 * pi
    elif theta <= -pi:
        theta += 2 * pi
    return theta


def _float_equals(val1, val2):
    return -float_info.epsilon <= val1 - val2 <= float_info.epsilon


def _in_range(value, _range):
    if _range[0] > _range[1]:
        return _range[0] >= value >= _range[1]
    return _range[1] >= value >= _range[0]
