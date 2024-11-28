import pygame
import sys
import math
from pygame import Color
from typing import Tuple, List
import random
import time

# Initialize Pygame and its font system
pygame.init()
pygame.font.init()

# Constants
WINDOW_SIZE = (360, 640)  # Half the size of the previous portrait dimensions
FPS = 60
PADDLE_LENGTH = WINDOW_SIZE[0] // 4  # Each snake is 1/4 of border length
PADDLE_THICKNESS = 15
BALL_RADIUS = 15
CENTRAL_ORB_RADIUS = 50
INITIAL_BALL_SPEED = 5  # Starting slower
PADDLE_SPEED = 5
INITIAL_LIVES = 3
INITIAL_REPEL_SPEED = 8  # Starting slower
NUM_STARS = 200
STAR_SPEED = 2
CENTRAL_ORB_COLOR = (100, 100, 255)  # Blue-ish central orb

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BRIGHT_GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
DARK_RED = (139, 0, 0)

class Ball:
    def __init__(self):
        self.center_pos = [WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2]
        self.speed = INITIAL_BALL_SPEED
        self.repel_speed = INITIAL_REPEL_SPEED
        self.reset()
        self.color = WHITE
        self.artifacts = []
        
    def reset(self):
        # Start from a random position on the border
        side = random.randint(0, 3)
        if side == 0:  # Bottom
            self.pos = [random.randint(0, WINDOW_SIZE[0]), WINDOW_SIZE[1]]
        elif side == 1:  # Right
            self.pos = [WINDOW_SIZE[0], random.randint(0, WINDOW_SIZE[1])]
        elif side == 2:  # Top
            self.pos = [random.randint(0, WINDOW_SIZE[0]), 0]
        else:  # Left
            self.pos = [0, random.randint(0, WINDOW_SIZE[1])]
            
        # Always aim towards the center initially
        dx = self.center_pos[0] - self.pos[0]
        dy = self.center_pos[1] - self.pos[1]
        dist = math.sqrt(dx*dx + dy*dy)
        
        self.vel = [
            self.speed * (dx/dist),
            self.speed * (dy/dist)
        ]
        self.moving_inward = True  # Track if ball is moving toward center
        
    def increase_speed(self):
        self.speed = min(self.speed * 1.1, 12)  # Cap at 12
        self.repel_speed = min(self.repel_speed * 1.1, 15)  # Cap at 15

    def move(self) -> bool:
        # Check for collision with central orb
        dx = self.pos[0] - self.center_pos[0]
        dy = self.pos[1] - self.center_pos[1]
        dist = math.sqrt(dx*dx + dy*dy)
        
        if self.moving_inward and dist <= BALL_RADIUS:  # Ball reaches center of orb
            # Random new direction away from center
            angle = random.uniform(0, 2 * math.pi)
            self.vel[0] = self.repel_speed * math.cos(angle)
            self.vel[1] = self.repel_speed * math.sin(angle)
            self.moving_inward = False  # Ball is now moving outward
            return True
            
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        return False
        
    def hit_snake(self, segments):
        """Check for collision with snake segments and handle bounce"""
        if len(segments) < 2:
            return False
            
        for i in range(len(segments) - 1):
            x1, y1 = segments[i]
            x2, y2 = segments[i + 1]
            
            # Calculate closest point on line segment to ball center
            line_vec = (x2 - x1, y2 - y1)
            line_len = math.sqrt(line_vec[0]**2 + line_vec[1]**2)
            line_unit = (line_vec[0]/line_len, line_vec[1]/line_len)
            
            ball_to_start = (self.pos[0] - x1, self.pos[1] - y1)
            proj_len = max(0, min(line_len, 
                                ball_to_start[0]*line_unit[0] + 
                                ball_to_start[1]*line_unit[1]))
            
            closest_point = (x1 + line_unit[0]*proj_len,
                           y1 + line_unit[1]*proj_len)
            
            # Check distance to closest point
            dx = self.pos[0] - closest_point[0]
            dy = self.pos[1] - closest_point[1]
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist <= BALL_RADIUS + PADDLE_THICKNESS/2:
                # Calculate bounce direction
                dx = self.center_pos[0] - self.pos[0]
                dy = self.center_pos[1] - self.pos[1]
                dist = math.sqrt(dx*dx + dy*dy)
                
                self.vel = [
                    self.speed * (dx/dist),
                    self.speed * (dy/dist)
                ]
                self.moving_inward = True  # Ball is now moving inward
                
                # Add impact effect at collision point
                for snake in game.snakes:  # Access game instance
                    if segments is snake.segments:
                        snake.add_impact_effect(closest_point)
                        break
                        
                return True
        return False

    def add_artifacts(self, color):
        """Add red artifacts when life is lost"""
        for _ in range(10):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 5)
            velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            self.artifacts.append([list(self.pos), velocity, 30, color])  # position, velocity, lifetime, color

    def draw(self, screen):
        # Draw the main ball with a subtle glow
        glow_surf = pygame.Surface((BALL_RADIUS*3, BALL_RADIUS*3), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 255, 255, 20), 
                         (BALL_RADIUS*1.5, BALL_RADIUS*1.5), BALL_RADIUS*1.2)
        screen.blit(glow_surf, 
                   (self.pos[0]-BALL_RADIUS*1.5, self.pos[1]-BALL_RADIUS*1.5))
        
        # Draw the main ball
        pygame.draw.circle(screen, self.color, 
                         (int(self.pos[0]), int(self.pos[1])), BALL_RADIUS)

        # Draw artifacts
        for artifact in self.artifacts[:]:
            pos, vel, lifetime, color = artifact
            pos[0] += vel[0]
            pos[1] += vel[1]
            lifetime -= 1
            if lifetime <= 0:
                self.artifacts.remove(artifact)
            alpha = int(255 * (lifetime / 30))
            pygame.draw.circle(screen, (*color, alpha), (int(pos[0]), int(pos[1])), 2)

class Snake:
    def __init__(self, start_side: int):
        """
        start_side: 0=bottom, 1=right, 2=top, 3=left
        """
        self.side = start_side
        self.progress = 0.25  # Start at 1/4 to center the snake
        self.segments = []  # List of points defining the snake
        self.is_vertical = (start_side % 2 == 1)  # right/left are odd numbers
        self.snake_length = 0.5  # 50% of border length for portrait mode
        self.impact_particles = []  # [(pos, vel, lifetime, color), ...]
        self.impact_glow = 0  # Glow intensity from impact
        self.generate_segments()
        
    def add_impact_effect(self, pos):
        """Add impact particles and glow when ball hits"""
        self.impact_glow = 1.0  # Full glow
        
        # Add spark particles
        num_particles = 15
        for _ in range(num_particles):
            angle = random.uniform(0, math.pi)  # Semicircle away from paddle
            if self.side in [0, 2]:  # Top/bottom
                if self.side == 0:  # Bottom
                    angle += math.pi  # Point upward
                speed = random.uniform(3, 8)
                vel = [math.cos(angle) * speed, math.sin(angle) * speed]
            else:  # Left/right
                if self.side == 1:  # Right
                    angle += math.pi  # Point leftward
                speed = random.uniform(3, 8)
                vel = [math.sin(angle) * speed, math.cos(angle) * speed]
            
            # Random bright color for sparks
            color = random.choice([
                (255, 255, 200),  # Bright yellow
                (255, 200, 150),  # Orange
                (200, 255, 255),  # Cyan
                (255, 255, 255)   # White
            ])
            
            self.impact_particles.append([
                list(pos),  # Position
                vel,       # Velocity
                30,       # Lifetime
                color     # Particle color
            ])
            
    def update_effects(self):
        """Update impact particles and glow"""
        # Update particles
        for particle in self.impact_particles[:]:
            particle[0][0] += particle[1][0]  # Update x position
            particle[0][1] += particle[1][1]  # Update y position
            particle[2] -= 1  # Decrease lifetime
            
            # Add gravity to vertical velocity
            particle[1][1] += 0.2
            
            if particle[2] <= 0:
                self.impact_particles.remove(particle)
                
        # Fade glow
        if self.impact_glow > 0:
            self.impact_glow *= 0.9
        
    def generate_segments(self):
        self.segments = []
        num_points = 20  # Number of points per segment for smooth appearance
        
        # Calculate the snake's body based on current position
        side = self.side
        progress = self.progress
        
        for i in range(num_points):
            p = progress + (i / (num_points - 1)) * self.snake_length
            if p >= 1:  # Wrap to next side
                p = p - 1
                side = (self.side + 1) % 4
            self.segments.append(self.get_point(side, p))
    
    def get_point(self, side: int, progress: float) -> Tuple[float, float]:
        """Get x,y coordinates for a point on a given side with given progress"""
        if side == 0:  # Bottom
            return (WINDOW_SIZE[0] * progress, WINDOW_SIZE[1])
        elif side == 1:  # Right
            return (WINDOW_SIZE[0], WINDOW_SIZE[1] * (1 - progress))
        elif side == 2:  # Top
            return (WINDOW_SIZE[0] * (1 - progress), 0)
        else:  # Left
            return (0, WINDOW_SIZE[1] * progress)
    
    def move(self, amount: float):
        self.progress += amount / 100.0  # Adjust speed
        if self.progress >= 1:
            self.progress = 0
            self.side = (self.side + 1) % 4
        elif self.progress < 0:
            self.progress = 1
            self.side = (self.side - 1) % 4
        self.generate_segments()
    
    def draw(self, screen, color):
        if len(self.segments) < 2:
            return
            
        # Draw shadow on central orb
        self.draw_shadow(screen)
            
        # Update particle effects
        self.update_effects()
        
        # Draw impact glow if active
        if self.impact_glow > 0.05:
            points = []
            for x, y in self.segments:
                points.append((int(x), int(y)))
            
            # Create glow surface
            glow_surf = pygame.Surface((WINDOW_SIZE[0], WINDOW_SIZE[1]), pygame.SRCALPHA)
            
            # Draw multiple layers of glow
            for i in range(3):
                glow_thickness = PADDLE_THICKNESS + i * 4
                glow_alpha = int(100 * self.impact_glow / (i + 1))
                if len(points) >= 2:
                    pygame.draw.lines(glow_surf, (*color, glow_alpha), 
                                   False, points, glow_thickness)
                    # Draw rounded ends with glow
                    pygame.draw.circle(glow_surf, (*color, glow_alpha), 
                                    points[0], glow_thickness // 2)
                    pygame.draw.circle(glow_surf, (*color, glow_alpha), 
                                    points[-1], glow_thickness // 2)
            
            screen.blit(glow_surf, (0, 0))
            
        # Draw the snake body
        points = []
        for x, y in self.segments:
            points.append((int(x), int(y)))
        
        # Draw thick line for the snake
        if len(points) >= 2:
            pygame.draw.lines(screen, color, False, points, PADDLE_THICKNESS)
            
        # Draw rounded ends
        pygame.draw.circle(screen, color, points[0], PADDLE_THICKNESS // 2)
        pygame.draw.circle(screen, color, points[-1], PADDLE_THICKNESS // 2)
        
        # Draw impact particles
        for particle in self.impact_particles:
            pos, _, lifetime, particle_color = particle
            alpha = int(255 * (lifetime / 30))
            pygame.draw.circle(screen, (*particle_color, alpha), (int(pos[0]), int(pos[1])), 2)

    def draw_shadow(self, screen):
        # Get orb center and radius
        orb_center = [WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2]
        orb_radius = CENTRAL_ORB_RADIUS
        light_offset = [-orb_radius*1.5, -orb_radius*1.5]  # Match CentralOrb light position
        light_pos = [orb_center[0] + light_offset[0], orb_center[1] + light_offset[1]]
        
        # Create shadow surface
        shadow_surf = pygame.Surface((WINDOW_SIZE[0], WINDOW_SIZE[1]), pygame.SRCALPHA)
        
        # Draw shadow for each segment
        for i in range(len(self.segments) - 1):
            x1, y1 = self.segments[i]
            x2, y2 = self.segments[i + 1]
            
            # Calculate shadow direction for each point
            for t in range(0, 100, 5):  # Interpolate between segments
                # Get point on snake
                x = x1 + (x2 - x1) * t / 100
                y = y1 + (y2 - y1) * t / 100
                
                # Calculate distance to orb center
                dx = x - orb_center[0]
                dy = y - orb_center[1]
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist < orb_radius + PADDLE_THICKNESS:
                    # Calculate shadow direction
                    shadow_dx = x - light_pos[0]
                    shadow_dy = y - light_pos[1]
                    shadow_len = 20  # Length of shadow
                    
                    # Draw shadow segment
                    shadow_x = x + shadow_dx * shadow_len / dist
                    shadow_y = y + shadow_dy * shadow_len / dist
                    
                    # Draw shadow with fade
                    shadow_alpha = int(80 * (1 - (dist - orb_radius) / PADDLE_THICKNESS))
                    if shadow_alpha > 0:
                        pygame.draw.circle(shadow_surf, (0, 0, 0, shadow_alpha), 
                                        (int(shadow_x), int(shadow_y)), 
                                        PADDLE_THICKNESS // 2)
        
        # Blend shadow onto screen
        screen.blit(shadow_surf, (0, 0))

class Star:
    def __init__(self):
        self.reset()
        
    def reset(self):
        # Start at random position
        self.x = random.randint(0, WINDOW_SIZE[0])
        self.y = random.randint(0, WINDOW_SIZE[1])
        self.z = random.randint(1, 10)  # Depth for parallax effect
        self.size = random.randint(1, 3)
        self.speed = STAR_SPEED * (11 - self.z) / 2  # Farther stars move slower
        
    def move(self):
        # Move star outward from center
        center_x = WINDOW_SIZE[0] // 2
        center_y = WINDOW_SIZE[1] // 2
        dx = self.x - center_x
        dy = self.y - center_y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist == 0:
            self.reset()
            return
            
        # Move star outward
        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed
        
        # Reset if off screen
        if (self.x < 0 or self.x > WINDOW_SIZE[0] or 
            self.y < 0 or self.y > WINDOW_SIZE[1]):
            self.reset()

class CentralOrb:
    def __init__(self):
        self.pos = [WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2]
        self.radius = CENTRAL_ORB_RADIUS
        self.shake_amount = 0
        self.particles = []
        self.glow_radius = self.radius
        self.exploding = False
        self.explosion_progress = 0
        self.imploding = False
        self.implosion_progress = 0
        self.background_color = (0, 0, 20)  # Dark blue start
        self.next_background = None
        self.light_offset = [-self.radius*1.5, -self.radius*1.5]
        self.light_occlusion = {}
        self.trapped_ball = None
        self.shake_phase = 0
        
    def trap_ball(self, ball):
        self.trapped_ball = ball
        self.shake_amount = 15  # Start with strong shake
        self.shake_phase = 0
        
    def update(self):
        if self.trapped_ball:
            # Orbit the ball around the center while shaking
            self.shake_phase += 0.2
            orbit_radius = CENTRAL_ORB_RADIUS * 0.8
            self.trapped_ball.pos[0] = self.pos[0] + math.cos(self.shake_phase) * orbit_radius
            self.trapped_ball.pos[1] = self.pos[1] + math.sin(self.shake_phase) * orbit_radius
            
            # Increase shake and eventually explode
            self.shake_amount = 15 * (1 + math.sin(self.shake_phase))
            if self.shake_phase >= math.pi * 4:  # After 2 full rotations
                self.start_explosion()
                self.trapped_ball = None
        else:
            # Update shake effect
            if self.shake_amount > 0:
                self.shake_amount *= 0.9
                
            # Update glow
            self.glow_radius = self.radius + 5 * math.sin(time.time() * 4)
            
            # Update particles
            for particle in self.particles[:]:
                particle[0][0] += particle[1][0]  # x position
                particle[0][1] += particle[1][1]  # y position
                particle[2] -= 1  # lifetime
                if particle[2] <= 0:
                    self.particles.remove(particle)
                    
            # Handle explosion animation
            if self.exploding:
                self.explosion_progress += 0.02
                if self.explosion_progress >= 1:
                    self.exploding = False
                    self.explosion_progress = 0
                    self.background_color = self.next_background
                    
            # Handle implosion animation
            if self.imploding:
                self.implosion_progress += 0.04
                if self.implosion_progress >= 1:
                    self.imploding = False
                    self.implosion_progress = 0
                    self.start_explosion()
                    
    def start_explosion(self):
        self.exploding = True
        self.explosion_progress = 0
        # Generate a new dark background color for next level
        self.next_background = (
            random.randint(0, 20),  # Dark red
            random.randint(0, 20),  # Dark green
            random.randint(20, 40)  # Slightly more blue for space feel
        )
        
    def start_implosion(self):
        self.imploding = True
        self.implosion_progress = 0
        
    def hit(self):
        self.shake_amount = 10
        # Add particles
        for _ in range(10):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 5)
            velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            self.particles.append([list(self.pos), velocity, 30])  # position, velocity, lifetime

    def calculate_light_occlusion(self, snakes):
        """Calculate how much light is blocked by each paddle"""
        self.light_occlusion.clear()
        light_pos = [self.pos[0] + self.light_offset[0], 
                    self.pos[1] + self.light_offset[1]]
        
        # For each point on the orb surface
        for angle in range(360):
            rad = math.radians(angle)
            # Point on orb surface
            px = self.pos[0] + math.cos(rad) * self.radius
            py = self.pos[1] + math.sin(rad) * self.radius
            
            # Calculate light ray to this point
            dx = px - light_pos[0]
            dy = py - light_pos[1]
            ray_length = math.sqrt(dx*dx + dy*dy)
            dx, dy = dx/ray_length, dy/ray_length
            
            # Check for intersections with paddles
            occlusion = 0
            for snake in snakes:
                for i in range(len(snake.segments) - 1):
                    x1, y1 = snake.segments[i]
                    x2, y2 = snake.segments[i + 1]
                    
                    # Check if ray intersects paddle segment
                    paddle_dx = x2 - x1
                    paddle_dy = y2 - y1
                    
                    # Ray-line intersection calculation
                    denom = dx * paddle_dy - dy * paddle_dx
                    if abs(denom) > 0.0001:
                        t1 = ((x1 - light_pos[0]) * paddle_dy - (y1 - light_pos[1]) * paddle_dx) / denom
                        t2 = ((x1 - light_pos[0]) * dy - (y1 - light_pos[1]) * dx) / denom
                        
                        if 0 <= t2 <= 1 and t1 > 0:  # Check if intersection is within segment
                            # Calculate distance-based occlusion
                            ix = light_pos[0] + dx * t1
                            iy = light_pos[1] + dy * t1
                            dist_to_intersection = math.sqrt((ix-light_pos[0])**2 + (iy-light_pos[1])**2)
                            dist_to_point = math.sqrt((px-light_pos[0])**2 + (py-light_pos[1])**2)
                            
                            if dist_to_intersection < dist_to_point:
                                # Add shadow based on distance from paddle
                                shadow_strength = 1.0 - min(1.0, abs(t2 - 0.5) * 2)
                                occlusion = max(occlusion, shadow_strength * 0.7)  # Max 70% darkness
            
            self.light_occlusion[angle] = 1.0 - occlusion
    
    def draw_lit_sphere(self, surface, base_color, center, radius, light_pos, alpha=255):
        """Draw a sphere with 3D lighting effect and paddle shadows"""
        for y in range(int(center[1] - radius), int(center[1] + radius)):
            for x in range(int(center[0] - radius), int(center[0] + radius)):
                # Check if point is within sphere
                dx = x - center[0]
                dy = y - center[1]
                dist_sq = dx*dx + dy*dy
                if dist_sq > radius*radius:
                    continue
                
                # Calculate angle for this point
                angle = int(math.degrees(math.atan2(dy, dx)) % 360)
                
                # Get light occlusion for this angle
                occlusion = self.light_occlusion.get(angle, 1.0)
                
                # Calculate normal vector at this point
                nx = dx / radius
                ny = dy / radius
                nz_sq = 1 - nx*nx - ny*ny
                if nz_sq < 0:
                    nz = 0
                else:
                    nz = math.sqrt(nz_sq)
                
                # Calculate light direction
                lx = light_pos[0] - x
                ly = light_pos[1] - y
                lz = radius * 2
                light_dist = math.sqrt(lx*lx + ly*ly + lz*lz)
                lx, ly, lz = lx/light_dist, ly/light_dist, lz/light_dist
                
                # Calculate diffuse lighting with occlusion
                diffuse = (nx*lx + ny*ly + nz*lz) * occlusion
                diffuse = max(0.2, min(1.0, diffuse))
                
                # Calculate specular highlight
                rx = 2 * diffuse * nx - lx
                ry = 2 * diffuse * ny - ly
                rz = 2 * diffuse * nz - lz
                specular = max(0, rz) * occlusion
                specular = specular ** 8
                
                # Combine lighting effects
                r = min(255, int(base_color[0] * diffuse + 255 * specular))
                g = min(255, int(base_color[1] * diffuse + 255 * specular))
                b = min(255, int(base_color[2] * diffuse + 255 * specular))
                
                surface.set_at((x, y), (r, g, b, alpha))

    def draw(self, screen, color, snakes):
        # Update light occlusion based on paddle positions
        self.calculate_light_occlusion(snakes)
        
        # Calculate shake offset
        shake_x = random.uniform(-self.shake_amount, self.shake_amount)
        shake_y = random.uniform(-self.shake_amount, self.shake_amount)
        
        # Draw glow first
        glow_surf = pygame.Surface((self.glow_radius * 4, self.glow_radius * 4), pygame.SRCALPHA)
        for i in range(3):
            glow_radius = self.glow_radius * (3 - i) / 3
            alpha = 60 - i * 20  # Reduced glow intensity
            pygame.draw.circle(glow_surf, (*color, alpha), 
                             (self.glow_radius * 2, self.glow_radius * 2), 
                             glow_radius)
        screen.blit(glow_surf, 
                   (self.pos[0] - self.glow_radius * 2 + shake_x,
                    self.pos[1] - self.glow_radius * 2 + shake_y))
        
        # Create surface for orb
        orb_surface = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        
        # Light position in orb surface coordinates
        light_pos = [self.radius * 2 + self.light_offset[0], 
                    self.radius * 2 + self.light_offset[1]]
        
        if self.exploding:
            # Explosion effect with lighting
            explosion_radius = self.radius * (1 + self.explosion_progress * 2)
            alpha = int(255 * (1 - self.explosion_progress))
            self.draw_lit_sphere(orb_surface, color, (self.radius * 2, self.radius * 2), 
                               explosion_radius, light_pos, alpha)
        elif self.imploding:
            # Implosion effect with lighting
            current_radius = self.radius * (1 - self.implosion_progress * 0.5)
            self.draw_lit_sphere(orb_surface, color, (self.radius * 2, self.radius * 2), 
                               current_radius, light_pos)
        else:
            # Normal orb with lighting
            self.draw_lit_sphere(orb_surface, color, (self.radius * 2, self.radius * 2), 
                               self.radius, light_pos)
        
        # Draw the lit orb
        screen.blit(orb_surface, (self.pos[0] - self.radius * 2 + shake_x,
                                 self.pos[1] - self.radius * 2 + shake_y))
        
        # Draw particles with lighting
        for particle in self.particles:
            pos, _, lifetime = particle
            alpha = int(255 * (lifetime / 30))
            particle_color = (*color, alpha)
            pygame.draw.circle(screen, particle_color, (int(pos[0]), int(pos[1])), 2)

class Game:
    def __init__(self):
        # Set up display to handle different screen sizes
        display_info = pygame.display.Info()
        self.screen_width = display_info.current_w
        self.screen_height = display_info.current_h
        
        target_ratio = WINDOW_SIZE[0] / WINDOW_SIZE[1]
        screen_ratio = self.screen_width / self.screen_height
        
        # Swap width and height for portrait mode
        if screen_ratio > target_ratio:
            self.screen_width = min(self.screen_width, 640)  # iPhone-like width
            self.screen_height = int(self.screen_width * (WINDOW_SIZE[1] / WINDOW_SIZE[0]))
        else:
            self.screen_height = min(self.screen_height, 1280)
            self.screen_width = int(self.screen_height * target_ratio)

        # Explicitly set the screen dimensions for portrait mode
        self.screen = pygame.display.set_mode((WINDOW_SIZE[0], WINDOW_SIZE[1]))
        pygame.display.set_caption("Orbital Pong")
        self.clock = pygame.time.Clock()
        
        # Initialize game state
        self.ball = Ball()
        self.lives = INITIAL_LIVES
        self.level = 1
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.hits = 0
        self.hits_for_next_level = 10
        self.orb_color = BRIGHT_GREEN
        self.countdown_active = False
        self.countdown_time = 0
        self.level_transition = False
        self.show_life_added = False
        self.life_added_time = 0
        
        # Initialize fonts with Press Start 2P
        try:
            self.font = pygame.font.Font("PressStart2P.ttf", 16)  # Smaller size for HUD as this font runs large
            self.big_font = pygame.font.Font("PressStart2P.ttf", 32)  # Larger for countdown/game over
        except:
            print("Could not load Press Start 2P font, falling back to system font")
            self.font = pygame.font.SysFont("Courier New", 28, bold=True)
            self.big_font = pygame.font.SysFont("Courier New", 56, bold=True)
        
        # Create exactly 4 snakes, one per border
        self.snakes = []
        # Create one snake for each border, positioned to take up middle 50%
        for i in range(4):
            snake = Snake(i)  # 0=bottom, 1=right, 2=top, 3=left
            self.snakes.append(snake)
            
        self.stars = [Star() for _ in range(NUM_STARS)]
        self.central_orb = CentralOrb()
        
    def draw_heart(self, screen, x, y, size=20, color=(255, 0, 0)):
        """
        Draw a filled heart using two circles and a rotated square
        :param screen: Pygame surface to draw on
        :param x: x-coordinate of heart center
        :param y: y-coordinate of heart center
        :param size: size of the heart
        :param color: color of the heart
        """
        # Adjust size and positioning
        radius = size // 2
        
        # Draw two filled circles for the top of the heart
        pygame.draw.circle(screen, color, 
                           (int(x - radius//2), int(y)), 
                           radius//2)
        pygame.draw.circle(screen, color, 
                           (int(x + radius//2), int(y)), 
                           radius//2)
        
        # Draw filled triangle for bottom of heart
        points = [
            (x, y + radius),  # bottom point
            (x - radius, y),  # left point
            (x + radius, y)   # right point
        ]
        pygame.draw.polygon(screen, color, points)

    def update_orb_color(self):
        progress = self.hits / self.hits_for_next_level
        if progress < 0.5:
            # Transition from green to yellow
            ratio = progress * 2
            r = int(255 * ratio)
            g = 255
            b = 0
        else:
            # Transition from yellow to dark red
            ratio = (progress - 0.5) * 2
            r = int(139 + (255 - 139) * (1 - ratio))
            g = int(255 * (1 - ratio))
            b = 0
        self.orb_color = (r, g, b)

    def update_score(self, points):
        self.score += points
        if self.score > self.high_score:
            self.high_score = self.score
            
    def move_paddles(self, amount):
        if amount == 0:
            return

        # Move each snake along the border path
        for snake in self.snakes:
            snake.move(amount)

    def check_ball_out(self):
        # Check if ball is out of bounds
        if (self.ball.pos[0] < -BALL_RADIUS or 
            self.ball.pos[0] > WINDOW_SIZE[0] + BALL_RADIUS or
            self.ball.pos[1] < -BALL_RADIUS or 
            self.ball.pos[1] > WINDOW_SIZE[1] + BALL_RADIUS):
            
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                # Change ball color to red and add red artifacts
                self.ball.color = DARK_RED
                self.ball.add_artifacts(DARK_RED)
                
                # Activate countdown and reset ball
                self.ball.reset()
                self.countdown_active = True
                self.countdown_time = time.time()

    def start_level_transition(self):
        self.level_transition = True
        self.central_orb.trap_ball(self.ball)
        
        # Add a life when a level is completed
        self.lives += 1
        self.show_life_added = True
        self.life_added_time = time.time()

    def draw_hud(self):
        # Create compact HUD elements
        margin = 10
        spacing = 15  # Reduced spacing between HUD elements
        
        # Prepare HUD text elements
        level_text = f"LVL {self.level}"
        score_text = f"{self.score:05d}"
        
        # Render text surfaces
        level_surf = self.font.render(level_text, True, WHITE)
        score_surf = self.font.render(score_text, True, (0, 150, 255))  # Blue color
        
        # Calculate total width of HUD elements
        total_width = (self.lives * 25)  # Space for hearts 
        
        # Draw level at the left
        self.screen.blit(level_surf, (margin, margin))
        
        # Draw score in blue, centered
        score_x = (WINDOW_SIZE[0] - score_surf.get_width()) // 2
        self.screen.blit(score_surf, (score_x, margin))
        
        # Draw hearts for lives aligned to the right
        heart_size = 15
        heart_spacing = 25
        total_hearts_width = self.lives * heart_spacing
        heart_x = WINDOW_SIZE[0] - total_hearts_width - margin
        for i in range(self.lives):
            self.draw_heart(self.screen, 
                            heart_x + i * heart_spacing, 
                            margin + level_surf.get_height() // 2, 
                            size=heart_size)
            
        # Show +1 life indicator
        if self.show_life_added and time.time() - self.life_added_time < 2:
            life_added_text = "+1 LIFE"
            life_added_surf = self.font.render(life_added_text, True, BRIGHT_GREEN)
            life_added_x = (WINDOW_SIZE[0] - life_added_surf.get_width()) // 2
            life_added_y = margin + level_surf.get_height() + 10
            self.screen.blit(life_added_surf, (life_added_x, life_added_y))
            
            # Reset flag after displaying
            if time.time() - self.life_added_time >= 2:
                self.show_life_added = False
                
    def draw_glitch_overlay(self):
        # Draw a glitchy overlay effect
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(50)  # Semi-transparent
        overlay.fill(DARK_RED)  # Red tint
        self.screen.blit(overlay, (0, 0))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.__init__()

            if not self.game_over:
                # Update stars
                for star in self.stars:
                    star.move()
                    
                # Update central orb
                self.central_orb.update()
                
                # Handle input
                keys = pygame.key.get_pressed()
                move = 0
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    move = -PADDLE_SPEED
                elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    move = PADDLE_SPEED

                # Move snakes
                for snake in self.snakes:
                    snake.move(move)

                # Handle countdown after life loss
                if self.countdown_active:
                    elapsed = time.time() - self.countdown_time
                    if elapsed >= 3:  # 3 second countdown
                        self.countdown_active = False
                        self.ball.color = WHITE
                else:
                    # Update ball
                    if not self.level_transition:
                        orb_hit = self.ball.move()
                        if orb_hit:
                            self.central_orb.hit()
                            self.hits += 1
                            self.update_orb_color()
                            # Add score for hitting the orb
                            self.update_score(100 * self.level)  # More points in higher levels
                            if self.hits >= self.hits_for_next_level:
                                self.start_level_transition()
                
                # Handle level transition
                if self.level_transition and not self.central_orb.trapped_ball:
                    self.level += 1
                    self.hits = 0
                    self.orb_color = BRIGHT_GREEN
                    self.ball.reset()
                    self.countdown_active = True
                    self.countdown_time = time.time()
                    self.level_transition = False
                else:
                    # Check for snake collisions
                    for snake in self.snakes:
                        if self.ball.hit_snake(snake.segments):
                            # Add score for paddle hits
                            self.update_score(10 * self.level)  # Small bonus for paddle hits
                            break

                    self.check_ball_out()

            # Draw
            if self.central_orb.next_background and self.central_orb.exploding:
                # Transition background during explosion
                progress = self.central_orb.explosion_progress
                current_color = [
                    int(self.central_orb.background_color[i] * (1 - progress) + 
                        self.central_orb.next_background[i] * progress)
                    for i in range(3)
                ]
                self.screen.fill(current_color)
            else:
                self.screen.fill(self.central_orb.background_color)
            
            # Draw stars
            for star in self.stars:
                pygame.draw.circle(self.screen, WHITE,
                                 (int(star.x), int(star.y)),
                                 star.size)
            
            # Draw central orb with effects and snake shadows
            self.central_orb.draw(self.screen, self.orb_color, self.snakes)

            # Draw snakes
            for snake in self.snakes:
                snake.draw(self.screen, WHITE)

            # Draw ball with trail
            self.ball.draw(self.screen)
            
            # Draw HUD
            self.draw_hud()
            
            # Draw countdown or game over
            if self.countdown_active:
                self.draw_glitch_overlay()
                countdown = 3 - int(time.time() - self.countdown_time)
                if countdown > 0:
                    countdown_text = self.big_font.render(str(countdown), True, WHITE)
                    text_rect = countdown_text.get_rect(center=(WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2))
                    self.screen.blit(countdown_text, text_rect)
                    ready_text = self.font.render("GET READY!", True, WHITE)
                    ready_rect = ready_text.get_rect(center=(WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2 + 50))
                    self.screen.blit(ready_text, ready_rect)

            if self.game_over:
                game_over_text = self.big_font.render('GAME OVER', True, WHITE)
                text_rect = game_over_text.get_rect(center=(WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2))
                self.screen.blit(game_over_text, text_rect)
                
                restart_text = self.font.render('PRESS SPACE TO RESTART', True, WHITE)
                restart_rect = restart_text.get_rect(center=(WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2 + 50))
                self.screen.blit(restart_text, restart_text)
                
            pygame.display.flip()
            self.clock.tick(FPS)

# Create global game instance
game = None

if __name__ == '__main__':
    game = Game()
    game.run()
