from operator import itemgetter
from random import uniform, randint, shuffle, seed
import operator
from collections import Counter
from math import factorial
from functools import reduce
from datetime import datetime


class Person:
    def __init__(self, preference):
        self.preference = preference

    def choose(self, popular_opinion, trend_strength, iteration, number_of_options):
        # I don't care about other people's opinions so I disregard current_pool
        return self.preference

    def __repr__(self):
        return str(self.bias)


class ReasonablePerson(Person):
    def __init__(self, preference, peer_pressure_threshold):
        Person.__init__(self, preference)
        self.peer_pressure_threshold = peer_pressure_threshold

    def choose(self, popular_opinion, trend_strength, iteration, number_of_options):
        # I might consider changing my mind if the pressure is strong enough
        if popular_opinion and trend_strength > self.peer_pressure_threshold:
            return popular_opinion
        elif iteration > number_of_options:
            return popular_opinion
        else:
            return self.preference

    def __repr__(self):
        return str(self.bias) + ' ' + str(self.peer_pressure_threshold)


def evaluate_majority(quorum, max_iterations=10):
    pool_result = {}
    iteration = 0
    quorum_size = len(quorum)
    number_of_options = 3
    # algorithm analysis data
    first_round = ()

    while not has_reached_majority(pool_result):
        previous_result = pool_result
        pool_result = {}
        result = most_popular(previous_result)
        if result:
            popular_opinion = result[0][0]
            maximum_votes = result[0][1]
        else:
            popular_opinion = None
            maximum_votes = 0

        trend_strength = float(maximum_votes / quorum_size)

        for member in quorum:
            vote = member.choose(popular_opinion, trend_strength, iteration, number_of_options)

            if vote not in pool_result:
                pool_result[vote] = 1
            else:
                pool_result[vote] += 1

        iteration += 1
        if iteration == 1:
            first_round = most_popular(pool_result)

        if iteration >= max_iterations:
            raise RuntimeError('Iteration {} ended, could not reach consensus.'.format(iteration),
                               (most_popular(pool_result), first_round))

    return pool_result, iteration, first_round


def has_reached_majority(pool):
    if len(pool) == 1:
        return True
    else:
        return False


def most_popular(pool):
    popularity_rank = sorted(pool.items(), key=itemgetter(1), reverse=True)
    # remove first member bias when dealing with equal distributions
    if all(item[1] == popularity_rank[0][1] for item in popularity_rank):
        shuffle(popularity_rank)
    if popularity_rank:
        return popularity_rank
    else:
        return None


def permute(elements):
    if len(elements) <= 1:
        yield elements
    else:
        for perm in permute(elements[1:]):
            for i in range(len(elements)):
                yield perm[:i] + elements[0:1] + perm[i:]


def generate_test_data(flavors, sample_size, min_threshold, max_threshold, reasonable=False, balanced=False):
    quorum = []
    for permutation in permute(flavors):
        group_preference = {}
        for index in range(len(permutation)):
            group_preference = permutation[index]

        if balanced:
            population_count = sample_size
        else:
            # reset pseudo random generator
            seed(datetime.now().microsecond)
            population_count = randint(1, sample_size)

        for n in range(population_count):
            if reasonable:
                # reset pseudo random generator
                seed(datetime.now().microsecond)
                quorum.append(ReasonablePerson(group_preference, uniform(min_threshold, max_threshold)))
            else:
                quorum.append(Person(group_preference))
    # make the sample random
    shuffle(quorum)
    return quorum


def count_permutations(symbols):
    numerator = factorial(len(symbols))
    terms = Counter(symbols).values()
    denominator = reduce(operator.mul, (factorial(term) for term in terms), 1)
    return numerator / denominator


def test_hypothesis(test_data, output_file):
    failures = 0
    try:
        result, iteration, first_round = evaluate_majority(test_data, max_iterations=10)
        output_file.write('{0}; {1}; {2}\n'.format(result, iteration, first_round))
    except RuntimeError as ex:
        failures += 1
        output_file.write('{0}; {1}; {2}\n'.format('FAIL', -1, ex))
    return failures

if __name__ == '__main__':
    min_threshold = 0.1
    max_threshold = 0.9
    failures = 0

    with open('data/extremely_low_quorum.txt', 'w') as extremely_low_quorum_file, \
            open('data/low_quorum.txt', 'w') as low_quorum_file, \
            open('data/low_quorum_balanced.txt', 'w') as low_quorum_file_balanced, \
            open('data/high_quorum.txt', 'w') as high_quorum_file, \
            open('data/high_quorum_balanced.txt', 'w') as high_quorum_file_balanced:

        for index in range(100):
            extremely_low_quorum = generate_test_data(['Chocolate', 'Vanilla', 'Strawberry'], 1,
                            min_threshold=min_threshold, max_threshold=max_threshold, reasonable=True)
            failures += test_hypothesis(extremely_low_quorum, extremely_low_quorum_file)

            low_quorum = generate_test_data(['Chocolate', 'Vanilla', 'Strawberry'], 10,
                            min_threshold=min_threshold, max_threshold=max_threshold, reasonable=True)
            failures += test_hypothesis(low_quorum, low_quorum_file)

            high_quorum = generate_test_data(['Chocolate', 'Vanilla', 'Strawberry'], 100,
                            min_threshold=min_threshold, max_threshold=max_threshold, reasonable=True)
            failures += test_hypothesis(high_quorum, high_quorum_file)

            low_quorum_balanced = generate_test_data(['Chocolate', 'Vanilla', 'Strawberry'], 10,
                            min_threshold=min_threshold, max_threshold=max_threshold, reasonable=True, balanced=True)
            failures += test_hypothesis(low_quorum_balanced, low_quorum_file_balanced)

            high_quorum_balanced = generate_test_data(['Chocolate', 'Vanilla', 'Strawberry'], 100,
                            min_threshold=min_threshold, max_threshold=max_threshold, reasonable=True, balanced=True)
            failures += test_hypothesis(high_quorum_balanced, high_quorum_file_balanced)

    print(failures)