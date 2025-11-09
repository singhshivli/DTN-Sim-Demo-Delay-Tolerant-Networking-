import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import math, random

@dataclass
class Message:
    mid: int
    src: int
    dst: int
    created_at: int
    ttl: int = 2000
    delivered_at: Optional[int] = None
    copies: Optional[int] = None  # used by Spray-and-Wait

    def alive(self, now: int) -> bool:
        return (now - self.created_at) <= self.ttl and self.delivered_at is None

@dataclass
class Node:
    nid: int
    pos: np.ndarray
    vel: np.ndarray
    buffer: Dict[int, Message] = field(default_factory=dict)

    def distance_to(self, other:'Node') -> float:
        return float(np.linalg.norm(self.pos - other.pos))

    def has_message(self, mid: int) -> bool:
        return mid in self.buffer

    def store(self, msg: Message):
        self.buffer[msg.mid] = msg

    def remove(self, mid: int):
        if mid in self.buffer:
            del self.buffer[mid]

class RandomWaypoint:
    def __init__(self, width: float, height: float, max_speed: float, seed: int = 42):
        self.width = width
        self.height = height
        self.max_speed = max_speed
        random.seed(seed)
        np.random.seed(seed)

    def init_node(self) -> Tuple[np.ndarray, np.ndarray]:
        x = random.uniform(0, self.width)
        y = random.uniform(0, self.height)
        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(0, self.max_speed)
        vx, vy = speed*math.cos(angle), speed*math.sin(angle)
        return np.array([x, y], dtype=float), np.array([vx, vy], dtype=float)

    def step(self, node: Node):
        node.pos += node.vel
        if node.pos[0] < 0 or node.pos[0] > self.width:
            node.vel[0] *= -1
            node.pos[0] = max(0, min(self.width, node.pos[0]))
        if node.pos[1] < 0 or node.pos[1] > self.height:
            node.vel[1] *= -1
            node.pos[1] = max(0, min(self.height, node.pos[1]))
        angle = random.uniform(-0.2, 0.2)
        rot = np.array([[math.cos(angle), -math.sin(angle)],
                        [math.sin(angle),  math.cos(angle)]])
        node.vel = rot @ node.vel
        speed = np.linalg.norm(node.vel)
        if speed > self.max_speed:
            node.vel = (self.max_speed / speed) * node.vel

class DTNSim:
    def __init__(self, n_nodes:int=40, width:float=400, height:float=400, radio_range:float=30,
                 max_speed:float=2.5, routing=None, seed:int=42, ttl:int=2000, gen_prob:float=0.02):
        self.n_nodes = n_nodes
        self.width = width
        self.height = height
        self.radio_range = radio_range
        self.mob = RandomWaypoint(width, height, max_speed, seed=seed)
        self.nodes: List[Node] = []
        for i in range(n_nodes):
            p, v = self.mob.init_node()
            self.nodes.append(Node(i, p, v))
        self.routing = routing
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        self.ttl = ttl
        self.gen_prob = gen_prob
        self.time = 0
        self.next_mid = 1
        self.all_messages: Dict[int, Message] = {}
        self.delivered = 0
        self.total_transmissions = 0
        self.event_log = []  # (t, delivered_this_step, transmissions_this_step, total_buffer)

    def generate_message(self):
        src = random.randrange(self.n_nodes)
        dst = random.randrange(self.n_nodes)
        while dst == src:
            dst = random.randrange(self.n_nodes)
        mid = self.next_mid
        self.next_mid += 1
        msg = Message(mid=mid, src=src, dst=dst, created_at=self.time, ttl=self.ttl)
        self.all_messages[mid] = msg
        self.nodes[src].store(msg)
        return msg

    def neighbors(self, i:int) -> List[int]:
        res = []
        ni = self.nodes[i]
        for j, nj in enumerate(self.nodes):
            if i == j: 
                continue
            if ni.distance_to(nj) <= self.radio_range:
                res.append(j)
        return res

    def step(self):
        for n in self.nodes:
            self.mob.step(n)

        import random as _r
        if _r.random() < self.gen_prob:
            self.generate_message()

        transmissions_this_step = 0
        delivered_this_step = 0
        for i in range(self.n_nodes):
            neigh = self.neighbors(i)
            for j in neigh:
                if i < j:
                    ti, tj = self.routing.exchange(self.nodes[i], self.nodes[j], self.time)
                    transmissions_this_step += (ti + tj)

        for n in self.nodes:
            to_del = []
            for mid, msg in n.buffer.items():
                if msg.dst == n.nid and msg.delivered_at is None:
                    msg.delivered_at = self.time
                    delivered_this_step += 1
                    self.delivered += 1
                    to_del.append(mid)
            for mid in to_del:
                n.remove(mid)

        for n in self.nodes:
            expired = [mid for mid, m in n.buffer.items() if not m.alive(self.time)]
            for mid in expired:
                n.remove(mid)

        total_buf = sum(len(n.buffer) for n in self.nodes)
        self.total_transmissions += transmissions_this_step
        self.event_log.append((self.time, delivered_this_step, transmissions_this_step, total_buf))
        self.time += 1

    def run(self, steps:int=1000):
        for _ in range(steps):
            self.step()

    def summary(self):
        delivered = sum(1 for m in self.all_messages.values() if m.delivered_at is not None)
        created = len(self.all_messages)
        delivery_ratio = delivered / created if created else 0.0
        delays = [m.delivered_at - m.created_at for m in self.all_messages.values() if m.delivered_at is not None]
        avg_delay = float(np.mean(delays)) if delays else None
        overhead = self.total_transmissions / delivered if delivered else None
        return {
            "messages_created": created,
            "messages_delivered": delivered,
            "delivery_ratio": delivery_ratio,
            "avg_delay_steps": avg_delay,
            "tx_overhead_per_delivery": overhead,
            "total_transmissions": self.total_transmissions
        }
