from enum import Enum

import pygame
import math

# Calculation related constants
AU = 149.6e9  # 1 AU (1 Astronomical Unit) = 149.6 million km = 149.6 billion m = 149.6e9 m
G = 6.67428e-11  # Gravitational constant

# UI related constants
WIDTH, HEIGHT = 800, 800
SCALE = 200 / AU
TIME_STEP = 60 * 60 * 24  # 1 day
FPS = 60


class Color(Enum):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    YELLOW = (255, 255, 0)
    GRAY = (128, 128, 128)
    ORANGE = (255, 128, 0)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)


class CelestialObject:

    def __init__(self,
                 name,
                 radius,
                 color,
                 mass,
                 position=(0, 0),
                 velocity=(0, 0)):
        self.name = name
        self.radius = radius
        self.color = color
        self.mass = mass

        self.x, self.y = position
        self.x_vel, self.y_vel = velocity

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def set_velocity(self, x_vel, y_vel):
        self.x_vel = x_vel
        self.y_vel = y_vel

    def get_position(self):
        return self.x, self.y

    def calculate_distance_vectors(self, other_body):
        other_x, other_y = other_body.get_position()
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        return distance_x, distance_y

    def calculate_force_vectors(self, other_body):
        distance_x, distance_y = self.calculate_distance_vectors(other_body)
        distance = math.dist(self.get_position(), other_body.get_position())

        force = G * self.mass * other_body.mass / distance**2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force

        return force_x, force_y

    def update_position(self, bodies):
        total_fx = total_fy = 0
        for body in bodies:
            if self == body:
                continue

            fx, fy = self.calculate_force_vectors(body)
            total_fx += fx
            total_fy += fy

        self.x_vel += total_fx / self.mass * TIME_STEP
        self.y_vel += total_fy / self.mass * TIME_STEP

        self.x += self.x_vel * TIME_STEP
        self.y += self.y_vel * TIME_STEP

    def draw(self, window, font):
        x = self.x * SCALE + WIDTH / 2
        y = self.y * SCALE + HEIGHT / 2

        pygame.draw.circle(window, self.color.value, (x, y), self.radius)
        body_name = font.render(self.name, True, Color.WHITE.value)
        window.blit(body_name, (x, y + self.radius))


class Planet(CelestialObject):

    def __init__(self,
                 name,
                 parent_star,
                 radius,
                 color,
                 mass,
                 position=(0, 0),
                 velocity=(0, 0)):
        super().__init__(name, radius, color, mass, position, velocity)

        self.orbit = []
        self.parent_star = parent_star
        self.distance_to_parent = math.dist(self.get_position(),
                                            parent_star.get_position())

    def draw(self, window, font):
        # Draw Orbit
        if len(self.orbit) > 2:
            updated_points = []
            for point in self.orbit:
                x, y = point
                x = x * SCALE + WIDTH / 2
                y = y * SCALE + HEIGHT / 2
                updated_points.append((x, y))
            pygame.draw.lines(window, self.color.value, False, updated_points,
                              1)

        x = self.x * SCALE + WIDTH / 2
        y = self.y * SCALE + HEIGHT / 2

        # Draw Planet
        pygame.draw.circle(window, self.color.value, (x, y), self.radius)

        # Display Name and Distance
        planet_name = font.render(self.name, True, Color.WHITE.value)
        window.blit(planet_name, (x, y + self.radius))

    def update_position(self, bodies):
        super().update_position(bodies)
        self.distance_to_parent = math.dist(self.get_position(),
                                            self.parent_star.get_position())
        self.orbit.append((self.x, self.y))

        tail_length = int(self.distance_to_parent * SCALE)

        if len(self.orbit) > tail_length:
            self.orbit = self.orbit[-tail_length:]


class SolarSystem:

    def __init__(self, name, star, planets):
        self.name = name
        self.star = star
        self.planets = planets

    def update_positions(self):
        self.star.update_position(self.planets)

        bodies = [self.star] + self.planets
        for planet in self.planets:
            planet.update_position(bodies)

    def draw(self, window, font):
        self.star.draw(window, font)
        for planet in self.planets:
            planet.draw(window, font)


def draw_line(window, start_planet, end_planet, color):
    start = (start_planet.x * SCALE + WIDTH / 2,
             start_planet.y * SCALE + HEIGHT / 2)
    end = (end_planet.x * SCALE + WIDTH / 2,
           end_planet.y * SCALE + HEIGHT / 2)
    pygame.draw.line(window, color, start, end)


def mostest_closest_neighbour(planet, other_planets):
    closest_neighbour = None
    closest_distance = math.inf

    for other_planet in other_planets:
        if other_planet == planet:
            continue

        distance = math.dist(planet.get_position(), other_planet.get_position())
        if distance < closest_distance:
            closest_distance = distance
            closest_neighbour = other_planet

    return closest_neighbour


def run_simulation(window, clock, font):
    sun = CelestialObject("Sun", 16, Color.YELLOW, 1.98892 * 10 ** 30)
    sun.set_position(0, 0)

    mercury = Planet("Mercury", sun, 4, Color.GRAY, 3.30 * 10 ** 23)
    mercury.set_position(0.387 * AU, 0)
    mercury.set_velocity(0, 47400)

    venus = Planet("Venus", sun, 5, Color.ORANGE, 4.8685 * 10 ** 24)
    venus.set_position(-0.723 * AU, 0)
    venus.set_velocity(0, -35020)

    earth = Planet("Earth", sun, 5, Color.BLUE, 5.9742 * 10 ** 24)
    earth.set_position(1 * AU, 0)
    earth.set_velocity(0, 29783)

    mars = Planet("Mars", sun, 4, Color.RED, 6.39 * 10 ** 23)
    mars.set_position(-1.524 * AU, 0)
    mars.set_velocity(0, -24077)

    planets = [mercury, venus, earth, mars]

    solar_system = SolarSystem("The Solar System", sun, planets)

    count = 0
    closest_count = {planet: 0 for planet in planets if planet != earth}

    def format_percentage(planet):
        txt_planet_name = planet.name.ljust(10)
        percentage = closest_count[planet] / count * 100
        txt_percentage = f"{str(round(percentage)).rjust(3)}%"
        return f"{txt_planet_name}{txt_percentage}"

    run = True
    while run:
        clock.tick(FPS)
        window.fill(Color.BLACK.value)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        solar_system.update_positions()

        count += 1
        closest_planet = mostest_closest_neighbour(earth, planets)
        closest_count[closest_planet] += 1

        txt_mercury = font.render(format_percentage(mercury), True, Color.WHITE.value)
        window.blit(txt_mercury, (5, 5))
        txt_venus = font.render(format_percentage(venus), True, Color.WHITE.value)
        window.blit(txt_venus, (5, 20))
        txt_mars = font.render(format_percentage(mars), True, Color.WHITE.value)
        window.blit(txt_mars, (5, 35))

        draw_line(window, earth, closest_planet, Color.WHITE.value)

        solar_system.draw(window, font)

        pygame.display.update()

    pygame.quit()


def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('monospace', 16)
    pygame.display.set_caption("Mostest Closest Neighbour")
    run_simulation(win, clock, font)


if __name__ == '__main__':
    main()
