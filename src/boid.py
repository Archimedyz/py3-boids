from math import atan2, cos, pi, sin, sqrt
from sys import float_info
import sim_state
import config

HALF_PI = pi / 2

class ComputedValues:
    def __init__(self):
        self.diff_pos = None
        self.squared_distance = None
        self.adjusted_angle = None
        self.multiplier = 0

    def reset(self):
        self.diff_pos = None
        self.squared_distance = None
        self.adjusted_angle = None
        self.multiplier = None
# END class ComputedValues

class Boid:
    __MAX_MAGNITUDE = 8
    __VIEW_DISTANCE = 75
    __SQUARED_VIEW_DISTANCE = __VIEW_DISTANCE ** 2
    __VIEW_ANGLE = 0.75 * pi
    __D_THETA_PER_UPDATE = pi / 4
    __D_MAGNITUDE_PER_UPDATE = 0.075

    __NEUTRAL_COLOR = (0, 0, 0)
    __ACTIVE_COLOR = (228, 235, 26)

    __next_id = 0

    def __init__(self, init_position, init_magnitude, init_theta):
        self.__id = f'boid_{Boid.__next_id}'
        self.__pos = [init_position[0], init_position[1]] # force to a list to allow reassignment.
        self.__magnitude = min(max(init_magnitude, 0), Boid.__MAX_MAGNITUDE)
        self.__theta = normalize_angle(init_theta)
        self.__poly = [(8, 0), (-8, 6), (-4, 0), (-8, -6)]
        self.__color = Boid.__NEUTRAL_COLOR

        # properties to help w/ computation
        self.__relative_group_center = [0, 0]
        self.__boids_in_view = 0
        self.__d_theta = 0

        self.__computation_color = False
        self.__computed_values_dict = {}

        # finally update the id counter
        Boid.__next_id += 1


    @staticmethod
    def get_view_distance():
        '''Get the view distance for Boids'''
        return Boid.__VIEW_DISTANCE


    @staticmethod
    def get_max_magnitude():
        '''Get the maximum magnitude for Boids'''
        return Boid.__MAX_MAGNITUDE


    def get_id(self):
        '''Returns the boid's ID'''
        return self.__id


    def get_pos(self):
        '''Returns the boid's position'''
        return self.__pos


    def get_color(self):
        '''Returns the boid's color'''
        return self.__color


    def get_vec(self):
        '''Returns the boid's velocity vector'''
        return (self.__magnitude, self.__theta)


    def get_poly(self):
        '''Returns the boid's rotated poly'''
        a = rotate(self.__poly[0], self.__theta)
        b = rotate(self.__poly[1], self.__theta)
        c = rotate(self.__poly[2], self.__theta)
        d = rotate(self.__poly[3], self.__theta)
        return transpose([a, b, c, d], self.__pos)


    def get_computed_values(self, other_id, other_computation_color):
        '''Return values computed against the other boid'''
        if other_computation_color != self.__computation_color:
            return None

        if other_id in self.__computed_values_dict:
            return self.__computed_values_dict[other_id]

        return None


    def update(self, boid_groups):
        '''Update the boids speed, then position based on active rules'''

        self.__color = Boid.__NEUTRAL_COLOR
        self.__computation_color = not self.__computation_color

        # if the boid is not moving, it need not do anything to avoid the collision
        if self.__magnitude == 0:
            return

        # read the state, in case it changes during execution.
        separation = sim_state.SEPARATION
        alignment = sim_state.ALIGNMENT
        cohesion = sim_state.COHESION

        # if o rule is active, no need to do anything
        if not (separation or alignment or cohesion):
            self.__update_position()
            return

        # some computation is bound to take place, so we perpare
        self.__reset_computation_properties()

        # iterate over each boid group
        for group in boid_groups:
            # iterate over each boid in the group
            for other in group:
                # don't check self
                if other.get_id() == self.__id:
                    continue

                # see if the other boid already computed some variables
                comp_vals = other.get_computed_values(self.__id, self.__computation_color)
                if comp_vals is None:
                    comp_vals = ComputedValues()
                    self.__computed_values_dict[other.get_id()] = comp_vals

                # If the other boid is not visible, we cannot act on it.
                if not self.__can_see(other, comp_vals):
                    continue

                # follow the 3 rules if active
                if separation:
                    self.__avoid_collision(other, comp_vals)

                if alignment:
                    self.__align(other, comp_vals)

                # cohesion will try to go towards the center of the local group
                # however we will only compute the relative center
                if cohesion:
                    self.__adjust_relative_center(comp_vals)
            # end boid loop
        # end group loop

        if cohesion:
            self.__merge()

        self.__theta += min(self.__d_theta, Boid.__MAX_MAGNITUDE)

        self.__update_position()


    def __reset_computation_properties(self):
        self.__relative_group_center = [0, 0]
        self.__boids_in_view = 0
        self.__d_theta = 0

        self.__computed_values_dict = {}


    def __enforce_bounds(self):
        # safety check: limit theta to +/- pi
        self.__theta = normalize_angle(self.__theta)

        # safety check: limit magnitude to [0, 8]
        self.__magnitude = min(max(self.__magnitude, 0), Boid.__MAX_MAGNITUDE)

        # wrapping behavior: wrap around to other end
        if self.__pos[0] > config.SCREEN_SIZE[0] or self.__pos[0] < 0:
            self.__pos[0] %= config.SCREEN_SIZE[0] + 1
        if self.__pos[1] > config.SCREEN_SIZE[1] or self.__pos[1] < 0:
            self.__pos[1] %= config.SCREEN_SIZE[1] + 1


    def __can_see(self, other, comp_vals):
        # determine if the other's relative position to self
        o_pos = other.get_pos()
        if comp_vals.diff_pos is None:
            comp_vals.diff_pos = (o_pos[0]-self.__pos[0], o_pos[1]-self.__pos[1])
        else:
            comp_vals.diff_pos = (-comp_vals.diff_pos[0], -comp_vals.diff_pos[1])

        # if the other is too far from self, we cannot see it
        if comp_vals.diff_pos[0] > Boid.__VIEW_DISTANCE or \
            comp_vals.diff_pos[1] > Boid.__VIEW_DISTANCE:
            return False

        # now we can compute and store the distance squared
        if comp_vals.squared_distance is None:
            comp_vals.squared_distance = comp_vals.diff_pos[0]**2 + comp_vals.diff_pos[1]**2

        if comp_vals.squared_distance > Boid.__SQUARED_VIEW_DISTANCE:
            return False

        # determine the other boid's angle relative to self
        if comp_vals.adjusted_angle is None:
            if comp_vals.diff_pos[0] == 0:
                angle_from_boid = HALF_PI if comp_vals.diff_pos[1] >= 0 else -HALF_PI
            else:
                angle_from_boid = atan2(comp_vals.diff_pos[1], comp_vals.diff_pos[0])

            # adjust relative angle
            comp_vals.adjusted_angle = normalize_angle(angle_from_boid - self.__theta)
        else:
            comp_vals.adjusted_angle = normalize_angle(comp_vals.adjusted_angle + pi - self.__theta)


        # if we cannot see the other boid, do nothing
        if comp_vals.adjusted_angle >= Boid.__VIEW_ANGLE or comp_vals.adjusted_angle <= -Boid.__VIEW_ANGLE:
            return False

        # we can see the other boid!
        self.__boids_in_view += 1
        self.__color = Boid.__ACTIVE_COLOR
        comp_vals.multiplier = 1 if comp_vals.squared_distance > 10 else 10 / sqrt(comp_vals.squared_distance)

        return True


    def __avoid_collision(self, other, comp_vals):
        # get the other's adjusted vector angle
        o_vec = other.get_vec()
        o_adjusted_theta = normalize_angle(o_vec[1] - self.__theta)

        ## first we consider some edge cases
        if float_equals(comp_vals.adjusted_angle, 0):
            # case 1: boid is directly in front
            if o_vec[0] == 0:
                # case 1.1: stationary boid, move out of the way
                self.__d_theta += Boid.__D_THETA_PER_UPDATE * comp_vals.multiplier
                return
            elif float_equals(o_adjusted_theta, 0):
                # case 1.2: moving away directly away. if too slow, dodge it otherwise no need to do anything
                if o_vec[0] < self.__magnitude:
                    self.__d_theta += Boid.__D_THETA_PER_UPDATE * comp_vals.multiplier
                return
        # note, we do not need to consider a boids directly behind as we cannot see them
        # at this point, we know there is no boid directly in front, but if it's not moving, don't need to avoid it.
        if o_vec[0] == 0:
            return

        # last thing to check is if a collision will occur
        if not in_range(o_adjusted_theta, (0, normalize_angle(pi + comp_vals.adjusted_angle))):
            return

        # finally, since a collision may occur, we veer away from the other boid
        if comp_vals.adjusted_angle <= 0:
            self.__d_theta += Boid.__D_THETA_PER_UPDATE * comp_vals.multiplier
        else:
            self.__d_theta -= Boid.__D_THETA_PER_UPDATE * comp_vals.multiplier


    def __align(self, other, comp_vals):
        # we should only try to align with boids going in the same general direction
        # the rule will be that the angle difference cannot be more than pi/2
        o_vec = other.get_vec()
        angle_diff = o_vec[1] - self.__theta

        # the absolute value must be less than pi/2
        if not -pi/2 <= angle_diff <= pi/2:
            return

        # optionally, if both boids are already going in the same direction, there is nothing to do.
        if float_equals(angle_diff, 0):
            return

        # otherwise, we will try to fall into it's trajectory, but based on our distance to it.
        self.__d_theta += angle_diff * comp_vals.multiplier


    def __adjust_relative_center(self, comp_vals):
        # we just add the values, no need to average as we want the angle in the end
        self.__relative_group_center[0] += comp_vals.diff_pos[0]
        self.__relative_group_center[1] += comp_vals.diff_pos[1]


    def __merge(self):
        if self.__boids_in_view == 0:
            return

        # at this point, we want to move toward the relative group center
        relative_angle = atan2(self.__relative_group_center[1], self.__relative_group_center[0])
        self.__d_theta += relative_angle * self.__boids_in_view / 50


    def __update_position(self):
        # get update the position based on the speed
        delta = to_vector(self.__magnitude, self.__theta)
        self.__pos[0] += delta[0]
        self.__pos[1] += delta[1]

        # enforce bounding
        self.__enforce_bounds()
# END class Boid

def to_vector(magnitude, theta):
    return [magnitude * cos(theta), magnitude * sin(theta)]


def rotate(coord, theta):
    return [
        coord[0] * cos(theta) - coord[1] * sin(theta),
        coord[0] * sin(theta) + coord[1] * cos(theta)
        ]

def transpose(coords, vec):
    updated_coords = []
    for point in coords:
        updated_coords.append([point[0] + vec[0], point[1] + vec[1]])
    return updated_coords


def normalize_angle(theta):
    if theta > pi:
        theta -= 2 * pi
    elif theta <= -pi:
        theta += 2 * pi
    return theta


def float_equals(val1, val2):
    return -float_info.epsilon <= val1 - val2 <= float_info.epsilon


def in_range(value, _range):
    if _range[0] > _range[1]:
        return _range[0] >= value >= _range[1]
    return _range[1] >= value >= _range[0]
