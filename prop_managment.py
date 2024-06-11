import math


class Position:
    def __init__(self, start_x, start_y, velocity_x, velocity_y, prop, r):
        self.start_x = start_x
        self.start_y = start_y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.pos_y = start_y
        self.pos_x = start_x
        self.prop = prop
        self.r = r
        self.rx = self.pos_x + r
        self.ry = self.pos_y + r
        self.amplitude = 120
        self.frequency = 0.1
        self.time = 0
        self.shoot_cooldown = 0
        self.shoot_frequency = 80
        self.is_ctf = False

    def is_outside(self):
        if self.pos_x >= 850 or self.pos_x <= -200:
            self.velocity_x = -self.velocity_x
        if self.pos_y >= 850 or self.pos_y <= -200:
            self.velocity_y = -self.velocity_y

    def set_pos_x(self, pos_x):
        self.pos_x = pos_x

    def get_pos_x(self):
        return self.pos_x

    def set_pos_y(self, pos_y):
        self.pos_y = pos_y

    def alien_move_on(self):
        self.time += 1
        new_x = self.start_x - self.velocity_x * self.time
        y = self.amplitude * math.sin(self.frequency * self.time)
        new_y = self.start_y + y
        if new_x < -500:
            self.set_pos_x(self.start_x)
            self.time = 0
            self.is_ctf = True
        self.set_pos_x(int(new_x))
        self.set_pos_y(int(new_y))
        self.shoot_cooldown -= 1
        if self.shoot_cooldown <= 0:
            self.shoot()
            self.shoot_cooldown = self.shoot_frequency

    def move_on(self):
        self.set_pos_y(pos_y=self.pos_y + self.velocity_y)
        self.set_pos_x(pos_x=self.pos_x + self.velocity_x)
        self.ry = self.pos_y + self.r
        self.rx = self.pos_x + self.r

    def get_pos_y(self):
        return self.pos_y

    def is_colision_with_meteor(self, player_x, player_y, prop_width, prop_height):
        distance_x_0 = player_x - self.rx
        distance_y_0 = player_y - self.ry
        distance_x_m = (player_x + prop_width) - self.rx
        distance_y_m = (player_y + prop_height) - self.ry
        distance_0_0 = (distance_x_0 ** 2 + distance_y_0 ** 2) ** 0.5
        distance_x_y = (distance_x_m ** 2 + distance_y_m ** 2) ** 0.5
        distance_0_y = (distance_x_0 ** 2 + distance_y_m ** 2) ** 0.5
        distance_x_0 = (distance_x_m ** 2 + distance_y_0 ** 2) ** 0.5
        return distance_0_0 <= self.r or distance_x_y <= self.r or distance_x_0 <= self.r or distance_0_y <= self.r

    def change_direction_and_speed(self, vx, vy, x, y, m_statku):
        max_v=10
        m_asteroidy = 0.5
        r = [x - self.get_pos_x(), y - self.get_pos_y()]
        v = [vx - self.velocity_x, vy - self.velocity_y]
        skalar_v_r = v[0] * r[0] + v[1] * r[1]
        sqr_r = r[0] ** 2 + r[1] ** 2
        vx = vx - ((2 * m_asteroidy) / (m_statku + m_asteroidy)) * (skalar_v_r / sqr_r) * r[0]
        vy = vy - ((2 * m_asteroidy) / (m_statku + m_asteroidy)) * (skalar_v_r / sqr_r) * r[1]
        self.velocity_x = self.velocity_x - ((2 * m_statku) / (m_statku + m_asteroidy)) * (skalar_v_r / sqr_r) * r[0]
        self.velocity_y = self.velocity_y - ((2 * m_statku) / (m_statku + m_asteroidy)) * (skalar_v_r / sqr_r) * r[1]
        self.velocity_x = int(self.velocity_x)
        self.velocity_y = int(self.velocity_y)
        vx = int(vx)
        vy = int(vy)

        vx = max(min(vx, max_v), -max_v)
        vy = max(min(vy, max_v), -max_v)
        self.velocity_x = max(min(self.velocity_x, max_v), -max_v)
        self.velocity_y = max(min(self.velocity_y, max_v), -max_v)

        return vx, vy
    def shoot(self):
        bullet_x = self.get_pos_x() - 0
        bullet_y = self.get_pos_y() + 20
        return bullet_x, bullet_y
    def simple_collision(self,vx,vy):
        vx=-vx
        vy=-vy
        self.velocity_x=-self.velocity_x
        self.velocity_y=-self.velocity_y
        return vx,vy

    def collision(self,vx, vy, x, y, m_statku,hard_mode):
        if hard_mode:
            return self.change_direction_and_speed(vx, vy, x, y, m_statku)
        else :
          return self.simple_collision(vx,vy)