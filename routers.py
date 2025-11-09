from typing import Tuple
from core import Message, Node

class EpidemicRouter:
    """Epidemic routing: on contact, exchange anything the other node lacks."""
    def exchange(self, a: Node, b: Node, now:int) -> Tuple[int, int]:
        tx_a = 0
        tx_b = 0
        for mid, msg in list(a.buffer.items()):
            if msg.alive(now) and not b.has_message(mid):
                b.store(msg); tx_a += 1
        for mid, msg in list(b.buffer.items()):
            if msg.alive(now) and not a.has_message(mid):
                a.store(msg); tx_b += 1
        return tx_a, tx_b

class SprayWaitRouter:
    """Binary Spray-and-Wait: start with L copies; on first transfers, split copies."""
    def __init__(self, L:int=8):
        self.L = max(1, int(L))

    def exchange(self, a: Node, b: Node, now:int) -> Tuple[int,int]:
        tx_a = tx_b = 0
        for mid, msg in list(a.buffer.items()):
            if not msg.alive(now) or b.has_message(mid): 
                continue
            if msg.copies is None:
                msg.copies = self.L
            if msg.copies > 1:
                give = msg.copies // 2
                if give > 0:
                    b.store(msg); msg.copies -= give; tx_a += 1
        for mid, msg in list(b.buffer.items()):
            if not msg.alive(now) or a.has_message(mid): 
                continue
            if msg.copies is None:
                msg.copies = self.L
            if msg.copies > 1:
                give = msg.copies // 2
                if give > 0:
                    a.store(msg); msg.copies -= give; tx_b += 1
        return tx_a, tx_b
