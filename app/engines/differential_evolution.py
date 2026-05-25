import random
from dataclasses import dataclass

from app.domain.models import OptimizationParameters


@dataclass(frozen=True)
class OptimizationResult:
    density_per_hectare: float
    duration_days: int
    objective_value: float
    generations: int
    converged: bool


class DifferentialEvolutionOptimizer:
    def __init__(self, seed: int) -> None:
        self._random = random.Random(seed)

    def optimize(
        self,
        bounds: list[tuple[float, float]],
        objective,
        params: OptimizationParameters,
    ) -> OptimizationResult:
        population = [self._random_vector(bounds) for _ in range(params.population_size)]
        fitness = [objective(*vector) for vector in population]

        best_index = max(range(len(population)), key=lambda index: fitness[index])
        best_vector = population[best_index][:]
        best_score = fitness[best_index]
        last_best_score = best_score
        converged = False

        for generation in range(1, params.max_generations + 1):
            for i in range(params.population_size):
                mutant = self._mutate(population, bounds, i, params.mutation_factor)
                trial = self._crossover(population[i], mutant, params.crossover_rate)
                trial_score = objective(*trial)
                if trial_score > fitness[i]:
                    population[i] = trial
                    fitness[i] = trial_score

            best_index = max(range(len(population)), key=lambda index: fitness[index])
            best_vector = population[best_index][:]
            best_score = fitness[best_index]

            if abs(best_score - last_best_score) <= params.epsilon:
                converged = True
                return OptimizationResult(
                    density_per_hectare=best_vector[0],
                    duration_days=max(1, round(best_vector[1])),
                    objective_value=best_score,
                    generations=generation,
                    converged=converged,
                )
            last_best_score = best_score

        return OptimizationResult(
            density_per_hectare=best_vector[0],
            duration_days=max(1, round(best_vector[1])),
            objective_value=best_score,
            generations=params.max_generations,
            converged=converged,
        )

    def _random_vector(self, bounds: list[tuple[float, float]]) -> list[float]:
        return [self._random.uniform(lower, upper) for lower, upper in bounds]

    def _mutate(
        self,
        population: list[list[float]],
        bounds: list[tuple[float, float]],
        current_index: int,
        mutation_factor: float,
    ) -> list[float]:
        candidates = [index for index in range(len(population)) if index != current_index]
        r1, r2, r3 = self._random.sample(candidates, 3)
        base, b, c = population[r1], population[r2], population[r3]
        mutant = []
        for index, (lower, upper) in enumerate(bounds):
            value = base[index] + mutation_factor * (b[index] - c[index])
            mutant.append(min(max(value, lower), upper))
        return mutant

    def _crossover(
        self,
        target: list[float],
        mutant: list[float],
        crossover_rate: float,
    ) -> list[float]:
        pivot = self._random.randrange(len(target))
        trial = []
        for index in range(len(target)):
            if index == pivot or self._random.random() < crossover_rate:
                trial.append(mutant[index])
            else:
                trial.append(target[index])
        return trial

