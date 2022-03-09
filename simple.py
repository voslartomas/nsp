"""Nurse scheduling problem with shift requests."""
from ortools.sat.python import cp_model


def main():
    # This program tries to find an optimal assignment of nurses to shifts
    # (3 shifts per day, for 7 days), subject to some constraints (see below).
    # Each nurse can request to be assigned to specific shifts.
    # The optimal assignment maximizes the number of fulfilled shift requests.
    names = ['Alena', 'Petra', 'Nada', 'Patricie', 'Lenka', 'Lucka']
    num_nurses = 6
    num_shifts = 2
    num_days = 30
    all_nurses = range(num_nurses)
    all_shifts = range(num_shifts)
    all_days = range(num_days)

    shift_requests = [[[1] * 2 for i in range(num_days)] for s in all_nurses];
    print(shift_requests)
    # Creates the model.
    model = cp_model.CpModel()

    # Creates shift variables.
    # shifts[(n, d, s)]: nurse 'n' works shift 's' on day 'd'.
    shifts = {}
    for n in all_nurses:
        for d in all_days:
            for s in all_shifts:
                shifts[(n, d, s)] = model.NewBoolVar('shift_n%id%is%i' % (n, d, s))

    # Each shift is assigned to exactly one nurse in .
    for d in all_days:
        for s in all_shifts:
            model.Add(sum(shifts[(n, d, s)] for n in all_nurses) == 1)

    # Each nurse works at most one shift per day.
    for n in all_nurses:
        for d in all_days:
            model.Add(sum(shifts[(n, d, s)] for s in all_shifts) <= 1)

    # Try to distribute the shifts evenly, so that each nurse works
    # min_shifts_per_nurse shifts. If this is not possible, because the total
    # number of shifts is not divisible by the number of nurses, some nurses will
    # be assigned one more shift.
    min_shifts_per_nurse = (num_shifts * num_days) // num_nurses
    if num_shifts * num_days % num_nurses == 0:
        max_shifts_per_nurse = min_shifts_per_nurse
    else:
        max_shifts_per_nurse = min_shifts_per_nurse + 1
    for n in all_nurses:
        num_shifts_worked = 0
        for d in all_days:
            for s in all_shifts:
                num_shifts_worked += shifts[(n, d, s)]
        model.Add(min_shifts_per_nurse <= num_shifts_worked)
        model.Add(num_shifts_worked <= max_shifts_per_nurse)

    # pylint: disable=g-complex-comprehension
    model.Maximize(
        sum(shift_requests[n][d][s] * shifts[(n, d, s)] for n in all_nurses
            for d in all_days for s in all_shifts))

    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        print('Solution:')
        for d in all_days:
            print('Day', d)
            for n in all_nurses:
                for s in all_shifts:
                    if solver.Value(shifts[(n, d, s)]) == 1:
                        if shift_requests[n][d][s] == 1:
                            print('Nurse', names[n], 'works shift', s, '(requested).')
                        else:
                            print('Nurse', names[n], 'works shift', s,
                                  '(not requested).')
            print()
        print(f'Number of shift requests met = {solver.ObjectiveValue()}',
              f'(out of {num_nurses * min_shifts_per_nurse})')
    else:
        print('No optimal solution found !')

    # Statistics.
    print('\nStatistics')
    print('  - conflicts: %i' % solver.NumConflicts())
    print('  - branches : %i' % solver.NumBranches())
    print('  - wall time: %f s' % solver.WallTime())


if __name__ == '__main__':
    main()
