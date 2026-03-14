import math
from datetime import datetime, timedelta

# Parâmetros FSRS v4 (Simplificado para o IPUB)
# Pesos padrão para o algoritmo FSRS
DEFAULT_W = [0.4, 0.6, 2.4, 5.8, 4.93, 0.94, 0.86, 0.01, 1.49, 0.14, 0.94, 2.18, 0.05, 0.34, 1.26, 0.26, 2.05]

class FSRS:
    def __init__(self, w=DEFAULT_W):
        self.w = w

    def init_card(self):
        """Inicializa um card novo (State 0)"""
        return {
            "state": 0,
            "stability": 0.0,
            "difficulty": 0.0,
            "elapsed_days": 0,
            "scheduled_days": 0,
            "reps": 0,
            "lapses": 0,
            "last_review": None,
            "due": datetime.now()
        }

    def next_interval(self, stability):
        new_interval = stability * 9 / 10 # Retenção de 90%
        return max(1, round(new_interval))

    def evaluate(self, card, rating):
        """
        Calcula o próximo estado do card com base na avaliação (1-4)
        Rating: 1=Again, 2=Hard, 3=Good, 4=Easy
        """
        # Simplificação do algoritmo FSRS para o IPUB
        # Em uma implementação real, usaríamos as fórmulas de estabilidade e dificuldade
        
        state = card['state']
        stability = card['stability']
        difficulty = card['difficulty']
        reps = card['reps']
        lapses = card['lapses']
        
        if state == 0: # New Card
            # Valores iniciais baseados no rating
            stability = self.w[rating - 1]
            difficulty = self.w[4] - (rating - 3) * self.w[5]
            state = 1 # Learning
        else:
            if rating == 1: # Again
                lapses += 1
                stability = self.w[4] / 2 # Reduz estabilidade significativamente
                state = 1 # Volta para aprendizado
            else:
                # Atualização de estabilidade e dificuldade (versão linear simplificada)
                difficulty = max(1, min(10, difficulty - (rating - 3) * 0.5))
                stability = stability * (1 + math.exp(self.w[6]) * (11 - difficulty) * math.pow(stability, -0.1))
                state = 2 # Review
                
        reps += 1
        scheduled_days = self.next_interval(stability)
        last_review = datetime.now()
        due = last_review + timedelta(days=scheduled_days)
        
        return {
            "state": state,
            "stability": stability,
            "difficulty": difficulty,
            "elapsed_days": scheduled_days,
            "scheduled_days": scheduled_days,
            "reps": reps,
            "lapses": lapses,
            "last_review": last_review,
            "due": due
        }
