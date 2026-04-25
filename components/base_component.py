import config

class Component:
    def __init__(self, name):
        self.name = name
        self.health = 1.0
        self.cumulative_stress = 0.0

    def get_status(self):
        if self.health >= config.HEALTH_FUNCTIONAL:
            return "FUNCTIONAL"
        elif self.health >= config.HEALTH_DEGRADED:
            return "DEGRADED"
        elif self.health >= config.HEALTH_CRITICAL:
            return "CRITICAL"
        else:
            return "FAILED"